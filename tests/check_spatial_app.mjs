import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const directory=resolve(process.argv[2]);
const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
try {
 const page=await browser.newPage({viewport:{width:1380,height:1100}});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto(process.env.UVIE_TEST_URL || 'http://127.0.0.1:8768');
 await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('Ready.'));
 await page.evaluate(()=>document.querySelector('#source').selectize.setValue('processed'));
 await page.locator('#datazip').setInputFiles(resolve(directory,'visium-spatial.zip'));
 await page.waitForFunction(()=>[...document.querySelectorAll('.progress-bar')].some(e=>e.textContent.includes('Upload complete')));
 await page.getByRole('button',{name:'Load processed expression',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('6 targets across 2825'),{},{timeout:60000});
 await page.getByRole('tab',{name:'Tissue map',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#tissue_map img')?.naturalWidth>0);
 const message=await page.locator('#spatial_status').textContent();
 if(!message.includes('spot')||!message.includes('pixel'))throw Error('Resolution and units missing');
 if(await page.locator('#tissue_map').getAttribute('class').then(c=>c.includes('shiny-output-error')))throw Error('Map rendering failed');
 const initialMap=await page.locator('#tissue_map img').getAttribute('src');
 await page.evaluate(()=>document.querySelector('#gene').selectize.setValue('Gfap'));
 await page.waitForFunction(previous=>{const image=document.querySelector('#tissue_map img');return image?.naturalWidth>0 && image.getAttribute('src')!==previous;},initialMap);
 await page.screenshot({path:resolve(directory,'tissue-map-browser.png'),fullPage:true});
 const map=page.waitForEvent('download');await page.locator('#map_png').click();await(await map).saveAs(resolve(directory,'downloaded-tissue-map.png'));
 const evidenceDownload=page.waitForEvent('download');await page.locator('#evidence').click();await(await evidenceDownload).saveAs(resolve(directory,'spatial-gene-evidence.json'));
 const evidence=JSON.parse(await readFile(resolve(directory,'spatial-gene-evidence.json'),'utf8'));
 const matrix=(await readFile(resolve(directory,'input/matrix.csv'),'utf8')).trim().split(/\r?\n/).map(line=>line.split(','));
 const coords=(await readFile(resolve(directory,'input/coordinates.csv'),'utf8')).trim().split(/\r?\n/).slice(1).map(line=>line.split(','));
 const lookup=new Map(coords.map(r=>[r[0],r]));
 const values=matrix.find(r=>r[0]===evidence.gene);
 if(evidence.observations.length!==2825||evidence.spatial.coordinates.length!==2825)throw Error('Spot count changed');
 for(const row of evidence.observations){const column=matrix[0].indexOf(row.sample);if(column<1||Number(values[column])!==row.expression_value)throw Error('Expression mismatch');}
 for(const row of evidence.spatial.coordinates){const source=lookup.get(row.Sample_ID);if(!source||Number(source[2])!==row.x||Number(source[3])!==row.y)throw Error('Coordinates mismatched');}
 const bundle=page.waitForEvent('download');await page.locator('#bundle').click();await(await bundle).saveAs(resolve(directory,'spatial-run.zip'));
 await page.getByRole('tab',{name:'Neighborhoods',exact:true}).click();
 await page.locator('#neighbor_radius').fill('1000');await page.locator('#neighbor_radius').press('Tab');
 await page.locator('#run_neighbors').click();
 await page.waitForFunction(()=>document.querySelector('#neighbor_status')?.textContent.includes('2825 positions;'),{},{timeout:60000});
 const graphDownload=page.waitForEvent('download');await page.locator('#neighbor_download').click();await(await graphDownload).saveAs(resolve(directory,'public-neighborhood-evidence.json'));
 await page.screenshot({path:resolve(directory,'neighborhood-browser.png'),fullPage:true});
 await page.getByRole('tab',{name:'Tissue map',exact:true}).click();
 await page.locator('#datazip').setInputFiles(resolve(directory,'invalid-spatial.zip'));
 await page.waitForFunction(()=>[...document.querySelectorAll('.progress-bar')].some(e=>e.textContent.includes('Upload complete')));
 await page.getByRole('button',{name:'Load processed expression',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('Spatial sample identifiers must match'));
 await page.waitForFunction(()=>!document.querySelector('#tissue_map img'));
 // Switching inputs must clear geometry and prevent a stale tissue map.
 await page.evaluate(()=>document.querySelector('#source').selectize.setValue('package'));
 await page.waitForFunction(()=>document.querySelector('#spatial_status')?.textContent.includes('No spatial map available'));
 await page.waitForFunction(()=>!document.querySelector('#tissue_map img'));
 if(errors.length)throw Error(errors.join('\n'));
 const report={status:'pass',scope:'Browser on the current test host; six-gene display subset, all 2825 measured spots',checks:['public input imported','registered PNG tissue map rendered','gene selection updates tissue map','spot resolution and pixel units explicit','all 2825 exported counts match source subset exactly','all 2825 exported positions match source exactly despite reversed rows','map PNG and run ZIP downloaded','public-data radius graph calculated and exported for independent checking','missing coordinate rejected and stale map cleared','source change clears stale geometry','no browser errors']};
 await writeFile(resolve(directory,'spatial-browser-checks.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify(report));
} finally {await browser.close();}
