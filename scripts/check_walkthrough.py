"""Optional standard-library checks for the pinned v0.5.0 walkthrough.

Checks downloaded release digests, recomputes a public geometry result from
the exact published example, or checks the separately synthetic paired result.
No downloads, archive extraction, package execution or biological inference.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import sys
import zipfile
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, tolerance, label):
    require(isinstance(actual, (int, float)) and not isinstance(actual, bool)
            and math.isfinite(actual) and abs(actual - expected) <= tolerance,
            f"{label}: expected {expected} within {tolerance}, got {actual}")


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def downloads(directory, expected):
    checked = []
    for name, sha in expected['assets'].items():
        path = directory / name
        if path.is_file():
            require(digest(path) == sha, f"Checksum mismatch: {name}")
            checked.append(name)
    require(checked, 'No recognized release assets found; preserve original filenames.')
    return {'matched_assets': checked,
            'not_checked': sorted(set(expected['assets']) - set(checked))}


def graph(example, evidence, expected):
    require(digest(example) == expected['assets']['Visium-mouse-brain-six-gene-example.zip'],
            'The public example ZIP differs from the pinned release.')
    p = expected['public_example']
    d = json.loads(evidence.read_text())
    require(d.get('schema_version') == 1 and d.get('gene') == p['gene'],
            'Use neighborhood schema 1 and the Gfap selection.')
    g = d['graph']
    require(g['radius'] == p['radius'] and g['units'] == p['units']
            and g['resolution'] == 'spot' and d['compartment_filter'] == 'All',
            'Use radius 1000 pixels, spot resolution and All compartments.')
    with zipfile.ZipFile(example) as z:
        coords = list(csv.DictReader(io.StringIO(z.read('coordinates.csv').decode())))
        matrix = list(csv.reader(io.StringIO(z.read('matrix.csv').decode())))
    require(len(matrix) - 1 == p['genes'], 'Example target count mismatch.')
    source = {r['Sample_ID']: (r['section_id'], float(r['x']), float(r['y'])) for r in coords}
    require(len(source) == p['positions'] == len(coords), 'Example positions mismatch.')
    row = next(r for r in matrix[1:] if r[0] == p['gene'])
    values = dict(zip(matrix[0][1:], map(float, row[1:])))
    ids = sorted(source)
    observed = {r['Sample_ID']: r for r in d['observations']}
    require(len(observed) == len(d['observations']) and set(observed) == set(ids),
            'Evidence observations do not match all source spots uniquely.')
    exported_coords = {r['Sample_ID']: (r['section_id'], r['x'], r['y']) for r in g['coordinates']}
    require(len(exported_coords) == len(g['coordinates']) and exported_coords == source,
            'Exported geometry differs from the source example.')
    neighbors = {s: [] for s in ids}
    wanted = {}
    for i, a in enumerate(ids):
        sa, x, y = source[a]
        require(sa == p['section'], 'Unexpected section.')
        for b in ids[i + 1:]:
            sb, xb, yb = source[b]
            distance = math.hypot(x - xb, y - yb)
            if sa == sb and distance <= p['radius']:
                wanted[(a, b)] = distance
                neighbors[a].append(b)
                neighbors[b].append(a)
    actual = {}
    for e in g['edges']:
        a, b = e['from'], e['to']
        require(a in source and b in source and a != b, 'Invalid endpoint or self edge.')
        require(source[a][0] == source[b][0] == e['section_id'], 'Cross-section edge.')
        key = tuple(sorted((a, b)))
        require(key not in actual, 'Duplicate undirected edge.')
        actual[key] = e['distance']
    require(set(actual) == set(wanted) and len(actual) == p['edges'], 'Edge set mismatch.')
    maximum_error = 0
    for key, value in wanted.items():
        close(actual[key], value, p['distance_atol'], 'edge distance')
        maximum_error = max(maximum_error, abs(actual[key] - value))
    for sample, ns in neighbors.items():
        r = observed[sample]
        require(r['section_id'] == source[sample][0] and r['neighbor_count'] == len(ns),
                'Observation section or neighbor count mismatch.')
        close(r['expression_value'], values[sample], p['expression_atol'], 'expression')
        if ns:
            close(r['neighbor_mean_expression'], sum(values[n] for n in ns) / len(ns),
                  p['expression_atol'], 'neighbor mean')
        else:
            require(r['neighbor_mean_expression'] is None, 'Isolate must retain a null mean.')
    return {'positions': len(ids), 'edges': len(actual), 'maximum_distance_error': maximum_error}


def comparison(path, expected):
    d = json.loads(path.read_text())
    s = expected['synthetic']
    require(d.get('schema_version') == 1, 'Use comparison schema 1.')
    for field in ['gene', 'design', 'condition_a', 'condition_b', 'compartment',
                  'participants_a', 'participants_b']:
        require(d.get(field) == s[field], f"Unexpected {field}.")
    require(d.get('inference_confirmed') is True and d['analysis_scale'] == 'supplied log2',
            'Use confirmed inference on the synthetic log2 example.')
    require('synthetic' in d['workflow']['supplied_provenance']['method'].lower(),
            'Synthetic provenance must be retained.')
    require(d['excluded_incomplete_participants'] == [], 'Unexpected incomplete pairs.')
    observed = {(r['participant'], r['condition']): r for r in d['participant_values']}
    require(len(observed) == len(d['participant_values']) == 6, 'Participant rows mismatch.')
    for i in range(1, 4):
        for condition, multiplier in [('A', 1), ('B', 2)]:
            r = observed[(f'P{i}', condition)]
            close(r['mean_log2_expression'], i * multiplier, s['atol'], 'participant mean')
            require(r['observations'] == 2 and r['sections'] == 1 and r['included'] is True,
                    'Unexpected participant sampling or inclusion.')
    close(d['effect_b_minus_a'], s['effect'], s['atol'], 'effect')
    for field, key in [('statistic', 't'), ('degrees_freedom', 'df'),
                       ('p_value_unadjusted', 'p')]:
        close(d['test'][field], s[key], s['atol'], field)
    require(len(d['test']['confidence_interval_95']) == 2, 'Confidence interval length mismatch.')
    for a, b in zip(d['test']['confidence_interval_95'], s['ci']):
        close(a, b, s['atol'], 'confidence interval')
    return {'synthetic_pairs': 3, 'effect': s['effect'], 'p_value_unadjusted': s['p']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads', type=Path)
    parser.add_argument('--visium-example', type=Path)
    parser.add_argument('--neighborhood', type=Path)
    parser.add_argument('--comparison', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if bool(args.visium_example) != bool(args.neighborhood):
        parser.error('--visium-example and --neighborhood must be supplied together')
    if not any([args.downloads, args.neighborhood, args.comparison]):
        parser.error('Choose at least one check; see REPRODUCE.md')
    expected = json.loads((Path(__file__).resolve().parents[1] /
                           'docs/reproducibility/expected-results.json').read_text())
    report = {'status': 'pass', 'release': expected['release'], 'checks': {},
              'scope': expected['scope']}
    if args.downloads:
        report['checks']['download_integrity'] = downloads(args.downloads, expected)
    if args.neighborhood:
        report['checks']['public_graph'] = graph(args.visium_example, args.neighborhood, expected)
    if args.comparison:
        report['checks']['synthetic_comparison'] = comparison(args.comparison, expected)
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + '\n')
    print(text)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, StopIteration) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
