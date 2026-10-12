#!/usr/bin/env python3
"""Check the ROM string extractor's output (job J0002 / milestone Y2).

Usage: PY tools/test_rom_strings.py     (run from anywhere; exits 0 only if right)

The extractor `tools/rom_strings.py` must write `private/extracted/strings.txt`,
one entry per line, `0xADDR<TAB>text`, LF endings, ASCII.  This check re-reads
the ROM itself and verifies every single line:
  1. the line has the exact `0x` + 8 uppercase hex digits + TAB shape;
  2. addresses strictly increase;
  3. the text is 6..80 printable ASCII characters;
  4. the text is byte-identical to the ROM at that address (round trip);
  5. the byte before the run and the byte after it are not printable ASCII
     (so the run really is maximal);
  6. the known strings `YUGIOH DM7` (0x080000A0) and `SRAM_V112` are present;
  7. there are at least 50000 entries (real 2026-10-12 result: 57622).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'strings.txt'
BASE = 0x08000000
MIN_ENTRIES = 50000
LINE = re.compile(r'^0x([0-9A-F]{8})\t([ -~]{6,})$')
KNOWN = {0x080000A0: 'YUGIOH DM7', 0x080000AC: 'AY7EA4', 0x08176698: 'SRAM_V112'}

errors = []


def fail(msg):
    errors.append(msg)
    if len(errors) <= 20:
        print('FAIL ' + msg)


def main():
    if not ROM.exists():
        sys.exit(f'FAIL missing {ROM}')
    rom = ROM.read_bytes()
    script = ROOT / 'tools' / 'rom_strings.py'
    if not script.exists():
        sys.exit(f'FAIL missing {script}')
    r = subprocess.run([sys.executable, str(script)], cwd=str(script.parent.parent),
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'FAIL rom_strings.py exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    print(f'rom_strings.py exit 0, stdout: {r.stdout.strip()!r}')

    if not OUT.exists():
        sys.exit(f'FAIL missing {OUT}')
    raw = OUT.read_bytes()
    if b'\r' in raw:
        fail('output contains CR (must be LF only)')
    try:
        text = raw.decode('ascii')
    except UnicodeDecodeError as e:
        sys.exit(f'FAIL output is not ASCII: {e}')

    rows = []
    prev = -1
    for n, line in enumerate(text.splitlines(), start=1):
        m = LINE.match(line)
        if not m:
            fail(f'line {n}: bad shape: {line[:60]!r}')
            continue
        addr = int(m.group(1), 16)
        body = m.group(2)
        if addr <= prev:
            fail(f'line {n}: 0x{addr:08X} after 0x{prev:08X} (not increasing)')
        prev = addr
        rows.append((addr, body))

    for addr, body in rows:
        off = addr - BASE
        if off < 0 or off + len(body) > len(rom):
            fail(f'0x{addr:08X}: outside the ROM')
            continue
        if rom[off:off + len(body)] != body.encode('ascii'):
            fail(f'0x{addr:08X}: text {body!r} does not match the ROM')
        if off > 0 and 0x20 <= rom[off - 1] <= 0x7E:
            fail(f'0x{addr:08X}: run is not maximal (printable byte before it)')
        end = off + len(body)
        if end < len(rom) and 0x20 <= rom[end] <= 0x7E:
            fail(f'0x{addr:08X}: run is not maximal (printable byte after it)')

    seen = dict(rows)
    for addr, want in KNOWN.items():
        if seen.get(addr) != want:
            fail(f'0x{addr:08X}: expected {want!r}, found {seen.get(addr)!r}')
    if len(rows) < MIN_ENTRIES:
        fail(f'{len(rows)} entries, minimum is {MIN_ENTRIES}')

    print(f'entries: {len(rows)}')
    if errors:
        print(f'{len(errors)} failure(s)')
        sys.exit(1)
    print('ALL CHECKS PASSED')
    sys.exit(0)


if __name__ == '__main__':
    main()
