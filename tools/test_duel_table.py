"""Check for `tools/duel_table.py` (the duel / opponent table extractor).

Runs the extractor in this checkout and compares its three output files with the expected
text recomputed here, independently, straight from the ROM. Then it asserts the structural
invariants the extractor's own documentation claims.

Spec (ROM = private/baserom.gba, file offset + 0x08000000 = ROM address), as in the extractor's
docstring:
  * `0x08D35C28` holds 200 little-endian words; word k -> record k, and the records are
    `0x080B4B5C + 0x28*k`;
  * record fields: +0x00 u16 a, +0x02 u16 b, +0x04 u32 deck pointer, +0x08 / +0x0C / +0x10 u32
    weighted-list pointers, +0x14 u32, +0x18 u32, +0x1C u16, +0x1E u16, +0x20 u8, +0x24 u16;
  * a deck is 40 u16 card ids at the deck pointer;
  * a weighted list is `u16 id, u16 weight` pairs, ending at the first pair whose id is 0;
  * text records are `$0<English>$1...$6` + 0x00; a field is decoded as: `0x87 <c>` = the letter
    from config/text_glyphs.csv (else `\\x87\\xNN`), `0x25` = `,`, `0x5E` and `0x23 0x30` = ` / `,
    0x20..0x7E = itself, anything else `\\xNN`; card id c uses the name record at
    `u32[0x08D310E4 + 4*(c-1)]`;
  * duel-start opcodes are the byte pair `23 38` ("#8") anywhere at or above `0x08D00000`,
    followed by the duel id byte; the enclosing text record is the nearest `$0` preceded by
    0x00 (within 3000 bytes back).

Invariants asserted here (each one is a claim in docs/game-data.md):
  * every record's deck array is 40 u16, each either 0 (the whole array) or 1..900;
  * every non-empty list08 / list10 has strictly increasing weights and ends at exactly 2047
    (the game rolls 0..0x7FF for those two lists), every non-empty list0c ends at exactly 29999
    (the game rolls 0..0x752F for that one);
  * all list ids are 1..900;
  * the 130 opcode sites: the byte after the id is 0x00, and every id is < 200.

Usage: PY tools/test_duel_table.py
"""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'duel_table.py'
OUT = ROOT / 'private' / 'extracted'
GLYPHS = ROOT / 'config' / 'text_glyphs.csv'
BASE = 0x08000000
TABLE = 0x08D35C28
COUNT = 200
REC0 = 0x080B4B5C
REC_SIZE = 0x28
CARDS = 40
NAMES = 0x08D310E4
MAXW = {8: 2047, 12: 29999, 16: 2047}   # record offset -> weight the list must end on


def glyphs():
    tab = {}
    for row in GLYPHS.read_text(encoding='utf-8').splitlines():
        row = row.strip()
        if not row or row[0] == '#' or row.startswith('code,'):
            continue
        cols = row.split(',')
        if cols[1] != '':
            tab[int(cols[0], 16)] = cols[1]
    return tab


def expected(d):
    """Recompute all three files from scratch."""
    tab = glyphs()

    def u16(a):
        return struct.unpack_from('<H', d, a - BASE)[0]

    def u32(a):
        return struct.unpack_from('<I', d, a - BASE)[0]

    def decode(blob):
        pos, out = 0, ''
        while pos < len(blob):
            b = blob[pos]
            if b == 0x87 and pos + 1 < len(blob):
                out += tab.get(blob[pos + 1], '\\x87\\x%02x' % blob[pos + 1])
                pos += 2
            elif b == 0x25:
                out += ','
                pos += 1
            elif b == 0x5E:
                out += ' / '
                pos += 1
            elif b == 0x23 and blob[pos + 1:pos + 2] == b'0':
                out += ' / '
                pos += 2
            elif 0x20 <= b <= 0x7e:
                out += chr(b)
                pos += 1
            else:
                out += '\\x%02x' % b
                pos += 1
        return out

    def english(addr):
        if not (BASE <= addr < BASE + len(d)):
            return ''
        o = addr - BASE
        end = d.find(b'\x00', o, o + 8192)
        if end < 0:
            return ''
        blob = d[o:end]
        marks = [(k, blob[k + 1]) for k in range(len(blob) - 1)
                 if blob[k] == 0x24 and 0x30 <= blob[k + 1] <= 0x39]
        for n, (start, dig) in enumerate(marks):
            if dig == 0x30:
                last = marks[n + 1][0] if n + 1 < len(marks) else len(blob)
                return decode(blob[start + 2:last])
        return ''

    def cname(cid):
        return english(u32(NAMES + 4 * (cid - 1))) if 1 <= cid <= 900 else '?'

    def wlist(addr):
        out = []
        for i in range(4096):
            cid, weight = struct.unpack_from('<HH', d, addr - BASE + 4 * i)
            if cid == 0:
                break
            out.append((cid, weight))
        return out

    trows = ['duel\trecord\tid_a\tid_b\tdeck_ptr\tf14\tf18\tf1c_a\tf1c_b\tf20\tf24'
             '\tlist08\tlist0c\tlist10\n']
    drows = ['duel\tcards\tempty\tdeck\n']
    problems = []
    for k in range(COUNT):
        rec = u32(TABLE + 4 * k)
        if rec != REC0 + REC_SIZE * k:
            problems.append('record %d is 0x%08X, expected 0x%08X' % (k, rec, REC0 + REC_SIZE * k))
        deck = [u16(u32(rec + 4) + 2 * i) for i in range(CARDS)]
        if any(c for c in deck):
            bad = [c for c in deck if not 1 <= c <= 900]
            if bad:
                problems.append('record %d deck has ids outside 1..900: %s' % (k, bad[:5]))
        lists = []
        for off in (8, 12, 16):
            pairs = wlist(u32(rec + off))
            lists.append(pairs)
            if pairs:
                ids = [p[0] for p in pairs]
                ws = [p[1] for p in pairs]
                if any(not 1 <= i <= 900 for i in ids):
                    problems.append('record %d list +0x%02X has ids outside 1..900' % (k, off))
                if any(b <= a for a, b in zip(ws, ws[1:])):
                    problems.append('record %d list +0x%02X weights not strictly increasing' % (k, off))
                if ws[-1] != MAXW[off]:
                    problems.append('record %d list +0x%02X ends on weight %d, expected %d'
                                    % (k, off, ws[-1], MAXW[off]))
        trows.append('\t'.join(str(c) for c in [
            k, '0x%08X' % rec, u16(rec), u16(rec + 2), '0x%08X' % u32(rec + 4),
            u32(rec + 20), u32(rec + 24), u16(rec + 28), u16(rec + 30),
            d[rec + 32 - BASE], u16(rec + 36),
            ' '.join('%d:%d' % p for p in lists[0]),
            ' '.join('%d:%d' % p for p in lists[1]),
            ' '.join('%d:%d' % p for p in lists[2])]) + '\n')
        counted = {}
        for cid in deck:
            counted[cid] = counted.get(cid, 0) + 1
        drows.append('\t'.join([str(k), str(len([c for c in deck if c])),
                                str(sum(1 for c in deck if c == 0)),
                                ' '.join('%dx %s(%d)' % (v, cname(c), c)
                                         for c, v in sorted(counted.items()) if c)]) + '\n')

    srows = ['duel\topcode_addr\trecord_addr\topcode_then_nul\tline\n']
    n_op = 0
    pos = 0
    while True:
        k = d.find(b'\x23\x38', pos)
        if k < 0:
            break
        pos = k + 1
        if BASE + k < 0x08D00000:
            continue
        start = None
        j = k
        while j > k - 3000 and j > 1:
            if d[j] == 0x30 and d[j - 1] == 0x24 and d[j - 2] == 0x00:
                start = j - 1
                break
            j -= 1
        if start is None:
            continue
        if d[k + 2] >= COUNT:
            problems.append('opcode at 0x%08X names duel %d, out of range' % (BASE + k, d[k + 2]))
        if d[k + 3] != 0:
            problems.append('opcode at 0x%08X is not followed by 0x00' % (BASE + k))
        n_op += 1
        srows.append('\t'.join([str(d[k + 2]), '0x%08X' % (BASE + k), '0x%08X' % (BASE + start),
                                str(int(d[k + 3] == 0)), english(BASE + start)]) + '\n')
    return trows, drows, srows, problems, n_op


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/duel_table.py does not exist')
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    for f in ('duel_table.tsv', 'duel_decks.tsv', 'duel_scripts.tsv'):
        p = OUT / f
        if p.exists():
            p.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit('FAIL duel_table.py exited %d\n%s\n%s' % (r.returncode, r.stdout[-2000:],
                                                           r.stderr[-2000:]))
    trows, drows, srows, problems, n_op = expected(ROM.read_bytes())
    for name, want in (('duel_table.tsv', trows), ('duel_decks.tsv', drows),
                       ('duel_scripts.tsv', srows)):
        p = OUT / name
        if not p.exists():
            sys.exit(f'FAIL {name} was not written')
        got = p.read_text(encoding='utf-8').split('\n')
        want_l = ''.join(want).split('\n')
        if got != want_l:
            for n, (a, b) in enumerate(zip(got, want_l)):
                if a != b:
                    sys.exit(f'FAIL {name} line {n + 1} differs\n  got : {a[:200]!r}\n'
                             f'  want: {b[:200]!r}')
            sys.exit(f'FAIL {name} length differs: got {len(got)} lines, want {len(want_l)}')
    if problems:
        sys.exit('FAIL structural invariants:\n  ' + '\n  '.join(problems[:10]))
    print('duels: %d' % (len(trows) - 1))
    print('decks: %d rows, distinct: %d' % (len(drows) - 1,
                                            len({r.split('\t')[3] for r in drows[1:]})))
    print('duel-start opcodes: %d (ids %s)' % (n_op, len({r.split('\t')[0] for r in srows[1:]})))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
