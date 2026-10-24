"""Check for local job J0005 (card property extractor).

Runs tools/extract_card_stats.py, recomputes the expected TSV independently and requires
private/extracted/card_stats.tsv to match it byte for byte.
Card property block (indexed by card number 0..900; card 0 is a dummy), see docs/game-data.md:
  u16 DEF @0x08087FDC, u16 ATK @0x080886E6, u32 @0x08088DF0, then eight u8 arrays every 901 bytes
  from 0x08089C04 (the one at 0x08089F89 is the level).
Usage: python3 tools/test_card_stats.py
"""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'card_stats.tsv'
SCRIPT = ROOT / 'tools' / 'extract_card_stats.py'
N = 901
BYTE_ARRAYS = [0x08089C04 + 901 * i for i in range(8)]


def expected(data):
    def u16(base, k): return struct.unpack_from('<H', data, base - 0x08000000 + 2 * k)[0]
    def u32(base, k): return struct.unpack_from('<I', data, base - 0x08000000 + 4 * k)[0]
    names = ['b_%08X' % a if a != 0x08089F89 else 'level' for a in BYTE_ARRAYS]
    lines = ['\t'.join(['card', 'atk', 'def', 'w_08088DF0'] + names)]
    for k in range(1, N):
        row = [str(k), str(u16(0x080886E6, k)), str(u16(0x08087FDC, k)), str(u32(0x08088DF0, k))]
        row += [str(data[a - 0x08000000 + k]) for a in BYTE_ARRAYS]
        lines.append('\t'.join(row))
    return ''.join(line + '\n' for line in lines)


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/extract_card_stats.py does not exist')
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(f'FAIL extract_card_stats.py exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    if r.stdout.strip() != 'wrote 900 cards' or len(r.stdout.strip().splitlines()) != 1:
        sys.exit(f'FAIL stdout must be exactly "wrote 900 cards", got {r.stdout!r}')
    if not OUT.exists():
        sys.exit('FAIL private/extracted/card_stats.tsv was not written')
    want = expected(ROM.read_bytes()).encode('ascii')
    got = OUT.read_bytes()
    if got != want:
        g, w = got.decode('ascii', 'replace').split('\n'), want.decode('ascii').split('\n')
        for k, (a, b) in enumerate(zip(g, w)):
            if a != b:
                sys.exit(f'FAIL line {k + 1} differs\n  got : {a!r}\n  want: {b!r}')
        sys.exit(f'FAIL length differs: got {len(g)} lines / {len(got)} bytes, want {len(w)} lines / {len(want)} bytes')
    print(f'cards: 900  bytes: {len(got)}')
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
