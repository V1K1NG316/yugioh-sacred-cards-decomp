"""THUMB pointer-table finder for Yu-Gi-Oh! The Sacred Cards ROM.

Scans the full ROM for runs of consecutive THUMB pointer words
(addressed in the 0x08000000…0x08FFFFFF range, lowest bit set)
and writes them as a simple text table.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'ptr_tables.txt'
MIN_RUN = 4


def is_ptr(w: int) -> bool:
    """Return True when *w* is a THUMB pointer word."""
    return (w & 1) == 1 and 0x08000000 <= w < 0x09000000


def main() -> None:
    if not ROM.exists():
        print(f'ERROR: ROM not found at {ROM}')
        sys.exit(1)

    data = ROM.read_bytes()
    n_words = len(data) // 4

    # Unpack every 4-byte word at offsets 0, 4, 8, ...
    words = struct.unpack('<{}I'.format(n_words), data[:n_words * 4])

    # Find runs of consecutive pointer words
    runs = []
    i = 0
    while i < n_words:
        if is_ptr(words[i]):
            j = i
            while j < n_words and is_ptr(words[j]):
                j += 1
            run_len = j - i
            if run_len >= MIN_RUN:
                runs.append((i, run_len, words[i:j]))
            i = j
        else:
            i += 1

    # Build output lines
    lines = []
    for first_off, count, run_words in runs:
        addr = 0x08000000 + first_off * 4
        parts = ['0x{:08X}'.format(addr), str(count)]
        for w in run_words:
            parts.append('0x{:08X}'.format(w))
        lines.append(','.join(parts))

    # Write output (create private/extracted if needed)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes((''.join(line + '\n' for line in lines)).encode('ascii'))

    print('wrote {} tables'.format(len(lines)))


if __name__ == '__main__':
    main()
