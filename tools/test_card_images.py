"""Check for the local job "card-picture extractor" (tools/extract_card_images.py).

Runs the tool in this checkout, then decodes all 900 pictures here, independently, and
compares the *pixel values* (palette indices) of every PNG the tool wrote with its own
decode, plus each PNG's size and palette. PNG bytes are never compared.

Spec the job must implement (ROM = private/baserom.gba, file offset + 0x08000000 = ROM address):
  * Card numbers are 1..900. The picture pointer table at 0x08D536F0 holds **901** little-endian
    u32; **entry n is card n** (so entry 1 = card 1 = Blue-Eyes White Dragon) and entry 0 is an
    unused dummy (it points at an all-zero picture). That is exactly how the game's own loader
    reads it: sub_08034AF8 / sub_080351A4 (literals at 0x08034B30 / 0x080351DC) do
    `ldr r0, =0x08D536F0; lsls r4, cardId, #2; adds r4, r4, r0; ldr r0, [r4]` with the 1-based
    card id, i.e. no "-4" trick (unlike the name reader sub_080073E4). Watch out: word 900 is in
    the table and word 901 is not.
  * Each entry is a BIOS-LZ77 blob (first byte 0x10, then a 24-bit little-endian output
    size). Decompressing it must give exactly 576 bytes.
  * Those 576 bytes are 8-bit-per-pixel palette indices, stored as 8x8-pixel tiles of
    64 bytes each (one byte per pixel, rows of 8), nine tiles in row-major order:
    tile t = index (row*3 + col) covers pixels x = col*8..col*8+7, y = row*8..row*8+7.
    The picture is therefore 24x24 pixels.
  * The palette is the 256-entry BGR555 table at 0x089C54B0 (512 bytes, little-endian u16).
    Convert a halfword v to 8-bit RGB with, exactly:
        r = (v & 0x1F) * 255 // 31, g = ((v >> 5) & 0x1F) * 255 // 31, b = ((v >> 10) & 0x1F) * 255 // 31
  * Writes one file per card, private/extracted/cards/<n>.png, an 8-bit palette PNG (colour
    type 3): width 24, height 24, bit depth 8, compression 0, filter 0, interlace 0, a PLTE
    chunk with all 256 colours in the order above, no tRNS, and (recommended) filter type 0
    on every scanline. Only these 900 files may be in private/extracted/cards/.
  * stdout: exactly "cards: 900" and "bytes: <total size of the 900 PNG files in bytes>".
No other output on stdout. The tool must exit 0.

Ground truth (measured in mGBA 0.10.5, REPORT [036]; see scripts/emu_*.py):
  the game composes a 32x32 8bpp card image, 8x8 tiles of 64 bytes, row-major (4 tiles per
  row), as frame asset (table 0x08D536C8, index = byte table 0x0808A693 card n, 0x400 bytes)
  with the 576-byte art pasted into a 24x24 window at (4,2).  The anchors below are the
  SHA-256 of that image and of the art for cards 1 and 2, taken from the emulator's own
  tile buffer / picture buffer; the check recomputes both from the ROM and must reproduce
  them, so the pixel rule here is pinned to the running game, not to itself.

Usage: PY tools/test_card_images.py
"""
import hashlib
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'extract_card_images.py'
OUTDIR = ROOT / 'private' / 'extracted' / 'cards'
BASE = 0x08000000
TABLE = 0x08D536F0
PALETTE = 0x089C54B0
COUNT = 900
PIXELS = 576          # 24 * 24 * 1 byte, one byte per pixel
TILE = 8
SIDE = 24
FRAME_TABLE = 0x08D536C8        # ten 0x400-byte frame assets
FRAME_ID_TABLE = 0x0808A693     # byte per card: frame index, entry n = card n
WINDOW_X, WINDOW_Y = 4, 2       # where the 24x24 art sits in the 32x32 composed image
# SHA-256 (composed 32x32 card image, 576-byte art, frame id) read out of the running game
ANCHORS = {
    1: ('380f8482996d9d4492440690d8b18a7b23a3f967f29b05704dd03f90dec07160',
        'a3079443a6fd1e7363c34b92cdfc656f1c7a845d9cbc5e94ab8802085ef8492d', 0),
    2: ('254f9f94c91b5b71e78bdb3203e29f355bb460068925e1e7f9b8cb434aa681ba',
        '78351907545cd6a4063e7247c6cd442399c356285d84d240afbd8d02c142b060', 1),
}


def lz77(data, off):
    """BIOS LZ77: 8 flag bits per group, 1 = back reference (hi>>4)+3 bytes at
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
                if dist > len(out) or len(out) + count > want:
                    raise ValueError('bad back reference at %#x' % (pos + BASE))
                for _ in range(count):
                    out.append(out[-dist])
            else:
                out.append(data[pos])
                pos += 1
    if len(out) != want:
        raise ValueError('LZ77 size mismatch at %#x' % (off + BASE))
    return bytes(out)


def expected_pixels(blob):
    """Tile order spelled out per pixel: pixel (x, y) lives in blob tile
    (y // 8) * 3 + (x // 8), byte (y % 8) * 8 + (x % 8)."""
    if len(blob) != PIXELS:
        raise SystemExit('FAIL a picture blob is %d bytes, not %d' % (len(blob), PIXELS))
    rows = []
    for y in range(SIDE):
        row = []
        for x in range(SIDE):
            tile = (y // TILE) * 3 + (x // TILE)
            row.append(blob[tile * 64 + (y % TILE) * 8 + (x % TILE)])
        rows.append(row)
    return rows


def composed_card(data, card):
    """The 32x32 image the game builds: frame asset + the 24x24 art at (4,2)."""
    frame_id = data[FRAME_ID_TABLE - BASE + card]
    fptr = int.from_bytes(data[FRAME_TABLE - BASE + 4 * frame_id:
                                FRAME_TABLE - BASE + 4 * frame_id + 4], 'little')
    img = bytearray(data[fptr - BASE:fptr - BASE + 1024])
    ptr = int.from_bytes(data[TABLE - BASE + 4 * card:TABLE - BASE + 4 * card + 4], 'little')
    blob = lz77(data, ptr - BASE)
    for y in range(SIDE):
        for x in range(SIDE):
            img[(y + WINDOW_Y) // 8 * 256 + (x + WINDOW_X) // 8 * 64
                + (y + WINDOW_Y) % 8 * 8 + (x + WINDOW_X) % 8] = \
                blob[(y // 8) * 3 * 64 + (x // 8) * 64 + (y % 8) * 8 + (x % 8)]
    return bytes(img), blob, frame_id


def anchor_check(data):
    """Reproduce the emulator's own numbers from the ROM; the pixels rule is pinned to them."""
    for card, (want_img, want_art, want_id) in sorted(ANCHORS.items()):
        img, blob, frame_id = composed_card(data, card)
        if frame_id != want_id:
            sys.exit('FAIL card %d: frame id %d, the emulator used %d' % (card, frame_id, want_id))
        if hashlib.sha256(blob).hexdigest() != want_art:
            sys.exit('FAIL card %d: the art dumped from the emulator (0x02018800) hashes %s, '
                     'this decode hashes %s' % (card, want_art, hashlib.sha256(blob).hexdigest()))
        if hashlib.sha256(img).hexdigest() != want_img:
            sys.exit('FAIL card %d: the 32x32 image in the emulator\'s tile buffer hashes %s, '
                     'this composition hashes %s' % (card, want_img, hashlib.sha256(img).hexdigest()))
    print('anchors: %d cards match the emulator dump' % len(ANCHORS))


def expected_palette(data):
    out = bytearray()
    for i in range(256):
        v = int.from_bytes(data[PALETTE - BASE + 2 * i:PALETTE - BASE + 2 * i + 2], 'little')
        out += bytes((((v & 0x1F) * 255 // 31), ((v >> 5) & 0x1F) * 255 // 31,
                      ((v >> 10) & 0x1F) * 255 // 31))
    return bytes(out)


def read_png(path):
    """Minimal PNG reader: returns (width, height, depth, colour, palette, pixels)."""
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit('FAIL %s is not a PNG' % path.name)
    pos, chunks, idat = 8, {}, bytearray()
    while pos < len(raw):
        ln = int.from_bytes(raw[pos:pos + 4], 'big')
        name = raw[pos + 4:pos + 8]
        body = raw[pos + 8:pos + 8 + ln]
        if zlib.crc32(name + body) & 0xFFFFFFFF != int.from_bytes(raw[pos + 8 + ln:pos + 12 + ln], 'big'):
            raise SystemExit('FAIL %s has a bad %s CRC' % (path.name, name.decode('latin1')))
        if name == b'IDAT':
            idat += body
        else:
            chunks[name] = body
        pos += 12 + ln
    w, h, depth, colour, comp, filt, inter = struct.unpack('>IIBBBBB', chunks[b'IHDR'])
    if (depth, colour, comp, filt, inter) != (8, 3, 0, 0, 0):
        raise SystemExit('FAIL %s: depth/colour/etc %s' % (path.name, (depth, colour, comp, filt, inter)))
    packed = zlib.decompress(bytes(idat))
    if len(packed) != h * (w + 1):
        raise SystemExit('FAIL %s: %d raw bytes, expected %d' % (path.name, len(packed), h * (w + 1)))
    rows, prev = [], bytearray(w)
    for y in range(h):
        ftype = packed[y * (w + 1)]
        line = bytearray(packed[y * (w + 1) + 1:(y + 1) * (w + 1)])
        for i in range(w):
            a = line[i - 1] if i else 0
            b = prev[i]
            c = prev[i - 1] if i else 0
            if ftype == 1:
                line[i] = (line[i] + a) & 0xFF
            elif ftype == 2:
                line[i] = (line[i] + b) & 0xFF
            elif ftype == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif ftype == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
            elif ftype != 0:
                raise SystemExit('FAIL %s: filter type %d on row %d' % (path.name, ftype, y))
        rows.append(list(line))
        prev = line
    return w, h, chunks.get(b'PLTE'), rows


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/extract_card_images.py does not exist')
    if not ROM.exists():
        sys.exit('FAIL no ROM at %s' % ROM)
    if OUTDIR.exists():
        for old in OUTDIR.iterdir():
            old.unlink()
    run = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if run.returncode != 0:
        sys.exit('FAIL extract_card_images.py exited %d\n%s\n%s' % (run.returncode, run.stdout[-2000:], run.stderr[-2000:]))
    data = ROM.read_bytes()
    anchor_check(data)
    pal = expected_palette(data)
    files = sorted(OUTDIR.glob('*.png'))
    names = set(f.name for f in files)
    want_names = set('%d.png' % n for n in range(1, COUNT + 1))
    if names != want_names or len(files) != COUNT:
        extra = sorted(names - want_names)
        missing = sorted(want_names - names)
        sys.exit('FAIL the folder must hold exactly 1.png..900.png; %d files, extra=%s missing=%s'
                 % (len(files), extra[:5], missing[:5]))
    total = sum(f.stat().st_size for f in files)
    if run.stdout.strip() != 'cards: %d\nbytes: %d' % (COUNT, total):
        sys.exit('FAIL stdout must be "cards: %d" / "bytes: %d", got %r' % (COUNT, total, run.stdout))
    for n in range(1, COUNT + 1):
        ptr = int.from_bytes(data[TABLE - BASE + 4 * n:TABLE - BASE + 4 * n + 4], 'little')
        want = expected_pixels(lz77(data, ptr - BASE))
        w, h, plte, got = read_png(OUTDIR / ('%d.png' % n))
        if (w, h) != (SIDE, SIDE):
            sys.exit('FAIL card %d: %dx%d, expected %dx%d' % (n, w, h, SIDE, SIDE))
        if plte != pal:
            sys.exit('FAIL card %d: PLTE is not the 256 colours of 0x089C54B0 (first difference at byte %s)'
                     % (n, next((i for i in range(768) if plte[i:i + 1] != pal[i:i + 1]), 'length')))
        if got != want:
            for y in range(h):
                if got[y] != want[y]:
                    x = next(i for i in range(w) if got[y][i] != want[y][i])
                    sys.exit('FAIL card %d: pixel (%d,%d) is %d, expected %d' % (n, x, y, got[y][x], want[y][x]))
    print('cards: %d' % COUNT)
    print('bytes: %d' % total)
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
