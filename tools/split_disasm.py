#!/usr/bin/env python3
"""Split private/asm/rom_full.s into one file per function plus data files (Y3).

usage: split_disasm.py [rom_full.s]

Output (all generated, all untracked under private/):

    private/asm/funcs/<name>.s    one assembly chunk per function: the
                                  *_func_start macro line, the address label and
                                  everything up to the next function (its own
                                  literal pools and any table wedged between the
                                  two functions stay with the earlier one);
    private/asm/data/*.s          the trailing data part of the ROM (from the last
                                  instruction onwards), cut into <= 64 KiB files so
                                  each one starts at a label;
    private/asm/rom.s             the build entry point: header + .include lines in
                                  address order.  This is what `make compare`
                                  assembles.

Grouping rule for the trailing data (my choice, per TASK [013] item 3): the data
part is the longest tail of data-only lines (label/.incbin/.4byte/.align), so a
literal pool that follows the very last instruction lands in asm/data rather than
in the last function; a data file holds about 64 KiB at most, and a `.incbin`
longer than that is cut into pieces, so asm/data doubles as an index of the ROM's
data space (what is "data" at all is the disassembler's decision, A8).

Prints the counts and the byte split (instructions vs .incbin).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_IN = REPO / 'private' / 'asm' / 'rom_full.s'
FUNCS_DIR = REPO / 'private' / 'asm' / 'funcs'
DATA_DIR = REPO / 'private' / 'asm' / 'data'
ROM_S = REPO / 'private' / 'asm' / 'rom.s'
BASE = 0x08000000
DATA_CHUNK = 0x10000

FUNC_MACRO_RE = re.compile(r'^\t(thumb_func_start|arm_func_start|non_word_aligned_thumb_func_start) (\S+)$')
FUNC_LABEL_RE = re.compile(r'^(\S+): @ 0x([0-9A-F]{8})$')
DATA_LABEL_RE = re.compile(r'^_([0-9A-F]{8}):')
INCBIN_RE = re.compile(r'^\t\.incbin "([^"]+)", 0x([0-9A-F]+), (\d+)$')
FOUR_RE = re.compile(r'^\t\.4byte\s+([^\n]+)$')
RAW_BYTE_RE = re.compile(r'^\t\.byte\s+([^\n]+)$')
ALIGN_RE = re.compile(r'^\t\.align\s+(\d+)(?:\s*,\s*\d+)?$')
DIRECTIVE_RE = re.compile(r'^\t\.(include "asm/macros\.inc"|syntax unified|text)$')
SAFE_RE = re.compile(r'[^A-Za-z0-9_]')


def items(arg):
    return len([x for x in arg.split('@')[0].replace(',', ' ').split() if x])


def line_bytes(line):
    """Bytes a data line emits, or None when the line is not a data line."""
    m = INCBIN_RE.match(line)
    if m:
        return int(m.group(3))
    m = FOUR_RE.match(line)
    if m:
        return 4 * items(m.group(1))
    m = DATA_LABEL_RE.match(line)
    if m:
        rest = line[m.end():].strip()
        if not rest:
            return 0
        m2 = FOUR_RE.match(rest) or RAW_BYTE_RE.match(rest)
        if m2:
            return (4 if rest.startswith('\t.4byte') else 1) * items(m2.group(1))
        return 0
    m = RAW_BYTE_RE.match(line)
    if m:
        return items(m.group(1))
    if ALIGN_RE.match(line):
        return 0
    return None


def is_data_line(line):
    return (not line.strip()) or line.lstrip().startswith('@') or line_bytes(line) is not None


def code_end(lines):
    """Index of the first line of the trailing data-only tail."""
    i = len(lines)
    while i > 0 and is_data_line(lines[i - 1]):
        i -= 1
    return i


def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')
    return len(text)


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_IN
    if not src.exists():
        sys.exit('missing %s -- run scripts/disasm.sh' % src)
    lines = src.read_text(encoding='utf-8').splitlines()

    macros = [i for i, l in enumerate(lines) if FUNC_MACRO_RE.match(l)]
    if not macros:
        sys.exit('%s has no *_func_start macros' % src)
    for i, l in enumerate(lines[:macros[0]]):
        if l.strip() and not (DIRECTIVE_RE.match(l) or l.lstrip().startswith('@')):
            sys.exit('unexpected line %d before the first function: %r' % (i + 1, l))

    cut = code_end(lines)
    if macros[-1] >= cut:
        sys.exit('unexpected: a function starts at or after the data tail (line %d)' % (macros[-1] + 1))

    FUNCS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for old in list(FUNCS_DIR.glob('*.s')) + list(DATA_DIR.glob('*.s')):
        old.unlink()

    # ---- functions ----
    includes = []
    seen = set()
    for n, start in enumerate(macros):
        end = macros[n + 1] if n + 1 < len(macros) else cut
        m = FUNC_MACRO_RE.match(lines[start])
        name, mode = m.group(2), 'arm' if m.group(1) == 'arm_func_start' else 'thumb'
        lm = FUNC_LABEL_RE.match(lines[start + 1]) if start + 1 < len(lines) else None
        if not lm or lm.group(1) != name:
            sys.exit('line %d: macro %r is not followed by its label' % (start + 1, lines[start]))
        addr = int(lm.group(2), 16)
        fname = SAFE_RE.sub('_', name) + '.s'
        if fname in seen:
            sys.exit('two functions want the file %s' % fname)
        seen.add(fname)
        body = lines[start:end]
        head = '@ %s  %s  0x%08X  (%d source lines)\n' % (name, mode, addr, len(body))
        write(FUNCS_DIR / fname, head + '\n'.join(body) + '\n')
        includes.append('private/asm/funcs/%s' % fname)

    # ---- trailing data ----
    # Atoms: (address, line).  A label line gives its own address, a long .incbin is
    # cut into DATA_CHUNK pieces so one file never holds more than that.
    atoms = []
    addr = None
    for i in range(cut, len(lines)):
        line = lines[i]
        m = DATA_LABEL_RE.match(line)
        if m:
            addr = int(m.group(1), 16)
            atoms.append((addr, line))
            continue
        m = INCBIN_RE.match(line)
        if m:
            off, length = int(m.group(2), 16), int(m.group(3))
            if addr is not None and BASE + off != addr:
                sys.exit('data tail line %d: .incbin starts at 0x%08X, expected 0x%08X'
                         % (i + 1, BASE + off, addr))
            for k in range(0, length, DATA_CHUNK):
                n = min(DATA_CHUNK, length - k)
                atoms.append((BASE + off + k,
                              '\t.incbin "private/baserom.gba", 0x%08X, %d' % (off + k, n)))
                addr = BASE + off + k + n
            continue
        n = line_bytes(line)
        if n:
            if addr is not None:
                addr += n
        atoms.append((addr, line))

    groups = []
    group = []
    size = 0
    for a, line in atoms:
        n = line_bytes(line) or 0
        if group and (size >= DATA_CHUNK or (DATA_LABEL_RE.match(line) and size >= DATA_CHUNK // 2)):
            groups.append(group)
            group, size = [], 0
        group.append((a, line))
        size += n
    if group:
        groups.append(group)

    incbin_bytes = sum(int(INCBIN_RE.match(l).group(3)) for l in lines if INCBIN_RE.match(l))
    for gi, group in enumerate(groups):
        addr = next((a for a, _ in group if a is not None), None)
        if addr is None:
            sys.exit('data group %d has no address to name it by' % gi)
        fname = 'data_%08X.s' % addr
        if fname in seen:
            sys.exit('two data groups want the file %s' % fname)
        seen.add(fname)
        total = sum(line_bytes(l) or 0 for _, l in group)
        head = '@ data 0x%08X-0x%08X (%d bytes)\n' % (addr, addr + total - 1, total)
        write(DATA_DIR / fname, head + '\n'.join(l for _, l in group) + '\n')
        includes.append('private/asm/data/%s' % fname)

    # ---- entry point ----
    text = ('@ Generated by scripts/disasm.sh -- do not edit.\n'
            '@ Whole-ROM disassembly of private/baserom.gba: %d functions and %d data files,\n'
            '@ included in address order by tools/split_disasm.py.\n\n'
            '\t.include "asm/macros.inc"\n'
            '\t.syntax unified\n'
            '\t.text\n\n' % (len(macros), len(groups)))
    text += ''.join('\t.include "%s"\n' % p for p in includes)
    write(ROM_S, text)

    print('split_disasm: %d function files, %d data files -> %s'
          % (len(macros), len(groups), ROM_S))
    if (REPO / 'private' / 'baserom.gba').exists():
        rom = (REPO / 'private' / 'baserom.gba').stat().st_size
        print('  .incbin bytes %d, instructions/pools/padding %d, ROM %d'
              % (incbin_bytes, rom - incbin_bytes, rom))


if __name__ == '__main__':
    main()
