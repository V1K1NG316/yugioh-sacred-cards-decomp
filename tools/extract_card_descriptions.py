"""Extract every card's description from the Yu-Gi-Oh! The Sacred Cards ROM.

Reads private/baserom.gba, resolves card-name and card-description pointer
tables, decodes the text, and writes private/extracted/card_descriptions.tsv.

Spec (file offset + 0x08000000 = ROM address)::

  Card numbers:        1..900
  NAME table base:     0x08D310E4
  DESC table base:     0x08E94E7C
  For card n (k=n-1): name_addr = u32(NAME+k*4), desc_addr = u32(DESC+k*4)

  Record = bytes from addr up to (not including) first 0x00 (must be within
  4096 bytes).  A field's text runs from the byte after "$0" (0x24 0x30) up
  to the next "$<digit>" marker pair, or to end of record for the last field.

  Glyph decoding (0x87 <code>): look up <code> in config/text_glyphs.csv
  (rows with empty char are not decodable). Other special bytes:
    0x87 <code>  -> glyph chars[code] if present, else \\x87\\x<code>
    0x5E         -> \\n
    0x23 0x30    -> \\n ;  0x23 with other byte stays '#'
    0x25         -> ','
    0x20-0x7E    -> byte itself
    other         -> \\x<code>

Output: private/extracted/card_descriptions.tsv
  One line per card (card 1 first), UTF-8, LF-separated:
    <n>\t<name_addr>\t<name_text>\t<desc_addr>\t<desc_text>
  Address formatted as 0x%08X.

Stdout:
    cards: 900
    bytes: <file size of card_descriptions.tsv>
"""
import csv
import struct
import sys
from pathlib import Path

BASE = 0x08000000
NAME_TABLE = 0x08D310E4
DESC_TABLE = 0x08E94E7C
COUNT = 900
MAX_RECORD = 4096

GLYPHS_CSV = Path(__file__).resolve().parents[1] / 'config' / 'text_glyphs.csv'
OUT = Path(__file__).resolve().parents[1] / 'private' / 'extracted' / 'card_descriptions.tsv'


def load_glyphs():
    """Load the glyph lookup table from config/text_glyphs.csv."""
    tab = {}
    for row in GLYPHS_CSV.read_text(encoding='utf-8').splitlines():
        col = row.strip().split(',')
        if len(col) < 3 or col[0].startswith('#') or col[0] == 'code' or col[1] == '':
            continue
        tab[int(col[0], 16)] = col[1]
    return tab


def u32_at(data, addr):
    """Read a little-endian u32 at file offset addr."""
    o = addr - BASE
    return int.from_bytes(data[o:o + 4], 'little')


def get_blob(data, addr):
    """Read bytes from addr up to the first 0x00 (max 4096 bytes).

    Returns the blob bytes.  Exits 1 on error."""
    if not BASE <= addr < BASE + len(data):
        print('ERROR: record address 0x%08X outside ROM' % addr, file=sys.stderr)
        sys.exit(1)
    o = addr - BASE
    window = data[o:o + MAX_RECORD]
    cut = window.find(b'\x00')
    if cut < 0:
        print('ERROR: no 0x00 in record at 0x%08X' % addr, file=sys.stderr)
        sys.exit(1)
    return window[:cut]


def find_markers(blob):
    """Find field marker positions: blob[i]==0x24 and blob[i+1] in 0x30..0x39."""
    marks = []
    for i in range(len(blob) - 1):
        if blob[i] == 0x24 and 0x30 <= blob[i + 1] <= 0x39:
            marks.append(i)
    return marks


def decode(raw, glyphs):
    """Decode a sequence of bytes using the glyph table and special bytes."""
    out = []
    i = 0
    while i < len(raw):
        byte = raw[i]
        if byte == 0x87:
            if i + 1 == len(raw):
                out.append(r'\x87\x%02x' % byte)
                i += 1
            else:
                code = raw[i + 1]
                if code in glyphs:
                    out.append(glyphs[code])
                else:
                    out.append(r'\x87\x%02x' % code)
                i += 2
        elif byte == 0x5E:
            out.append(r'\n')
            i += 1
        elif byte == 0x23 and raw[i + 1:i + 2] == b'0':
            out.append(r'\n')
            i += 2
        elif byte == 0x25:
            out.append(',')
            i += 1
        elif 0x20 <= byte <= 0x7E:
            out.append(chr(byte))
            i += 1
        else:
            out.append(r'\x%02x' % byte)
            i += 1
    return ''.join(out)


def extract_english(data, addr, glyphs):
    """Extract the English ('$0') field text from a record at `addr`."""
    blob = get_blob(data, addr)
    marks = find_markers(blob)
    if not marks:
        print('ERROR: no marker in record at 0x%08X' % addr, file=sys.stderr)
        sys.exit(1)
    if blob[marks[0] + 1] != 0x30:
        print('ERROR: first marker is not $0 in record at 0x%08X' % addr, file=sys.stderr)
        sys.exit(1)
    if len(marks) > 1:
        end = marks[1]
    else:
        end = len(blob)
    return decode(blob[marks[0] + 2:end], glyphs)


def rom(data, addr):
    """Validate that addr is within the ROM bounds."""
    if not BASE <= addr < BASE + len(data):
        raise SystemExit('FAIL the table points outside the ROM at 0x%08X' % addr)
    return addr


def main():
    rom_path = Path(__file__).resolve().parents[1] / 'private' / 'baserom.gba'
    if not rom_path.exists():
        sys.exit('FAIL no ROM at %s' % rom_path)
    data = rom_path.read_bytes()
    glyphs = load_glyphs()
    glyphs_csv = load_glyphs.__globals__['GLYPHS_CSV']

    lines = []
    for k in range(COUNT):
        name_addr = rom(data, NAME_TABLE + 4 * k)
        name_addr = u32_at(data, name_addr)
        desc_addr = rom(data, DESC_TABLE + 4 * k)
        desc_addr = u32_at(data, desc_addr)

        name_text = extract_english(data, name_addr, glyphs)
        desc_text = extract_english(data, desc_addr, glyphs)

        line = '%d\t0x%08X\t%s\t0x%08X\t%s\n' % (
            k + 1, name_addr, name_text, desc_addr, desc_text)
        lines.append(line)

    out_bytes = ''.join(lines).encode('utf-8')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(out_bytes)

    print('cards: %d' % COUNT)
    print('bytes: %d' % len(out_bytes))


if __name__ == '__main__':
    main()
