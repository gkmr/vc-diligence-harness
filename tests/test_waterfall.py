import itertools
import json
import os
import tempfile
import unittest

from _paths import CAP_TABLE, EXPECTED, read, run_tool

import waterfall as W

M = 1e6


def classes_from(spec):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
        json.dump({'classes': spec}, fh)
        path = fh.name
    try:
        return W.load_cap_table(path)
    finally:
        os.unlink(path)


class KnownCases(unittest.TestCase):
    """Hand-checked cases on the example cap table (stack $33.7M, 22,000,000 fully diluted)."""

    @classmethod
    def setUpClass(cls):
        cls.cap = W.load_cap_table(CAP_TABLE)

    def test_stack(self):
        stack = sum(W.preference(c) for c in self.cap if c['kind'] == 'preferred')
        self.assertAlmostEqual(stack, 33.7 * M, places=2)

    def test_exit_below_stack_gives_common_zero(self):
        for exit_value in (0, 10 * M, 20 * M, 33.0 * M):
            self.assertEqual(W.common_per_share(exit_value, self.cap), 0.0, exit_value)

    def test_exit_equal_to_stack_gives_common_zero(self):
        self.assertAlmostEqual(W.common_per_share(33.7 * M, self.cap), 0.0, places=9)

    def test_senior_series_paid_first_when_short(self):
        paid, converting = W.solve(20 * M, self.cap)
        self.assertEqual(converting, set())
        self.assertAlmostEqual(paid['Series B'], 20 * M)
        self.assertAlmostEqual(paid['Series A'], 0.0)
        self.assertAlmostEqual(paid['Series Seed'], 0.0)

    def test_large_exit_converts_everyone(self):
        paid, converting = W.solve(500 * M, self.cap)
        self.assertEqual(converting, {'Series B', 'Series A', 'Series Seed'})
        self.assertAlmostEqual(W.common_per_share(500 * M, self.cap), 500 * M / 22e6, places=9)

    def test_middle_exit_by_hand(self):
        # $100M: Series B ($8.40) keeps its $25.2M preference; A ($2.00) and Seed ($0.50)
        # convert, so 74.8M is shared by 19,000,000 shares.
        paid, converting = W.solve(100 * M, self.cap)
        self.assertEqual(converting, {'Series A', 'Series Seed'})
        self.assertAlmostEqual(paid['Series B'], 25.2 * M)
        self.assertAlmostEqual(W.common_per_share(100 * M, self.cap), 74.8 * M / 19e6, places=9)

    def test_breakeven_for_the_block(self):
        be = W.breakeven_exit(self.cap, 4.50)
        self.assertAlmostEqual(be / M, 110.7, places=1)          # 25.2M + 4.50 x 19,000,000
        self.assertGreaterEqual(W.common_per_share(be, self.cap), 4.50 - 1e-9)
        self.assertLess(W.common_per_share(be - 1000, self.cap), 4.50)

    def test_charter_reading_lowers_the_stack(self):
        cap = W.load_cap_table(CAP_TABLE, {'Series B': 4.20})
        stack = sum(W.preference(c) for c in cap if c['kind'] == 'preferred')
        self.assertAlmostEqual(stack, 21.1 * M, places=2)
        self.assertAlmostEqual(W.breakeven_exit(cap, 4.50) / M, 99.0, places=1)  # all convert: 4.50 x 22M


class Invariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cap = W.load_cap_table(CAP_TABLE)
        cls.exits = [x * M for x in range(0, 601, 5)]

    def test_money_is_conserved(self):
        for x in self.exits:
            paid, _ = W.solve(x, self.cap)
            self.assertAlmostEqual(sum(paid.values()), x, delta=1e-3, msg=x)

    def test_common_value_never_falls_as_exit_rises(self):
        values = [W.common_per_share(x, self.cap) for x in self.exits]
        for a, b in zip(values, values[1:]):
            self.assertGreaterEqual(b + 1e-9, a)

    def test_conversion_choice_is_stable(self):
        prefs = [c['name'] for c in self.cap if c['kind'] == 'preferred']
        for x in self.exits:
            _, conv = W.solve(x, self.cap)
            for name in prefs:
                now = W.distribute(x, self.cap, conv)[name]
                flipped = conv ^ {name}
                self.assertLessEqual(W.distribute(x, self.cap, flipped)[name], now + 1e-6, (x, name))

    def test_matches_brute_force_over_all_conversion_sets(self):
        prefs = [c['name'] for c in self.cap if c['kind'] == 'preferred']
        for x in self.exits:
            stable = []
            for k in range(len(prefs) + 1):
                for combo in itertools.combinations(prefs, k):
                    conv = set(combo)
                    pay = W.distribute(x, self.cap, conv)
                    if all(W.distribute(x, self.cap, conv ^ {n})[n] <= pay[n] + 1e-6 for n in prefs):
                        stable.append(pay)
            self.assertTrue(stable, x)
            got, _ = W.solve(x, self.cap)
            common = [c['name'] for c in self.cap if c['kind'] == 'common']
            want = {round(sum(p[n] for n in common), 2) for p in stable}
            self.assertIn(round(sum(got[n] for n in common), 2), want, x)


class SmallTables(unittest.TestCase):
    def test_pari_passu_split_by_preference_amount(self):
        cap = classes_from([
            {'name': 'A', 'kind': 'preferred', 'shares': 1_000_000, 'issue_price': 6.0, 'seniority': 1},
            {'name': 'B', 'kind': 'preferred', 'shares': 1_000_000, 'issue_price': 4.0, 'seniority': 1},
            {'name': 'Common', 'kind': 'common', 'shares': 8_000_000},
        ])
        paid, conv = W.solve(5 * M, cap)
        self.assertEqual(conv, set())
        self.assertAlmostEqual(paid['A'], 3 * M)
        self.assertAlmostEqual(paid['B'], 2 * M)
        self.assertAlmostEqual(paid['Common'], 0.0)

    def test_multiple_and_conversion_ratio(self):
        cap = classes_from([
            {'name': 'P', 'kind': 'preferred', 'shares': 1_000_000, 'issue_price': 1.0, 'multiple': 2.0,
             'conversion_ratio': 2.0, 'seniority': 1},
            {'name': 'Common', 'kind': 'common', 'shares': 2_000_000},
        ])
        # Holding: 2.0M preference. Converting: 2,000,000 of 4,000,000 shares.
        paid, conv = W.solve(3 * M, cap)
        self.assertEqual(conv, set())
        self.assertAlmostEqual(paid['P'], 2 * M)
        paid, conv = W.solve(10 * M, cap)
        self.assertEqual(conv, {'P'})
        self.assertAlmostEqual(paid['P'], 5 * M)

    def test_participating_is_rejected(self):
        with self.assertRaises(ValueError):
            classes_from([{'name': 'P', 'kind': 'preferred', 'shares': 1, 'issue_price': 1, 'participating': True}])

    def test_unknown_price_override_is_rejected(self):
        with self.assertRaises(ValueError):
            W.load_cap_table(CAP_TABLE, {'Series Z': 1.0})


class Cli(unittest.TestCase):
    ARGS = ['examples/larchwick-secondary/cap-table.json', '--exits', '25,50,75,100,150,185,300,500',
            '--block-shares', '600000', '--price-paid', '4.50']

    def test_spa_price_table_matches_expected(self):
        code, out = run_tool('waterfall.py', *self.ARGS)
        self.assertEqual(code, 0)
        self.assertEqual(out, read(os.path.join(EXPECTED, 'waterfall_spa-price.md')))

    def test_charter_price_table_matches_expected(self):
        code, out = run_tool('waterfall.py', *(self.ARGS + ['--set-price', 'Series B=4.20']))
        self.assertEqual(code, 0)
        self.assertEqual(out, read(os.path.join(EXPECTED, 'waterfall_charter-price.md')))


if __name__ == '__main__':
    unittest.main()
