"""UVIE Spatial: dependency-free GeoMx intake and numerical agreement checks.

Raw-count exploration is not a substitute for GeoMx QC or normalization.
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import re
import statistics
import tarfile
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def dcc(text):
    sections = {}
    section = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('</'):
            section = None
        elif line.startswith('<') and line.endswith('>'):
            section = line[1:-1]
            sections[section] = {}
        elif section and line:
            row = next(csv.reader([line]))
            if len(row) != 2 or row[0] in sections[section]:
                raise ValueError('Malformed or duplicate DCC entry')
            sections[section][row[0]] = row[1]
    if 'Code_Summary' not in sections:
        raise ValueError('DCC has no Code_Summary')
    counts = {}
    for key, value in sections['Code_Summary'].items():
        number = int(value)
        if number < 0:
            raise ValueError('Negative raw count')
        counts[key] = number
    return counts, sections.get('NGS_Processing_Attributes', {})


def probe_map(pkc):
    result = {}
    for target in pkc['Targets']:
        for probe in target['Probes']:
            key = probe['RTS_ID']
            if key in result:
                raise ValueError('Duplicate probe mapping')
            result[key] = (target['DisplayName'], target['CodeClass'])
    return result


def gene_counts(counts, mapping):
    # WTA endogenous targets have one probe per gene. Never silently aggregate
    # a multi-probe target: that belongs in the established QC pipeline.
    genes = {}
    for probe, (gene, code) in mapping.items():
        if not code.startswith('Endogenous'):
            continue
        if gene in genes:
            raise ValueError('Multi-probe endogenous target requires GeomxTools')
        genes[gene] = counts.get(probe, 0)
    unknown = sorted(set(counts) - set(mapping))
    if unknown:
        raise ValueError(f'{len(unknown)} counts lack probe mappings')
    return genes


def xlsx_rows(blob):
    """Read the vendor Template sheet without a spreadsheet dependency."""
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(t.itertext()) for t in
                       ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns)]
        book = ET.fromstring(z.read('xl/workbook.xml'))
        sheet = next(s for s in book.findall('m:sheets/m:sheet', ns)
                     if s.attrib['name'] == 'Template')
        rid = sheet.attrib['{' + ns['r'] + '}id']
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        target = next(r.attrib['Target'] for r in rels if r.attrib['Id'] == rid)
        path = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        rows = []
        for row in ET.fromstring(z.read(path)).findall('m:sheetData/m:row', ns):
            cells = {}
            for cell in row.findall('m:c', ns):
                col = re.match(r'[A-Z]+', cell.attrib['r'])[0]
                idx = 0
                for char in col:
                    idx = idx * 26 + ord(char) - 64
                val = cell.find('m:v', ns)
                text = val.text if val is not None else ''
                if cell.attrib.get('t') == 's':
                    text = strings[int(text)]
                elif cell.attrib.get('t') == 'inlineStr':
                    text = ''.join(cell.find('m:is', ns).itertext())
                cells[idx - 1] = text
            rows.append(cells)
        header = rows[0]
        return [{name: row.get(i, '') for i, name in header.items()}
                for row in rows[1:] if row.get(0)]


def soft_samples(text):
    samples = {}
    for block in text.split('^SAMPLE = ')[1:]:
        lines = block.splitlines()
        sid = lines[0].strip()
        props = {}
        for line in lines:
            if line.startswith('!Sample_characteristics_ch1 = '):
                k, v = line.split(' = ', 1)[1].split(': ', 1)
                props[k] = v
            elif line.startswith('!Sample_title = '):
                props['title'] = line.split(' = ', 1)[1]
        if sid in samples:
            raise ValueError('Duplicate sample metadata')
        samples[sid] = props
    return samples


def kidney(data):
    with zipfile.ZipFile(data / 'kidney-reference.zip') as z:
        prefix = 'Kidney_Dataset/'
        mapping = probe_map(json.loads(z.read(prefix + 'pkcs/TAP_H_WTA_v1.0.pkc')))
        rows = xlsx_rows(z.read(prefix + 'annotation/kidney_demo_AOI_Annotations.xlsx'))
        samples, values = [], []
        for row in rows:
            sid = row['Sample_ID']
            counts, qc = dcc(z.read(prefix + 'dccs/' + sid + '.dcc').decode())
            genes = gene_counts(counts, mapping)
            # Keep NTCs in the inventory but outside biological exploration.
            samples.append({'id': sid, 'participant': row['slide name'],
                            'tissue': row['class'] or 'No template control',
                            'compartment': row['region'] or 'No template control',
                            'roi': row['roi'], 'area': row['area'],
                            'nuclei': row['nuclei'], 'qc': qc,
                            'control': not bool(row['class'])})
            values.append(genes)
    return samples, values


def endometriosis(data):
    mapping = probe_map(json.load(gzip.open(data / 'GSE263897_Hs_R_NGS_WTA_v1.0.pkc.gz', 'rt')))
    meta = soft_samples(gzip.open(data / 'GSE263897_family.soft.gz', 'rt').read())
    samples, values = [], []
    with tarfile.open(data / 'GSE263897_RAW.tar') as t:
        members = [m for m in t.getmembers() if m.isfile() and m.name.endswith('.dcc.gz')]
        for member in sorted(members, key=lambda m: m.name):
            sid = member.name.split('_', 1)[0]
            row = meta[sid]
            counts, qc = dcc(gzip.decompress(t.extractfile(member).read()).decode())
            samples.append({'id': sid, 'participant': row['sampleID'],
                            'tissue': row['tissue'], 'compartment': row['cell type'],
                            'roi': row['title'], 'area': None, 'nuclei': None,
                            'qc': qc, 'control': False})
            values.append(gene_counts(counts, mapping))
    if {s['id'] for s in samples} != set(meta):
        raise ValueError('Assay files and metadata do not match')
    return samples, values


def read_matrix(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) < 2 or len(set(header[1:])) != len(header[1:]):
            raise ValueError('Invalid or duplicate sample columns')
        rows = {}
        for row in reader:
            if len(row) != len(header) or row[0] in rows:
                raise ValueError('Invalid or duplicate gene row')
            numbers = [float(v) for v in row[1:]]
            if not all(math.isfinite(v) for v in numbers):
                raise ValueError('Matrix contains non-finite values')
            rows[row[0]] = dict(zip(header[1:], numbers))
    if not rows:
        raise ValueError('Empty matrix')
    return rows


def compare(reference, candidate, atol=1e-8, rtol=1e-6):
    if atol < 0 or rtol < 0 or not math.isfinite(atol + rtol):
        raise ValueError('Invalid tolerances')
    missing = extra = failed = count = 0
    mean = m2 = absolute_sum = squared_sum = maximum = 0.0
    for gene in sorted(set(reference) | set(candidate)):
        ref, got = reference.get(gene, {}), candidate.get(gene, {})
        missing += len(set(ref) - set(got))
        extra += len(set(got) - set(ref))
        for sample in sorted(set(ref) & set(got)):
            if not math.isfinite(ref[sample]) or not math.isfinite(got[sample]):
                raise ValueError('Non-finite comparison input')
            difference = got[sample] - ref[sample]
            if not math.isfinite(difference):
                raise ValueError('Numeric overflow in comparison')
            count += 1
            delta = difference - mean
            mean += delta / count
            m2 += delta * (difference - mean)
            absolute_sum += abs(difference)
            squared_sum += difference * difference
            maximum = max(maximum, abs(difference))
            failed += abs(difference) > atol + rtol * abs(ref[sample])
    return {'status': 'pass' if count and not (missing or extra or failed) else 'fail',
            'scope': 'Supplied matrices only; no claim about other processing stages',
            'atol': atol, 'rtol': rtol, 'compared_values': count,
            'missing_values': missing, 'extra_values': extra,
            'outside_tolerance': failed,
            'mean_signed_error': mean if count else None,
            'residual_sample_sd': math.sqrt(max(0, m2 / (count - 1))) if count > 1 else None,
            'mae': absolute_sum / count if count else None,
            'rmse': math.sqrt(squared_sum / count) if count else None,
            'max_absolute_error': maximum if count else None}


def build(data, output, dataset, selected):
    samples, values = (kidney if dataset == 'kidney' else endometriosis)(data)
    genes = sorted(values[0])
    if len({s['id'] for s in samples}) != len(samples):
        raise ValueError('Duplicate sample identifiers')
    if any(set(row) != set(genes) for row in values):
        raise ValueError('Gene sets differ between samples')
    requested = selected or ['C3', 'CD68', 'EPCAM', 'ACTA2', 'WNT5A', 'FN1',
                             'IL6', 'TGFB1', 'VEGFA', 'NPHS1', 'NPHS2', 'A2M']
    missing = [g for g in requested if g not in genes]
    chosen = [g for g in requested if g in genes]
    if not chosen:
        raise ValueError('No selected genes are present')
    output.mkdir(parents=True, exist_ok=True)
    matrix = output / 'raw_counts.csv'
    with matrix.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['gene'] + [s['id'] for s in samples])
        for gene in genes:
            writer.writerow([gene] + [row[gene] for row in values])
    checkpoints = None
    if dataset == 'kidney':
        expected = read_matrix(ROOT / 'benchmarks/kidney_raw_checkpoint.csv')
        actual = {g: {sid: values[next(i for i,s in enumerate(samples) if s['id'] == sid)][g]
                      for sid in row} for g, row in expected.items()}
        checkpoints = compare(expected, actual, 0, 0)
        checkpoints['scope'] = '10 published raw target-count checkpoints only'
    provenance = json.loads((ROOT / 'datasets.json').read_text())
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in data.iterdir() if p.is_file() and p.name in provenance[dataset]['files']}
    expected_hashes = provenance[dataset].get('sha256', {})
    if any(hashes.get(name) != digest for name, digest in expected_hashes.items()):
        raise ValueError('Source checksum mismatch')
    payload = {'schema_version': 1, 'dataset': dataset, 'source': provenance[dataset]['source'],
               'measurement': 'GeoMx compartment RNA counts', 'value_type': 'raw counts',
               'qc_status': 'Not evaluated', 'normalization_status': 'Not run',
               'full_benchmark_status': 'Pending R workflow execution and comparison',
               'coordinates_available': False, 'source_sha256': hashes,
               'matrix_sha256': hashlib.sha256(matrix.read_bytes()).hexdigest(),
               'available_gene_count': len(genes), 'missing_requested_genes': missing,
               'samples': samples, 'genes': chosen,
               'counts': {g: [row[g] for row in values] for g in chosen},
               'raw_checkpoint': checkpoints,
               'limits': ['Raw counts are affected by segment size and sequencing depth.',
                          'Do not infer differential expression from raw-count differences.',
                          'ROI segments are not independent biological participants.',
                          'No cell coordinates, protein measurements, or drug efficacy results.']}
    if dataset == 'kidney':
        payload['limits'].append('Vendor ZIP has 277 biological compartments; tutorial describes 276. Resolve the input-version difference before full benchmarking.')
    (output / 'evidence.json').write_text(json.dumps(payload, indent=2, allow_nan=False))
    encoded = json.dumps(payload, allow_nan=False).replace('<', '\\u003c')
    template = (ROOT / 'web/explorer.html').read_text()
    (output / 'explorer.html').write_text(template.replace('__PAYLOAD__', encoded))
    return {'samples': len(samples), 'genes': len(genes), 'raw_checkpoint': checkpoints,
            'output': str(output)}


def download(data, dataset):
    spec = json.loads((ROOT / 'datasets.json').read_text())[dataset]
    data.mkdir(parents=True, exist_ok=True)
    for name, url in spec['files'].items():
        dest = data / name
        if not dest.exists():
            temporary = dest.with_suffix(dest.suffix + '.part')
            try:
                with urllib.request.urlopen(url, timeout=90) as source, temporary.open('wb') as out:
                    while chunk := source.read(1024 * 1024):
                        out.write(chunk)
                digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
                if digest != spec['sha256'][name]:
                    raise ValueError('Download checksum mismatch')
                temporary.replace(dest)
            finally:
                temporary.unlink(missing_ok=True)
        if hashlib.sha256(dest.read_bytes()).hexdigest() != spec['sha256'][name]:
            raise ValueError('Existing download checksum mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ['fetch', 'build']:
        p = commands.add_parser(command)
        p.add_argument('--dataset', choices=['kidney', 'endometriosis'], default='kidney')
        p.add_argument('--data', type=Path, default=ROOT / 'data')
        if command == 'build':
            p.add_argument('--output', type=Path, default=ROOT / 'output')
            p.add_argument('--genes', nargs='+')
    p = commands.add_parser('compare')
    p.add_argument('reference', type=Path)
    p.add_argument('candidate', type=Path)
    p.add_argument('--atol', type=float, default=1e-8)
    p.add_argument('--rtol', type=float, default=1e-6)
    p.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.command == 'fetch':
        download(args.data, args.dataset)
        print('Dataset downloaded and checksums verified')
    elif args.command == 'build':
        print(json.dumps(build(args.data, args.output, args.dataset, args.genes), indent=2))
    else:
        result = compare(read_matrix(args.reference), read_matrix(args.candidate), args.atol, args.rtol)
        text = json.dumps(result, indent=2, allow_nan=False)
        if args.output:
            args.output.write_text(text)
        print(text)
        raise SystemExit(0 if result['status'] == 'pass' else 1)


if __name__ == '__main__':
    main()
