#!/usr/bin/env python3
"""Check config/functions.csv (milestone Y2, tools/find_functions.py output).

Exits 0 only when every one of these holds:
  1. the header is exactly `address,name,mode,source`;
  2. addresses are unique, sorted and inside 0x08000000..0x08FFFFFF;
  3. thumb rows have even addresses, arm rows are 4-aligned;
  4. the step-1 entry points are present (reset, crt0, IRQ handler, main) and
     the two handlers from the crt0's interrupt table at 0x0807F420;
  5. there are at least MIN_ROWS rows (real result 2026-10-12: 158);
  6. for 20 randomly chosen thumb rows (fixed seed 20261012) a THUMB `BL`
     instruction anywhere in the ROM targets that address, or the address is
     one of the entry points above.
"""
import random
import struct
import sys
from array import array
from pathlib import Path

REPO = Path(r'D:\Yugioh_DeComp_V2')
CSV = REPO / 'config' / 'functions.csv'
ROM = REPO / 'private' / 'baserom.gba'
BASE = 0x08000000
LIMIT = 0x08FFFFFF
HEADER = 'address,name,mode,source'
MIN_ROWS = 150      # real finder result was 158 rows on 2026-10-12
SEED = 20261012
SAMPLE = 20

ENTRIES = {         # step-1 / step-1-derived entry points (exempt from check 6)
    0x08000000: 'reset', 0x080000C0: 'crt0', 0x080000FC: 'irq_handler',
    0x08016928: 'main',
    0x08003B70: 'irq_table word[0]', 0x08003B94: 'irq_table words[1..13]',
}

errors = []


def fail(msg):
    errors.append(msg)
    print('FAIL ' + msg)


def thumb_bl_targets():
    """Every address targeted by a THUMB BL pair, from scanning the whole ROM."""
    rom = ROM.read_bytes()
    words = array('H')
    words.frombytes(rom[:len(rom) // 2 * 2])
    out = set()
    for i in range(len(words) - 1):
        hw = words[i]
        if (hw & 0xF800) != 0xF000:
            continue
        hw2 = words[i + 1]
        if (hw2 & 0xF800) != 0xF800:
            continue
        off = ((hw & 0x7FF) << 12) | ((hw2 & 0x7FF) << 1)
        if off & 0x400000:
            off -= 0x800000
        t = (BASE + i * 2 + 4 + off) & ~1
        out.add(t)
    return out


def main():
    if not CSV.exists():
        sys.exit(f'FAIL missing {CSV}')
    lines = CSV.read_text(encoding='ascii').splitlines()
    if not lines or lines[0] != HEADER:
        fail(f'header is {lines[0]!r}, expected {HEADER!r}')
    rows = []
    for n, line in enumerate(lines[1:], start=2):
        parts = line.split(',')
        if len(parts) != 4:
            fail(f'line {n}: {len(parts)} fields, expected 4')
            continue
        addr, name, mode, source = parts
        if mode not in ('thumb', 'arm'):
            fail(f'line {n}: bad mode {mode!r}')
        try:
            rows.append((int(addr, 16), name, mode, source))
        except ValueError:
            fail(f'line {n}: bad address {addr!r}')

    addrs = [r[0] for r in rows]
    if len(set(addrs)) != len(addrs):
        fail('addresses are not unique')
    if addrs != sorted(addrs):
        fail('addresses are not sorted')
    for a, name, mode, source in rows:
        if not (BASE <= a <= LIMIT):
            fail(f'0x{a:08X} outside 0x08000000..0x08FFFFFF')
        if mode == 'thumb' and a % 2:
            fail(f'0x{a:08X} thumb address is odd')
        if mode == 'arm' and a % 4:
            fail(f'0x{a:08X} arm address is not 4-aligned')
        if not name.startswith('sub_') and name not in ('reset', 'crt0', 'irq_handler', 'main'):
            fail(f'0x{a:08X} unexpected name {name!r}')

    present = set(addrs)
    for a, what in ENTRIES.items():
        if a not in present:
            fail(f'entry {what} (0x{a:08X}) missing')

    if len(rows) < MIN_ROWS:
        fail(f'{len(rows)} rows, minimum is {MIN_ROWS}')

    targets = thumb_bl_targets()
    print(f'rom THUMB BL targets: {len(targets)}')
    thumbs = [r for r in rows if r[2] == 'thumb']
    rng = random.Random(SEED)
    sample = rng.sample(thumbs, min(SAMPLE, len(thumbs)))
    for a, name, mode, source in sample:
        if a in ENTRIES or a in targets:
            print(f'  ok  0x{a:08X} {name} (source={source})')
        else:
            fail(f'0x{a:08X} {name}: no THUMB BL targets it and it is not an entry')

    print(f'rows: {len(rows)}  thumb: {len(thumbs)}  arm: {len(rows) - len(thumbs)}')
    if errors:
        print(f'{len(errors)} failure(s)')
        sys.exit(1)
    print('ALL CHECKS PASSED')
    sys.exit(0)


if __name__ == '__main__':
    main()
