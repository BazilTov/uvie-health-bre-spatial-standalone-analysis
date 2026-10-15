"""Prepare checksum-pinned public inputs without changing application code."""
import csv
import gzip
import hashlib
import json
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import spatial

root = Path(sys.argv[1]).resolve()
manifest = json.loads(Path(__file__).with_name('input-manifest.json').read_text())
for name, expected in manifest['files'].items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected['sha256']:
        raise SystemExit(f'Input checksum mismatch: {name}')
destination = root / 'intake'
destination.mkdir(exist_ok=True)
mapping = spatial.probe_map(json.loads(gzip.open(root / 'panel.pkc.gz', 'rt').read()))
metadata = spatial.soft_samples(gzip.open(root / 'family.soft.gz', 'rt').read())
samples = {}
annotations = []
with tarfile.open(root / 'raw.tar') as archive:
    for member in archive.getmembers():
        if not member.isfile():
            continue
        accession, filename = Path(member.name).name.split('_', 1)
        if not filename.endswith('.dcc.gz'):
            raise ValueError('Unexpected raw archive member')
        filename = filename.removesuffix('.gz')
        if filename in samples:
            raise ValueError('Duplicate sample identifier')
        text = gzip.decompress(archive.extractfile(member).read()).decode()
        counts, _ = spatial.dcc(text)
        spatial.gene_counts(counts, mapping)  # validates mapping and target support
        samples[filename] = counts
        (destination / filename).write_text(text)
        row = metadata[accession]
        annotations.append([filename.removesuffix('.dcc'), accession, row['sample type'],
                            row['segment'], row['roi'], row['slide'], row['nuclei']])
with (root / 'sample-annotation.csv').open('w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Sample_ID', 'GEO_sample', 'group', 'segment', 'roi', 'slide', 'nuclei'])
    writer.writerows(annotations)
with (root / 'python-imported-probes.csv').open('w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Probe_ID', *samples])
    for probe in mapping:
        writer.writerow([probe, *[counts.get(probe, 0) for counts in samples.values()]])
with gzip.open(root / 'panel.pkc.gz', 'rt') as file:
    (destination / 'panel.pkc').write_text(file.read())
with gzip.open(root / 'published-normalized.csv.gz', 'rt') as file:
    (root / 'published-normalized.csv').write_text(file.read())
print('Pinned public inputs prepared; no QC thresholds or application code changed.')
