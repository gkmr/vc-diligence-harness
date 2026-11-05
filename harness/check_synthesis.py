#!/usr/bin/env python3
"""Structural lint for a master synthesis. Checks form, not truth.

Usage:
    python3 harness/check_synthesis.py MASTER.md [--data-room DIR]

Rules (each maps to a quality gate in skills/vc-diligence/SKILL.md):
  1. The first "## " section is Contradictions. Then Gates, then Asks.
  2. Contradictions are "### C<n> [CRITICAL|HIGH|MEDIUM] ..." in severity
     order, each with Conflict, Why it matters to price, Read and Ask
     lines, and at least two source tags on the Conflict line.
  3. Gates 1 to 4 appear in order, each with a Status line, an Asks line
     and at least one source tag.
  4. In Contradictions and Gates, every bullet that states a figure
     (money, percent, multiple, or a count with thousands separators)
     carries a source tag, and every table has a tagged caption line
     directly above it (blank lines allowed). Ask lines are exempt.
  5. Asks are a numbered list, numbered 1..n without gaps.
  6. The last non-empty line starts with "**Decisive open item:**".
  7. With --data-room, every [Dnn] tag names a document in that folder.

Source tags: [D02 §1.1], [calc ...], [offer ...], [ext ...].
"""
import argparse
import os
import re
import sys

TAG_RX = re.compile(r'\[(D\d{2}|calc|offer|ext)\b[^\]]*\]')
DOC_TAG_RX = re.compile(r'\[(D\d{2})\b')
CONTRA_RX = re.compile(r'^### C(\d+) \[(CRITICAL|HIGH|MEDIUM)\]')
GATE_RX = re.compile(r'^### Gate (\d)\b')
FIGURE_RX = re.compile(
    r'\$\s?\d|\d(?:\.\d+)?\s?%|\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?\s?(?:x|M|B|bn|million|billion)\b')
SEV = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
CONTRA_PARTS = ['**Conflict:**', '**Why it matters to price:**', '**Read:**', '**Ask:**']


def sections(lines):
    """[(heading, start, end)] for "## " headings."""
    idx = [i for i, l in enumerate(lines) if l.startswith('## ')]
    return [(lines[i][3:].strip(), i, (idx[k + 1] if k + 1 < len(idx) else len(lines)))
            for k, i in enumerate(idx)]


def blocks(lines, start, end, rx):
    """[(match, start, end)] for "### " headings matching rx inside a section."""
    idx = [i for i in range(start, end) if lines[i].startswith('### ')]
    out = []
    for k, i in enumerate(idx):
        m = rx.match(lines[i])
        if m:
            out.append((m, i, idx[k + 1] if k + 1 < len(idx) else end))
    return out


def untagged_numbers(lines, start, end):
    """Problems for bullets with figures but no tag, and tables without a tagged caption."""
    probs = []
    i = start
    while i < end:
        line = lines[i]
        s = line.strip()
        if s.startswith('|'):
            j = i
            while j < end and lines[j].strip().startswith('|'):
                j += 1
            k = i - 1
            while k >= start and not lines[k].strip():
                k -= 1
            caption = lines[k] if k >= start else ''
            if caption.lstrip().startswith(('- ', '#')) or not TAG_RX.search(caption):
                probs.append('line %d: table has no tagged caption line directly above it' % (i + 1))
            i = j
            continue
        if s.startswith('- ') and FIGURE_RX.search(s) and not TAG_RX.search(s):
            if not s.startswith(('- **Ask', '- Ask')):
                probs.append('line %d: figure without a source tag: %s' % (i + 1, s[:80]))
        i += 1
    return probs


def check(text, doc_ids=None):
    lines = text.splitlines()
    probs = []
    secs = sections(lines)
    names = [h.lower() for h, _, _ in secs]

    def find(word):
        for k, n in enumerate(names):
            if word in n:
                return k
        return None

    c_i, g_i, a_i = find('contradiction'), find('gate'), find('ask')
    if c_i is None or g_i is None or a_i is None:
        probs.append('missing a section: need Contradictions, Gates and Asks')
        return probs, {}
    if c_i != 0:
        probs.append('rule 1: the first "## " section must be Contradictions, found "%s"' % secs[0][0])
    if not (c_i < g_i < a_i):
        probs.append('rule 1: sections must run Contradictions, Gates, Asks')

    _, cs, ce = secs[c_i]
    contras = blocks(lines, cs, ce, CONTRA_RX)
    if not contras:
        probs.append('rule 2: no "### C<n> [SEVERITY]" blocks')
    last = -1
    for m, bs, be in contras:
        body = lines[bs:be]
        sev = SEV[m.group(2)]
        if sev < last:
            probs.append('rule 2: C%s is out of severity order' % m.group(1))
        last = max(last, sev)
        for part in CONTRA_PARTS:
            if not any(part in l for l in body):
                probs.append('rule 2: C%s has no %s line' % (m.group(1), part))
        conflict = [l for l in body if '**Conflict:**' in l]
        if conflict and len(TAG_RX.findall(conflict[0])) < 2:
            probs.append('rule 2: C%s Conflict line needs two source tags' % m.group(1))
    probs += ['rule 4: ' + p for p in untagged_numbers(lines, cs, ce)]

    _, gs, ge = secs[g_i]
    gates = blocks(lines, gs, ge, GATE_RX)
    if [int(m.group(1)) for m, _, _ in gates] != [1, 2, 3, 4]:
        probs.append('rule 3: need Gate 1, Gate 2, Gate 3, Gate 4 in order')
    for m, bs, be in gates:
        body = '\n'.join(lines[bs:be])
        if '**Status:**' not in body:
            probs.append('rule 3: Gate %s has no **Status:** line' % m.group(1))
        if '**Asks:**' not in body:
            probs.append('rule 3: Gate %s has no **Asks:** line' % m.group(1))
        if not TAG_RX.search(body):
            probs.append('rule 3: Gate %s has no source tags' % m.group(1))
    probs += ['rule 4: ' + p for p in untagged_numbers(lines, gs, ge)]

    _, as_, ae = secs[a_i]
    nums = [int(m.group(1)) for m in (re.match(r'^\s*(\d+)\. ', l) for l in lines[as_:ae]) if m]
    if not nums:
        probs.append('rule 5: Asks has no numbered items')
    elif nums != list(range(1, len(nums) + 1)):
        probs.append('rule 5: Asks numbering is not 1..n')

    tail = [l for l in lines if l.strip()]
    if not tail or not tail[-1].startswith('**Decisive open item:**'):
        probs.append('rule 6: last line must start with **Decisive open item:**')

    if doc_ids is not None:
        for tag in sorted(set(DOC_TAG_RX.findall(text))):
            if tag not in doc_ids:
                probs.append('rule 7: tag %s is not a document in the data room' % tag)

    stats = {'contradictions': len(contras), 'gates': len(gates), 'asks': len(nums),
             'tags': len(TAG_RX.findall(text))}
    return probs, stats


def data_room_ids(folder):
    ids = set()
    for fn in os.listdir(folder):
        m = re.match(r'^(\d{2})-', fn)
        if m:
            ids.add('D' + m.group(1))
    return ids


def main(argv=None):
    ap = argparse.ArgumentParser(description='Structural lint for a master synthesis.')
    ap.add_argument('synthesis')
    ap.add_argument('--data-room', help='folder of NN-* files, used to validate [Dnn] tags')
    args = ap.parse_args(argv)
    with open(args.synthesis, encoding='utf-8') as fh:
        text = fh.read()
    ids = data_room_ids(args.data_room) if args.data_room else None
    probs, stats = check(text, ids)
    for p in probs:
        print(p)
    if probs:
        print('check_synthesis.py: %d problem(s)' % len(probs))
        return 1
    print('check_synthesis.py: OK (%d contradictions, %d gates, %d asks, %d source tags)'
          % (stats['contradictions'], stats['gates'], stats['asks'], stats['tags']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
