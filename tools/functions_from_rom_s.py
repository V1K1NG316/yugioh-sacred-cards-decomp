#!/usr/bin/env python3
"""Refresh config/functions.csv from the generated disassembly (Y3, proposal 1).

usage: functions_from_rom_s.py [rom.s] [functions.csv]

The disassembler finds function entry points that the Y2 census missed: gbadisasm
emits a `*_func_start` macro for every function it decodes, including the 943 BL
targets that tools/find_functions.py never saw (its BL closure ran inside census
extents, which stop at the first return -- see AI_Conversation [011]).

Rules:
  * every `*_func_start <name>` line followed by `<name>: @ 0xADDR` is one row;
    mode comes from the macro (thumb / arm / thumb for non_word_aligned_thumb_func_start);
  * a row that is already in the CSV keeps its `source` (reset_vector, ptr_prologue,
    ...); a new address gets `source = disasm`;
  * `size` is the distance to the next function start (the last row runs to the
    sentinel 0x08FFFFFC of tools/make_disasm_cfg.py).  Extents are therefore
    contiguous and never overlap; they are not "code only" -- a literal pool or a
    data table between two functions is inside the earlier row's extent
    (docs/approximations.md A5).
  * an address present in the CSV but absent from the disassembly is an error
    (gbadisasm must echo back every *_func line of private/asm/rom.cfg).

Writes config/functions.csv only; prints the counts.
"""
import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_S = REPO / 'private' / 'asm' / 'rom_full.s'
DEFAULT_CSV = REPO / 'config' / 'functions.csv'
BASE = 0x08000000
SENTINEL = BASE + 0x01000000 - 4

MACRO_RE = re.compile(r'^\t(thumb_func_start|arm_func_start|non_word_aligned_thumb_func_start) (\S+)$')
LABEL_RE = re.compile(r'^(\S+): @ 0x([0-9A-F]{8})$')
MODES = {'thumb_func_start': 'thumb', 'non_word_aligned_thumb_func_start': 'thumb',
         'arm_func_start': 'arm'}


def parse_starts(path):
    """[(address, name, mode)] in file order."""
    lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
    out = []
    for i, line in enumerate(lines):
        m = MACRO_RE.match(line)
        if not m:
            continue
        if i + 1 >= len(lines):
            sys.exit('%s:%d: function macro is the last line' % (path, i + 1))
        lm = LABEL_RE.match(lines[i + 1])
        if not lm or lm.group(1) != m.group(2):
            sys.exit('%s:%d: macro %r is not followed by its label: %r'
                     % (path, i + 1, line, lines[i + 1]))
        out.append((int(lm.group(2), 16), m.group(2), MODES[m.group(1)]))
    return out


def read_csv(path):
    if not path.exists():
        return {}
    with path.open(newline='') as f:
        return {int(r['address'], 16): r for r in csv.DictReader(f)}


def main():
    s_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_S
    csv_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CSV
    if not s_path.exists():
        sys.exit('missing %s -- run scripts/disasm.sh' % s_path)

    starts = parse_starts(s_path)
    if not starts:
        sys.exit('no *_func_start macros in %s' % s_path)
    addrs = [a for a, _, _ in starts]
    if len(set(addrs)) != len(addrs):
        sys.exit('duplicate function start in %s' % s_path)
    if addrs != sorted(addrs):
        sys.exit('function starts in %s are not in address order' % s_path)
    for a, _, m in starts:
        if m == 'arm' and a % 4:
            sys.exit('arm function 0x%08X is not 4-aligned' % a)
        if m == 'thumb' and a % 2:
            sys.exit('thumb function 0x%08X is not 2-aligned' % a)

    old = read_csv(csv_path)
    missing = sorted(set(old) - set(addrs))
    if missing:
        sys.exit('in the CSV but not in the disassembly: %s (gbadisasm must echo every '
                 '*_func line of rom.cfg)' % ', '.join('0x%08X' % a for a in missing))

    rows = []
    kept = new = 0
    for i, (a, name, mode) in enumerate(starts):
        size = (starts[i + 1][0] if i + 1 < len(starts) else SENTINEL) - a
        unit = 2 if mode == 'thumb' else 4
        if size < unit:
            sys.exit('0x%08X size %d < %d (two starts too close together)' % (a, size, unit))
        prev = old.get(a)
        if prev is not None:
            if prev['mode'] != mode:
                sys.exit('0x%08X changed mode %s -> %s' % (a, prev['mode'], mode))
            source = prev['source']
            kept += 1
        else:
            source = 'disasm'
            new += 1
        rows.append((a, name, mode, size, source))

    with csv_path.open('w', newline='', encoding='ascii') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['address', 'name', 'mode', 'size', 'source'])
        for a, name, mode, size, source in rows:
            w.writerow(['0x%08X' % a, name, mode, size, source])

    thumb = sum(1 for r in rows if r[2] == 'thumb')
    print('functions_from_rom_s: %d functions (thumb %d, arm %d) from %s'
          % (len(rows), thumb, len(rows) - thumb, s_path.name))
    print('  kept %d, new %d (source=disasm), stale 0' % (kept, new))
    print('  wrote %s' % csv_path)


if __name__ == '__main__':
    main()
