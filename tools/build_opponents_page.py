"""Build the opponents datamine page (Matter_Scatter's one-day project, 2026-10-12).

Reads private/baserom.gba with the verified formats in docs/game-data.md (card names/stats/types/attributes,
duel table 0x08D35C28 -> records 0x080B4B5C + 0x28*k: deck +0x04, drop lists +0x08 / +0x0C / +0x10) and, if
present, private/extracted/duel_names.tsv (duel -> opponent name). Writes the self-contained page
private/extracted/opponents.html (game-derived: stays private, never committed).
Usage: PY tools/build_opponents_page.py
"""
import collections
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import duel_rewards as dr  # noqa: E402  (verified decoder + glyph table)

ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'opponents.html'
NAMES_TSV = ROOT / 'private' / 'extracted' / 'duel_names.tsv'
B = 0x08000000
LISTS = (('Prize after a win (normal ante)', 8, 2048), ('Hidden counter (not a prize)', 12, 30000), ('Prize after a win (weak ante)', 16, 2048))


def main():
    d = ROM.read_bytes()
    tab = dr.load_glyphs()
    u16 = lambda a: struct.unpack_from('<H', d, a - B)[0]
    u32 = lambda a: struct.unpack_from('<I', d, a - B)[0]

    def text(ptr):
        # first language field ($0..) of a $-record, decoded with the verified glyph table
        o = ptr - B
        while d[o:o + 2] != b'$0':
            o += 1
        e = o + 2
        while d[e] not in (0x24, 0x00):
            e += 1
        return dr.decode(d[o + 2:e], tab).replace('%', ',').strip()

    def table_names(base, n):
        return [text(u32(base + 4 * i)) for i in range(n)]

    types = table_names(0x08D4BC3C, 24)
    attrs = table_names(0x08D419E0, 12)
    cards = {}
    for k in range(1, 901):
        atk, df = u16(0x080886E6 + 2 * k), u16(0x08087FDC + 2 * k)
        cards[k] = {
            'n': text(u32(0x08D310E4 + 4 * (k - 1))),
            'atk': None if atk == 0xFFFF else atk, 'def': None if df == 0xFFFF else df,
            'lv': d[0x89F89 + k], 'type': types[d[0x8A30E + k]] if d[0x8A30E + k] < 24 else '',
            'attr': attrs[d[0x89C04 + k]] if d[0x89C04 + k] < 12 else '', 'cost': u32(0x08088DF0 + 4 * k),
        }

    names = {}
    if NAMES_TSV.exists():
        rows = NAMES_TSV.read_text(encoding='utf-8').splitlines()
        col = {h: i for i, h in enumerate(rows[0].split('\t'))}
        for row in rows[1:]:
            f = row.split('\t')
            get = lambda h: f[col[h]].strip() if h in col and col[h] < len(f) else ''
            entry = {}
            if get('name'):
                entry.update(name=get('name'), conf=get('confidence'))
            if get('pre_duel_line'):
                entry['line'] = ' '.join(get('pre_duel_line').replace('^', ' ').replace('|', ' ').split())
            if entry:
                names[int(f[0])] = entry

    def read_list(p, roll):
        # (card id, cumulative weight) pairs; a leading (0, 0) entry is an empty slot, card 0 is never a drop
        items, prev, o = [], 0, p
        while True:
            cid, w = u16(o), u16(o + 2)
            if cid:
                items.append((cid, round((w - prev) * 100.0 / roll, 3)))
            prev = w
            o += 4
            if w >= roll - 1 or len(items) > 900:
                break
        return tuple(sorted(items, key=lambda x: -x[1]))

    raw = []
    for k in range(200):
        rec = 0x080B4B5C + 0x28 * k
        deck = collections.Counter(u16(u32(rec + 4) + 2 * i) for i in range(40))
        lists = [(label, roll, read_list(u32(rec + off), roll)) for label, off, roll in LISTS]
        raw.append((k, deck, lists))
    # identical lists used by many duels are shown once ("shared"); a single 100% card is a placeholder
    use = collections.Counter(items for _, _, ls in raw for _, _, items in ls)
    shared, sid = {}, {}
    for items, n in use.most_common():
        if n >= 20 and items not in sid:
            sid[items] = len(shared)
            role = next(label for _, _, ls in raw for label, _, it in ls if it == items)
            shared[len(shared)] = {'n': n, 'items': list(items), 'placeholder': len(items) == 1, 'label': role}
    duels = []
    for k, deck, lists in raw:
        if not any(deck) or set(deck) == {0}:
            continue  # unused duel slot
        out = []
        for label, roll, items in lists:
            if not items:
                continue
            entry = {'label': label, 'roll': roll}
            entry.update({'shared': sid[items]} if items in sid else {'items': list(items)})
            out.append(entry)
        duels.append({'id': k, **names.get(k, {}), 'deck': sorted(deck.items(), key=lambda x: (-x[1], x[0])),
                      'lists': out})

    # the 49 "weak ante" card ids (0x080BA280): anteing one of these switches the prize to the shared pool C
    weak_ante = [u16(0x080BA280 + 2 * i) for i in range(49)]
    data = json.dumps({'cards': cards, 'duels': duels, 'shared': shared, 'weakAnte': weak_ante},
                      separators=(',', ':'))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(PAGE.replace('__DATA__', data), encoding='utf-8', newline='\n')
    named = sum(1 for x in duels if 'name' in x)
    print('wrote %s: %d duels (%d named), %d cards' % (OUT, len(duels), named, len(cards)))


PAGE = Path(__file__).with_name('opponents_page.html').read_text(encoding='utf-8')

if __name__ == '__main__':
    main()
