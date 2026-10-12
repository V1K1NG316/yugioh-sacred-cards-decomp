"""Check for local job J0004 (English card-name extractor).

Runs tools/extract_card_names.py, recomputes the expected output independently and requires
private/extracted/card_names.tsv to match it byte for byte.
Card-name pointer table: 900 words at ROM 0x08D310E4 (card 1 = Blue-Eyes White Dragon). Each word points
to a record `$0<English>$1<French>$2<German>$3<Italian>$4<Spanish>$5<Japanese>` + NUL.
Usage: PY tools/test_card_names.py
"""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'card_names.tsv'
SCRIPT = ROOT / 'tools' / 'extract_card_names.py'
TABLE, COUNT = 0x08D310E4, 900


def expected(data):
    lines = []
    for k in range(COUNT):
        ptr = struct.unpack_from('<I', data, TABLE - 0x08000000 + 4 * k)[0]
        o = ptr - 0x08000000
        assert data[o:o + 2] == b'$0', hex(ptr)
        end = o + 2
        while data[end] not in (0x24, 0x00):          # '$' or NUL
            end += 1
        name = ''.join(chr(b) if 0x20 <= b <= 0x7E and b != 0x5C else '\\x%02X' % b for b in data[o + 2:end])
        lines.append('%03d\t0x%08X\t%s\n' % (k + 1, ptr, name))
    return ''.join(lines)


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/extract_card_names.py does not exist')
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(f'FAIL extract_card_names.py exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    if r.stdout.strip() != f'wrote {COUNT} cards' or len(r.stdout.strip().splitlines()) != 1:
        sys.exit(f'FAIL stdout must be exactly "wrote {COUNT} cards", got {r.stdout!r}')
    if not OUT.exists():
        sys.exit('FAIL private/extracted/card_names.tsv was not written')
    want = expected(ROM.read_bytes()).encode('ascii')
    got = OUT.read_bytes()
    if got != want:
        g, w = got.decode('ascii', 'replace').split('\n'), want.decode('ascii').split('\n')
        for k, (a, b) in enumerate(zip(g, w)):
            if a != b:
                sys.exit(f'FAIL line {k + 1} differs\n  got : {a!r}\n  want: {b!r}')
        sys.exit(f'FAIL length differs: got {len(g)} lines / {len(got)} bytes, want {len(w)} lines / {len(want)} bytes')
    print(f'cards: {COUNT}  bytes: {len(got)}')
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
