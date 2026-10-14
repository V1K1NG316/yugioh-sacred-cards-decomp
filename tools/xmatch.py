"""Find Sacred Cards functions that are the same code as a function in Yu-Gi-Oh! The Eternal Duelist Soul (EDS),
whose matching decomp (github.com/CosmicScribe64/eds-decomp, MIT) is cloned in private/ref/eds-decomp.
(Claude, 2026-10-14, Matter_Scatter's idea to look at decomp lists.)

Same compiler (old_agbcc) + same C => same instruction bytes, except what depends on addresses: BL targets and the
literal-pool words that hold addresses. Both are masked; equal masked bytes of equal length => a "twin".
Output: private/ref/twins.tsv  (ours, our_addr, size, eds_name, eds_addr, eds_unit, matched_here)
Usage: PY tools/xmatch.py
"""
import csv
import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('D:/Yugioh_DeComp_V2')
OURS = REPO / 'private' / 'baserom.gba'
EDS = REPO / 'private' / 'ref' / 'eds.gba'
EDS_FUNCS = REPO / 'private' / 'ref' / 'eds-decomp' / 'config' / 'functions.tsv'
B = 0x08000000


def masked(rom, addr, size):
    o = addr - B
    b = bytearray(rom[o:o + size])
    n = len(b) // 2
    hw = [struct.unpack_from('<H', b, 2 * i)[0] for i in range(n)]
    mask = [False] * len(b)
    i = 0
    while i < n:
        h = hw[i]
        if (h & 0xF800) == 0xF000 and i + 1 < n and (hw[i + 1] & 0xF800) == 0xF800:   # BL pair
            for k in range(4):
                mask[2 * i + k] = True
            i += 2
            continue
        if (h & 0xF800) == 0x4800:                                                     # ldr rN, [pc, #imm]
            t = ((addr + 2 * i + 4) & ~3) + (h & 0xFF) * 4 - addr
            for k in range(4):
                if 0 <= t + k < len(b):
                    mask[t + k] = True
        i += 1
    return bytes(0 if m else x for x, m in zip(b, mask))


def sig(rom, addr, size):
    return hashlib.sha1(masked(rom, addr, size)).hexdigest() + ':%d' % size


def main():
    ours = OURS.read_bytes()
    eds = EDS.read_bytes()
    matched = {p.stem for p in (REPO / 'src' / 'funcs').glob('*.c')}
    table = {}
    for line in EDS_FUNCS.read_text().splitlines():
        if line.startswith('#') or not line.strip():
            continue
        f = line.split('\t')
        addr, mode, size, name, unit = int(f[0], 16), f[1], int(f[2], 16), f[3], f[4]
        if mode != 't' or size < 4 or size > 0x4000:
            continue
        table.setdefault(sig(eds, addr, size), []).append((name, addr, unit))
    rows, tot, hit = [], 0, 0
    for r in csv.DictReader(open(ROOT / 'config' / 'functions.csv')):
        if r['mode'] != 'thumb':
            continue
        addr, size = int(r['address'], 16), int(r['size'])
        if size < 4 or size > 0x4000:
            continue
        tot += 1
        # our extents may include trailing padding / hidden functions (A35): try the exact size first, then shrink
        cands = table.get(sig(ours, addr, size))
        if not cands:
            for s in range(size - 2, max(size - 64, 3), -2):
                cands = table.get(sig(ours, addr, s))
                if cands:
                    break
        if cands:
            hit += 1
            n, a, u = cands[0]
            rows.append((r['name'], r['address'], size, n, '0x%08X' % a, u, 'y' if r['name'] in matched else 'n'))
    out = REPO / 'private' / 'ref' / 'twins.tsv'
    with open(out, 'w', encoding='utf-8') as f:
        f.write('ours\tour_addr\tsize\teds_name\teds_addr\teds_unit\tmatched_here\n')
        for row in rows:
            f.write('\t'.join(map(str, row)) + '\n')
    new = [x for x in rows if x[6] == 'n']
    print('our thumb functions: %d; twins in EDS: %d (%d not matched here yet, %d bytes)'
          % (tot, hit, len(new), sum(x[2] for x in new)))


if __name__ == '__main__':
    main()
