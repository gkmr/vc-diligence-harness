#!/usr/bin/env python3
"""Exit waterfall for common under non-participating liquidation preferences.

Usage:
    python3 harness/waterfall.py CAP_TABLE.json [--exits 25,50,100,185,300]
        [--block-shares 600000] [--price-paid 4.50] [--set-price "Series B=4.20"]
        [--json]

Exit values are in $ millions. Cap table JSON:

    {"classes": [
      {"name": "Series B", "kind": "preferred", "shares": 3000000,
       "issue_price": 8.40, "seniority": 1},
      {"name": "Common", "kind": "common", "shares": 9700000}
    ]}

Model:
- Each preferred series gets the greater of its preference
  (multiple x issue_price x shares, multiple defaults to 1) or its
  as-converted share of what is left. Conversion is 1:1 unless
  conversion_ratio is given. Participating preferred is rejected.
- Preferences are paid by seniority: rank 1 first. Equal ranks are
  pari passu, pro rata to preference amount.
- Options and warrants are entered as kind "common", as-exercised, with
  exercise cash ignored. That slightly understates common per share.
- Conversion choices are solved by best response: each series converts
  only if that pays more given the others' choices, repeated until stable.
"""
import argparse
import json
import sys

DEFAULT_EXITS = [25, 50, 100, 185, 300, 500]


def load_cap_table(path, set_prices=None):
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    classes = [dict(c) for c in data['classes']]
    for c in classes:
        c.setdefault('kind', 'common')
        if c['kind'] not in ('common', 'preferred'):
            raise ValueError('%s: kind must be common or preferred' % c['name'])
        if c.get('participating'):
            raise ValueError('%s: participating preferred is not modeled' % c['name'])
        if c['kind'] == 'preferred':
            c.setdefault('multiple', 1.0)
            c.setdefault('seniority', 1)
            c.setdefault('conversion_ratio', 1.0)
    for name, price in (set_prices or {}).items():
        match = [c for c in classes if c['name'] == name]
        if not match:
            raise ValueError('no class named %r' % name)
        match[0]['issue_price'] = price
    return classes


def preference(c):
    return c['multiple'] * c['issue_price'] * c['shares']


def as_converted_shares(c):
    return c['shares'] * (c.get('conversion_ratio', 1.0) if c['kind'] == 'preferred' else 1.0)


def distribute(exit_value, classes, converting):
    """Proceeds per class name, given the set of preferred names that convert."""
    paid = {c['name']: 0.0 for c in classes}
    remaining = float(exit_value)
    holding = [c for c in classes if c['kind'] == 'preferred' and c['name'] not in converting]
    for rank in sorted({c['seniority'] for c in holding}):
        group = [c for c in holding if c['seniority'] == rank]
        owed = sum(preference(c) for c in group)
        pay = min(remaining, owed)
        for c in group:
            paid[c['name']] = pay * preference(c) / owed if owed else 0.0
        remaining -= pay
    sharing = [c for c in classes if c['kind'] == 'common' or c['name'] in converting]
    total = sum(as_converted_shares(c) for c in sharing)
    for c in sharing:
        paid[c['name']] = remaining * as_converted_shares(c) / total if total else 0.0
    return paid


def solve(exit_value, classes, max_rounds=100):
    """Return (paid_by_class, converting_set) at a stable set of conversion choices."""
    prefs = [c for c in classes if c['kind'] == 'preferred']
    converting = set()
    for _ in range(max_rounds):
        changed = False
        for c in prefs:
            hold = distribute(exit_value, classes, converting - {c['name']})[c['name']]
            conv = distribute(exit_value, classes, converting | {c['name']})[c['name']]
            want = conv > hold + 1e-9
            if want != (c['name'] in converting):
                converting = (converting | {c['name']}) if want else (converting - {c['name']})
                changed = True
        if not changed:
            return distribute(exit_value, classes, converting), converting
    raise RuntimeError('conversion choices did not settle')


def common_per_share(exit_value, classes):
    paid, _ = solve(exit_value, classes)
    common = [c for c in classes if c['kind'] == 'common']
    shares = sum(c['shares'] for c in common)
    return sum(paid[c['name']] for c in common) / shares if shares else 0.0


def breakeven_exit(classes, target, hi=1e12, iters=200):
    """Smallest exit value at which common per share reaches target (bisection)."""
    lo = 0.0
    if common_per_share(hi, classes) < target:
        return None
    for _ in range(iters):
        mid = (lo + hi) / 2
        if common_per_share(mid, classes) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def rows(classes, exits_musd, block_shares=None, price_paid=None):
    out = []
    pref_names = [c['name'] for c in classes if c['kind'] == 'preferred']
    for x in exits_musd:
        ev = x * 1e6
        paid, converting = solve(ev, classes)
        cps = common_per_share(ev, classes)
        row = {
            'exit_musd': x,
            'pref_paid_musd': sum(paid[n] for n in pref_names if n not in converting) / 1e6,
            'converted': [n for n in pref_names if n in converting],
            'common_per_share': cps,
        }
        if block_shares:
            row['block_value_musd'] = cps * block_shares / 1e6
            if price_paid:
                row['block_multiple'] = cps / price_paid
        out.append(row)
    return out


def render(table, block_shares=None, price_paid=None):
    head = ['Exit ($M)', 'Preference paid ($M)', 'Converted to common', 'Common $/share']
    if block_shares:
        head.append('Block value ($M)')
        if price_paid:
            head.append('Multiple on $%.2f' % price_paid)
    lines = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    for r in table:
        cells = ['%g' % r['exit_musd'], '%.1f' % r['pref_paid_musd'],
                 ', '.join(r['converted']) or 'none', '%.2f' % r['common_per_share']]
        if 'block_value_musd' in r:
            cells.append('%.2f' % r['block_value_musd'])
        if 'block_multiple' in r:
            cells.append('%.2fx' % r['block_multiple'])
        lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='Common waterfall under 1x non-participating preferences.')
    ap.add_argument('cap_table')
    ap.add_argument('--exits', default=','.join(str(x) for x in DEFAULT_EXITS), help='exit values in $M')
    ap.add_argument('--block-shares', type=float, help='shares in the block being bought')
    ap.add_argument('--price-paid', type=float, help='price per share paid for the block')
    ap.add_argument('--set-price', action='append', metavar='NAME=PRICE', help='override a class issue_price')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)

    overrides = {}
    for item in args.set_price or []:
        name, _, val = item.rpartition('=')
        overrides[name.strip()] = float(val)
    classes = load_cap_table(args.cap_table, overrides)
    exits = [float(x) for x in args.exits.split(',') if x.strip()]
    table = rows(classes, exits, args.block_shares, args.price_paid)
    stack = sum(preference(c) for c in classes if c['kind'] == 'preferred')
    be = breakeven_exit(classes, args.price_paid) if args.price_paid else None
    if args.json:
        print(json.dumps({'preference_stack_usd': stack, 'breakeven_exit_usd': be, 'rows': table}, indent=2))
        return 0
    sys.stdout.write('Preference stack: $%.1fM\n\n' % (stack / 1e6))
    sys.stdout.write(render(table, args.block_shares, args.price_paid))
    if be is not None:
        sys.stdout.write('\nExit at which common reaches $%.2f/share: $%.1fM\n' % (args.price_paid, be / 1e6))
    return 0


if __name__ == '__main__':
    sys.exit(main())
