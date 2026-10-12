"""Side-by-side diff of one function's C against the ROM's own bytes (Y5).

Usage (Git Bash, from the repo root or from a job worktree):
  PY tools/diff_func.py sub_08004750      # or: tools/diff_func.sh sub_08004750

Compiles src/funcs/<name>.c with agbcc, links it at the function's ROM address, and shows the
result next to the ROM's own instructions with asm-differ (private/tools/asm-differ/diff.py, set
up by scripts/decomp_tools.sh). The left column is the ROM -- the truth -- and the right one is
our C; a line marked with `|` (or `<--`) is a real difference.

It takes the same inputs as tools/match_func.py, a job worktree's src/funcs included, so what it
shows is what the check measures. The exit code is asm-differ's: 0 when a diff was produced.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from match_func import CSV, MAIN, WSL_DISTRO, WSL_MAIN, load_functions, wsl_path  # noqa: E402

BUILD = ('private', 'build', 'match')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('name', help='function name, e.g. sub_08004750 (also the .c file name)')
    ap.add_argument('--main', default=str(MAIN), help='main checkout (default: %(default)s)')
    ap.add_argument('--keep', action='store_true',
                    help='keep the build directory and print its path')
    a = ap.parse_args()

    main_dir = Path(a.main)
    root = Path(__file__).resolve().parents[1]
    name = a.name

    funcs = load_functions(main_dir / CSV)
    if name not in funcs:
        sys.exit('diff_func: %s is not in %s' % (name, CSV))
    row = funcs[name]
    if row['mode'] != 'thumb':
        sys.exit('diff_func: %s is %s code; only THUMB C functions are supported' % (name, row['mode']))
    src = root / 'src' / 'funcs' / (name + '.c')
    if not src.exists():
        sys.exit('diff_func: no such file: %s' % src)

    build_root = main_dir.joinpath(*BUILD).resolve()
    work = build_root / ('%s.diff.%d' % (name, os.getpid()))
    try:
        cmd = ['wsl', '-d', WSL_DISTRO, '--cd', WSL_MAIN, '--', 'bash', 'scripts/diff_func.sh',
               name, '0x%08X' % row['addr'], wsl_path(src.parent), wsl_path(work)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout:
            print(r.stdout, end='')
        if r.stderr:
            print(r.stderr, end='')
        if a.keep:
            print('diff_func: build dir %s (kept), objects: %s/%s.o and %s/ref/%s.o'
                  % (work, work, name, work, name))
        return r.returncode
    finally:
        if not a.keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
