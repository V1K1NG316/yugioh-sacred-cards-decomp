"""Function census (Claude, 2026-10-14; idea from the GT Advance 3 decomp): find Thumb functions hidden inside
another function's extent in config/functions.csv (approximation A35).

A candidate is a Thumb `push {..., lr}` (halfword 0xB5xx) at offset > 0 inside a thumb function's extent, right
after something that ends code: `bx lr` (0x4770), `bx rN` (0x47x0), `pop {..., pc}` (0xBDxx), an unconditional
branch (0xE000-0xE7FF), or alignment/literal padding. Bare `bx lr` stubs are found the same way. This is a
heuristic: candidates still need a look (or the asm) before the function list is split.

Usage: python3 tools/census.py [--tsv OUT]     (reads private/baserom.gba from the main checkout)
"""
import argparse
import csv
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
B = 0x08000000


def ends_code(h):
    return h == 0x4770 or (h & 0xFF87) == 0x4700 or (h & 0xFF00) == 0xBD00 or 0xE000 <= h <= 0xE7FF


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tsv')
    a = ap.parse_args()
    d = ROM.read_bytes()
    rows = [r for r in csv.DictReader(open(ROOT / 'config' / 'functions.csv')) if r['mode'] == 'thumb']
    found = []
    for r in rows:
        start, size = int(r['address'], 16), int(r['size'])
        if size > 0x4000:            # the two giant "functions" are mostly data
            continue
        o = start - B
        hw = [struct.unpack_from('<H', d, o + i)[0] for i in range(0, size - 1, 2)]
        for i in range(1, len(hw)):
            h = hw[i]
            prev = hw[i - 1]
            pad = prev == 0 or (i >= 2 and ends_code(hw[i - 2]))   # alignment halfword or a literal word after a return
            if (h & 0xFF00) == 0xB500 and (ends_code(prev) or pad):
                found.append((r['name'], start + 2 * i, 'push lr'))
    with_push = {n for n, _, _ in found}
    print('thumb functions scanned: %d; candidates: %d in %d functions' % (len(rows), len(found), len(with_push)))
    if a.tsv:
        with open(a.tsv, 'w', encoding='utf-8') as f:
            f.write('container\taddress\tkind\n')
            for n, addr, k in found:
                f.write('%s\t0x%08X\t%s\n' % (n, addr, k))
    for n, addr, k in found[:15]:
        print('%-14s 0x%08X %s' % (n, addr, k))


if __name__ == '__main__':
    main()
