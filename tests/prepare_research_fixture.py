"""Small synthetic design fixture: known geometry and known paired effects, not biological validation."""
import csv,json,sys,zipfile
from pathlib import Path
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
ids=[];meta=[];coords=[];values=[]
for p in range(1,4):
    for condition in ('A','B'):
        for repeat in range(2):
            sample=f'P{p}_{condition}_{repeat}'
            ids.append(sample);values.append(p*(1 if condition=='A' else 2))
            meta.append([sample,f'P{p}',condition,'tissue','stroma','FALSE'])
            coords.append([sample,f'P{p}_{condition}',3*repeat,4*repeat])
def write(name,rows):
    with (out/name).open('w',newline='') as f:csv.writer(f).writerows(rows)
write('matrix.csv',[['gene',*ids],['Target',*values],['Other',*[v*2 for v in values]]])
write('metadata.csv',[['Sample_ID','participant','condition','tissue','compartment','is_control'],*reversed(meta)])
write('coordinates.csv',[['Sample_ID','section_id','x','y'],*reversed(coords)])
(out/'provenance.json').write_text(json.dumps({'schema_version':1,'method':'Synthetic known-value verification fixture; not biological data','value_type':'synthetic normalized expression','scale':'log2','qc_status':'not_assessed'}))
(out/'spatial.json').write_text(json.dumps({'schema_version':1,'units':'um','resolution':'spot','source':'Synthetic measured-coordinate test fixture','y_direction':'down'}))
with zipfile.ZipFile(out/'research-fixture.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['matrix.csv','metadata.csv','coordinates.csv','provenance.json','spatial.json']:z.write(out/name,name)
