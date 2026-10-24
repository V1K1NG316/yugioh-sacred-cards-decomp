"""Check for the local job "text decoder" (tools/decode_text.py).

Runs tools/decode_text.py in this checkout, feeds it a fixed list of 920 ROM addresses
(all 900 card names + the first 20 card descriptions) and compares its stdout with the
expected output recomputed here, independently, straight from the ROM.

Spec the job must implement (ROM = private/baserom.gba, file offset + 0x08000000 = ROM address):
  * Addresses come from argv, or from stdin one per line when argv is empty (blank lines are
    ignored). The check uses stdin.
  * A record is the bytes from its address up to (not including) the first 0x00 byte, which
    must appear within 4096 bytes (else the tool must exit non-zero). A language field starts
    at each byte pair "$<digit>" (0x24 then 0x30-0x39) inside the record; a field's text runs
    from the byte after that pair up to the next pair, and for the last field up to the end of
    the record.
  * One output line per field, in record order and field order:
        <address as "0x%08X">\\t<language digit>\\t<decoded text>\\n
  * Decoding a field, byte by byte:
        0x87 <code> -> the character for <code> from config/text_glyphs.csv (rows whose char
                       field is empty are not decodable), else the 5 characters \\x87\\xNN
                       (lowercase hex); a trailing 0x87 at the end of the field -> \\x87
        0x5E        -> \\n
        0x23 0x30   -> \\n   ('#' followed by any other byte stays '#')
        0x25        -> ,
        0x20-0x7E   -> the byte itself
        other       -> \\xNN (lowercase)
stdout must hold exactly the data lines and nothing else.

Fixed address list: private/baserom.gba word at 0x08D310E4 + 4k (card names, k = 0..899) and
at 0x08E94E7C + 4k (card descriptions, k = 0..19).

Usage: python3 tools/test_decode_text.py
"""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'decode_text.py'
GLYPHS = ROOT / 'config' / 'text_glyphs.csv'
BASE = 0x08000000
NAMES = 0x08D310E4
DESCS = 0x08E94E7C
MAX_RECORD = 4096


def glyph_table():
    tab = {}
    for row in GLYPHS.read_text(encoding='utf-8').splitlines():
        row = row.strip()
        if row == '' or row[0] == '#' or row.startswith('code,'):
            continue
        cols = row.split(',')
        if cols[1] != '':
            tab[int(cols[0], 16)] = cols[1]
    return tab


def one_field(blob, tab):
    """Decode one field (bytes only, no markers) the way the spec says."""
    pos, out = 0, ''
    while pos < len(blob):
        byte = blob[pos]
        if byte == 0x87 and pos + 1 < len(blob):
            nxt = blob[pos + 1]
            out += tab[nxt] if nxt in tab else '\\x87\\x%02x' % nxt
            pos += 2
        elif byte == 0x87:
            out += '\\x87'
            pos += 1
        elif byte == 0x5E:
            out += '\\n'
            pos += 1
        elif byte == 0x23 and blob[pos + 1:pos + 2] == b'0':
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


def expected(data, addrs):
    """Whole stdout recomputed here: for each address, every field, line by line."""
    tab = glyph_table()
    lines = []
    for addr in addrs:
        if not BASE <= addr < BASE + len(data):
            raise SystemExit('FAIL 0x%08X is outside the ROM' % addr)
        window = data[addr - BASE:addr - BASE + MAX_RECORD]
        cut = window.find(b'\x00')
        if cut < 0:
            raise SystemExit('FAIL no 0x00 in the record at 0x%08X' % addr)
        blob = window[:cut]
        marks = [(k, blob[k + 1]) for k in range(len(blob) - 1)
                 if blob[k] == 0x24 and 0x30 <= blob[k + 1] <= 0x39]
        if not marks:
            raise SystemExit('FAIL no field marker at 0x%08X' % addr)
        for n, (start, digit) in enumerate(marks):
            first = start + 2
            last = marks[n + 1][0] if n + 1 < len(marks) else len(blob)
            lines.append('0x%08X\t%d\t%s\n' % (addr, digit - 0x30, one_field(blob[first:last], tab)))
    return ''.join(lines)


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/decode_text.py does not exist')
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    data = ROM.read_bytes()
    addrs = [struct.unpack_from('<I', data, NAMES - BASE + 4 * k)[0] for k in range(900)]
    addrs += [struct.unpack_from('<I', data, DESCS - BASE + 4 * k)[0] for k in range(20)]
    want = expected(data, addrs)
    stdin_text = ''.join('0x%08X\n' % a for a in addrs)
    r = subprocess.run([sys.executable, str(SCRIPT)], input=stdin_text, capture_output=True,
                       text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit('FAIL decode_text.py exited %d\n%s\n%s' % (r.returncode, r.stdout[-2000:],
                                                            r.stderr[-2000:]))
    got = r.stdout
    if got != want:
        gl, wl = got.split('\n'), want.split('\n')
        for k in range(max(len(gl), len(wl))):
            a = gl[k] if k < len(gl) else '<missing>'
            b = wl[k] if k < len(wl) else '<missing>'
            if a != b:
                sys.exit('FAIL line %d differs\n  got : %r\n  want: %r' % (k + 1, a, b))
        sys.exit('FAIL stdout differs in length: got %d bytes, want %d' % (len(got), len(want)))
    rows = want.splitlines()
    print('records: %d' % len(addrs))
    print('fields: %d' % len(rows))
    print('bytes: %d' % len(want))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
