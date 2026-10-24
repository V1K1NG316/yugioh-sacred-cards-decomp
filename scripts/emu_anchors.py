"""Emulator-derived anchors for the card pictures (Y4 part 4).

Recomputes, from the ROM alone, the two things the mGBA run measured, and prints their
SHA-256 so the values can be compared with the emulator dumps in private/tmp:

  art      = BIOS-LZ77 blob of card n -> 576 bytes (24x24, 8-bit-per-pixel, 8x8 tiles,
             row-major 3x3 grid) = the bytes the game leaves at 0x02018800
             (dumps: private/tmp/emu_pic_1.bin, emu_pic_2.bin)
  composed = 32x32, 8bpp, 8x8 tiles, row-major (4 tiles per row, 64 B each) = the frame
             asset (table 0x08D536C8, frame id = byte table 0x0808A693 card n) with the art
             pasted into a 24x24 window at (4,2).  The game writes it into its tile buffer at
             dest byte = i + 768*(i // 256), so reading the buffer at those offsets in image
             order gives the image (dumps: private/tmp/emu_scratch2.bin, cards 1 and 2).

Usage: python3 scripts/emu_anchors.py            (prints the hashes; compares with the dumps
                                             under private/tmp when they are present)
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
TMP = ROOT / 'private' / 'tmp'
BASE = 0x08000000
PIC_TABLE = 0x08D536F0      # 901 words, entry n = card n (1-based)
FRAME_TABLE = 0x08D536C8    # 10 words, 0x400 bytes of frame each
FRAME_ID_TABLE = 0x0808A693  # byte per card, entry n = card n
WINDOW_X, WINDOW_Y = 4, 2
ANCHORS = {                 # measured on 2026-10-12 with mGBA 0.10.5 + its gdb stub
    1: ('380f8482996d9d4492440690d8b18a7b23a3f967f29b05704dd03f90dec07160',
        'a3079443a6fd1e7363c34b92cdfc656f1c7a845d9cbc5e94ab8802085ef8492d', 0),
    2: ('254f9f94c91b5b71e78bdb3203e29f355bb460068925e1e7f9b8cb434aa681ba',
        '78351907545cd6a4063e7247c6cd442399c356285d84d240afbd8d02c142b060', 1),
}


def lz77(data, off):
    if data[off] != 0x10:
        raise ValueError('no LZ77 header at %#x' % (off + BASE))
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
                for _ in range(count):
                    out.append(out[-dist])
            else:
                out.append(data[pos])
                pos += 1
    return bytes(out)


def image_byte(x, y):
    """byte of pixel (x, y) in a 32x32 8bpp image stored as 8x8 tiles, row-major"""
    return (y // 8) * 256 + (x // 8) * 64 + (y % 8) * 8 + (x % 8)


def art(card, data):
    ptr = int.from_bytes(data[PIC_TABLE - BASE + 4 * card:PIC_TABLE - BASE + 4 * card + 4], 'little')
    return lz77(data, ptr - BASE)


def composed(card, data):
    frame_id = data[FRAME_ID_TABLE - BASE + card]
    fptr = int.from_bytes(data[FRAME_TABLE - BASE + 4 * frame_id:FRAME_TABLE - BASE + 4 * frame_id + 4],
                          'little')
    img = bytearray(data[fptr - BASE:fptr - BASE + 1024])
    blob = art(card, data)
    for y in range(24):
        for x in range(24):
            img[image_byte(x + WINDOW_X, y + WINDOW_Y)] = blob[(y // 8) * 192 + (x // 8) * 64
                                                               + (y % 8) * 8 + (x % 8)]
    return bytes(img), frame_id


def main():
    data = ROM.read_bytes()
    ok = True
    for card, (want_img, want_art, want_fid) in sorted(ANCHORS.items()):
        img, fid = composed(card, data)
        blob = art(card, data)
        got_img, got_art = hashlib.sha256(img).hexdigest(), hashlib.sha256(blob).hexdigest()
        print('card %d: frame id %d (anchor %d)' % (card, fid, want_fid))
        print('  composed %s  %s' % (got_img, 'OK' if got_img == want_img else 'MISMATCH'))
        print('  art      %s  %s' % (got_art, 'OK' if got_art == want_art else 'MISMATCH'))
        ok &= got_img == want_img and got_art == want_art and fid == want_fid
        dump_art = TMP / ('emu_pic_%d.bin' % card)
        if dump_art.exists():
            print('  emulator picture dump matches: %s' % (dump_art.read_bytes() == blob))
        scratch = TMP / 'emu_scratch2.bin'
        if scratch.exists():
            buf = scratch.read_bytes()[(card - 1) * 0x1000:card * 0x1000]
            emu_img = bytes(buf[i + 768 * (i // 256)] for i in range(1024))
            print('  emulator tile-buffer image matches: %s' % (emu_img == img))
    print('ANCHORS OK' if ok else 'ANCHORS MISMATCH')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
