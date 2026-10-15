"""Regenerate scoped comparison results, retaining negative-control failures."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import spatial

root = Path(sys.argv[1]).resolve()
raw = spatial.compare(spatial.read_matrix(root / 'geomxtools-imported-probes.csv'),
                      spatial.read_matrix(root / 'python-imported-probes.csv'), atol=0, rtol=0)
(root / 'raw-import-agreement.json').write_text(json.dumps(raw, indent=2))
reference = spatial.read_matrix(root / 'published-normalized.csv')
candidate = spatial.read_matrix(root / 'conditional-log2-q3.csv')
controls = {'NegProbe-WTX'}
report = {'scope': 'Conditional normalization using published target/sample inclusion; QC not reproduced'}
for name, selected in [('all_targets', None), ('endogenous_genes', False), ('negative_control', True)]:
    def subset(matrix):
        return matrix if selected is None else {g: values for g, values in matrix.items()
                                               if (g in controls) == selected}
    report[name] = spatial.compare(subset(reference), subset(candidate), atol=1e-6, rtol=0)
(root / 'regenerated-normalization-agreement.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'raw': raw, 'normalized': report}, indent=2))
