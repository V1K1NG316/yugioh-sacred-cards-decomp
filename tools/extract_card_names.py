#!/usr/bin/env python3
"""English card-name extractor for Yugioh Sacred Cards ROM.

Reads 900 card-name pointers from ROM address 0x08D310E4,
extracts English names, and writes private/extracted/card_names.tsv.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'card_names.tsv'
TABLE_OFFSET = 0xD310E4  # file offset of pointer table (0x08D310E4 - 0x08000000)
COUNT = 900


def decode_name(raw):
    """Decode name bytes to text per the spec.
    
    Byte 0x20 to 0x7E (except backslash 0x5C) becomes that ASCII character.
    Every other byte and the backslash becomes \\x + 2 uppercase hex digits.
    """
    parts = []
    for b in raw:
        if b == 0x5C:
            parts.append('\\x%02X' % b)
        elif 0x20 <= b <= 0x7E:
            parts.append(chr(b))
        else:
            parts.append('\\x%02X' % b)
    return ''.join(parts)


def main():
    if not ROM.exists():
        print(f'ERROR: ROM file not found at {ROM}')
        sys.exit(1)

    data = ROM.read_bytes()

    lines = []
    for k in range(COUNT):
        # Read pointer (little-endian 4-byte) at offset TABLE_OFFSET + 4*k
        ptr = struct.unpack_from('<I', data, TABLE_OFFSET + 4 * k)[0]
        # Convert ROM address to file offset
        o = ptr - 0x08000000

        # The name starts after the $0 (two bytes at offset o)
        end = o + 2
        while data[end] not in (0x24, 0x00):
            end += 1

        # Extract English name bytes
        name_bytes = data[o + 2:end]
        name = decode_name(name_bytes)

        # Format: NNN<TAB>0xPPPPPPPP<TAB>name
        card_num = k + 1
        line = '%03d\t0x%08X\t%s\n' % (card_num, ptr, name)
        lines.append(line)

    # Create output directory if needed
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # Write output as bytes
    OUT.write_bytes(''.join(lines).encode('ascii'))

    print(f'wrote {COUNT} cards')


if __name__ == '__main__':
    main()
