#!/usr/bin/env python3
"""Build the document register for a data-room folder.

Usage:
    python3 harness/register.py DATA_ROOM_DIR [--synthesis MASTER.md] [--check]

Files are grouped by stem: "02-spa.pdf", "02-spa_verbatim.md",
"02-spa_extract.md" and "02-spa_bluf.md" are one document. A stem that
starts with two digits keeps that number. Other stems get the next free
number in name order, so a raw data room can be registered before any
file is renamed.

Title, type, date and basis come from the extract when it exists.
Merged is ticked when --synthesis is given and that file cites the
document's tag (for example "[D02"). --check exits 1 if any document is
missing a layer or, with --synthesis, is never cited.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_format import LAYERS, read_extract, split_stem  # noqa: E402

DATE_RX = re.compile(r'(\d{4}-\d{2}-\d{2})')
SKIP = {'README.md', '.DS_Store'}


def collect(folder):
    """{stem: {'files': [...], 'layers': {layer: path}}} for files directly in folder."""
    docs = {}
    for fn in sorted(os.listdir(folder)):
        path = os.path.join(folder, fn)
        if fn in SKIP or fn.startswith('.') or not os.path.isfile(path):
            continue
        stem, layer = split_stem(fn)
        entry = docs.setdefault(stem, {'files': [], 'layers': {}})
        entry['files'].append(fn)
        if layer:
            entry['layers'][layer] = path
    return docs


def number(stems):
    """Map stem -> two-digit number, keeping numbers already in the name."""
    taken, out = set(), {}
    for s in stems:
        m = re.match(r'^(\d{2})-', s)
        if m:
            out[s] = int(m.group(1))
            taken.add(int(m.group(1)))
    n = 1
    for s in stems:
        if s in out:
            continue
        while n in taken:
            n += 1
        out[s] = n
        taken.add(n)
    return out


def build(folder, synthesis_text=None):
    docs = collect(folder)
    nums = number(sorted(docs))
    rows = []
    for stem in sorted(docs, key=lambda s: (nums[s], s)):
        entry = docs[stem]
        meta = read_extract(entry['layers']['extract']) if 'extract' in entry['layers'] else {}
        doc_id = meta.get('doc_id') or 'D%02d' % nums[stem]
        title = meta.get('title', '') or stem
        title = re.sub(r'^D\d{2}\s*-\s*', '', title)
        title = re.sub(r'\s*\(extract\)\s*$', '', title)
        date = meta.get('date', '')
        if not date:
            m = DATE_RX.search(stem)
            date = m.group(1) if m else ''
        missing = [layer for layer in LAYERS if layer not in entry['layers']]
        merged = None
        if synthesis_text is not None:
            merged = ('[' + doc_id) in synthesis_text
        rows.append({
            'num': nums[stem], 'doc_id': doc_id, 'stem': stem, 'title': title,
            'doc_type': meta.get('doc_type', ''), 'date': date or '?',
            'basis': meta.get('basis', '') or '?', 'missing': missing, 'merged': merged,
        })
    return rows


def render(rows, source_label):
    box = lambda ok: '[x]' if ok else '[ ]'
    lines = [
        '# Document register',
        '',
        'Built by harness/register.py from `%s`. Merged = the master synthesis cites the tag.' % source_label,
        '',
        '| # | Tag | Document | Type | Date | Basis | Verbatim | Extract | BLUF | Merged |',
        '|---|---|---|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        merged = '-' if r['merged'] is None else box(r['merged'])
        lines.append('| %02d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['num'], r['doc_id'], r['title'], r['doc_type'] or '?', r['date'], r['basis'],
            box('verbatim' not in r['missing']), box('extract' not in r['missing']),
            box('bluf' not in r['missing']), merged))
    gaps = [r for r in rows if r['missing'] or r['merged'] is False]
    lines += ['', '%d document(s), %d with gaps' % (len(rows), len(gaps))]
    for r in gaps:
        why = []
        if r['missing']:
            why.append('missing ' + ', '.join(r['missing']))
        if r['merged'] is False:
            why.append('not cited in synthesis')
        lines.append('- %s %s: %s' % (r['doc_id'], r['stem'], '; '.join(why)))
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='Build the document register for a data-room folder.')
    ap.add_argument('folder')
    ap.add_argument('--synthesis', help='master synthesis file, used to tick Merged')
    ap.add_argument('--check', action='store_true', help='exit 1 if any document has gaps')
    ap.add_argument('--label', help='folder label to print instead of the path')
    args = ap.parse_args(argv)

    text = None
    if args.synthesis:
        with open(args.synthesis, encoding='utf-8') as fh:
            text = fh.read()
    rows = build(args.folder, text)
    if not rows:
        print('no files in %s' % args.folder, file=sys.stderr)
        return 2
    sys.stdout.write(render(rows, args.label or os.path.basename(os.path.normpath(args.folder))))
    gaps = any(r['missing'] or r['merged'] is False for r in rows)
    return 1 if (args.check and gaps) else 0


if __name__ == '__main__':
    sys.exit(main())
