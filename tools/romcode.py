"""Shared helper: how many bytes of a function in config/functions.csv are code.

The Y3 disassembly puts the ROM's bytes in one file per function plus the data files, and every
run of bytes the disassembler did not decode as a label or an instruction appears as
`.incbin "private/baserom.gba", <rom offset>, <length>`. So:

    code bytes of a function = its extent (approximation A5: distance to the next start)
                               minus the `.incbin` bytes that fall inside that extent

Data files matter here: the last function's extent covers the whole 16 MB data tail, which lives
in `private/asm/data/`, not in the function's own file.
"""
import csv
import re
from pathlib import Path

ROM_BASE = 0x08000000
INCBIN = re.compile(r'\.incbin\s+"[^"]*",\s*0x([0-9A-Fa-f]+),\s*(\d+)')


def read_functions(root):
    """[(name, address, extent)] from config/functions.csv, in file order."""
    rows = []
    with (root / 'config' / 'functions.csv').open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows.append((r['name'], int(r['address'], 16), int(r['size']), r['mode']))
    return rows


def data_ranges(root):
    """[(start, end)] ROM addresses of every byte the disassembly left as `.incbin`."""
    out = []
    for d in ('funcs', 'data'):
        for path in sorted((root / 'private' / 'asm' / d).glob('*.s')):
            text = path.read_text(encoding='utf-8', errors='replace')
            for off, length in INCBIN.findall(text):
                start = ROM_BASE + int(off, 16)
                out.append((start, start + int(length)))
    return sorted(out)


def code_bytes(addr, extent, ranges):
    """Bytes of [addr, addr+extent) that no `.incbin` covers."""
    end = addr + extent
    data = 0
    for s, e in ranges:
        if e <= addr:
            continue
        if s >= end:
            break
        data += min(e, end) - max(s, addr)
    return extent - data
