"""Duel reward / drop tables extractor for Yu-Gi-Oh! The Sacred Cards.

Reads private/baserom.gba and writes private/extracted/duel_rewards.tsv.
Standard library only.
"""
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'duel_rewards.tsv'
GLYPHS = ROOT / 'config' / 'text_glyphs.csv'
BASE = 0x08000000
TABLE = 0x08D35C28
COUNT = 200
CARDS = 40
NAMES = 0x08D310E4
LISTS = (('deck', 4, 0), ('08', 8, 2048), ('0C', 12, 30000), ('10', 16, 2048))


def load_glyphs():
    """Load the text_glyphs.csv code -> letter map."""
    tab = {}
    text = GLYPHS.read_text(encoding='utf-8')
    for row in text.splitlines():
        row = row.strip()
        if not row or row[0] == '#' or row.startswith('code,'):
            continue
        cols = row.split(',')
        if cols[1]:
            tab[int(cols[0], 16)] = cols[1]
    return tab


def decode(blob, tab):
    """Decode bytes using the glyph table to a string."""
    pos = 0
    out = []
    length = len(blob)
    while pos < length:
        b = blob[pos]
        if b == 0x87 and pos + 1 < length:
            next_byte = blob[pos + 1]
            ch = tab.get(next_byte)
            if ch is not None:
                out.append(ch)
            else:
                out.append('\\x87\\x{:02x}'.format(next_byte))
            pos += 2
        elif b == 0x25:
            out.append(',')
            pos += 1
        elif b == 0x5E:
            out.append(' / ')
            pos += 1
        elif b == 0x23 and pos + 1 < length and blob[pos + 1] == 0x30:
            out.append(' / ')
            pos += 2
        elif 0x20 <= b <= 0x7E:
            out.append(chr(b))
            pos += 1
        else:
            out.append('\\x{:02x}'.format(b))
            pos += 1
    return ''.join(out)


def cname(c, data, tab):
    """Return the English name of card c (1..900, 0 -> '')."""
    if c == 0:
        return ''
    if not 1 <= c <= 900:
        return ''
    name_addr = struct.unpack_from('<I', data, NAMES + 4 * (c - 1) - BASE)[0]
    o = name_addr - BASE
    end = data.find(b'\x00', o, o + 8192)
    if end < 0:
        return ''
    blob = data[o:end]
    marks = []
    for k in range(len(blob) - 1):
        if blob[k] == 0x24 and 0x30 <= blob[k + 1] <= 0x39:
            marks.append((k, blob[k + 1]))
    for n, (start, dig) in enumerate(marks):
        if dig == 0x30:
            last = marks[n + 1][0] if n + 1 < len(marks) else len(blob)
            return decode(blob[start + 2:last], tab)
    return ''


def main():
    if not ROM.exists():
        print('ERROR: no ROM at {}'.format(ROM), file=sys.stderr)
        sys.exit(1)

    data = ROM.read_bytes()
    tab = load_glyphs()

    def u16(a):
        return struct.unpack_from('<H', data, a - BASE)[0]

    def u32(a):
        return struct.unpack_from('<I', data, a - BASE)[0]

    lines = ['duel\tlist\troll\tcard_id\tcard\tweight\tprev\tchance_ppm\n']
    row_count = 0

    for k in range(COUNT):
        rec = u32(TABLE + 4 * k)

        for name, off, roll in LISTS:
            if name == 'deck':
                deck_start = u32(rec + 4)
                for i in range(CARDS):
                    cid = u16(deck_start + 2 * i)
                    card = cname(cid, data, tab)
                    lines.append('%d\tdeck\t0\t%d\t%s\t0\t0\t0\n' % (k, cid, card))
                    row_count += 1
                continue

            addr = u32(rec + off)
            prev = 0
            entry_count = 0
            while True:
                cid, weight = struct.unpack_from('<HH', data, addr - BASE + 4 * entry_count)
                if cid == 0:
                    break
                card = cname(cid, data, tab)
                chance = (weight - prev) * 1000000 // roll
                lines.append('%d\t%s\t%d\t%d\t%s\t%d\t%d\t%d\n' % (
                    k, name, roll, cid, card, weight, prev, chance))
                prev = weight
                entry_count += 1
            row_count += entry_count

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(''.join(lines), encoding='utf-8', newline='')
    print('wrote %d rows' % row_count)


if __name__ == '__main__':
    main()
