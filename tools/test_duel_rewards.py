"""Check for the local job "duel reward tables" (tools/duel_rewards.py).

Runs tools/duel_rewards.py in this checkout and compares its output file with the expected text
recomputed here, independently, straight from the ROM.

What the job writes: `private/extracted/duel_rewards.tsv`, one line per entry of every weighted
list of every duel record, plus one "deck" line per duel. The model (all verified, see
docs/game-data.md "Opponents, decks and drops"):

  * `0x08D35C28` = 200 words, word k -> a 40-byte record (`0x080B4B5C + 0x28*k`);
  * record +0x08 (call it list 08) and +0x10 (list 10) are walked by `sub_0801649C` with a random
    roll in 0..2047; record +0x0C (list 0C) is walked by `sub_08016768` with a roll in 0..29999.
    A list is `u16 card id, u16 cumulative weight` pairs; the walk stops at the first id 0 and
    returns the first entry whose weight is greater than the roll. So an entry covers the
    (previous weight, own weight] slice of the roll space and its chance in parts per million is
    `(weight - previous_weight) * 1000000 // (roll_range)` where roll_range is 2048 or 30000.
  * a deck is 40 u16 card ids at `u32[record + 4]` (0 = the slot is empty).

Output format (tab separated, LF, no trailing blank line beyond the last `\\n`):
    header:  duel\\tlist\\troll\\tcard_id\\tcard\\tweight\\tprev\\tchance_ppm\\n
    one row per deck card, list = "deck", roll = 0, card_id = the id (0 allowed), card = the name
    (empty string for id 0), weight = 0, prev = 0, chance_ppm = 0;
    then, for list in 08, 0C, 10 (that order) and only when the list is not empty, one row per
    entry: roll = 2048 / 30000 / 2048, prev = the previous entry's weight (0 for the first),
    chance_ppm = (weight - prev) * 1000000 // roll.
Card names come from the name table: card c -> the English `$0` field of the record at
`u32[0x08D310E4 + 4*(c-1)]`, decoded as: `0x87 <c>` = the letter in config/text_glyphs.csv (else
`\\x87\\xNN`), `0x25` = `,`, `0x5E` and `0x23 0x30` = ` / `, 0x20..0x7E = itself, else `\\xNN`.
Row order: duel 0..199, and inside a duel: deck rows, then list 08, then list 0C, then list 10.

Usage: python3 tools/test_duel_rewards.py
"""
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
SCRIPT = ROOT / 'tools' / 'duel_rewards.py'
OUT = ROOT / 'private' / 'extracted' / 'duel_rewards.tsv'
GLYPHS = ROOT / 'config' / 'text_glyphs.csv'
BASE = 0x08000000
TABLE = 0x08D35C28
COUNT = 200
CARDS = 40
NAMES = 0x08D310E4
LISTS = (('deck', 4, 0), ('08', 8, 2048), ('0C', 12, 30000), ('10', 16, 2048))


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

    def cname(c):
        if not 1 <= c <= 900:
            return ''
        o = u32(NAMES + 4 * (c - 1)) - BASE
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

    lines = ['duel\tlist\troll\tcard_id\tcard\tweight\tprev\tchance_ppm\n']
    for k in range(COUNT):
        rec = u32(TABLE + 4 * k)
        for name, off, roll in LISTS:
            if name == 'deck':
                ids = [u16(u32(rec + 4) + 2 * i) for i in range(CARDS)]
                for c in ids:
                    lines.append('%d\tdeck\t0\t%d\t%s\t0\t0\t0\n' % (k, c, cname(c) if c else ''))
                continue
            addr = u32(rec + off)
            prev = 0
            i = 0
            while True:
                cid, weight = struct.unpack_from('<HH', d, addr - BASE + 4 * i)
                if cid == 0:
                    break
                lines.append('%d\t%s\t%d\t%d\t%s\t%d\t%d\t%d\n'
                             % (k, name, roll, cid, cname(cid), weight, prev,
                                (weight - prev) * 1000000 // roll))
                prev = weight
                i += 1
    return ''.join(lines)


def main():
    if not SCRIPT.exists():
        sys.exit('FAIL tools/duel_rewards.py does not exist')
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    if OUT.exists():
        OUT.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit('FAIL duel_rewards.py exited %d\n%s\n%s' % (r.returncode, r.stdout[-2000:],
                                                             r.stderr[-2000:]))
    want = expected(ROM.read_bytes())
    if not OUT.exists():
        sys.exit('FAIL private/extracted/duel_rewards.tsv was not written')
    got = OUT.read_text(encoding='utf-8')
    if got != want:
        gl, wl = got.split('\n'), want.split('\n')
        for n in range(max(len(gl), len(wl))):
            a = gl[n] if n < len(gl) else '<missing>'
            b = wl[n] if n < len(wl) else '<missing>'
            if a != b:
                sys.exit('FAIL line %d differs\n  got : %r\n  want: %r' % (n + 1, a, b))
        sys.exit('FAIL length differs: got %d bytes, want %d' % (len(got), len(want)))
    rows = want.splitlines()[1:]
    decks = [r2 for r2 in rows if '\tdeck\t' in r2]
    print('rows: %d' % len(rows))
    print('deck rows: %d' % len(decks))
    print('reward rows: %d' % (len(rows) - len(decks)))
    print('bytes: %d' % len(want))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
