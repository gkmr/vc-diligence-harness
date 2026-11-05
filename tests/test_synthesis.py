"""The expected synthesis passes the lint, broken copies fail it, and it agrees with the tools."""
import os
import re
import unittest

from _paths import DATA_ROOM, EXPECTED, read, run_tool

import check_synthesis as S
import contradictions as C

SYNTH = os.path.join(EXPECTED, 'master-synthesis.md')


class ExpectedSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(SYNTH)
        cls.ids = S.data_room_ids(DATA_ROOM)

    def test_passes_lint(self):
        probs, stats = S.check(self.text, self.ids)
        self.assertEqual(probs, [])
        self.assertEqual((stats['contradictions'], stats['gates']), (5, 4))

    def test_cli(self):
        code, out = run_tool('check_synthesis.py', 'examples/larchwick-secondary/expected/master-synthesis.md',
                             '--data-room', 'examples/larchwick-secondary/data-room')
        self.assertEqual(code, 0, out)
        self.assertTrue(out.startswith('check_synthesis.py: OK'))

    def test_every_tool_finding_is_in_the_synthesis(self):
        findings, _ = C.find_contradictions(C.load_docs(DATA_ROOM))
        tool_blocks = re.findall(r'\*\*Found by:\*\* contradictions\.py, spread ([\d.]+)%', self.text)
        self.assertEqual(len(tool_blocks), len(findings))
        self.assertEqual(sorted(float(x) for x in tool_blocks),
                         sorted(round(f['spread'] * 100, 1) for f in findings))

    def test_waterfall_table_is_tool_output_not_hand_typed(self):
        table = [l for l in read(os.path.join(EXPECTED, 'waterfall_spa-price.md')).splitlines() if l.startswith('|')]
        self.assertTrue(table)
        for line in table:
            self.assertIn(line, self.text)


class BrokenCopies(unittest.TestCase):
    """Each mutation breaks one rule and must be caught."""

    @classmethod
    def setUpClass(cls):
        cls.text = read(SYNTH)
        cls.ids = S.data_room_ids(DATA_ROOM)

    def assertCaught(self, text, rule):
        probs, _ = S.check(text, self.ids)
        self.assertTrue(any(p.startswith(rule) for p in probs), (rule, probs))

    def test_narrative_before_contradictions(self):
        broken = self.text.replace('## 1. Contradictions', '## Summary\n\nThe company looks great.\n\n## 1. Contradictions', 1)
        self.assertCaught(broken, 'rule 1')

    def test_gates_before_contradictions(self):
        c = self.text.index('## 1. Contradictions')
        g = self.text.index('## 2. Four gates')
        a = self.text.index('## 3. Consolidated asks')
        broken = self.text[:c] + self.text[g:a] + self.text[c:g] + self.text[a:]
        self.assertCaught(broken, 'rule 1')

    def test_severity_out_of_order(self):
        self.assertCaught(self.text.replace('### C5 [MEDIUM]', '### C5 [CRITICAL]', 1), 'rule 2')

    def test_missing_read(self):
        start = self.text.index('### C2')
        read_at = self.text.index('- **Read:**', start)
        broken = self.text[:read_at] + '- **View:**' + self.text[read_at + len('- **Read:**'):]
        self.assertCaught(broken, 'rule 2')

    def test_conflict_with_one_source(self):
        broken = self.text.replace('vs core ARR of $11.2M at 2026-08-31 [D08 tab 1].',
                                   'vs core ARR of $11.2M at 2026-08-31.', 1)
        self.assertCaught(broken, 'rule 2')

    def test_missing_gate(self):
        self.assertCaught(self.text.replace('### Gate 4 - Exit path', '### Exit path', 1), 'rule 3')

    def test_untagged_figure(self):
        broken = self.text.replace('- Lockup: 180 days after an IPO, binding on transferees [D04 §2.11].',
                                   '- Lockup: 180 days after an IPO, and we think a 25% haircut is fair.', 1)
        self.assertCaught(broken, 'rule 4')

    def test_table_without_caption(self):
        broken = self.text.replace('Income statement, $M, unaudited [D06 P&L, note 4]. The two rows marked calc are ours [calc].',
                                   'Income statement, $M, unaudited.', 1)
        self.assertCaught(broken, 'rule 4')

    def test_asks_numbering_gap(self):
        self.assertCaught(self.text.replace('\n9. Monthly inference', '\n10. Monthly inference', 1), 'rule 5')

    def test_missing_closing_line(self):
        cut = self.text.index('**Decisive open item:**')
        self.assertCaught(self.text[:cut], 'rule 6')

    def test_tag_for_a_document_that_does_not_exist(self):
        self.assertCaught(self.text.replace('[D04 §2.11]', '[D12 §2.11]', 1), 'rule 7')


if __name__ == '__main__':
    unittest.main()
