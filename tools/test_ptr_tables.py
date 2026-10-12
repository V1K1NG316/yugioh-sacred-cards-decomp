"""Check for local job J0003 (THUMB pointer-table finder).

Runs tools/find_ptr_tables.py, then recomputes the expected output independently and requires
private/extracted/ptr_tables.txt to match it byte for byte (so nothing can be missing or extra).
Run from the repo root or a job worktree: paths come from this file's location.
Usage: PY tools/test_ptr_tables.py
"""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'ptr_tables.txt'
SCRIPT = ROOT / 'tools' / 'find_ptr_tables.py'
MIN_RUN = 4


def is_ptr(v):
    return v & 1 == 1 and 0x08000000 <= v < 0x09000000


def expected(data):
    n = len(data) // 4
    words = struct.unpack('<%dI' % n, data[:n * 4])
    lines, i = [], 0
    while i < n:
        if not is_ptr(words[i]):
            i += 1
            continue
        j = i
        while j < n and is_ptr(words[j]):
            j += 1
        if j - i >= MIN_RUN:
            lines.append('0x%08X,%d,' % (0x08000000 + 4 * i, j - i) +
                         ','.join('0x%08X' % w for w in words[i:j]))
        i = j
    return ''.join(line + '\n' for line in lines), len(lines)


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/find_ptr_tables.py does not exist')
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(f'FAIL find_ptr_tables.py exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    want_text, count = expected(ROM.read_bytes())
    want_stdout = f'wrote {count} tables'
    if r.stdout.strip() != want_stdout or len(r.stdout.strip().splitlines()) != 1:
        sys.exit(f'FAIL stdout must be exactly {want_stdout!r}, got {r.stdout!r}')
    if not OUT.exists():
        sys.exit('FAIL private/extracted/ptr_tables.txt was not written')
    got = OUT.read_bytes()
    want = want_text.encode('ascii')
    if got != want:
        got_lines, want_lines = got.decode('ascii', 'replace').split('\n'), want_text.split('\n')
        for k, (g, w) in enumerate(zip(got_lines, want_lines)):
            if g != w:
                sys.exit(f'FAIL line {k + 1} differs\n  got : {g[:160]!r}\n  want: {w[:160]!r}')
        sys.exit(f'FAIL length differs: got {len(got)} bytes / {len(got_lines)} lines, '
                 f'want {len(want)} bytes / {len(want_lines)} lines')
    if count < 10:
        sys.exit(f'FAIL only {count} tables: the scan is probably wrong')
    print(f'tables: {count}  bytes: {len(got)}')
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
