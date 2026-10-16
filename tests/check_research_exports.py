"""Assert complete runs retain current analyses and remove invalidated ones."""
import json,sys,zipfile
from pathlib import Path
p=Path(sys.argv[1])
with zipfile.ZipFile(p/'research-run.zip') as z:
    assert json.loads(z.read('comparison.json'))==json.loads((p/'participant-comparison.json').read_text())
    assert json.loads(z.read('neighborhoods.json'))['graph']['radius']==1
    for name in ('matrix.csv','metadata.csv','provenance.json','coordinates.csv','spatial.json'):assert z.read(name)==(p/name).read_bytes()
with zipfile.ZipFile(p/'cleared-research-run.zip') as z:
    assert 'comparison.json' not in z.namelist() and 'neighborhoods.json' not in z.namelist()
    for name in ('matrix.csv','metadata.csv','provenance.json','coordinates.csv','spatial.json'):assert z.read(name)==(p/name).read_bytes()
report={'status':'pass','checks':['current participant and neighborhood JSON included in complete run','original inputs unchanged','stale analysis files removed after selection changes']}
(p/'research-export-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
