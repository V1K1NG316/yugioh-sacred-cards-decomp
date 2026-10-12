#!/usr/bin/env python3
"""Report the code/data split of private/baserom.gba from config/functions.csv.

Prints, for docs/rom-map.md:
  * code bytes covered by the listed extents, and the code region's end;
  * every gap larger than GAP_MIN inside the code region, with a one-line
    reading of the bytes at its start (valid THUMB? printable text? zero run?);
  * a 1 MiB block profile of the ROM after the code end (zero / ASCII /
    ROM-pointer density) as a first cut at the data regions.

Read-only; writes nothing.
"""
import bisect
import struct
import sys
from array import array
from pathlib import Path

REPO = Path(r'D:\Yugioh_DeComp_V2')
CSV = REPO / 'config' / 'functions.csv'
ROM = REPO / 'private' / 'baserom.gba'
BASE = 0x08000000
GAP_MIN = 0x1000        # 4 KiB
BLOCK = 0x100000        # 1 MiB

sys.path.insert(0, str(REPO / 'tools'))
import find_functions as F    # thumb_ok / u16 / u32 (same ROM, same base)


def classify(rom, a, n=64):
    chunk = rom[a - BASE:a - BASE + n]
    if all(b == 0 for b in chunk):
        return 'zero run'
    printable = sum(1 for b in chunk if 0x20 <= b < 0x7F)
    if printable >= n * 0.8:
        return 'ASCII text'
    if a % 2 == 0 and F.thumb_ok(a, 4):
        return 'valid THUMB (code-like)'
    return 'not code-like (table/data)'


def main():
    rom = ROM.read_bytes()
    rows = []
    for line in CSV.read_text().splitlines()[1:]:
        a, name, mode, size, source = line.split(',')
        rows.append((int(a, 16), int(size), source))
    rows.sort()
    starts = [r[0] for r in rows]
    ends = [r[0] + r[1] for r in rows]

    code_bytes = sum(r[1] for r in rows)
    code_end = max(ends)
    print(f'ROM: {len(rom)} bytes (0x{BASE:08X}..0x{BASE + len(rom):08X})')
    print(f'functions: {len(rows)}  code bytes: {code_bytes} '
          f'({100.0 * code_bytes / len(rom):.2f}% of the ROM)')
    print(f'code region: 0x{min(starts):08X}..0x{code_end:08X} '
          f'({100.0 * code_bytes / (code_end - BASE):.2f}% of it is function extents)')

    print(f'\ngaps > {GAP_MIN} bytes inside the code region '
          f'(preceded by extent ending at `end`):')
    total_gap = 0
    for i in range(len(rows) - 1):
        gap = starts[i + 1] - ends[i]
        if gap > GAP_MIN:
            total_gap += gap
            print(f'  0x{ends[i]:08X}-0x{starts[i + 1]:08X}  {gap:6d} B  '
                  f'{classify(rom, ends[i])}')
    print(f'  gaps > {GAP_MIN}: {total_gap} bytes total')

    print(f'\nblocks after the code end (0x{code_end:08X}), 1 MiB each:')
    a = (code_end + BLOCK - 1) // BLOCK * BLOCK
    while a < BASE + len(rom):
        chunk = rom[a - BASE:a - BASE + BLOCK]
        n = len(chunk)
        zeros = sum(1 for b in chunk if b == 0)
        printable = sum(1 for b in chunk if 0x20 <= b < 0x7F)
        words = array('I')
        words.frombytes(chunk[:n // 4 * 4])
        ptr = sum(1 for w in words if (w & 0xFE000000) == 0x08000000
                  and (w & 1) and w < BASE + len(rom))
        print(f'  0x{a:08X}  zero {100.0 * zeros / n:5.1f}%  '
              f'ASCII {100.0 * printable / n:5.1f}%  odd-RAM-ptr words {ptr:6d}')
        a += BLOCK


if __name__ == '__main__':
    main()
