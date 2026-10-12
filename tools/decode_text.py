#!/usr/bin/env python3
"""Text decoder for Yu-Gi-Oh! The Sacred Cards ROM.

Reads ROM addresses from stdin (one per line) or from command-line arguments.
Each address is decoded: the record blob is extracted from the ROM, fields are
identified by "$<digit>" markers, and each field's byte range is decoded to text.
"""
import sys
import struct
from pathlib import Path

# --- Config ---
WORKTREE = Path(__file__).resolve().parents[1]
ROM_PATH = WORKTREE / 'private' / 'baserom.gba'
GLYPHS_PATH = WORKTREE / 'config' / 'text_glyphs.csv'
BASE = 0x08000000
MAX_RECORD = 4096


def load_glyph_table():
    """Load the glyph table from text_glyphs.csv.
    
    Returns a dict mapping code (int) -> char (str) for decodable entries.
    Lines starting with '#' and blank lines are skipped. The header line
    starting with 'code,' is skipped. Only rows whose char field is non-empty
    are included.
    """
    tab = {}
    text = GLYPHS_PATH.read_text(encoding='utf-8')
    for row in text.splitlines():
        row = row.strip()
        if row == '' or row[0] == '#' or row.startswith('code,'):
            continue
        cols = row.split(',')
        code = int(cols[0], 16)
        char = cols[1]
        if char != '':
            tab[code] = char
    return tab


def read_addresses():
    """Read addresses from stdin (one per line) when no CLI args.
    
    Accepts formats like "0x080A67A8" or "080A67A8". Returns list of int addresses.
    """
    lines = sys.stdin.read().splitlines()
    addrs = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        if line.lower().startswith('0x'):
            addr = int(line, 16)
        else:
            addr = int(line, 16)
        addrs.append(addr)
    return addrs


def parse_args_addresses():
    """Read addresses from command-line arguments."""
    addrs = []
    for arg in sys.argv[1:]:
        arg = arg.strip()
        if arg == '':
            continue
        if arg.lower().startswith('0x'):
            addr = int(arg, 16)
        else:
            addr = int(arg, 16)
        addrs.append(addr)
    return addrs


def decode_field_bytes(blob, glyph_tab):
    """Decode a byte range (blob) to text, one field's content.
    
    Byte-by-byte rules:
        0x87 <code> -> char for code from glyph table, or \\x87\\xHH if not decodable
        0x87 at end -> \\x87
        0x5E       -> \\n
        0x23 0x30  -> \\n (skip both bytes)
        0x25       -> ,
        0x20-0x7E  -> chr(byte)
        else       -> \\xHH
    """
    pos = 0
    out = ''
    while pos < len(blob):
        byte = blob[pos]
        if byte == 0x87 and pos + 1 < len(blob):
            code = blob[pos + 1]
            if code in glyph_tab:
                out += glyph_tab[code]
            else:
                out += '\\x87\\x%02x' % code
            pos += 2
        elif byte == 0x87:
            out += '\\x87'
            pos += 1
        elif byte == 0x5E:
            out += '\\n'
            pos += 1
        elif byte == 0x23 and pos + 1 < len(blob) and blob[pos + 1] == 0x30:
            out += '\\n'
            pos += 2
        elif byte == 0x25:
            out += ','
            pos += 1
        elif 0x20 <= byte <= 0x7E:
            out += chr(byte)
            pos += 1
        else:
            out += '\\x%02x' % byte
            pos += 1
    return out


def decode_address(addr, rom_data, glyph_tab):
    """Decode one address. Returns (language_digit, text) or raises SystemExit."""
    if addr < BASE or addr >= BASE + len(rom_data):
        print('ERROR 0x%08X is outside the ROM' % addr, file=sys.stderr)
        raise SystemExit(1)
    
    offset = addr - BASE
    window = rom_data[offset:offset + MAX_RECORD]
    
    # Find first 0x00 byte
    cut = window.find(b'\x00')
    if cut < 0:
        print('ERROR no 0x00 in record at 0x%08X' % addr, file=sys.stderr)
        raise SystemExit(1)
    
    blob = window[:cut]
    
    # Find field markers: positions where blob[i] == 0x24 and blob[i+1] == 0x30..0x39
    marks = []
    for i in range(len(blob) - 1):
        if blob[i] == 0x24 and 0x30 <= blob[i + 1] <= 0x39:
            marks.append((i, blob[i + 1] - 0x30))
    
    if not marks:
        print('ERROR no field marker at 0x%08X' % addr, file=sys.stderr)
        raise SystemExit(1)
    
    # Output one line per field
    for n, (marker_pos, digit) in enumerate(marks):
        first = marker_pos + 2
        if n + 1 < len(marks):
            last = marks[n + 1][0]
        else:
            last = len(blob)
        
        field_text = decode_field_bytes(blob[first:last], glyph_tab)
        print('0x%08X\t%d\t%s' % (addr, digit, field_text))


def main():
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")  # exact UTF-8 + LF on Windows too (critics J0034)
    glyph_tab = load_glyph_table()
    rom_data = ROM_PATH.read_bytes()
    
    if len(sys.argv) > 1:
        # Addresses from CLI arguments
        addrs = parse_args_addresses()
    else:
        # Addresses from stdin
        addrs = read_addresses()
    
    if not addrs:
        raise SystemExit('ERROR: no addresses provided')
    
    for addr in addrs:
        decode_address(addr, rom_data, glyph_tab)


if __name__ == '__main__':
    main()
