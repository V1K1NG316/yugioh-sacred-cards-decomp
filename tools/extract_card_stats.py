"""Card property extractor for Yugioh Sacred Cards (J0005).

Reads baserom.gba, extracts DEF, ATK, W, and eight byte arrays
(B0..B7) for cards 1..900, writes private/extracted/card_stats.tsv.
Standard library only.
"""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'card_stats.tsv'

N = 901  # card 0 is a dummy; we output k = 1..900
BYTE_ARRAYS = [0x08089C04 + 901 * i for i in range(8)]
LEVEL_ADDR = 0x08089F89


def main():
    if not ROM.exists():
        print(f'ERROR: ROM not found at {ROM}')
        raise SystemExit(1)

    data = ROM.read_bytes()
    base = 0x08000000

    def u16(addr, k):
        return struct.unpack_from('<H', data, addr - base + 2 * k)[0]

    def u32(addr, k):
        return struct.unpack_from('<I', data, addr - base + 4 * k)[0]

    # Build header: card atk def w b0 b1 .. b7
    fields = ['card', 'atk', 'def', 'w_08088DF0']
    for a in BYTE_ARRAYS:
        fields.append('level' if a == LEVEL_ADDR else 'b_%08X' % a)
    header = '\t'.join(fields)

    # Build data lines
    lines = [header]
    for k in range(1, N):
        row = [
            str(k),
            str(u16(0x080886E6, k)),  # ATK
            str(u16(0x08087FDC, k)),  # DEF
            str(u32(0x08088DF0, k)),  # W
        ]
        for a in BYTE_ARRAYS:
            row.append(str(data[a - base + k]))
        lines.append('\t'.join(row))

    # Write output (raw bytes, LF endings)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(('\n'.join(line for line in lines) + '\n').encode('ascii'))
    print('wrote 900 cards')


if __name__ == '__main__':
    main()
