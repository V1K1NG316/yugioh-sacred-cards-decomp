"""Extract the four multi-language text tables from the Yu-Gi-Oh! TSC ROM to a TSV."""

import struct
import sys
from pathlib import Path

ROM_PATH = Path(__file__).resolve().parents[1] / "private" / "baserom.gba"
OUT_PATH = Path(__file__).resolve().parents[1] / "private" / "extracted" / "text_tables.tsv"

BASE = 0x08000000
ROM_SIZE = 16777216

TABLES = [
    (0x08D30310, 140, "credits text"),
    (0x08D36130, 124, "duel messages"),
    (0x08D419E0, 12, "attribute names"),
    (0x08D4BC3C, 24, "card-type names"),
]


def main():
    rom = ROM_PATH.read_bytes()
    if len(rom) != ROM_SIZE:
        print(f"ERROR: ROM is {len(rom)} bytes, expected {ROM_SIZE}")
        sys.exit(1)

    lines = []

    for table, count, desc in TABLES:
        for k in range(count):
            off = (table - BASE) + 4 * k
            ptr = struct.unpack_from("<I", rom, off)[0]
            if ptr < BASE or ptr >= BASE + len(rom):
                print(
                    f"ERROR: table 0x{table:08X} entry {k} points outside ROM: 0x{ptr:08X}"
                )
                sys.exit(1)
            start = ptr - BASE
            end = rom.find(b"\x00", start, start + 4096)
            if end < 0:
                print(
                    f"ERROR: table 0x{table:08X} entry {k} no terminator at 0x{ptr:08X}"
                )
                sys.exit(1)
            record_hex = rom[start:end].hex()
            lines.append(
                f"0x{table:08X}\t{count}\t{k}\t0x{ptr:08X}\t{record_hex}"
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(("\n".join(lines) + "\n").encode("ascii"))

    print(f"tables: {len(TABLES)}")
    print(f"records: {sum(c for _, c, _ in TABLES)}")


if __name__ == "__main__":
    main()
