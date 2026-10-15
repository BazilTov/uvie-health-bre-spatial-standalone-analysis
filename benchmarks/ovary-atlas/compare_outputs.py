import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import spatial
if len(sys.argv)!=2: raise SystemExit('Supply DATA_DIRECTORY')
b=Path(sys.argv[1])
c=spatial.read_matrix(b/'geomxtools-imported-probes.csv')
c={g:{s.removesuffix('.dcc'):v for s,v in row.items()} for g,row in c.items()}
raw=spatial.compare(spatial.read_matrix(b/'python-imported-probes.csv'),c,atol=0,rtol=0)
normalized=spatial.compare(spatial.read_matrix(b/'published-donor2-centroids.csv'),spatial.read_matrix(b/'candidate-donor2-centroids.csv'),atol=1e-6,rtol=0)
for name,result in [('raw-import-agreement',raw),('donor2-centroid-agreement',normalized)]:
 (b/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
 print(name,result['status'])
