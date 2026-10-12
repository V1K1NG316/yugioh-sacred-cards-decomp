"""How much of the ROM is decompiled C (milestone Y5).

Usage: PY tools/progress.py [--verbose]

A function counts as matched when src/funcs/<name>.c exists. Its byte count is the length agbcc
produced (private/build/match/<name>/size.txt: code + literal pool), which `make compare` proves
equal to the ROM's bytes at that address. The total is the ROM's code bytes, from tools/romcode.py.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import romcode  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src' / 'funcs'
MATCH = ROOT / 'private' / 'build' / 'match'


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--verbose', action='store_true', help='one line per matched function')
    a = ap.parse_args()

    rows = romcode.read_functions(ROOT)
    ranges = romcode.data_ranges(ROOT)
    total_code = sum(romcode.code_bytes(addr, ext, ranges) for _, addr, ext, _ in rows)
    by_name = {name: romcode.code_bytes(addr, ext, ranges) for name, addr, ext, _ in rows}

    matched = sorted(p.stem for p in SRC.glob('*.c'))
    got, missing = 0, []
    for n in matched:
        size = MATCH / n / 'size.txt'
        if size.exists():
            got += int(size.read_text().strip())
        else:
            missing.append(n)
            got += by_name.get(n, 0)

    pct = (100.0 * len(matched) / len(rows)) if rows else 0.0
    bpct = (100.0 * got / total_code) if total_code else 0.0
    print('%d/%d functions matched (%.2f%%)' % (len(matched), len(rows), pct))
    print('%d/%d code bytes linked from C (%.2f%%)' % (got, total_code, bpct))
    if missing:
        print('matched but not built yet (run make compare): %s' % ', '.join(missing))
    if a.verbose:
        for name, addr, _, _ in rows:
            size = MATCH / name / 'size.txt'
            if size.exists():
                print('  0x%08X  %-16s %3d bytes' % (addr, name, int(size.read_text().strip())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
