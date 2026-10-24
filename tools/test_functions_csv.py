#!/usr/bin/env python3
"""Check config/functions.csv (milestone Y2 + Y3: the true function list).

Exits 0 only when every one of these holds:
  1. the header is exactly `address,name,mode,size,source`;
  2. addresses are unique, sorted and inside 0x08000000..0x08FFFFFF;
  3. thumb rows have even addresses, arm rows are 4-aligned; size >= 2 (thumb)
     or >= 4 (arm) and the extent stays inside the ROM;
  4. the step-1 entry points are present (reset, crt0, IRQ handler, main) and
     the two handlers from the crt0's interrupt table at 0x0807F420;
  5. there are at least MIN_ROWS rows (real result 2026-10-12: 1977);
  6. extents (address .. address+size) never overlap each other.  Since Y3 the
     extent of a row runs to the next row's address, so a data table between two
     functions counts as part of the earlier row (docs/approximations.md A5);
  7. every `ptr_prologue` row really begins with a THUMB `push {..., lr}`
     prologue (first two bytes 0xB5xx);
  8. every `bl_thumb` row is the target of a THUMB `BL` whose own address lies
     inside the extent of another listed function.  (Check 5 of the previous
     version accepted any even address, because it counted `BL`-shaped
     halfwords anywhere in the ROM, data included - see [006] finding 2.)
  9. when private/asm/rom_full.s exists (the generated disassembly), the CSV must
     be exactly its function-start set: same addresses, names and modes.  That is
     the fixpoint test of scripts/disasm.sh; it is skipped when the file is
     absent, i.e. on a fresh clone before the first disassembly run.

Deliberately NOT checked: that no call target is missing.
"""
import bisect
import re
import struct
import sys
from array import array
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CSV = REPO / 'config' / 'functions.csv'
ROM = REPO / 'private' / 'baserom.gba'
BASE = 0x08000000
LIMIT = 0x08FFFFFF
HEADER = 'address,name,mode,size,source'
MIN_ROWS = 1900     # real fixpoint result was 1977 rows on 2026-10-12

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


def parse_rom_full_starts(path):
    """{(address, name, mode)} for every *_func_start macro in the generated asm.

    Written out separately from tools/functions_from_rom_s.py on purpose: the check
    must not share the code it is checking.
    """
    out = set()
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'\t(thumb_func_start|arm_func_start|non_word_aligned_thumb_func_start) (\S+)$',
                     line)
        if not m or i + 1 >= len(lines):
            continue
        lm = re.match(r'^(\S+): @ 0x([0-9A-F]{8})$', lines[i + 1])
        if not lm or lm.group(1) != m.group(2):
            continue
        mode = 'arm' if m.group(1) == 'arm_func_start' else 'thumb'
        out.add((int(lm.group(2), 16), m.group(2), mode))
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
        if source == 'disasm' and not name.startswith('sub_'):
            fail(f'0x{a:08X} source=disasm but name {name!r} is not gbadisasm-shaped')

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

    # 9. the CSV is exactly the function-start set of the generated disassembly
    full = REPO / 'private' / 'asm' / 'rom_full.s'
    if full.exists():
        found = parse_rom_full_starts(full)
        csv_set = {(a, name, mode) for a, name, mode, _, _ in rows}
        if found != csv_set:
            only_csv = sorted(csv_set - found)[:5]
            only_asm = sorted(found - csv_set)[:5]
            fail(f'the CSV is not the function-start set of {full.name}: '
                 f'{len(csv_set - found)} only in the CSV {only_csv}, '
                 f'{len(found - csv_set)} only in the asm {only_asm}')
        else:
            print(f'fixpoint: the CSV equals the {len(found)} function starts of {full.name}')
    else:
        print(f'fixpoint check skipped: {full} does not exist yet')

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
