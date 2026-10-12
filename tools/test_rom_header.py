"""Check for the 'ROM header printer' local job (J0001).

Runs the candidate script and exits 0 only when its stdout is exactly the six expected
key=value lines. PY must be used because plain `python` is a broken Store stub.

Run from the repo root or from a job worktree (the script under test is looked up
relative to the current directory, so a worktree's own copy is the one checked).
"""
import subprocess
import sys

PY = (r"C:\Users\USER\AppData\Local\hermes\hermes-agent\.hermes-runtime"
      r"\python\cpython-3.11-windows-x86_64-none\python.exe")

EXPECTED = [
    "title=YUGIOH DM7",
    "code=AY7E",
    "maker=A4",
    "version=0",
    "entry_branch_target=0x080000C0",
    "size=16777216",
]


def main():
    r = subprocess.run([PY, "tools/rom_header.py"], capture_output=True)
    if r.returncode != 0:
        print("FAIL: tools/rom_header.py exited %d" % r.returncode)
        print("stderr:", r.stderr.decode(errors="replace"))
        return 1
    got = [ln.strip() for ln in r.stdout.decode(errors="replace").splitlines() if ln.strip()]
    if got != EXPECTED:
        print("FAIL: stdout does not match the six expected lines")
        print("expected:", EXPECTED)
        print("got     :", got)
        return 1
    print("test_rom_header: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
