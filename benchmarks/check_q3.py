"""Independently verify the reference package's Q3 arithmetic in Python.

This verifies normalization on the retained input matrix; it does not validate
the biological model or independently establish filtering ground truth.
"""
import argparse
import csv
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from spatial import compare, read_matrix


def quantile7(values, probability=.75):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    raw = read_matrix(args.directory / 'retained_raw.csv')
    normalized = read_matrix(args.directory / 'q3_normalized.csv')
    samples = list(next(iter(raw.values())))
    quantiles = {s: quantile7([row[s] for row in raw.values()]) for s in samples}
    if any(q <= 0 for q in quantiles.values()):
        raise ValueError('Q3 must be positive')
    geomean = math.exp(statistics.mean(math.log(q) for q in quantiles.values()))
    expected = {gene: {s: value * geomean / quantiles[s] for s, value in row.items()}
                for gene, row in raw.items()}
    result = compare(expected, normalized, atol=1e-8, rtol=1e-9)
    result['scope'] = 'Independent Q3 arithmetic against GeomxTools on the retained matrix, not independent validation of filtering or biology'
    result['method'] = 'R type-7 75th percentile per segment; factor = Q3 / geometric mean of segment Q3 values'
    (args.directory / 'q3-arithmetic-agreement.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'pass' else 1)


if __name__ == '__main__':
    main()
