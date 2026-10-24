"""Check for the local job "whole-ROM text-table finder" (tools/find_text_tables.py).

Runs tools/find_text_tables.py in this checkout and recomputes the expected map of pointer
tables independently, then compares byte for byte.

Spec the job must implement (ROM = private/baserom.gba, addresses = file offset + 0x08000000):
  * a word site is any 4-aligned file offset whose little-endian u32 is a ROM address v with
    v + 2 <= end of ROM and the two bytes at v are "$0" (0x24 0x30) - the marker every
    multi-language text record of this game starts with;
  * sites are walked in increasing address order and grouped into runs: a site continues the
    current run when it is at most 8 bytes after the previous site in that run (i.e. one
    non-matching word is allowed inside a run - the duel-message table needs it). A run with
    fewer than 4 sites is discarded;
  * output: private/extracted/text_table_map.tsv, one line per kept run in address order:
    "<first site 0x%08X>\t<last site 0x%08X>\t<sites in the run>\t<first site's target 0x%08X>";
  * stdout exactly one line: "tables: N" (N = kept runs).

Usage: python3 tools/test_find_text_tables.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'find_text_tables.py'
OUT = ROOT / 'private' / 'extracted' / 'text_table_map.tsv'
BASE = 0x08000000
MIN_RUN = 4
MAX_GAP = 8


def expected(d):
    """Independent scan: returns the whole TSV text."""
    n = len(d)
    sites = []
    for off in range(0, n - 3, 4):
        v = d[off] | (d[off + 1] << 8) | (d[off + 2] << 16) | (d[off + 3] << 24)
        if v < BASE or v + 2 > BASE + n:
            continue
        if d[v - BASE] == 0x24 and d[v - BASE + 1] == 0x30:
            sites.append((off, v))
    runs = []
    for off, v in sites:
        if runs and off - runs[-1][-1][0] <= MAX_GAP:
            runs[-1].append((off, v))
        else:
            runs.append([(off, v)])
    lines = []
    kept = 0
    for run in runs:
        if len(run) < MIN_RUN:
            continue
        kept += 1
        lines.append('0x%08X\t0x%08X\t%d\t0x%08X\n'
                     % (BASE + run[0][0], BASE + run[-1][0], len(run), run[0][1]))
    return ''.join(lines), kept


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/find_text_tables.py does not exist')
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(f'FAIL find_text_tables.py exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    want, kept = expected(ROM.read_bytes())
    want_stdout = 'tables: %d' % kept
    if r.stdout.strip() != want_stdout:
        sys.exit(f'FAIL stdout differs\n  got : {r.stdout.strip()!r}\n  want: {want_stdout!r}')
    if not OUT.exists():
        sys.exit('FAIL private/extracted/text_table_map.tsv was not written')
    got = OUT.read_bytes()
    if got != want.encode('ascii'):
        g, w = got.decode('ascii', 'replace').split('\n'), want.split('\n')
        for k, (a, b) in enumerate(zip(g, w)):
            if a != b:
                sys.exit(f'FAIL line {k + 1} differs\n  got : {a!r}\n  want: {b!r}')
        sys.exit(f'FAIL length differs: got {len(g)} lines / {len(got)} bytes, want {len(w)} lines / {len(want)} bytes')
    print(want_stdout)
    print('bytes: %d' % len(got))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
