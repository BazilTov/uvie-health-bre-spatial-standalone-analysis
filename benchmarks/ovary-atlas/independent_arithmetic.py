from pathlib import Path
import csv,gzip,json,re,tarfile,sys
import numpy as np
if len(sys.argv)!=2: raise SystemExit('Usage: independent_arithmetic.py DATA_DIRECTORY')
b=Path(sys.argv[1])
meta=[r for r in csv.DictReader((b/'sample-annotation.csv').open()) if r['donor']=='2']
meta.sort(key=lambda r:r['Sample_ID'])
ids=[r['Sample_ID']+'.dcc' for r in meta]
pkc=json.load(gzip.open(b/'panel.pkc.gz','rt'))
genes={}
for t in pkc['Targets']:
 if t['CodeClass'].startswith('Endogenous'):
  assert len(t['Probes'])==1
  assert t['DisplayName'] not in genes
  genes[t['DisplayName']]=t['Probes'][0]['RTS_ID']
labels=sorted(genes)
x=np.zeros((len(labels),len(meta)),dtype=float)
with tarfile.open(b/'raw.tar') as archive:
 files={m.name.split('_',1)[1].removesuffix('.gz'):m for m in archive if m.isfile()}
 for j,sid in enumerate(ids):
  text=gzip.decompress(archive.extractfile(files[sid]).read()).decode()
  section=text.split('<Code_Summary>')[1].split('</Code_Summary>')[0]
  counts=dict(csv.reader(line for line in section.splitlines() if line.strip()))
  x[:,j]=[max(1,int(counts.get(genes[g],0))) for g in labels]
logcpm=np.log2(x/x.sum(axis=0)[None,:]*1e6)
sorted_values=np.sort(logcpm,axis=0)
target=sorted_values.mean(axis=1)
q=np.empty_like(logcpm)
for j in range(x.shape[1]):
 order=np.argsort(logcpm[:,j],kind='stable');v=logcpm[order,j]
 starts=np.r_[0,np.flatnonzero(v[1:]!=v[:-1])+1];ends=np.r_[starts[1:],len(v)]
 ranks=np.repeat((starts+ends-1)/2,ends-starts)
 q[order,j]=np.interp(ranks,np.arange(len(target)),target)
clusters=np.array([r['cluster'] for r in meta]);centroids=np.column_stack([q[:,clusters==str(k)].mean(axis=1) for k in range(1,10)])
def compare(path,values,expected_columns):
 reader=csv.reader(path.open());header=next(reader)[1:];assert len(header)==len(set(header))
 data={r[0]:[float(v) for v in r[1:]] for r in reader};assert set(data)==set(labels)
 reference=np.array([[data[g][header.index(s)] for s in expected_columns] for g in labels])
 errors=values-reference
 return {'compared_values':errors.size,'outside_tolerance':int(np.sum(np.abs(errors)>1e-10)),'max_absolute_error':float(np.max(np.abs(errors))),'rmse':float(np.sqrt(np.mean(errors**2)))}
report={'scope':'Independent NumPy arithmetic from original DCCs; same provisional annotations and explicitly specified algorithm, not proof of author recipe or mapping',
 'normalized_matrix_vs_R':compare(b/'donor2-log2-cpm-quantile.csv',q,ids),
 'cluster_means_vs_R':compare(b/'candidate-donor2-centroids.csv',centroids,[str(k) for k in range(1,10)]),
 'mapping_status':'provisional; no labels changed or optimized to match reference',
 'numpy_version':np.__version__}
report['status']='pass' if all(report[k]['outside_tolerance']==0 for k in ['normalized_matrix_vs_R','cluster_means_vs_R']) else 'fail'
(b/'independent-arithmetic-agreement.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
