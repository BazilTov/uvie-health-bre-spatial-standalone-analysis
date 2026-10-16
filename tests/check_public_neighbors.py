"""Independent stdlib brute-force check of the public browser-exported radius graph."""
import csv,json,math,sys
from pathlib import Path
root=Path(sys.argv[1]);data=json.loads((root/'public-neighborhood-evidence.json').read_text())
coords=list(csv.DictReader((root/'input/coordinates.csv').open()))
coord={r['Sample_ID']:(r['section_id'],float(r['x']),float(r['y'])) for r in coords}
with (root/'input/matrix.csv').open() as f:
    reader=csv.reader(f);header=next(reader);gene=next(row for row in reader if row[0]==data['gene'])
values=dict(zip(header[1:],map(float,gene[1:])))
ids=[r['Sample_ID'] for r in data['observations']]
assert len(ids)==2825 and len(set(ids))==2825
expected={}; neighbors={sample:[] for sample in ids}
for i,a in enumerate(ids):
    section,x,y=coord[a]
    for b in ids[i+1:]:
        sb,xb,yb=coord[b]
        distance=math.hypot(x-xb,y-yb)
        if section==sb and distance<=1000:
            expected[tuple(sorted((a,b)))]=distance
            neighbors[a].append(b);neighbors[b].append(a)
actual={}
for row in data['graph']['edges']:
    assert row['from']!=row['to']
    key=tuple(sorted((row['from'],row['to'])))
    assert key not in actual and coord[row['from']][0]==coord[row['to']][0]==row['section_id']
    actual[key]=row['distance']
assert expected.keys()==actual.keys()
error=max((abs(expected[k]-actual[k]) for k in expected),default=0)
assert error<1e-9
for row in data['observations']:
    sample=row['Sample_ID']; nn=neighbors[sample]
    assert row['neighbor_count']==len(nn) and row['expression_value']==values[sample]
    if nn:
        assert abs(row['neighbor_mean_expression']-sum(values[n] for n in nn)/len(nn))<1e-9
    else:assert row['neighbor_mean_expression'] is None
report={'status':'pass','scope':'Independent Python math.hypot brute-force comparison with R graph and browser export on public Visium coordinates; no biological inference','positions':len(ids),'undirected_edges':len(expected),'radius':1000,'units':'pixel','maximum_distance_error':error,'checks':['every possible pair independently evaluated','edge set identical','distances agree within 1e-9','all neighbor counts and selected-gene means agree','no cross-section or self edges']}
(root/'public-neighborhood-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
