import contextlib
import io
import os
import tempfile
import unittest

from _paths import DATA_ROOM, EXPECTED, read, run_tool

import register as R


def touch(folder, name, text='x\n'):
    with open(os.path.join(folder, name), 'w', encoding='utf-8') as fh:
        fh.write(text)


class ExampleRegister(unittest.TestCase):
    def test_nine_documents_all_layers_all_merged(self):
        synthesis = read(os.path.join(EXPECTED, 'master-synthesis.md'))
        rows = R.build(DATA_ROOM, synthesis)
        self.assertEqual([r['doc_id'] for r in rows], ['D%02d' % i for i in range(1, 10)])
        self.assertTrue(all(not r['missing'] for r in rows))
        self.assertTrue(all(r['merged'] for r in rows))
        self.assertEqual(rows[4]['date'], '2026-02-27')
        self.assertEqual(rows[6]['basis'], 'third-party report')

    def test_cli_matches_expected_and_check_passes(self):
        code, out = run_tool('register.py', 'examples/larchwick-secondary/data-room',
                             '--synthesis', 'examples/larchwick-secondary/expected/master-synthesis.md', '--check')
        self.assertEqual(code, 0)
        self.assertEqual(out, read(os.path.join(EXPECTED, 'register.md')))


class RawFolder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_numbers_unnumbered_files_around_numbered_ones(self):
        touch(self.dir, '02-voting-agreement.pdf')
        touch(self.dir, 'Board deck 2026-05-01.pdf')
        touch(self.dir, 'cap table.xlsx')
        rows = R.build(self.dir)
        got = {r['stem']: (r['num'], r['date']) for r in rows}
        self.assertEqual(got['02-voting-agreement'], (2, '?'))
        self.assertEqual(got['Board deck 2026-05-01'], (1, '2026-05-01'))
        self.assertEqual(got['cap table'][0], 3)
        self.assertTrue(all(r['missing'] == ['verbatim', 'extract', 'bluf'] for r in rows))

    def test_gaps_and_unmerged_fail_check(self):
        touch(self.dir, '01-spa_verbatim.md')
        touch(self.dir, '01-spa_extract.md', '# D01 - SPA (extract)\n\n- date: 2026-03-02\n')
        touch(self.dir, '01-spa_bluf.md')
        touch(self.dir, '02-charter_extract.md', '# D02 - Charter (extract)\n')
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        touch(other.name, 'synth.md', 'cites [D01 §1.1] only\n')
        synth = os.path.join(other.name, 'synth.md')
        rows = {r['doc_id']: r for r in R.build(self.dir, read(synth))}
        self.assertEqual(set(rows), {'D01', 'D02'})
        self.assertEqual(rows['D01']['missing'], [])
        self.assertTrue(rows['D01']['merged'])
        self.assertEqual(rows['D02']['missing'], ['verbatim', 'bluf'])
        self.assertFalse(rows['D02']['merged'])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = R.main([self.dir, '--synthesis', synth, '--check'])
        self.assertEqual(code, 1)
        self.assertIn('D02 02-charter: missing verbatim, bluf; not cited in synthesis', out.getvalue())


if __name__ == '__main__':
    unittest.main()
