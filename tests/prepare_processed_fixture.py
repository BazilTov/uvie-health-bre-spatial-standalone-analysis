"""Build a real-data browser fixture from checksum-pinned public inputs.

Downloads occur only on an explicitly requested developer test run.
"""
import argparse,csv,gzip,hashlib,io,json,re,sys,urllib.request,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import spatial
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('output',type=Path)
parser.add_argument('--source-directory',type=Path)
parser.add_argument('--download',action='store_true')
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
source=args.source_directory or args.output
manifest=json.loads((Path(__file__).resolve().parents[1]/'benchmarks/baylor-lung/input-manifest.json').read_text())['files']
for name in ('family.soft.gz','published-normalized.csv.gz'):
 p=source/name
 if not p.exists():
  if not args.download:raise SystemExit('Missing pinned input: '+str(p))
  p.write_bytes(urllib.request.urlopen(manifest[name]['url'],timeout=120).read())
 if hashlib.sha256(p.read_bytes()).hexdigest()!=manifest[name]['sha256']:raise SystemExit('Input checksum mismatch: '+name)
soft=gzip.open(source/'family.soft.gz','rt').read();props=spatial.soft_samples(soft);metadata={}
for block in soft.split('^SAMPLE = ')[1:]:
 accession=block.splitlines()[0].strip()
 file=re.search(r'^!Sample_supplementary_file_1 = (.+)$',block,re.M).group(1).split('/')[-1]
 sid=file.split('_',1)[1].removesuffix('.gz')
 metadata[sid]={'accession':accession,**props[accession]}
rows=list(csv.reader(gzip.open(source/'published-normalized.csv.gz','rt')));ids=rows[0][1:]
rows[0][0]='gene';rows=[rows[0]]+[r for r in rows[1:] if r[0]!='NegProbe-WTX']
f=io.StringIO();csv.writer(f).writerows(rows);matrix=f.getvalue()
f=io.StringIO();w=csv.writer(f);w.writerow(['Sample_ID','participant','tissue','compartment','is_control','GEO_sample','nuclei','roi'])
for s in reversed(ids):
 r=metadata[s];w.writerow([s,'unknown',r['sample type']+' lung',r['segment'],'FALSE',r['accession'],r['nuclei'],r['roi']])
meta=f.getvalue()
p=json.dumps({'schema_version':1,'method':'Authors published log2 Q3 matrix; public sample and target selections',
 'value_type':'log2 Q3-normalized RNA','scale':'log2','qc_status':'partial','source':'GSE326968',
 'limitations':['Full author QC and sample selection have not been independently reproduced.','Participant identity is not supplied by this adapter; unknown is explicit.','NegProbe-WTX excluded from gene expression rows.']},indent=2)
for name,annotation in [('baylor-processed.zip',meta),('invalid-processed.zip',meta.replace(ids[0],'wrong_sample'))]:
 with zipfile.ZipFile(args.output/name,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('matrix.csv',matrix);z.writestr('metadata.csv',annotation);z.writestr('provenance.json',p)
c3=next(r for r in rows[1:] if r[0]=='C3')
(args.output/'expected-C3.json').write_text(json.dumps(dict(zip(ids,map(float,c3[1:])))))
print('Pinned published-data fixture:',len(rows)-1,'genes x',len(ids),'compartments; metadata order reversed.')
