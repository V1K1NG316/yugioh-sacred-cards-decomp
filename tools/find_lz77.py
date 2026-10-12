"""LZ77 blob extractor for the Yu-Gi-Oh! The Sacred Cards ROM (GBA BIOS LZ77).

Reads private/baserom.gba, finds all valid LZ77 blobs, writes decompressed
output to private/extracted/lz77/.
"""
import os
import sys
from pathlib import Path

OFFSET_FLAG = 0x10
BASE = 0x08000000
MAX_OUT = 0x40000

def decompress(rom, off):
    """Try to decompress one LZ77 blob at file offset off.
    Returns (decompressed bytes, compressed bytes used) or None."""
    n = len(rom)
    if off + 4 > n or rom[off] != OFFSET_FLAG:
        return None
    size = rom[off + 1] | (rom[off + 2] << 8) | (rom[off + 3] << 16)
    if size < 1 or size > MAX_OUT:
        return None
    src = off + 4
    buf = bytearray()
    while len(buf) < size:
        if src >= n:
            return None
        flags = rom[src]
        src += 1
        for bit in range(7, -1, -1):
            if len(buf) >= size:
                break
            if not (flags >> bit) & 1:
                if src >= n:
                    return None
                buf.append(rom[src])
                src += 1
                continue
            if src + 2 > n:
                return None
            hi = rom[src]
            lo = rom[src + 1]
            src += 2
            length = (hi >> 4) + 3
            distance = ((hi & 0x0F) << 8) + lo + 1
            if distance > len(buf) or len(buf) + length > size:
                return None
            for _ in range(length):
                buf.append(buf[len(buf) - distance])
    return bytes(buf), src - off


def find_blobs(rom):
    """Scan rom[off] for the LZ77 flag byte and return accepted blobs."""
    found = []
    for off in range(0, len(rom) - 4):
        if rom[off] != OFFSET_FLAG:
            continue
        r = decompress(rom, off)
        if r:
            out_bytes, in_size = r
            addr = BASE + off
            found.append((off, out_bytes, in_size, addr))
    # Drop duplicates: keep leftmost, drop if start inside accepted blob.
    kept = []
    for off, out_bytes, in_size, addr in found:
        if kept and off < kept[-1][0] + kept[-1][2]:
            continue
        kept.append((off, out_bytes, in_size, addr))
    return kept


def main():
    worktree = Path(__file__).resolve().parent.parent
    rom_path = worktree / 'private' / 'baserom.gba'
    rom = rom_path.read_bytes()
    blobs = find_blobs(rom)

    out_dir = worktree / 'private' / 'extracted' / 'lz77'
    out_dir.mkdir(parents=True, exist_ok=True)
    # Start clean (spec step 4): stale .bin files from an older run must not survive.
    for old in out_dir.glob('*.bin'):
        old.unlink()

    total_out = 0
    total_in = 0

    # Write index.tsv
    lines = []
    for _off, out_bytes, in_size, addr in blobs:
        lines.append('0x%08X\t%d\t%d\n' % (addr, len(out_bytes), in_size))
        index_name = '%08X.bin' % addr
        index_path = out_dir / index_name
        index_path.write_bytes(out_bytes)
        total_out += len(out_bytes)
        total_in += in_size

    index_path = out_dir / 'index.tsv'
    index_path.write_bytes(''.join(lines).encode('ascii'))

    # Print to stdout
    print('blobs: %d' % len(blobs))
    print('out bytes: %d' % total_out)
    print('in bytes: %d' % total_in)


if __name__ == '__main__':
    main()
