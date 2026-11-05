#!/usr/bin/env python3
"""Flag numeric disagreements on shared fields across per-document extracts.

Usage:
    python3 harness/contradictions.py DATA_ROOM_DIR [--tol 0.01]
        [--field-tol arr_usd=0.02 ...] [--json] [--verbose] [--fail-on-find]

Two facts are compared when they share the same field name and the same
as_of date (blank as_of matches blank). A field is flagged when

    (max - min) / max(|max|, |min|) > tolerance

Suggested severity is by spread only: >= 25% CRITICAL, >= 10% HIGH, else
MEDIUM. It is a triage default. The analyst sets the final severity by
impact on price, in the master synthesis.

This checks same-field drift only. Cross-field tensions (a 409A value
against a headline valuation, a rights threshold against a block size)
need a reader.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_format import find_extracts, read_extract  # noqa: E402

SEVERITY_ORDER = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}


def severity(spread):
    if spread >= 0.25:
        return 'CRITICAL'
    if spread >= 0.10:
        return 'HIGH'
    return 'MEDIUM'


def spread_of(values):
    hi, lo = max(values), min(values)
    denom = max(abs(hi), abs(lo))
    return 0.0 if denom == 0 else (hi - lo) / denom


def group_facts(docs):
    """{(field, as_of): [fact + doc_id, ...]} for numeric facts only."""
    groups = {}
    for doc in docs:
        for f in doc['facts']:
            if f['value'] is None or not f['field']:
                continue
            row = dict(f, doc_id=doc['doc_id'], doc_title=doc.get('title', ''))
            groups.setdefault((f['field'], f['as_of']), []).append(row)
    return groups


def find_contradictions(docs, tol=0.01, field_tol=None):
    """Return (findings, agreed). Each item covers one (field, as_of) key seen 2+ times."""
    field_tol = field_tol or {}
    findings, agreed = [], []
    for (field, as_of), rows in sorted(group_facts(docs).items()):
        if len(rows) < 2:
            continue
        values = [r['value'] for r in rows]
        spread = spread_of(values)
        limit = field_tol.get(field, tol)
        item = {
            'field': field,
            'as_of': as_of,
            'spread': round(spread, 6),
            'tolerance': limit,
            'facts': [{k: r[k] for k in ('doc_id', 'raw', 'value', 'source')} for r in rows],
        }
        if spread > limit:
            item['severity'] = severity(spread)
            findings.append(item)
        else:
            agreed.append(item)
    findings.sort(key=lambda x: (SEVERITY_ORDER[x['severity']], -x['spread'], x['field']))
    return findings, agreed


def load_docs(folder):
    return [read_extract(p) for p in find_extracts(folder)]


def render(docs, findings, agreed, tol, verbose=False):
    n_facts = sum(1 for d in docs for f in d['facts'] if f['value'] is not None)
    lines = [
        'contradictions.py: %d extract(s), %d numeric fact(s), %d shared field(s), default tolerance %.1f%%'
        % (len(docs), n_facts, len(findings) + len(agreed), tol * 100),
        '%d contradiction(s), %d shared field(s) agree within tolerance' % (len(findings), len(agreed)),
        '',
    ]
    for i, f in enumerate(findings, 1):
        key = f['field'] + (' @ ' + f['as_of'] if f['as_of'] else '')
        lines.append('C%d [%s] %s  spread %.1f%%' % (i, f['severity'], key, f['spread'] * 100))
        for r in f['facts']:
            lines.append('    %-4s %-16s %s' % (r['doc_id'], r['raw'], r['source']))
        lines.append('')
    if verbose and agreed:
        lines.append('Agreed within tolerance:')
        for a in agreed:
            key = a['field'] + (' @ ' + a['as_of'] if a['as_of'] else '')
            docs_ = ', '.join('%s %s' % (r['doc_id'], r['raw']) for r in a['facts'])
            lines.append('    %s  spread %.2f%%  (%s)' % (key, a['spread'] * 100, docs_))
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def parse_field_tol(pairs):
    out = {}
    for p in pairs or []:
        name, _, val = p.partition('=')
        out[name.strip()] = float(val)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('folder', help='folder that holds *_extract.md or *_extract.json files')
    ap.add_argument('--tol', type=float, default=0.01, help='relative tolerance, default 0.01 (1%%)')
    ap.add_argument('--field-tol', action='append', metavar='FIELD=TOL', help='per-field tolerance override')
    ap.add_argument('--json', action='store_true', help='print findings as JSON')
    ap.add_argument('--verbose', action='store_true', help='also list shared fields that agree')
    ap.add_argument('--fail-on-find', action='store_true', help='exit 1 when any contradiction is found')
    args = ap.parse_args(argv)

    docs = load_docs(args.folder)
    if not docs:
        print('no *_extract.md or *_extract.json files under %s' % args.folder, file=sys.stderr)
        return 2
    findings, agreed = find_contradictions(docs, args.tol, parse_field_tol(args.field_tol))
    if args.json:
        print(json.dumps({'findings': findings, 'agreed': agreed}, indent=2))
    else:
        sys.stdout.write(render(docs, findings, agreed, args.tol, args.verbose))
    return 1 if (findings and args.fail_on_find) else 0


if __name__ == '__main__':
    sys.exit(main())
