"""Mechanical drafts from matched siblings (Claude, 2026-10-14). For each row of private/drafts/siblings.tsv with
ratio >= --min, the two functions' ROM bytes are walked in parallel: every literal-pool word and every BL target that
differs gives an address mapping (sibling value -> target value). The sibling's C is copied with the function
renamed and every address-named symbol / hex constant mapped. The draft must still pass tools/match_func.py.
Writes private/drafts/<name>.sib.c and prints the names.   Usage: python3 tools/sibling_drafts.py [--min 0.95]
"""
import argparse
import csv
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT
B = 0x08000000


def refs(rom, addr, size):
    """Ordered list of ('bl', target) / ('pool', word) used by the function."""
    o = addr - B
    hw = [struct.unpack_from('<H', rom, o + i)[0] for i in range(0, size - 1, 2)]
    out, i = [], 0
    while i < len(hw):
        h = hw[i]
        if (h & 0xF800) == 0xF000 and i + 1 < len(hw) and (hw[i + 1] & 0xF800) == 0xF800:
            off = ((h & 0x7FF) << 12) | ((hw[i + 1] & 0x7FF) << 1)
            if off & 0x400000:
                off -= 0x800000
            out.append(('bl', addr + 2 * i + 4 + off))
            i += 2
            continue
        if (h & 0xF800) == 0x4800:
            t = ((addr + 2 * i + 4) & ~3) + (h & 0xFF) * 4
            if t + 4 <= addr + size:
                out.append(('pool', struct.unpack_from('<I', rom, t - B)[0]))
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min', type=float, default=0.95)
    a = ap.parse_args()
    rom = (REPO / 'private' / 'baserom.gba').read_bytes()
    fn = {r['name']: (int(r['address'], 16), int(r['size'])) for r in csv.DictReader(open(ROOT / 'config' / 'functions.csv'))}
    made = []
    for line in (REPO / 'private' / 'drafts' / 'siblings.tsv').read_text().splitlines()[1:]:
        tgt, _, sib, ratio = line.split('\t')
        if float(ratio) < a.min:
            continue
        src = REPO / 'src' / 'funcs' / (sib + '.c')
        if not src.exists():
            continue
        (ta, ts), (sa, ss) = fn[tgt], fn[sib]
        rt, rs = refs(rom, ta, ts), refs(rom, sa, ss)
        if len(rt) != len(rs) or any(x[0] != y[0] for x, y in zip(rt, rs)):
            continue
        mp = {}
        for (k, sv), (_, tv) in zip(rs, rt):
            if sv != tv:
                if mp.get(sv, tv) != tv:
                    break
                mp[sv] = tv
        else:
            c = src.read_text(encoding='utf-8')
            c = re.sub(r'\b%s\b' % sib, tgt, c)
            def sym(m):
                v = int(m.group(2), 16)
                for base in (v, v | 1, v & ~1):
                    if base in mp:
                        nv = mp[base] & ~1 if m.group(1) == 'sub_' else mp[base]
                        return '%s%08X' % (m.group(1), nv)
                return m.group(0)
            c = re.sub(r'\b(sub_|gUnk_)([0-9A-Fa-f]{8})\b', sym, c)
            c = re.sub(r'\b0x([0-9A-Fa-f]{7,8})\b',
                       lambda m: ('0x%08X' % mp[int(m.group(1), 16)]) if int(m.group(1), 16) in mp else m.group(0), c)
            (REPO / 'private' / 'drafts' / (tgt + '.sib.c')).write_text(c, encoding='utf-8', newline='\n')
            made.append(tgt)
    print(' '.join(made))


if __name__ == '__main__':
    main()
