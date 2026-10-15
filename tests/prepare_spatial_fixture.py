"""Create a declared six-gene display fixture from official 10x Visium files.

Retains every filtered barcode. This is an import/alignment/display test, not a
full-transcriptome normalization or biological validation benchmark.
"""
import csv
import gzip
import hashlib
import io
import json
import shutil
import tarfile
import zipfile
from pathlib import Path
import argparse
import subprocess

ARCHIVES = {
    'spatial.tar.gz': '783a21a101a2fc3f39aa76a33f40dff67be9162464a43839b90fe7d1d836537e',
    'filtered_feature_bc_matrix.tar.gz': '8b0267ad2e433cec1b7cad89320735e778abe8e0e524b5a3c3f8e40b23eec8a3',
}

def prepare(root):
    root = Path(root)
    for name, expected in ARCHIVES.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Public input archive changed: ' + name)
    output = root / 'input'
    output.mkdir(exist_ok=True)
    with tarfile.open(root / 'spatial.tar.gz') as archive:
        positions = list(csv.reader(io.TextIOWrapper(archive.extractfile('spatial/tissue_positions_list.csv'))))
        scale = json.load(archive.extractfile('spatial/scalefactors_json.json'))
        with (output / 'tissue.png').open('wb') as handle:
            shutil.copyfileobj(archive.extractfile('spatial/tissue_lowres_image.png'), handle)
    with tarfile.open(root / 'filtered_feature_bc_matrix.tar.gz') as archive:
        def lines(name):
            member = next(m for m in archive.getmembers() if m.name.endswith('/' + name + '.gz'))
            return io.TextIOWrapper(gzip.GzipFile(fileobj=archive.extractfile(member)))
        barcodes = [line.strip() for line in lines('barcodes.tsv')]
        features = [line.rstrip().split('\t') for line in lines('features.tsv')]
        chosen = ['C3', 'Gfap', 'Mbp', 'Slc17a7', 'Aqp4', 'Pecam1']
        indices = {i + 1: feature[1] for i, feature in enumerate(features) if feature[1] in chosen}
        if sorted(indices.values()) != sorted(chosen):
            raise ValueError('Selected genes missing or duplicated')
        counts = {name: [0] * len(barcodes) for name in chosen}
        stream = lines('matrix.mtx')
        line = next(stream)
        while line.startswith('%'):
            line = next(stream)
        dimensions = list(map(int, line.split()))
        entries = 0
        for line in stream:
            feature, column, count = map(int, line.split())
            if feature in indices:
                counts[indices[feature]][column - 1] = count
            entries += 1
        if dimensions[:2] != [len(features), len(barcodes)] or entries != dimensions[2]:
            raise ValueError('Matrix dimensions or entry count inconsistent')
    lookup = {row[0]: row for row in positions}
    if len(lookup) != len(positions) or not all(b in lookup and lookup[b][1] == '1' for b in barcodes):
        raise ValueError('Filtered barcodes do not match measured in-tissue positions')
    def write(name, rows):
        with (output / name).open('w', newline='') as handle:
            csv.writer(handle).writerows(rows)
    write('matrix.csv', [['gene', *barcodes]] + [[gene, *counts[gene]] for gene in chosen])
    write('metadata.csv', [['Sample_ID', 'participant', 'tissue', 'compartment', 'is_control']] +
          [[b, 'mouse_1', 'brain', 'unannotated_spot', 'FALSE'] for b in reversed(barcodes)])
    write('coordinates.csv', [['Sample_ID', 'section_id', 'x', 'y']] +
          [[b, 'sagittal_anterior_section_2', lookup[b][5], lookup[b][4]] for b in reversed(barcodes)])
    source = 'https://www.10xgenomics.com/datasets/mouse-brain-serial-section-2-sagittal-anterior-1-standard-1-0-0'
    provenance = dict(schema_version=1, method='Space Ranger 1.0.0 filtered UMI counts; six-gene display subset; no additional normalization',
                      value_type='UMI counts', scale='linear', qc_status='partial', source=source,
                      species='Mus musculus', license='CC BY 4.0', attribution='10x Genomics',
                      limits='One section, one donor; no cell annotation, disease inference or participant comparison.')
    spatial = dict(schema_version=1, units='pixel', resolution='spot', y_direction='down', source=source,
                   calibration='Full-resolution source-image pixels; vendor tissue_lowres_scalef maps to preview pixels. No micrometre conversion asserted.',
                   images=[dict(section_id='sagittal_anterior_section_2', file='tissue.png',
                                pixels_per_unit=scale['tissue_lowres_scalef'], x_origin=0, y_origin=0)])
    for name, data in [('provenance.json', provenance), ('spatial.json', spatial)]:
        (output / name).write_text(json.dumps(data, indent=2))
    with zipfile.ZipFile(root / 'visium-spatial.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output.iterdir()):
            archive.write(path, path.name)
    with zipfile.ZipFile(root / 'invalid-spatial.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output.iterdir()):
            data = path.read_bytes()
            if path.name == 'coordinates.csv':
                data = b'\n'.join(data.splitlines()[:-1]) + b'\n'
            archive.writestr(path.name, data)
    report = dict(scope='Six selected genes, all filtered spots; display and identifier integrity only',
                  source=source, original_dimensions=dimensions, selected_genes=chosen, spots=len(barcodes),
                  coordinates_match=True, metadata_order='Deliberately reversed to test identifier joins',
                  archive_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.tar.gz')})
    (root / 'fixture-intake.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    root = Path(args.directory)
    root.mkdir(parents=True, exist_ok=True)
    if args.download:
        prefix = 'https://cf.10xgenomics.com/samples/spatial-exp/1.0.0/V1_Mouse_Brain_Sagittal_Anterior_Section_2/V1_Mouse_Brain_Sagittal_Anterior_Section_2_'
        for name, expected in ARCHIVES.items():
            target = root / name
            if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                temporary = root / (name + '.partial')
                # Use the same standard download client used for the original
                # verified acquisition; the public CDN rejects urllib's client.
                subprocess.run(['curl', '--fail', '--location', '--retry', '3',
                                '--connect-timeout', '30', '--max-time', '180',
                                prefix + name, '--output', str(temporary)], check=True)
                if hashlib.sha256(temporary.read_bytes()).hexdigest() != expected:
                    raise ValueError('Downloaded public archive checksum mismatch: ' + name)
                temporary.replace(target)
    prepare(root)
