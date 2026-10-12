#!/usr/bin/env python3
"""Check config/functions.csv (milestone Y2, tools/find_functions.py output).

Exits 0 only when every one of these holds:
  1. the header is exactly `address,name,mode,size,source`;
  2. addresses are unique, sorted and inside 0x08000000..0x08FFFFFF;
  3. thumb rows have even addresses, arm rows are 4-aligned; size >= 2 (thumb)
     or >= 4 (arm) and the extent stays inside the ROM;
  4. the step-1 entry points are present (reset, crt0, IRQ handler, main) and
     the two handlers from the crt0's interrupt table at 0x0807F420;
  5. there are at least MIN_ROWS rows (real result 2026-10-12: 1034);
  6. extents (address .. address+size) never overlap each other;
  7. every `ptr_prologue` row really begins with a THUMB `push {..., lr}`
     prologue (first two bytes 0xB5xx);
  8. every `bl_thumb` row is the target of a THUMB `BL` whose own address lies
     inside the extent of another listed function.  (Check 5 of the previous
     version accepted any even address, because it counted `BL`-shaped
     halfwords anywhere in the ROM, data included - see [006] finding 2.)

Deliberately NOT checked: that the extents are complete (a function may be cut
short - docs/approximations.md A1) and that no call target is missing.
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
LIMIT = 0x08FFFFFF
HEADER = 'address,name,mode,size,source'
MIN_ROWS = 1000     # real finder result was 1034 rows on 2026-10-12

ENTRIES = {         # entry points (exempt from check 8)
    0x08000000: 'reset', 0x080000C0: 'crt0', 0x080000FC: 'irq_handler',
    0x08016928: 'main',
    0x08003B70: 'irq_table word[0]', 0x08003B94: 'irq_table words[1..13]',
}
NAMES_OK = ('reset', 'crt0', 'irq_handler', 'main')

errors = []


def fail(msg):
    errors.append(msg)
    print('FAIL ' + msg)


def thumb_bl_pairs(rom):
    """Every (source, target) of a THUMB `BL` pair anywhere in the ROM."""
    words = array('H')
    words.frombytes(rom[:len(rom) // 2 * 2])
    out = []
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
        out.append((BASE + i * 2, (BASE + i * 2 + 4 + off) & ~1))
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
        if len(parts) != 5:
            fail(f'line {n}: {len(parts)} fields, expected 5')
            continue
        addr, name, mode, size, source = parts
        if mode not in ('thumb', 'arm'):
            fail(f'line {n}: bad mode {mode!r}')
        try:
            rows.append((int(addr, 16), name, mode, int(size), source))
        except ValueError:
            fail(f'line {n}: bad address/size in {line!r}')

    rom_size = ROM.stat().st_size if ROM.exists() else None
    addrs = [r[0] for r in rows]
    if len(set(addrs)) != len(addrs):
        fail('addresses are not unique')
    if addrs != sorted(addrs):
        fail('addresses are not sorted')
    for a, name, mode, size, source in rows:
        unit = 2 if mode == 'thumb' else 4
        if not (BASE <= a <= LIMIT):
            fail(f'0x{a:08X} outside 0x08000000..0x08FFFFFF')
        if mode == 'thumb' and a % 2:
            fail(f'0x{a:08X} thumb address is odd')
        if mode == 'arm' and a % 4:
            fail(f'0x{a:08X} arm address is not 4-aligned')
        if size < unit:
            fail(f'0x{a:08X} size {size} < {unit}')
        if rom_size and not (a + size <= BASE + rom_size):
            fail(f'0x{a:08X} extent runs past the ROM')
        if not name.startswith('sub_') and name not in NAMES_OK:
            fail(f'0x{a:08X} unexpected name {name!r}')

    present = set(addrs)
    for a, what in ENTRIES.items():
        if a not in present:
            fail(f'entry {what} (0x{a:08X}) missing')

    if len(rows) < MIN_ROWS:
        fail(f'{len(rows)} rows, minimum is {MIN_ROWS}')

    # 6. extents must not overlap
    starts = addrs
    for a, name, mode, size, source in rows:
        i = bisect.bisect_right(starts, a)
        if i < len(starts) and starts[i] < a + size:
            fail(f'0x{a:08X} extent (size {size}) overlaps 0x{starts[i]:08X}')

    # 7. ptr_prologue rows really start with a THUMB push {...} with LR
    if not ROM.exists():
        sys.exit(f'FAIL missing {ROM}')
    rom = ROM.read_bytes()
    pp = [r for r in rows if r[4] == 'ptr_prologue']
    for a, name, mode, size, source in pp:
        hw = struct.unpack_from('<H', rom, a - BASE)[0]
        if (hw & 0xFF00) != 0xB500:
            fail(f'0x{a:08X} ptr_prologue but first bytes are 0x{hw:04X}, not 0xB5xx')

    # 8. every bl_thumb row is backed by a BL that sits inside real code
    pairs = thumb_bl_pairs(rom)
    targets = {}
    for src, tgt in pairs:
        targets.setdefault(tgt, []).append(src)

    def inside_other_extent(src, tgt):
        i = bisect.bisect_right(starts, src)
        if i == 0:
            return False
        j = i - 1
        a, name, mode, size, source = rows[j]
        return a != tgt and a <= src < a + size

    bl_rows = [r for r in rows if r[4] == 'bl_thumb']
    for a, name, mode, size, source in bl_rows:
        srcs = targets.get(a, [])
        if not any(inside_other_extent(s, a) for s in srcs):
            if a in ENTRIES:
                print(f'  entry 0x{a:08X} {name}: exempt from check 8')
                continue
            fail(f'0x{a:08X} bl_thumb: no THUMB BL into it from inside another extent')

    print(f'rom THUMB BL pairs: {len(pairs)}  distinct targets: {len(targets)}')
    print(f'rows: {len(rows)}  thumb: {sum(1 for r in rows if r[2] == "thumb")}  '
          f'arm: {sum(1 for r in rows if r[2] == "arm")}')
    print(f'ptr_prologue rows: {len(pp)}  bl_thumb rows: {len(bl_rows)}')
    if errors:
        print(f'{len(errors)} failure(s)')
        sys.exit(1)
    print('ALL CHECKS PASSED')
    sys.exit(0)


if __name__ == '__main__':
    main()
