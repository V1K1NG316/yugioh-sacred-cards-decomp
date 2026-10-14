"""Write mechanical C drafts for the simplest function shapes (Claude, 2026-10-14; idea from DeepSeek's
private/drafts/make_batch5-7.sh). No guessing: a function is drafted only if its whole asm is one of

  empty stub       bx lr
  call chain       push {lr} / bl A / bl B / ... / pop {r0} / bx r0      (1..8 calls, no other instruction)

Callees are read from the asm (`bl sub_XXXXXXXX`). Everything else is skipped. Drafts go to
private/drafts/<name>.c (game-derived, never committed); existing drafts and matched functions are skipped.
Every draft must still pass `PY tools/match_func.py <name>` before it is queued.

Usage: PY tools/gen_wrapper_drafts.py [--skip-list FILE] [--limit N]   (prints the drafted names)
"""
import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('D:/Yugioh_DeComp_V2')   # private/ lives in the main checkout, also when run from a worktree
INSTR = re.compile(r'^\s+([a-z][a-z.]*)\b(.*)$')


def shape(asm_text):
    ins = []
    for line in asm_text.splitlines():
        if line.lstrip().startswith(('@', '.', 'thumb_func_start')) or not line.strip():
            continue
        m = INSTR.match(line)
        if m:
            ins.append((m.group(1), m.group(2).strip()))
    if ins == [('bx', 'lr')]:
        return ('empty', [])
    if len(ins) >= 4 and ins[0] == ('push', '{lr}') and ins[-2:] == [('pop', '{r0}'), ('bx', 'r0')]:
        mid = ins[1:-2]
        if 1 <= len(mid) <= 8 and all(op == 'bl' and re.fullmatch(r'sub_[0-9A-F]{8}', a) for op, a in mid):
            return ('calls', [a for _, a in mid])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skip-list', help='file with names to skip (e.g. a batch DeepSeek is drafting)')
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    skip = set(Path(a.skip_list).read_text().split()) if a.skip_list else set()
    done = {p.stem for p in (ROOT / 'src' / 'funcs').glob('*.c')}
    drafts = REPO / 'private' / 'drafts'
    out = []
    for r in csv.DictReader(open(ROOT / 'config' / 'functions.csv')):
        n = r['name']
        if r['mode'] != 'thumb' or not n.startswith('sub_') or n in done or n in skip or (drafts / (n + '.c')).exists():
            continue
        asm = REPO / 'private' / 'asm' / 'funcs' / (n + '.s')
        if not asm.exists():
            continue
        s = shape(asm.read_text())
        if not s:
            continue
        kind, calls = s
        if kind == 'empty':
            body = '#include "global.h"\n\nvoid %s(void)\n{\n}\n' % n
        else:
            decls = ''.join('void %s(void);\n' % c for c in dict.fromkeys(calls))
            body = '#include "global.h"\n\n%s\nvoid %s(void)\n{\n%s}\n' % (decls, n, ''.join('    %s();\n' % c for c in calls))
        (drafts / (n + '.c')).write_text(body, newline='\n')
        out.append(n)
        if a.limit and len(out) >= a.limit:
            break
    print(' '.join(out))


if __name__ == '__main__':
    main()
