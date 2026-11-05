import json
import os
import tempfile
import unittest

from _paths import DATA_ROOM, EXPECTED, read, run_tool

import contradictions as C
from extract_format import parse_value

PLANTED = {
    ('series_b_price_per_share', ''): ('CRITICAL', {'D01': 8.40, 'D02': 8.40, 'D05': 4.20}),
    ('arr_usd', '2026-08-31'): ('HIGH', {'D01': 14.0e6, 'D08': 11.2e6}),
    ('fully_diluted_shares', ''): ('MEDIUM', {'D02': 22e6, 'D07': 21e6}),
}


def write_extract(folder, name, rows, meta=None):
    meta = meta or {}
    lines = ['# %s (extract)' % name, '']
    for k, v in meta.items():
        lines.append('- %s: %s' % (k, v))
    lines += ['', '## Facts', '', '| field | value | source | as_of |', '|---|---|---|---|']
    for r in rows:
        r = list(r) + [''] * (4 - len(r))
        lines.append('| %s | %s | %s | %s |' % tuple(r))
    path = os.path.join(folder, name + '_extract.md')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    return path


class ExampleDataRoom(unittest.TestCase):
    """The worked example has exactly three planted contradictions."""

    @classmethod
    def setUpClass(cls):
        cls.docs = C.load_docs(DATA_ROOM)
        cls.findings, cls.agreed = C.find_contradictions(cls.docs)

    def test_loads_all_nine_extracts(self):
        self.assertEqual([d['doc_id'] for d in self.docs], ['D%02d' % i for i in range(1, 10)])

    def test_finds_the_three_planted_and_nothing_else(self):
        found = {(f['field'], f['as_of']) for f in self.findings}
        self.assertEqual(found, set(PLANTED))

    def test_values_sources_and_severity(self):
        for f in self.findings:
            sev, values = PLANTED[(f['field'], f['as_of'])]
            self.assertEqual(f['severity'], sev, f['field'])
            got = {r['doc_id']: r['value'] for r in f['facts']}
            self.assertEqual(set(got), set(values), f['field'])
            for doc_id, v in values.items():
                self.assertAlmostEqual(got[doc_id], v, places=6)
            self.assertTrue(all(r['source'] for r in f['facts']), 'every fact keeps its source')

    def test_ranked_by_severity(self):
        self.assertEqual([f['severity'] for f in self.findings], ['CRITICAL', 'HIGH', 'MEDIUM'])

    def test_near_misses_agree(self):
        agreed = {a['field'] for a in self.agreed}
        # $185M vs $184.8M and 78% vs 77.6% sit inside the 1% tolerance on purpose
        self.assertIn('post_money_valuation_usd', agreed)
        self.assertIn('gross_margin_fy2025_pct', agreed)
        self.assertEqual(len(self.agreed), 7)

    def test_cli_output_matches_expected_file(self):
        code, out = run_tool('contradictions.py', 'examples/larchwick-secondary/data-room', '--verbose')
        self.assertEqual(code, 0)
        self.assertEqual(out, read(os.path.join(EXPECTED, 'contradictions.txt')))

    def test_fail_on_find_exit_code(self):
        code, _ = run_tool('contradictions.py', 'examples/larchwick-secondary/data-room', '--fail-on-find')
        self.assertEqual(code, 1)

    def test_json_output(self):
        code, out = run_tool('contradictions.py', 'examples/larchwick-secondary/data-room', '--json')
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)['findings']), 3)


class ParseValue(unittest.TestCase):
    def test_numbers(self):
        cases = {
            '$8.40': 8.40, '8.40': 8.40, '22,000,000': 22e6, '$14.0M': 14e6, '$1.2B': 1.2e9,
            '$2.8mm': 2.8e6, '750k': 750e3, '75%': 75.0, '1.5x': 1.5, '-$9.99M': -9.99e6,
            '600,000 shares': 600e3, '15 days': 15.0, '$4.50 per share': 4.50, 7: 7.0,
        }
        for raw, want in cases.items():
            self.assertAlmostEqual(parse_value(raw), want, msg=repr(raw))

    def test_text_is_not_a_number(self):
        for raw in ['70+', '2026-02-14', 'majority of Preferred', '', None, 'Series B', '1x non-participating', '3 to 5']:
            self.assertIsNone(parse_value(raw), repr(raw))


class Rules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def run_find(self, **kw):
        return C.find_contradictions(C.load_docs(self.dir), **kw)

    def test_tolerance_boundary(self):
        write_extract(self.dir, '01-a', [('post_money_valuation_usd', '$185M', 'p.1')])
        write_extract(self.dir, '02-b', [('post_money_valuation_usd', '$184.8M', 'p.2')])
        self.assertEqual(self.run_find(tol=0.01)[0], [])
        self.assertEqual(len(self.run_find(tol=0.0005)[0]), 1)

    def test_field_tolerance_override(self):
        write_extract(self.dir, '01-a', [('arr_usd', '$10.0M', 'p.1', '2026-01-31')])
        write_extract(self.dir, '02-b', [('arr_usd', '$10.3M', 'tab 1', '2026-01-31')])
        self.assertEqual(len(self.run_find()[0]), 1)
        self.assertEqual(self.run_find(field_tol={'arr_usd': 0.05})[0], [])

    def test_different_as_of_dates_are_not_compared(self):
        write_extract(self.dir, '01-a', [('arr_usd', '$6.4M', 'tab 1', '2025-08-31')])
        write_extract(self.dir, '02-b', [('arr_usd', '$11.2M', 'tab 1', '2026-08-31')])
        findings, agreed = self.run_find()
        self.assertEqual((findings, agreed), ([], []))

    def test_text_values_are_ignored(self):
        write_extract(self.dir, '01-a', [('core_customers', '70+', 'p.3')])
        write_extract(self.dir, '02-b', [('core_customers', '52', 'tab 3')])
        self.assertEqual(self.run_find(), ([], []))

    def test_json_and_markdown_extracts_mix(self):
        write_extract(self.dir, '01-a', [('series_a_price_per_share', '$2.00', '§1.1')])
        with open(os.path.join(self.dir, '02-b_extract.json'), 'w', encoding='utf-8') as fh:
            json.dump({'doc_id': 'D02', 'facts': [
                {'field': 'series_a_price_per_share', 'value': 1.00, 'source': 'Art. IV'}]}, fh)
        findings, _ = self.run_find()
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['severity'], 'CRITICAL')
        self.assertEqual({r['doc_id'] for r in findings[0]['facts']}, {'D01', 'D02'})

    def test_only_the_facts_section_is_read(self):
        path = write_extract(self.dir, '01-a', [('fully_diluted_shares', '22,000,000', '§3.2')])
        with open(path, 'a', encoding='utf-8') as fh:
            fh.write('\n## Notes\n\n| fully_diluted_shares | 1 | not a fact | |\n')
        write_extract(self.dir, '02-b', [('fully_diluted_shares', '22,000,000', 'p.6')])
        findings, agreed = self.run_find()
        self.assertEqual(findings, [])
        self.assertEqual(len(agreed[0]['facts']), 2)

    def test_severity_thresholds(self):
        self.assertEqual(C.severity(0.50), 'CRITICAL')
        self.assertEqual(C.severity(0.25), 'CRITICAL')
        self.assertEqual(C.severity(0.20), 'HIGH')
        self.assertEqual(C.severity(0.10), 'HIGH')
        self.assertEqual(C.severity(0.045), 'MEDIUM')


if __name__ == '__main__':
    unittest.main()
