#!/usr/bin/env python3
"""Extract maximal runs of printable ASCII from the ROM."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
BASE = 0x08000000
MIN_LEN = 6
OUT_DIR = ROOT / 'private' / 'extracted'
OUT_FILE = OUT_DIR / 'strings.txt'

PR_BEGIN = 0x20
PR_END = 0x7E


def main():
    if not ROM.exists():
        print(f'error: ROM not found at {ROM}')
        sys.exit(1)

    rom = ROM.read_bytes()
    n = len(rom)

    runs = []
    i = 0
    while i < n:
        if PR_BEGIN <= rom[i] <= PR_END:
            j = i + 1
            while j < n and PR_BEGIN <= rom[j] <= PR_END:
                j += 1
            length = j - i
            if length >= MIN_LEN:
                runs.append((i, rom[i:j]))
            i = j
        else:
            i += 1

    if not OUT_DIR.exists():
        OUT_DIR.mkdir(parents=True)

    lines = bytearray()
    for offset, data in runs:
        addr = BASE + offset
        text = data.decode('ascii')
        line = f'0x{addr:08X}\t{text}\n'
        lines.extend(line.encode('ascii'))

    OUT_FILE.write_bytes(lines)

    count = len(runs)
    print(f'wrote {count} strings')


if __name__ == '__main__':
    main()
