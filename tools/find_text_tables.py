#!/usr/bin/env python3
"""Whole-ROM text-table finder.

Walks the entire Yu-Gi-Oh! The Sacred Cards ROM, finds every 4-aligned pointer
table entry that targets a multi-language text record (starting with "$0"),
groups them into runs, and writes a TSV of the results.

Output: private/extracted/text_table_map.tsv
Stdout: tables: N
"""

import struct
from pathlib import Path

ROM_PATH = Path(__file__).resolve().parents[1] / "private" / "baserom.gba"
OUT_PATH = Path(__file__).resolve().parents[1] / "private" / "extracted" / "text_table_map.tsv"
BASE = 0x08000000
MIN_RUN = 4
MAX_GAP = 8


def find_tables():
    rom = ROM_PATH.read_bytes()
    n = len(rom)

    # 1. Walk every 4-aligned offset, collect hits
    sites = []
    for off in range(0, n - 3, 4):
        v = int.from_bytes(rom[off:off + 4], "little")
        if v >= BASE and v + 2 <= BASE + n and rom[v - BASE] == 0x24 and rom[v - BASE + 1] == 0x30:
            sites.append((off, v))

    # 2. Group into runs
    if not sites:
        return []

    runs = [[sites[0]]]
    for off, v in sites[1:]:
        prev = runs[-1][-1]
        if off - prev[0] <= MAX_GAP:
            runs[-1].append((off, v))
        else:
            runs.append([(off, v)])

    # 3. Filter runs < 4 hits
    return [r for r in runs if len(r) >= MIN_RUN]


def write_tsv(runs):
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for run in runs:
        first_off, first_target = run[0]
        last_off, _ = run[-1]
        count = len(run)
        lines.append("0x%08X\t0x%08X\t%d\t0x%08X\n" % (BASE + first_off, BASE + last_off, count, first_target))
    OUT_PATH.write_bytes("".join(lines).encode("ascii"))


def main():
    runs = find_tables()
    write_tsv(runs)
    print("tables: %d" % len(runs))


if __name__ == "__main__":
    main()
