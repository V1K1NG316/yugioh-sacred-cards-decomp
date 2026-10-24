"""Extract the 900 card pictures from the ROM (Y4 part 4, job "card_images").

Each card picture is a BIOS-LZ77 blob of exactly 576 bytes: 24x24 pixels, one byte per
palette index, stored as nine 8x8-pixel tiles of 64 bytes in row-major order
(`tile = (y // 8) * 3 + (x // 8)`, byte `(y % 8) * 8 + (x % 8)`).  The colours are the
256-entry BGR555 table at 0x089C54B0.  Writes one 8-bit indexed PNG per card to
`private/extracted/cards/<n>.png` (24x24, PLTE = those 256 colours, no tRNS).

Usage: python3 tools/extract_card_images.py
Before writing it deletes the `*.png` files already in `private/extracted/cards/` — and nothing
else there, so other files and subdirectories survive. A missing `private/baserom.gba` is a
one-line error on stderr, exit 1.
Prints exactly "cards: <n>" and "bytes: <total size of the PNGs>".
Spec and independent check: tools/test_card_images.py.
"""
import argparse
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUTDIR = ROOT / 'private' / 'extracted' / 'cards'
BASE = 0x08000000
TABLE = 0x08D536F0     # 901 words, entry n = card n (1-based, no "-4" trick)
PALETTE = 0x089C54B0   # 256 BGR555 halfwords
COUNT = 900
SIDE = 24
TILE = 8
LEVEL = 9              # zlib level; 1085114 total bytes over the 900 files


def lz77(data, off):
    """BIOS LZ77: 8 flag bits per group, 1 = back reference (hi >> 4) + 3 bytes at
    distance ((hi & 15) << 8) + lo + 1."""
    if data[off] != 0x10:
        raise ValueError('no 0x10 LZ77 header at %#x' % (off + BASE))
    want = int.from_bytes(data[off + 1:off + 4], 'little')
    out = bytearray()
    pos = off + 4
    while len(out) < want:
        flags = data[pos]
        pos += 1
        for bit in range(7, -1, -1):
            if len(out) >= want:
                break
            if flags >> bit & 1:
                hi, lo = data[pos], data[pos + 1]
                pos += 2
                count = (hi >> 4) + 3
                dist = ((hi & 15) << 8) + lo + 1
                if dist > len(out):
                    raise ValueError('bad back reference at %#x' % (pos + BASE))
                for _ in range(count):
                    out.append(out[-dist])
            else:
                out.append(data[pos])
                pos += 1
    if len(out) != want:
        raise ValueError('LZ77 size mismatch at %#x' % (off + BASE))
    return bytes(out)


def palette(data):
    """The 256 BGR555 colours as RGB bytes."""
    out = bytearray()
    for i in range(256):
        v = int.from_bytes(data[PALETTE - BASE + 2 * i:PALETTE - BASE + 2 * i + 2], 'little')
        out += bytes((((v & 0x1F) * 255 // 31), ((v >> 5) & 0x1F) * 255 // 31,
                      ((v >> 10) & 0x1F) * 255 // 31))
    return bytes(out)


def scanlines(blob):
    """576 tile bytes -> the 24 scanlines of palette indices, x in 0..23."""
    if len(blob) != SIDE * SIDE:
        raise ValueError('a picture is %d bytes, not %d' % (len(blob), SIDE * SIDE))
    rows = bytearray()
    for y in range(SIDE):
        for x in range(SIDE):
            rows.append(blob[(y // TILE) * 3 * TILE * TILE + (x // TILE) * TILE * TILE
                             + (y % TILE) * TILE + (x % TILE)])
    return bytes(rows)


def chunk(name, body):
    return (struct.pack('>I', len(body)) + name + body
            + struct.pack('>I', zlib.crc32(name + body) & 0xFFFFFFFF))


def png(rows, pal, level):
    """An 8-bit palette PNG: 24x24, filter type 0 on every scanline, no tRNS."""
    raw = bytearray()
    for y in range(SIDE):
        raw.append(0)
        raw += rows[y * SIDE:(y + 1) * SIDE]
    ihdr = struct.pack('>IIBBBBB', SIDE, SIDE, 8, 3, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'PLTE', pal)
            + chunk(b'IDAT', zlib.compress(bytes(raw), level)) + chunk(b'IEND', b''))


def clear_pngs(outdir):
    """Delete the *.png files in the output folder and nothing else.

    The folder belongs to this tool, but a later run must not leave a stale picture behind
    (a removed card would keep an old PNG). Only regular `*.png` entries are unlinked: any
    other file, and any subdirectory, is left alone.
    """
    if not outdir.is_dir():
        return 0
    gone = 0
    for p in outdir.iterdir():
        if p.suffix.lower() == '.png' and not p.is_dir() and (p.is_file() or p.is_symlink()):
            p.unlink()
            gone += 1
    return gone


def main():
    ap = argparse.ArgumentParser(description='Extract the 900 card pictures as PNGs.')
    ap.add_argument('--level', type=int, default=LEVEL, help='zlib level (default: %(default)s)')
    a = ap.parse_args()

    if not ROM.is_file():
        print('extract_card_images: the ROM %s is missing (it is not tracked; copy it there)'
              % ROM, file=sys.stderr)
        return 1
    data = ROM.read_bytes()
    pal = palette(data)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    clear_pngs(OUTDIR)
    total = 0
    for card in range(1, COUNT + 1):
        ptr = int.from_bytes(data[TABLE - BASE + 4 * card:TABLE - BASE + 4 * card + 4], 'little')
        if not BASE <= ptr < BASE + len(data):
            raise SystemExit('card %d: picture pointer %#x is outside the ROM' % (card, ptr))
        blob = lz77(data, ptr - BASE)
        raw_png = png(scanlines(blob), pal, a.level)
        (OUTDIR / ('%d.png' % card)).write_bytes(raw_png)
        total += len(raw_png)
    print('cards: %d' % COUNT)
    print('bytes: %d' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
