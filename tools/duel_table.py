"""Duel / opponent table extractor (Yugioh: The Sacred Cards, GBA, USA).

Writes, from `private/baserom.gba`:
  private/extracted/duel_table.tsv    one row per duel record (200 rows)
  private/extracted/duel_decks.tsv    one row per duel: the 40-card deck with names
  private/extracted/duel_scripts.tsv  one row per `#8 <id>` duel-start opcode found in the
                                      story scripts, with the text record it sits in

What the table is (all verified, see docs/game-data.md "Opponents, decks and drops"):
  * `0x08D35C28` is a pointer table of exactly 200 words; entry k -> a 40-byte record
    (`0x080B4B5C + 0x28*k` for every k in 0..199, verified).
  * The story script opcode `#8 <id>` (`sub_08031E40` case 8 at `0x08031FC6`) stores the
    byte <id> into `0x02020D30 + 0x10`; the duel code (`sub_080164EC`) reads that word as
    the index into this table. So <id> = duel number = table index.
  * 40-byte record:
        +0x00 u16 a, u16 b
        +0x04 u32 -> 40 x u16 card ids (the opponent's deck; all-zero for the dummy/empty
                     record and for the "no deck" duels)
        +0x08 u32 -> weighted list A: u16 (card id, cumulative weight), 0-terminated
        +0x0C u32 -> weighted list B, same shape
        +0x10 u32 -> weighted list C, same shape
        +0x14 u16, u16
        +0x18 u32
        +0x1C u16, u16
        +0x20 u8, u8, u8 (a switch value 0..15)
        +0x24 u16
  * `sub_0801649C` walks list at record +0x08 (or +0x10) with a random roll in 0..0x7FF and
    picks the first entry whose weight is greater than the roll; `sub_08016768` does the same
    for record +0x0C with a roll in 0..0x752F (29999). Both stop at a zero id.

Usage: python3 tools/duel_table.py
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUTDIR = ROOT / 'private' / 'extracted'
GLYPHS = ROOT / 'config' / 'text_glyphs.csv'

BASE = 0x08000000
DUEL_TABLE = 0x08D35C28
DUEL_COUNT = 200
REC_SIZE = 0x28
DECK_CARDS = 40
CARD_NAMES = 0x08D310E4
# random roll ranges the game uses for the weighted lists (from the readers)
ROLL_A = 0x800          # 0..2047  (sub_0801649C, lists at +0x08 / +0x10)
ROLL_B = 0x752F + 1     # 0..29999 (sub_08016768, list at +0x0C)
OPCODE = b'\x23\x38'    # "#8" = duel start in the story script bytecode


def load_glyphs():
    tab = {}
    for row in GLYPHS.read_text(encoding='utf-8').splitlines():
        row = row.strip()
        if not row or row[0] == '#' or row.startswith('code,'):
            continue
        cols = row.split(',')
        if cols[1] != '':
            tab[int(cols[0], 16)] = cols[1]
    return tab


def main():
    if not ROM.exists():
        sys.exit(f'FAIL no ROM at {ROM}')
    data = ROM.read_bytes()
    glyphs = load_glyphs()

    def u16(a):
        return struct.unpack_from('<H', data, a - BASE)[0]

    def u32(a):
        return struct.unpack_from('<I', data, a - BASE)[0]

    def decode(blob):
        """One Latin text field: 0x25 = comma, 0x87 <c> = accented letter, 0x5E/0x230 = break."""
        pos, out = 0, ''
        while pos < len(blob):
            b = blob[pos]
            if b == 0x87 and pos + 1 < len(blob):
                out += glyphs.get(blob[pos + 1], '\\x87\\x%02x' % blob[pos + 1])
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

    def english_record(addr):
        """English ($0) field of the text record at `addr`, or ''."""
        if not (BASE <= addr < BASE + len(data)):
            return ''
        o = addr - BASE
        end = data.find(b'\x00', o, o + 8192)
        if end < 0:
            return ''
        blob = data[o:end]
        marks = [(k, blob[k + 1]) for k in range(len(blob) - 1)
                 if blob[k] == 0x24 and 0x30 <= blob[k + 1] <= 0x39]
        for n, (start, dig) in enumerate(marks):
            if dig == 0x30:
                last = marks[n + 1][0] if n + 1 < len(marks) else len(blob)
                return decode(blob[start + 2:last])
        return ''

    def card_name(cid):
        if not 1 <= cid <= 900:
            return '?'
        return english_record(u32(CARD_NAMES + 4 * (cid - 1)))

    def deck_of(rec):
        ptr = u32(rec + 4)
        return [u16(ptr + 2 * i) for i in range(DECK_CARDS)]

    def wlist(addr):
        out = []
        for i in range(4096):
            cid, weight = struct.unpack_from('<HH', data, addr - BASE + 4 * i)
            if cid == 0:
                break
            out.append((cid, weight))
        return out

    def fmt_list(pairs):
        return ' '.join('%d:%d' % p for p in pairs)

    OUTDIR.mkdir(parents=True, exist_ok=True)

    rows, decks = [], []
    for k in range(DUEL_COUNT):
        rec = u32(DUEL_TABLE + 4 * k)
        deck = deck_of(rec)
        a, b, c = wlist(u32(rec + 8)), wlist(u32(rec + 12)), wlist(u32(rec + 16))
        rows.append([
            k, '0x%08X' % rec, u16(rec), u16(rec + 2), '0x%08X' % u32(rec + 4),
            u32(rec + 20), u32(rec + 24), u16(rec + 28), u16(rec + 30),
            data[rec + 32 - BASE], u16(rec + 36),
            fmt_list(a), fmt_list(b), fmt_list(c),
        ])
        counted = {}
        for cid in deck:
            counted[cid] = counted.get(cid, 0) + 1
        decks.append([k, len([c for c in deck if c]), sum(1 for c in deck if c == 0),
                      ' '.join('%dx %s(%d)' % (v, card_name(c), c)
                               for c, v in sorted(counted.items()) if c)])

    (OUTDIR / 'duel_table.tsv').write_text(
        'duel\trecord\tid_a\tid_b\tdeck_ptr\tf14\tf18\tf1c_a\tf1c_b\tf20\tf24\tlist08\tlist0c\tlist10\n'
        + ''.join('\t'.join(str(c) for c in r) + '\n' for r in rows), encoding='utf-8')
    (OUTDIR / 'duel_decks.tsv').write_text(
        'duel\tcards\tempty\tdeck\n'
        + ''.join('\t'.join(str(c) for c in r) + '\n' for r in decks), encoding='utf-8')

    # story scripts: every "#8 <id>" opcode in the data half of the ROM
    script_rows = []
    pos = 0
    while True:
        k = data.find(OPCODE, pos)
        if k < 0:
            break
        pos = k + 1
        if BASE + k < 0x08D00000:
            continue                      # graphics/code half: coincidences
        start = None
        j = k
        while j > k - 3000 and j > 1:
            if data[j] == 0x30 and data[j - 1] == 0x24 and data[j - 2] == 0x00:
                start = j - 1
                break
            j -= 1
        if start is None:
            continue
        script_rows.append([data[k + 2], '0x%08X' % (BASE + k), '0x%08X' % (BASE + start),
                            int(data[k + 3] == 0), english_record(BASE + start)])

    (OUTDIR / 'duel_scripts.tsv').write_text(
        'duel\topcode_addr\trecord_addr\topcode_then_nul\tline\n'
        + ''.join('\t'.join(str(c) for c in r) + '\n' for r in script_rows), encoding='utf-8')

    ids = sorted({r[0] for r in script_rows})
    distinct_decks = len({tuple(deck_of(u32(DUEL_TABLE + 4 * k))) for k in range(DUEL_COUNT)})
    print('duels: %d' % len(rows))
    print('distinct decks: %d' % distinct_decks)
    print('script-referenced duel ids: %d (min %d, max %d)' % (len(ids), ids[0], ids[-1]))
    print('wrote %s' % (OUTDIR / 'duel_table.tsv'))
    print('wrote %s' % (OUTDIR / 'duel_decks.tsv'))
    print('wrote %s' % (OUTDIR / 'duel_scripts.tsv'))


if __name__ == '__main__':
    main()
