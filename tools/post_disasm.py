#!/usr/bin/env python3
"""Turn raw gbadisasm output into private/asm/rom_full.s, which GNU as accepts.

usage: post_disasm.py <raw.s> <rom_full.s>

Three jobs:

1. Header: macro include, unified syntax, .text.
2. Every run of `.byte` lines becomes one
   `.incbin "private/baserom.gba", <file offset>, <length>` line (Y3 proposal 3).
   Labels are untouched, so every `_0800xxxx` symbol still exists.  `.4byte`
   lines are kept as they are: the 626 pointer/jump-table words name symbols
   (`_08000E9C`), which is exactly the readable form Y4 wants.
3. The few bytes gbadisasm drops after its final label are appended.

A LABEL_DATA prints no line of its own, so the sentinel `data_label` that
tools/make_disasm_cfg.py writes into private/asm/rom.cfg turns into a plain gap
of .byte lines running from the end of the code to the sentinel; only the last 4
bytes of the ROM (the sentinel's own content) are dropped.

Address tracking (the safety net): every label in the raw output carries its
address, so this script walks the body keeping `known`, the ROM address of the
next line.  Labels must agree with it, a data run without a known address is an
error, and the walk must finish on the sentinel -- otherwise the .incbin offsets
and lengths could drift without anyone noticing.
"""
import re
import sys
from pathlib import Path

BASE = 0x08000000
ROM_SIZE = 0x01000000
SENTINEL = BASE + ROM_SIZE - 4
ROM = Path(__file__).resolve().parents[1] / 'private' / 'baserom.gba'
COLUMNS = 16

FUNC_LABEL_RE = re.compile(r'^\S+: @ 0x([0-9A-F]{8})$')
DATA_LABEL_RE = re.compile(r'^_([0-9A-F]{8}):(?:\s+(\.byte|\.4byte)([^@]*?))?\s*(?:@[^\n]*)?$')
RAW_BYTE_RE = re.compile(r'^\t\.byte\s+([^\n]+)$')
FOUR_RE = re.compile(r'^\t\.4byte\s+([^\n]+)$')
ALIGN_RE = re.compile(r'^\t\.align\s+(\d+)(?:\s*,\s*\d+)?$')
LABEL_RE = DATA_LABEL_RE

# A symbol declared with `non_word_aligned_thumb_func_start` carries the Thumb
# function bit (LSB=1) at an address that is only 2-aligned, so GNU as refuses
# the 2-byte encoding of a plain `b <sym>` and silently widens it to a 4-byte
# `b.w`/BL -- bytes the original ROM does not have. `b.n <sym>` forces the
# narrow encoding (verified: same bug reproduced in a 20-line test file, and
# `b.n` fixed it). Only the mnemonics that have a 2-byte form are touched; `bl`
# is always 4 bytes and is left alone.
NARROW_BRANCHES = {'b', 'beq', 'bne', 'bcs', 'bhs', 'bcc', 'blo', 'bmi', 'bpl',
                   'bvs', 'bvc', 'bhi', 'bls', 'bge', 'blt', 'bgt', 'ble', 'bal'}
NWA_START_RE = re.compile(r'^\tnon_word_aligned_thumb_func_start (\S+)$')
BRANCH_TO_RE = re.compile(r'^\t(b[a-z]*)\s+(\S+)$')


def narrow_branches(lines):
    """Force 2-byte branches to non-word-aligned Thumb functions. Returns (lines, n)."""
    targets = {m.group(1) for m in (NWA_START_RE.match(l) for l in lines) if m}
    if not targets:
        return lines, 0
    out = []
    n = 0
    for line in lines:
        m = BRANCH_TO_RE.match(line)
        if m and m.group(1) in NARROW_BRANCHES and m.group(2) in targets:
            out.append('\t%s.n %s' % (m.group(1), m.group(2)))
            n += 1
        else:
            out.append(line)
    return out, n



def item_count(arg, width=1):
    """Bytes a .byte/.4byte operand list covers ('@ comment' stripped)."""
    return width * len([x for x in arg.split('@')[0].replace(',', ' ').split() if x])


def die(msg):
    sys.exit('post_disasm: %s' % msg)


def rewrite(lines):
    """Replace `.byte` runs with `.incbin`, tracking addresses. Returns (lines, stats)."""
    out = []
    known = None            # ROM address of the next line, or None when unknown
    runs = bytes_ = pad = 0
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]

        m = DATA_LABEL_RE.match(line)
        if m:
            addr = int(m.group(1), 16)
            if known is not None and addr != known:
                die('label at line %d says 0x%08X, the byte count says 0x%08X'
                    % (i + 1, addr, known))
            known = addr + (item_count(m.group(3), 4 if m.group(2) == '.4byte' else 1)
                            if m.group(2) else 0)
            out.append(line)
            i += 1
            continue

        m = FUNC_LABEL_RE.match(line)
        if m:
            addr = int(m.group(1), 16)
            if known is not None and addr != known:
                die('function label at line %d says 0x%08X, the byte count says 0x%08X'
                    % (i + 1, addr, known))
            known = addr
            out.append(line)
            i += 1
            continue

        m = RAW_BYTE_RE.match(line)
        if m:
            if known is None:
                die('a .byte run at line %d has no label to give it an address' % (i + 1))
            start = known
            while i < n:
                m = RAW_BYTE_RE.match(lines[i])
                if not m:
                    break
                known += item_count(m.group(1))
                i += 1
            length = known - start
            out.append('\t.incbin "private/baserom.gba", 0x%08X, %d'
                       % (start - BASE, length))
            runs += 1
            bytes_ += length
            continue

        m = FOUR_RE.match(line)
        if m:
            if known is not None:
                known += item_count(m.group(1), 4)
            out.append(line)
            i += 1
            continue

        m = ALIGN_RE.match(line)
        if m:
            if known is not None:
                a = 1 << int(m.group(1))
                new = (known + a - 1) & ~(a - 1)
                pad += new - known
                known = new
            out.append(line)
            i += 1
            continue

        known = None        # an instruction: its length is not in the text
        out.append(line)
        i += 1

    if known is not None and known != SENTINEL:
        die('the body ends at 0x%08X, expected the sentinel 0x%08X' % (known, SENTINEL))
    return out, {'runs': runs, 'bytes': bytes_, 'pad': pad}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    raw_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    raw = raw_path.read_text(encoding='utf-8', errors='replace')
    lines = raw.splitlines()

    labels = [int(m.group(1), 16) for m in (DATA_LABEL_RE.match(l) for l in lines) if m]
    if not labels:
        die('no labels found in %s' % raw_path)
    if max(labels) >= SENTINEL:
        die('raw output has a label at or past the sentinel 0x%08X (0x%08X): '
            'the tail is no longer a fixed 4 bytes' % (SENTINEL, max(labels)))
    if not lines[-1].startswith('\t.byte'):
        die('raw output does not end in a .byte line: %r' % lines[-1])

    rom = ROM.read_bytes()
    tail = rom[SENTINEL - BASE:]
    body, stats = rewrite(lines)
    body, narrowed = narrow_branches(body)

    header = [
        '@ Generated by scripts/disasm.sh -- do not edit.',
        '@ Whole-ROM disassembly of private/baserom.gba, function list from config/functions.csv.',
        '@ Data is .incbin; tools/split_disasm.py splits this file into asm/funcs and asm/data.',
        '',
        '\t.include "asm/macros.inc"',
        '\t.syntax unified',
        '\t.text',
        '',
    ]
    text = '\n'.join(header) + '\n' + '\n'.join(body) + '\n'
    text += ('\n@ bytes 0x%08X-0x%08X: after the disassembler\'s final label\n_%08X:\n'
             '\t.incbin "private/baserom.gba", 0x%08X, %d\n'
             % (SENTINEL, BASE + len(rom) - 1, SENTINEL, SENTINEL - BASE, len(tail)))

    out_path.write_text(text, encoding='utf-8', newline='\n')
    print('raw -> %s : %d lines, %d labels, last label 0x%08X'
          % (raw_path.name, len(lines), len(labels), max(labels)))
    print('wrote %s: %d data runs -> .incbin (%d bytes, A8), %d trailing bytes appended, '
          '%d branches narrowed to .n' % (out_path, stats['runs'], stats['bytes'],
                                          len(tail), narrowed))
    print('  non-.incbin bytes: %d = instructions + .4byte words + .align padding (%d bytes of '
          '.align padding could be pinned by the address tracker)'
          % (len(rom) - stats['bytes'], stats['pad']))


if __name__ == '__main__':
    main()
