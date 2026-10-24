"""For every unmatched function, find the most similar already-matched function (idea: EDS decomp's similar.py).
(Claude, 2026-10-14.) Similarity = difflib ratio over the asm instruction sequence with registers, immediates and
labels normalised away; only functions of similar size are compared. A close matched sibling's C is usually a far
better draft than starting from scratch.
Output: private/drafts/siblings.tsv  (unmatched, size, sibling, ratio)   Usage: python3 tools/siblings.py [--min 0.75]
"""
import argparse
import csv
import difflib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT
INS = re.compile(r'^\s+([a-z][a-z0-9.]*)\s*(.*)$')


def norm(name):
    p = REPO / 'private' / 'asm' / 'funcs' / (name + '.s')
    if not p.exists():
        return []
    out = []
    for line in p.read_text(errors='replace').splitlines():
        if line.lstrip().startswith(('@', '.', 'thumb_func', 'arm_func')):
            continue
        m = INS.match(line)
        if not m:
            continue
        op = m.group(1)
        # matched functions' .s is agbcc output (divided syntax: mov/add/lsl), the rest is gbadisasm (movs/adds/lsls)
        if op in ('movs', 'adds', 'subs', 'lsls', 'lsrs', 'asrs', 'ands', 'orrs', 'eors', 'bics', 'mvns', 'negs',
                  'muls', 'rsbs', 'adcs', 'sbcs', 'rors', 'tsts', 'cmns'):
            op = op[:-1]
        op = {'ldrsh': 'ldsh', 'ldrsb': 'ldsb'}.get(op, op)
        ops = re.sub(r'\br\d+\b|\bsb\b|\bsl\b|\bip\b|\bfp\b|\bsp\b|\blr\b|\bpc\b', 'R', m.group(2))
        ops = re.sub(r'#-?(0x[0-9a-fA-F]+|\d+)', '#', ops)
        ops = re.sub(r'\.?L?[A-Za-z_]*_?[0-9A-Fa-f]{6,}[A-Za-z0-9_+]*|\b0x[0-9a-fA-F]+\b|\.L\w+', 'L', ops)
        ops = re.sub(r'\s*@.*$', '', ops).replace(' ', '')
        out.append(op + ' ' + ops)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min', type=float, default=0.75)
    a = ap.parse_args()
    matched = {p.stem for p in (REPO / 'src' / 'funcs').glob('*.c')}
    rows = [r for r in csv.DictReader(open(ROOT / 'config' / 'functions.csv'))
            if r['mode'] == 'thumb' and 16 <= int(r['size']) <= 0x800]
    m_seq = {r['name']: norm(r['name']) for r in rows if r['name'] in matched}
    m_size = {r['name']: int(r['size']) for r in rows if r['name'] in matched}
    res = []
    for r in rows:
        n, sz = r['name'], int(r['size'])
        if n in matched:
            continue
        s = norm(n)
        if not s:
            continue
        best = (0.0, '')
        for mn, ms in m_seq.items():
            if not (0.7 * sz <= m_size[mn] <= 1.3 * sz) or not ms:
                continue
            sm = difflib.SequenceMatcher(None, s, ms, autojunk=False)
            if sm.real_quick_ratio() < best[0] or sm.quick_ratio() < best[0]:
                continue
            q = sm.ratio()
            if q > best[0]:
                best = (q, mn)
        if best[0] >= a.min:
            res.append((n, sz, best[1], round(best[0], 3)))
    out = REPO / 'private' / 'drafts' / 'siblings.tsv'
    with open(out, 'w', encoding='utf-8') as f:
        f.write('unmatched\tsize\tsibling\tratio\n')
        for row in sorted(res, key=lambda x: -x[3]):
            f.write('%s\t%d\t%s\t%.3f\n' % row)
    print('unmatched functions with a matched sibling >= %.2f: %d (>=0.9: %d)'
          % (a.min, len(res), sum(1 for x in res if x[3] >= 0.9)))


if __name__ == '__main__':
    main()
