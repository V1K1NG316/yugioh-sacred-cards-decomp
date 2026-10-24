"""Pick the next functions to decompile (milestone Y5), smallest first.

Usage: python3 tools/pick_decomp_targets.py [N] [--min-code 6] [--max-code 64] [--list]

A function is a candidate when config/functions.csv has it, it is THUMB (the ARM ones need a
different agbcc and a different stub), and src/funcs/<name>.c does not exist yet. "Smallest" is
`code` from tools/romcode.py: instructions plus literal pool, not the data behind them.
--min-code skips the one-instruction stubs (`bx lr` is 2 bytes, `movs r0, #0; bx lr` is 4): they
match, but they teach nobody anything.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import romcode  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src' / 'funcs'


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('count', nargs='?', type=int, default=10)
    ap.add_argument('--min-code', type=int, default=6)
    ap.add_argument('--max-code', type=int, default=64)
    ap.add_argument('--list', action='store_true', help='print only the names')
    a = ap.parse_args()

    rows = romcode.read_functions(ROOT)
    ranges = romcode.data_ranges(ROOT)
    matched = {p.stem for p in SRC.glob('*.c')}
    out = []
    for name, addr, extent, mode in rows:
        if mode != 'thumb' or name in matched:
            continue
        code = romcode.code_bytes(addr, extent, ranges)
        if a.min_code <= code <= a.max_code:
            out.append((code, name, addr))
    out.sort()
    for code, name, addr in out[:a.count]:
        print(name if a.list else '0x%08X  %-16s code=%d' % (addr, name, code))
    print('%d candidate(s) in 6..64 code bytes, showing %d; %d functions, %d matched'
          % (len(out), min(a.count, len(out)), len(rows), len(matched)), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
