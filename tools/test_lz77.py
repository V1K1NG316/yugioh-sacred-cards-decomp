"""Check for the local job "LZ77 blob extractor" (tools/find_lz77.py).

Runs tools/find_lz77.py in this checkout, then recomputes the whole expected output
independently (this file's own copy of the BIOS LZ77 reader, not the job's) and requires
byte-for-byte agreement: the index file, every decompressed blob, and the script's stdout.

Spec the job must implement (ROM = private/baserom.gba, addresses = file offset + 0x08000000):
  * a blob header is byte 0x10 followed by a 24-bit little-endian output size (1..0x40000);
  * the stream at header+4 must decompress to exactly that many bytes; a read past the end of
    the ROM, a back-reference farther back than the bytes already produced, or a final copy that
    would overshoot the declared size all mean "not a blob";
  * candidates are kept left to right and one that starts inside an accepted blob's compressed
    range is dropped;
  * output: private/extracted/lz77/index.tsv, one line "0x<address>\t<out size>\t<in size>" per
    blob in address order; one private/extracted/lz77/<ADDRESS>.bin per blob (8 uppercase hex
    digits of the ROM address) holding the decompressed bytes; stdout exactly
    "blobs: N" / "out bytes: N" / "in bytes: N".

Usage: PY tools/test_lz77.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'find_lz77.py'
OUT = ROOT / 'private' / 'extracted' / 'lz77'
BASE = 0x08000000
MAX_OUT = 0x40000


def decompress(d, off):
    """Independent BIOS LZ77 reader. Returns (bytes, compressed length) or None."""
    n = len(d)
    if off + 4 > n or d[off] != 0x10:
        return None
    size = d[off + 1] | (d[off + 2] << 8) | (d[off + 3] << 16)
    if size < 1 or size > MAX_OUT:
        return None
    src = off + 4
    buf = bytearray()
    while len(buf) < size:
        if src >= n:
            return None
        flags = d[src]
        src += 1
        for bit in range(7, -1, -1):
            if len(buf) >= size:
                break
            if not (flags >> bit) & 1:
                if src >= n:
                    return None
                buf.append(d[src])
                src += 1
                continue
            if src + 2 > n:
                return None
            pair = (d[src] << 8) | d[src + 1]
            src += 2
            length = (pair >> 12) + 3
            back = (pair & 0x0FFF) + 1
            if back > len(buf) or len(buf) + length > size:
                return None
            for _ in range(length):
                buf.append(buf[len(buf) - back])
    return bytes(buf), src - off


def expected(d):
    """The blobs the job must find: [(rom address, out bytes, in size), ...]."""
    found = []
    for off in range(0, len(d) - 4):
        if d[off] != 0x10:
            continue
        r = decompress(d, off)
        if r:
            found.append((off, r[0], r[1]))
    kept = []
    for off, out, used in found:
        if kept and off < kept[-1][0] + kept[-1][2]:
            continue
        kept.append((off, out, used))
    return kept


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/find_lz77.py does not exist')
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    if OUT.exists():
        for f in sorted(OUT.iterdir()):
            if f.is_file():
                f.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(f'FAIL find_lz77.py exited {r.returncode}\n{r.stdout}\n{r.stderr}')
    kept = expected(ROM.read_bytes())
    want_index = ''.join('0x%08X\t%d\t%d\n' % (BASE + off, len(out), used) for off, out, used in kept)
    want_stdout = '\n'.join(['blobs: %d' % len(kept),
                             'out bytes: %d' % sum(len(o) for _, o, _ in kept),
                             'in bytes: %d' % sum(u for _, _, u in kept)])
    got_stdout = r.stdout.strip()
    if got_stdout != want_stdout:
        sys.exit(f'FAIL stdout differs\n  got : {got_stdout!r}\n  want: {want_stdout!r}')
    if not OUT.exists():
        sys.exit('FAIL private/extracted/lz77 was not created')
    idx = OUT / 'index.tsv'
    if not idx.exists():
        sys.exit('FAIL private/extracted/lz77/index.tsv was not written')
    got_index = idx.read_bytes()
    if got_index != want_index.encode('ascii'):
        g, w = got_index.decode('ascii', 'replace').split('\n'), want_index.split('\n')
        for k, (a, b) in enumerate(zip(g, w)):
            if a != b:
                sys.exit(f'FAIL index.tsv line {k + 1} differs\n  got : {a!r}\n  want: {b!r}')
        if len(g) != len(w):
            sys.exit(f'FAIL index.tsv has {len(g) - 1} lines, want {len(w) - 1}')
        sys.exit(f'FAIL index.tsv differs in length: got {len(got_index)} B, want {len(want_index)} B')
    want_names = {'index.tsv'} | {'%08X.bin' % (BASE + off) for off, _, _ in kept}
    got_names = {f.name for f in OUT.iterdir() if f.is_file()}
    if got_names != want_names:
        extra, missing = sorted(got_names - want_names)[:5], sorted(want_names - got_names)[:5]
        sys.exit(f'FAIL file set differs: {len(got_names)} files, want {len(want_names)}'
                 f' (unexpected {extra}, missing {missing})')
    for off, out, _ in kept:
        got = (OUT / ('%08X.bin' % (BASE + off))).read_bytes()
        if got != out:
            sys.exit('FAIL blob 0x%08X differs: %d bytes, want %d' % (BASE + off, len(got), len(out)))
    print('blobs: %d' % len(kept))
    print('out bytes: %d' % sum(len(o) for _, o, _ in kept))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
