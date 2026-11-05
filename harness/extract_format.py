"""Read per-document extract files (markdown or JSON) into plain dicts.

Markdown extract format (see templates/doc-extract.md):

    # D02 - Series B preferred stock purchase agreement (extract)

    - doc_id: D02
    - doc_type: stock-purchase-agreement
    - date: 2026-03-02
    - basis: executed contract

    ## Facts

    | field | value | source | as_of |
    |---|---|---|---|
    | series_b_price_per_share | $8.40 | §1.1(a) | |

JSON extract format:

    {"doc_id": "D02", "title": "...", "date": "2026-03-02", "basis": "...",
     "facts": [{"field": "series_b_price_per_share", "value": "$8.40",
                "source": "§1.1(a)", "as_of": ""}]}

Only rows under a heading that starts with "## Facts" are read as facts.
Everything else in the file is for humans.
"""
import json
import os
import re

LAYERS = ('verbatim', 'extract', 'bluf')
STEM_RX = re.compile(r'^(?P<stem>.+?)_(?P<layer>verbatim|extract|bluf)$')
NUM_RX = re.compile(
    r'^\s*(?P<neg>-)?\s*\$?\s*(?P<num>\d[\d,]*(?:\.\d+)?|\.\d+)\s*'
    r'(?P<suffix>k|m|mm|b|bn|%|x)?(?:\s+[a-z][a-z ]*)?\s*$',
    re.I,
)
MULT = {'k': 1e3, 'm': 1e6, 'mm': 1e6, 'b': 1e9, 'bn': 1e9}
META_RX = re.compile(r'^\s*(?:-\s+)?(doc_id|title|doc_type|date|basis):\s*(.*?)\s*$')


def parse_value(raw):
    """Return a float for a numeric cell, or None for text.

    Accepts $8.40, 14,000,000, $14.0M, $1.2B, 75%, 2.5x and a trailing unit
    word ("600,000 shares", "15 days"). Dates, ranges and "70+" stay text.
    Percent and x values keep their face value (75% -> 75.0).
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return float(raw)
    m = NUM_RX.match(str(raw))
    if not m:
        return None
    val = float(m.group('num').replace(',', ''))
    suffix = (m.group('suffix') or '').lower()
    val *= MULT.get(suffix, 1.0)
    return -val if m.group('neg') else val


def split_stem(filename):
    """'02-spa_extract.md' -> ('02-spa', 'extract'); other files -> (stem, None)."""
    base = os.path.splitext(os.path.basename(filename))[0]
    m = STEM_RX.match(base)
    if m:
        return m.group('stem'), m.group('layer')
    return base, None


def _fact(field, value, source='', as_of=''):
    field = (field or '').strip()
    raw = '' if value is None else str(value).strip()
    return {
        'field': field,
        'raw': raw,
        'value': parse_value(value),
        'source': (source or '').strip(),
        'as_of': (as_of or '').strip(),
    }


def read_markdown(path):
    doc = {'path': path, 'title': '', 'doc_id': '', 'doc_type': '', 'date': '', 'basis': '', 'facts': []}
    in_facts = False
    with open(path, encoding='utf-8') as fh:
        text = fh.read()
    for line in text.splitlines():
        if line.startswith('# ') and not doc['title']:
            doc['title'] = line[2:].strip()
            continue
        if line.startswith('## '):
            in_facts = line[3:].strip().lower().startswith('facts')
            continue
        if not in_facts:
            m = META_RX.match(line)
            if m and not doc[m.group(1)]:
                doc[m.group(1)] = m.group(2)
            continue
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not cells or cells[0].lower() == 'field' or set(cells[0]) <= set('-: '):
            continue
        cells += [''] * (4 - len(cells))
        doc['facts'].append(_fact(cells[0], cells[1], cells[2], cells[3]))
    return doc


def read_json(path):
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    doc = {'path': path, 'facts': []}
    for key in ('title', 'doc_id', 'doc_type', 'date', 'basis'):
        doc[key] = str(data.get(key, '') or '')
    for f in data.get('facts', []):
        doc['facts'].append(_fact(f.get('field'), f.get('value'), f.get('source', ''), f.get('as_of', '')))
    return doc


def read_extract(path):
    doc = read_json(path) if path.endswith('.json') else read_markdown(path)
    if not doc['doc_id']:
        stem, _ = split_stem(path)
        m = re.match(r'^(\d{2})-', stem)
        doc['doc_id'] = 'D' + m.group(1) if m else stem
    return doc


def find_extracts(folder):
    """All *_extract.md and *_extract.json files under folder, sorted by name."""
    out = []
    for dp, dns, fns in os.walk(folder):
        dns[:] = sorted(d for d in dns if not d.startswith('.'))
        for fn in sorted(fns):
            stem, layer = split_stem(fn)
            if layer == 'extract' and fn.endswith(('.md', '.json')):
                out.append(os.path.join(dp, fn))
    return out
