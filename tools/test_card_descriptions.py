"""Check for the local job "card-description extractor" (tools/extract_card_descriptions.py).

Runs the tool in this checkout, then recomputes the whole expected file here, independently,
straight from the ROM, and compares byte for byte.

Spec the job must implement (ROM = private/baserom.gba, file offset + 0x08000000 = ROM address):
  * Card numbers are 1..900. Card number n is entry k = n-1 of the card-name pointer table at
    0x08D310E4 (900 little-endian u32) and of the card-description pointer table at 0x08E94E7C
    (900 little-endian u32). (These are the tables the game itself reads: `sub_080073E4` and
    `sub_08006BE4`.)
  * The texts are the English ("$0") field of each record, decoded with the rules below; the
    padding spaces of the pre-wrapped text are kept.
  * Writes private/extracted/card_descriptions.tsv: one line per card, UTF-8, "\\n" separated,
        <n>\\t<name address "0x%08X">\\t<name text>\\t<description address "0x%08X">\\t<description text>
    Records in card order (1 first).
  * stdout: exactly "cards: 900" and "bytes: <file size>".
Decoding a field, byte by byte:
        0x87 <code> -> the character for <code> from config/text_glyphs.csv (a row with an empty
                       char is not decodable), else the 5 characters \\x87\\xNN (lowercase hex)
        0x5E        -> \\n
        0x23 0x30   -> \\n ; '#' followed by anything else stays '#'
        0x25        -> ,
        0x20-0x7E   -> the byte itself
        other       -> \\xNN (lowercase)
A record is the bytes from its address up to (not including) the first 0x00 byte, which must
appear within 4096 bytes (else the tool must exit non-zero). A field's text runs from the byte
after its "$0" pair up to the next "$<digit>" pair, or to the end of the record for the last
field. The extracted text is the English field, which holds no 0x87 escapes; the glyph path of
the decoder is covered by tools/test_decode_text.py.

Usage: python3 tools/test_card_descriptions.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'extract_card_descriptions.py'
GLYPHS = ROOT / 'config' / 'text_glyphs.csv'
OUT = ROOT / 'private' / 'extracted' / 'card_descriptions.tsv'
BASE = 0x08000000
NAME_TABLE = 0x08D310E4
DESC_TABLE = 0x08E94E7C
COUNT = 900
MAX_RECORD = 4096


def glyphs():
    tab = {}
    for row in GLYPHS.read_text(encoding='utf-8').splitlines():
        cols = row.strip().split(',')
        if len(cols) < 3 or cols[0].startswith('#') or cols[0] == 'code' or cols[1] == '':
            continue
        tab[int(cols[0], 16)] = cols[1]
    return tab


def u32(data, addr):
    o = addr - BASE
    return int.from_bytes(data[o:o + 4], 'little')


def decode(raw, tab):
    out, i = '', 0
    while i < len(raw):
        byte = raw[i]
        if byte == 0x87:
            if i + 1 == len(raw):
                out, i = out + '\\x87', i + 1
            else:
                code = raw[i + 1]
                out += tab[code] if code in tab else '\\x87\\x%02x' % code
                i += 2
        elif byte == 0x5E:
            out, i = out + '\\n', i + 1
        elif byte == 0x23 and raw[i + 1:i + 2] == b'0':
            out, i = out + '\\n', i + 2
        elif byte == 0x25:
            out, i = out + ',', i + 1
        elif 0x20 <= byte <= 0x7E:
            out, i = out + chr(byte), i + 1
        else:
            out, i = out + '\\x%02x' % byte, i + 1
    return out


def english(data, addr, tab):
    if not BASE <= addr < BASE + len(data):
        raise SystemExit('FAIL the table points outside the ROM at 0x%08X' % addr)
    window = data[addr - BASE:addr - BASE + MAX_RECORD]
    cut = window.find(b'\x00')
    if cut < 0:
        raise SystemExit('FAIL no 0x00 in the record at 0x%08X' % addr)
    blob = window[:cut]
    marks = [k for k in range(len(blob) - 1)
             if blob[k] == 0x24 and 0x30 <= blob[k + 1] <= 0x39]
    if not marks or blob[marks[0] + 1] != 0x30:
        raise SystemExit('FAIL no "$0" field in the record at 0x%08X' % addr)
    end = marks[1] if len(marks) > 1 else len(blob)
    return decode(blob[marks[0] + 2:end], tab)


def expected(data):
    tab = glyphs()
    out = []
    for k in range(COUNT):
        name_addr = u32(data, NAME_TABLE + 4 * k)
        desc_addr = u32(data, DESC_TABLE + 4 * k)
        out.append('%d\t0x%08X\t%s\t0x%08X\t%s\n'
                   % (k + 1, name_addr, english(data, name_addr, tab),
                      desc_addr, english(data, desc_addr, tab)))
    return ''.join(out).encode('utf-8')


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/extract_card_descriptions.py does not exist')
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit('FAIL extract_card_descriptions.py exited %d\n%s\n%s'
                 % (r.returncode, r.stdout[-2000:], r.stderr[-2000:]))
    want = expected(ROM.read_bytes())
    if r.stdout.strip() != 'cards: %d\nbytes: %d' % (COUNT, len(want)):
        sys.exit('FAIL stdout must be "cards: %d" / "bytes: %d", got %r'
                 % (COUNT, len(want), r.stdout))
    if not OUT.exists():
        sys.exit('FAIL private/extracted/card_descriptions.tsv was not written')
    got = OUT.read_bytes()
    if got != want:
        gl, wl = got.split(b'\n'), want.split(b'\n')
        for k in range(max(len(gl), len(wl))):
            a = gl[k] if k < len(gl) else b'<missing>'
            b = wl[k] if k < len(wl) else b'<missing>'
            if a != b:
                sys.exit('FAIL line %d differs\n  got : %r\n  want: %r' % (k + 1, a, b))
        sys.exit('FAIL file length differs: got %d bytes, want %d' % (len(got), len(want)))
    print('cards: %d' % COUNT)
    print('bytes: %d' % len(got))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
