import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from spatial import compare, dcc, gene_counts, probe_map, read_matrix


class IntakeTests(unittest.TestCase):
    def test_sparse_zero_and_negative_control_separation(self):
        mapping = {'p1': ('C3', 'Endogenous01'), 'p2': ('CD68', 'Endogenous01'),
                   'n1': ('Neg', 'Negative01')}
        self.assertEqual(gene_counts({'p1': 7, 'n1': 80}, mapping), {'C3': 7, 'CD68': 0})

    def test_missing_mapping_is_not_silently_discarded(self):
        with self.assertRaises(ValueError):
            gene_counts({'unknown': 3}, {})

    def test_duplicate_and_negative_dcc_counts_rejected(self):
        for body in ['p1,3\np1,4', 'p1,-1']:
            with self.assertRaises(ValueError):
                dcc('<Code_Summary>\n' + body + '\n</Code_Summary>')

    def test_multi_probe_requires_established_pipeline(self):
        with self.assertRaises(ValueError):
            gene_counts({}, {'p1': ('C3', 'Endogenous'), 'p2': ('C3', 'Endogenous')})

    def test_csv_rejects_nonfinite_and_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'matrix.csv'
            for text in ['gene,S\nC3,nan\n', 'gene,S,S\nC3,1,2\n',
                         'gene,S\nC3,1\nC3,2\n']:
                p.write_text(text)
                with self.assertRaises(ValueError):
                    read_matrix(p)


class AgreementTests(unittest.TestCase):
    def test_alignment_uses_identifiers_not_order(self):
        a = {'C3': {'S1': 2, 'S2': 3}, 'CD68': {'S1': 4, 'S2': 5}}
        b = {'CD68': {'S2': 5, 'S1': 4}, 'C3': {'S2': 3, 'S1': 2}}
        self.assertEqual(compare(a, b)['status'], 'pass')

    def test_bias_cannot_hide_behind_zero_sd(self):
        result = compare({'C3': {'S1': 2, 'S2': 3}}, {'C3': {'S1': 3, 'S2': 4}}, 0, 0)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['residual_sample_sd'], 0)
        self.assertEqual(result['mean_signed_error'], 1)
        self.assertEqual(result['rmse'], 1)

    def test_missing_extra_and_empty_data_fail(self):
        self.assertEqual(compare({'C3': {'S': 1}}, {})['status'], 'fail')
        self.assertEqual(compare({}, {})['status'], 'fail')
        self.assertEqual(compare({'C3': {'S': 1}}, {'C3': {'S': 1, 'T': 1}})['status'], 'fail')

    def test_tolerance_boundary_and_single_value_sd(self):
        result = compare({'C3': {'S': 1}}, {'C3': {'S': 1.125}}, .125, 0)
        self.assertEqual(result['status'], 'pass')
        self.assertIsNone(result['residual_sample_sd'])

    def test_negative_tolerance_rejected(self):
        with self.assertRaises(ValueError):
            compare({}, {}, -1, 0)


if __name__ == '__main__':
    unittest.main()
