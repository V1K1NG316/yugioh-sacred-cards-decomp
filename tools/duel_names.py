#!/usr/bin/env python3
"""Opponent names for the 200 duel records, taken from the game's own dialogue.

Where a duel starts
-------------------
The story-script interpreter `sub_08031E40` dispatches on `#<digit>` inside a dialogue
record; its case 8 (`#8 <id>`, at `0x08031FC6`) takes the byte after the `8`, stores it in
`0x02020D30+0x10`, and the duel code uses it as the index of the 200-word pointer table at
`0x08D35C28`, whose word k points at duel record k (`0x080B4B5C + 0x28*k`).  So a `#8`
opcode sits in the last line an NPC says before the duel: the speaker of that record *is*
the opponent.

Which text counts as "the same scene"
------------------------------------
Dialogue records are stored back to back (each ends in `00`, the next starts with `$0`), so
the records immediately before the opcode's record are the same NPC's earlier lines -- the
usual pattern is `<challenge line>` then `<the line with #8>`.  Looking further back drifts
into other NPCs' records (checked: a 16-record window picks up Bonz 11 records before duel
93, a different character), so the window is capped at WINDOW records: the opcode's record
plus the two before it.

Confidence (column `confidence`) and its basis (`basis`)
--------------------------------------------------------
high     `self-intro`   the speaker names himself in the window: "I'm <Name>", "My name is
                        <Name>", "They call me <Name>", or "<Name>, the ...".
medium   `own-line + deck`    a name appears in the record that carries the `#8` opcode
                        *and* the duel's own 40 cards match that name's card theme.
low      `nearby-line + deck` a name appears in the one or two records before the opcode's
                        (the same NPC's earlier line) and the deck matches.
blank    the evidence was not good enough -- a bare mention in passing ("I have to find Mr.
                        Kaiba") is kept in `mention`/`also_mentioned` but never promoted to a
                        name.  Nothing is guessed.

So a `name` is only written when the game itself supports it twice over: the speaker names
himself, or the name is used next to the duel *and* the deck the game gives that duel
matches that character's deck theme (deck check = `agree (n/40)`, from the game's own
type/attribute columns in `private/extracted/card_stats.tsv`).  The deck is a check, never
a source.

Columns
-------
duel, name, confidence, basis, mention, evidence_addr, evidence_line, dist, deck_check,
also_mentioned, pre_duel_line.  `mention` is the name the evidence refers to even when it
was not good enough for `name`; `dist` is how many records before the opcode's record the
text is (0 = the opponent's own line); `also_mentioned` lists the other lexicon names in the
window; `pre_duel_line` is the game's own line for that duel (the English text of the record
that carries the `#8` opcode), so a duel without a name still has its own label.

Usage
-----
    python3 tools/duel_names.py                 write private/extracted/duel_names.tsv
    python3 tools/duel_names.py --scan          list every self-introduction found
    python3 tools/duel_names.py --duel 93       print the window of duel 93 in full

Read-only w.r.t. the ROM; the only file written is the output TSV (untracked).
"""
import argparse
import csv
import re
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = ROOT / 'private' / 'baserom.gba'
GLYPHS_PATH = ROOT / 'config' / 'text_glyphs.csv'
STATS_PATH = ROOT / 'private' / 'extracted' / 'card_stats.tsv'
OUT_PATH = ROOT / 'private' / 'extracted' / 'duel_names.tsv'

BASE = 0x08000000
DUEL_PTR_TABLE = 0x08D35C28
DUEL_REC_BASE = 0x080B4B5C
DUEL_REC_SIZE = 0x28
DUEL_COUNT = 200
SCRIPT_MIN = 0x08D00000     # the ROM's data half: dialogue and tables, no code
WINDOW = 3                  # records of one speaker to look at (the opcode's + 2 before it)

TYPES = ['', 'Dragon', 'Magician', 'Zombie', 'Warrior', 'BeastWarrior', 'Beast', 'Wing Beast',
         'Fiend', 'Fairy', 'Insect', 'Dinosaur', 'Reptile', 'Fish', 'Sea Dragon', 'Machine',
         'Thunder', 'Aqua', 'Pyro', 'Rock', 'Plant', 'Magic', 'Trap', 'Ritual']
ATTRS = ['', 'Shadow', 'Light', 'Fiend', 'Dreams', 'Pyro', 'Forest', 'Wind', 'Earth', 'Thunder',
         'Aqua', 'Divine']

# The names the game itself uses, spelled as it spells them; the regexes are matched
# case-sensitively on word boundaries, so "Mai" does not match "Maiden" and "Rex" does not
# match the card "Two-Headed King Rex".  `types`/`attrs` feed the deck check only.
LEXICON = [
    dict(name='Bandit Keith', pats=[r'Bandit Keith', r'Keith'],
         types=['Machine'], attrs=[]),
    dict(name='Bonz', pats=[r'Bonz'], types=['Zombie', 'Fiend'], attrs=[]),
    dict(name='Weevil Underwood', pats=[r'Weevil Underwood', r'Weevil', r'Underwood'],
         types=['Insect', 'Plant'], attrs=['Forest']),
    dict(name='Rex Raptor', pats=[r'Rex Raptor', r'Raptor', r'Rex'],
         types=['Dinosaur', 'Reptile'], attrs=[]),
    dict(name='Mako Tsunami', pats=[r'Mako Tsunami', r'Mako', r'Tsunami'],
         types=['Aqua', 'Fish', 'Sea Dragon', 'Reptile'], attrs=['Aqua']),
    dict(name='Mai Valentine', pats=[r'Mai Valentine', r'Valentine'],
         types=['Wing Beast', 'Fairy'], attrs=['Wind']),
    dict(name='Joey Wheeler', pats=[r'Joey Wheeler', r'Joey', r'Wheeler'],
         types=['Warrior', 'BeastWarrior'], attrs=[]),
    dict(name='Yugi Muto', pats=[r'Yugi Muto', r'Yugi'], types=[], attrs=[]),
    dict(name='Seto Kaiba', pats=[r'Seto Kaiba', r'Seto', r'Kaiba'],
         types=['Dragon', 'Machine'], attrs=['Light']),
    dict(name='Mokuba Kaiba', pats=[r'Mokuba'], types=[], attrs=[]),
    dict(name='Marik Ishtar', pats=[r'Marik Ishtar', r'Marik', r'Ishtar'],
         types=['Fiend'], attrs=['Fiend']),
    dict(name='Odion', pats=[r'Odion'], types=[], attrs=[]),
    dict(name='Ryou Bakura', pats=[r'Ryou Bakura', r'Bakura', r'Ryou'],
         types=['Fiend', 'Zombie'], attrs=['Shadow']),
    dict(name='Pegasus', pats=[r'Pegasus'], types=['Magic'], attrs=[]),
    dict(name='Tristan Taylor', pats=[r'Tristan'], types=[], attrs=[]),
    dict(name='Tea Gardner', pats=[r'Tea'], types=[], attrs=[]),
    dict(name='Espa Roba', pats=[r'Espa Roba', r'Espa', r'Roba'], types=[], attrs=[]),
]

PAT = r"(?:%s)" % '|'.join(p for e in LEXICON for p in e['pats'])
INTRO = [
    r"\b(?:I'?m|I am|[Mm]y name is|[Tt]hey call me|[Cc]all me) (%s)\b" % PAT,
    r"\b(%s), the \w" % PAT,                      # "Bonz, the undead, shall duel forever!"
    r"\b(%s) here\b" % PAT,
]
CONF = {'self-intro': 'high', 'own-line': 'medium', 'nearby-line': 'low'}
HEADER = ['duel', 'name', 'confidence', 'basis', 'mention', 'evidence_addr', 'evidence_line',
          'dist', 'deck_check', 'also_mentioned', 'pre_duel_line']

# Mentions the tool found but that a human read shows are *not* the opponent; they are kept
# out of `name` on purpose, with the reason, rather than shipped as a wrong name.  Each one
# was checked against the quoted line -- nothing here is a guess either.
EXCLUDED = {
    12: 'the line asks "why are they after us?" about Marik, the duel is with a Ghoul',
    72: 'the line is a simile: "I\'m kind of like Mako Tsunami", an unnamed sea-deck duelist',
    76: 'the line is someone looking for Kaiba ("Oh where could Mr. Kaiba be?"), not Kaiba',
    87: 'the line addresses Marik ("Master Marik Ishtar... I beg your forgiveness"), a Ghoul',
}


def load_glyphs():
    tab = {}
    for row in GLYPHS_PATH.read_text(encoding='utf-8').splitlines():
        row = row.strip()
        if not row or row[0] == '#' or row.startswith('code,'):
            continue
        cols = row.split(',')
        if cols[1] != '':
            tab[int(cols[0], 16)] = cols[1]
    return tab


def decode(blob, glyph):
    """One text field -> readable text: '|' = line break, ',' = comma, other codes \\xNN."""
    out = []
    pos = 0
    while pos < len(blob):
        b = blob[pos]
        if b == 0x87 and pos + 1 < len(blob):
            out.append(glyph.get(blob[pos + 1], '?'))
            pos += 2
        elif b == 0x23 and blob[pos + 1:pos + 2] in (b'0', b'1'):
            out.append('|')
            pos += 2
        elif b == 0x5E:
            out.append('|')
            pos += 1
        elif b == 0x25:
            out.append(',')
            pos += 1
        elif 0x20 <= b <= 0x7E:
            out.append(chr(b))
            pos += 1
        else:
            out.append('\\x%02x' % b)
            pos += 1
    return ''.join(out)


class Rom:
    def __init__(self, data, glyph):
        self.d = data
        self.glyph = glyph
        self._stats = None

    def record_text(self, addr):
        """The English field of the record starting at `addr` (None if it is not a record)."""
        o = addr - BASE
        if not (self.d[o] == 0x24 and self.d[o + 1] == 0x30):
            return None
        end = self.d.find(b'\x00', o, o + 8192)
        if end < 0:
            return None
        return decode(self.d[o + 2:end].split(b'$1')[0], self.glyph)

    def prev_record_start(self, addr):
        """Start of the previous record = last '00 $0' before `addr` (records are contiguous)."""
        j = addr - BASE - 1
        while j > 2:
            if self.d[j] == 0x30 and self.d[j - 1] == 0x24 and self.d[j - 2] == 0x00:
                return BASE + j - 1
            j -= 1
        return None

    def u16(self, a):
        return struct.unpack_from('<H', self.d, a - BASE)[0]

    def u32(self, a):
        return struct.unpack_from('<I', self.d, a - BASE)[0]

    def duel_record(self, k):
        return self.u32(DUEL_PTR_TABLE + 4 * k)

    def deck(self, k):
        ptr = self.u32(self.duel_record(k) + 4)
        cards = [self.u16(ptr + 2 * i) for i in range(40)]
        return cards if any(cards) else []

    def card_stats(self):
        if self._stats is None:
            with STATS_PATH.open(encoding='utf-8') as f:
                self._stats = {int(r['card']): r for r in csv.DictReader(f, delimiter='\t')}
        return self._stats


def find_sites(rom):
    """Every '#8 <id>' opcode in the data half -> (duel id, opcode addr, record start addr)."""
    sites = []
    pos = 0
    while True:
        k = rom.d.find(b'\x238', pos)
        if k < 0:
            break
        pos = k + 1
        addr = BASE + k
        if addr < SCRIPT_MIN:
            continue
        rec = rom.prev_record_start(addr)
        if rec is not None:
            sites.append((rom.d[k + 2], addr, rec))
    return sites


def window(rom, rec_start, limit=WINDOW):
    """[opcode's record, the one before, the two before] as (addr, text), nearest first."""
    out = []
    addr = rec_start
    while addr is not None and len(out) < limit:
        txt = rom.record_text(addr)
        if txt is None:
            break
        out.append((addr, txt))
        addr = rom.prev_record_start(addr)
    return out


def all_names(txt):
    """[(lexicon index, matched text, match start)] for every lexicon name in one record."""
    found = []
    for i, e in enumerate(LEXICON):
        for pat in e['pats']:
            for m in re.finditer(r'\b%s\b' % pat, txt):
                found.append((i, m.group(0), m.start()))
    return found


def is_intro(txt, text):
    for pat in INTRO:
        for m in re.finditer(pat, txt):
            if m.group(1) == text:
                return True
    return False


def quote(txt, pos, n, width=60):
    lo, hi = max(0, pos - 25), min(len(txt), pos + n + width)
    return ('...' if lo > 0 else '') + txt[lo:hi] + ('...' if hi < len(txt) else '')


def evidence(rom, records):
    """The strongest name in the window -> (key, lexicon index, kind, dist, addr, text, quote).

    self-intro at dist 0..1 (the speaker's own line), then a name in the opcode's own
    record (medium), then anything at dist <= 2 (low)."""
    rank = {'self-intro': 0, 'own-line': 1, 'nearby-line': 2}
    best = None
    for dist, (addr, txt) in enumerate(records):
        for i, text, pos in all_names(txt):
            if is_intro(txt, text) and dist <= 1:
                kind = 'self-intro'
            elif dist == 0:
                kind = 'own-line'
            else:
                kind = 'nearby-line'
            key = (rank[kind], dist)
            if best is None or key < best[0]:
                best = (key, i, kind, dist, addr, text, quote(txt, pos, len(text)))
    return best


def deck_check(rom, k, lex_index):
    if lex_index is None:
        return '-'
    cards = rom.deck(k)
    if not cards:
        return 'no deck'
    e = LEXICON[lex_index]
    if not e['types'] and not e['attrs']:
        return 'no theme'
    stats = rom.card_stats()
    tc = Counter(TYPES[int(stats[c]['b_0808A30E'])] for c in cards
                 if c in stats and int(stats[c]['b_0808A30E']) < len(TYPES))
    ac = Counter(ATTRS[int(stats[c]['b_08089C04'])] for c in cards
                 if c in stats and int(stats[c]['b_08089C04']) < len(ATTRS))
    hit = max([tc[t] for t in e['types']] + [ac[a] for a in e['attrs']] + [0])
    return '%s (%d/40)' % ('agree' if hit >= 15 else 'differ', hit)


def build(rom):
    sites = find_sites(rom)
    by_duel = {}
    for duel, op, rec in sites:
        by_duel.setdefault(duel, []).append((op, rec))
    rows = []
    for k in range(DUEL_COUNT):
        if k not in by_duel:
            rows.append([k, '', '', 'no #8 opcode', '', '', '', '', '', '', ''])
            continue
        best = None
        for op, rec in sorted(by_duel[k]):
            recs = window(rom, rec)
            pre = recs[0][1][:120] if recs else ''
            got = evidence(rom, recs)
            if got is None:
                if best is None:
                    best = ((9, 9),
                            [k, '', '', 'no name in window', '', '0x%08X' % op, '', '', '',
                             '', pre])
                continue
            key, lex, kind, dist, addr, text, quo = got
            other = sorted({LEXICON[i]['name'] for a, t in recs for i, _, _ in all_names(t)}
                           - {LEXICON[lex]['name']})
            check = deck_check(rom, k, lex)
            # A mention becomes the duel's *name* only when the game corroborates it: the
            # speaker names himself, or the duel's own 40-card deck matches the name's card
            # theme.  Otherwise the name stays blank and the mention is kept in `mention`.
            ok = kind == 'self-intro' or check.startswith('agree')
            row = [k, LEXICON[lex]['name'] if ok else '', CONF[kind] if ok else '',
                   ('%s + deck' % kind) if (ok and kind != 'self-intro') else kind,
                   LEXICON[lex]['name'], '0x%08X' % addr, quo, dist, check, ' '.join(other), pre]
            if k in EXCLUDED and ok:
                row[1], row[2] = '', ''
                row[3] = 'excluded: ' + EXCLUDED[k]
            if best is None or key < best[0]:
                best = (key, row)
        rows.append(best[1])
    return rows, sites


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--scan', action='store_true', help='list every self-introduction found')
    ap.add_argument('--duel', type=int, help='print one duel id window in full')
    ap.add_argument('--out', default=str(OUT_PATH))
    args = ap.parse_args(argv)

    rom = Rom(ROM_PATH.read_bytes(), load_glyphs())

    if args.scan:
        for duel, op, rec in find_sites(rom):
            for addr, txt in window(rom, rec):
                for pat in INTRO:
                    for m in re.finditer(pat, txt):
                        print('duel %3d 0x%08X  %s' % (duel, addr, m.group(0).replace('|', ' ')))
        return 0

    if args.duel is not None:
        for duel, op, rec in find_sites(rom):
            if duel != args.duel:
                continue
            print('duel %d  opcode 0x%08X  record 0x%08X  deck: %s'
                  % (duel, op, rec, ' '.join(str(c) for c in rom.deck(duel)[:12]) or '(none)'))
            for dist, (addr, txt) in enumerate(window(rom, rec)):
                print('   dist=%d 0x%08X  %s' % (dist, addr, txt[:130]))
        return 0

    rows, sites = build(rom)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(HEADER) + '\n')
        for r in rows:
            f.write('\t'.join(str(c) for c in r) + '\n')
    conf = Counter(r[2] for r in rows if r[1])
    basis = Counter(r[3] for r in rows)
    print('duels: %d   sites: %d   duel ids referenced: %d'
          % (DUEL_COUNT, len(sites), len({s[0] for s in sites})))
    print('named: %d of %d  (confidence: %s)' % (
        sum(conf.values()), DUEL_COUNT,
        ', '.join('%s %d' % (c, conf[c]) for c in ('high', 'medium', 'low') if conf[c])))
    print('basis: %s' % ', '.join('%s %d' % kv for kv in sorted(basis.items(),
                                                                key=lambda kv: -kv[1])))
    print('mentions kept without a name: %d' % sum(1 for r in rows if not r[1] and r[4]))
    print('wrote %s' % args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
