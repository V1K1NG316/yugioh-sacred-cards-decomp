"""Check for the local job "multi-language text-table extractor" (tools/extract_text_tables.py).

Runs tools/extract_text_tables.py in this checkout and recomputes the whole expected TSV
independently from the ROM (pointer table -> record -> raw bytes) and compares byte for byte.

Spec the job must implement (ROM = private/baserom.gba, addresses = file offset + 0x08000000).
The four tables, each a run of little-endian u32 pointers to a record that starts with "$0":
    0x08D30310  140 entries   (credits / "Original character design")
    0x08D36130  124 entries   (duel UI messages: "Duel victory!", "It's #5's turn.")
    0x08D419E0   12 entries   (attribute names: "Light", "Shadow", "Fiend")
    0x08D4BC3C   24 entries   (card-type names: "Dragon", "Magician", "Zombie")
A record is the bytes from its pointer up to (not including) the next 0x00 byte; a pointer with
no 0x00 within 4096 bytes, or outside the ROM, is an error and the script must exit non-zero.
Output: private/extracted/text_tables.tsv, one line per record in table order, each entry of a
table immediately after the previous one:
    <table address "0x%08X">\t<entries in that table>\t<index k, 0-based>\t<record address "0x%08X">\t<record bytes as lowercase hex>
stdout exactly two lines: "tables: 4" and "records: 300".

Usage: PY tools/test_text_tables.py
"""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'extract_text_tables.py'
OUT = ROOT / 'private' / 'extracted' / 'text_tables.tsv'
BASE = 0x08000000
TABLES = [(0x08D30310, 140), (0x08D36130, 124), (0x08D419E0, 12), (0x08D4BC3C, 24)]


def expected(d):
    """Read the four tables straight from the ROM; returns the whole TSV text."""
    lines = []
    for table, count in TABLES:
        for k in range(count):
            ptr = struct.unpack_from('<I', d, table - BASE + 4 * k)[0]
            if not BASE <= ptr < BASE + len(d):
                raise SystemExit('FAIL table 0x%08X entry %d points outside the ROM: 0x%08X'
                                 % (table, k, ptr))
            o = ptr - BASE
            end = d.find(b'\x00', o, o + 4096)
            if end < 0:
                raise SystemExit('FAIL table 0x%08X entry %d has no terminator at 0x%08X'
                                 % (table, k, ptr))
            lines.append('0x%08X\t%d\t%d\t0x%08X\t%s\n' % (table, count, k, ptr, d[o:end].hex()))
    return ''.join(lines)


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/extract_text_tables.py does not exist')
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(f'FAIL extract_text_tables.py exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    want = expected(ROM.read_bytes())
    if r.stdout.strip() != 'tables: %d\nrecords: %d' % (len(TABLES), sum(c for _, c in TABLES)):
        sys.exit(f'FAIL stdout must be "tables: {len(TABLES)}" / "records: {sum(c for _, c in TABLES)}",'
                 f' got {r.stdout!r}')
    if not OUT.exists():
        sys.exit('FAIL private/extracted/text_tables.tsv was not written')
    got = OUT.read_bytes()
    if got != want.encode('ascii'):
        g, w = got.decode('ascii', 'replace').split('\n'), want.split('\n')
        for k, (a, b) in enumerate(zip(g, w)):
            if a != b:
                sys.exit(f'FAIL line {k + 1} differs\n  got : {a!r}\n  want: {b!r}')
        sys.exit(f'FAIL length differs: got {len(g)} lines / {len(got)} bytes, want {len(w)} lines / {len(want)} bytes')
    print('tables: %d' % len(TABLES))
    print('records: %d' % sum(c for _, c in TABLES))
    print('bytes: %d' % len(got))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
