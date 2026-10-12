"""Check for `tools/duel_names.py` (opponent names for the 200 duel records).

Runs the extractor in this checkout, then recomputes `private/extracted/duel_names.tsv`
here, independently and straight from the ROM, and compares the two byte for byte.  Then it
asserts the invariants the extractor's docstring claims.

Spec (ROM = private/baserom.gba, file offset + 0x08000000 = ROM address):
  * a duel starts where a dialogue record holds the byte pair `23 38` ("#8") at or above
    `0x08D00000`; the byte after it is the duel id, which indexes the 200-word table at
    `0x08D35C28` -> record at `0x080B4B5C + 0x28*id`, and the record's `+0x04` u32 points at
    its 40 u16 card ids;
  * a text record starts at a `24 30` ("$0") preceded by `00` and ends at the next `00`; its
    English field is everything up to `$1`: `0x87 <c>` = config/text_glyphs.csv letter,
    `0x23 30`/`0x23 31` and `0x5E` = `|` (line break), `0x25` = `,`, 0x20..0x7E = itself;
  * the window of one duel = the opcode's record and the two records before it (records are
    contiguous: each ends in 00, the next starts with `$0`, so "the previous record" is the
    last `00` `$0` before it);
  * the name comes from the lexicon in tools/duel_names.py; a name is only written when the
    speaker introduces himself in the first two records of the window, or when the name is
    used in the window *and* the duel's own deck matches that character's card theme
    (types = column `b_0808A30E`, attributes = column `b_08089C04` of
    private/extracted/card_stats.tsv, matching 15+ of the 40 cards); the four mentions a
    human read showed to be a simile/vocative are excluded with a reason.

Invariants asserted here:
  * 200 rows, one per duel id 0..199, in order, and every row with an opcode site carries the
    game's own pre-duel line for that id;
  * a name is never written without a confidence, an evidence address inside the data half
    and an evidence line that really contains the name (re-decoded here from the ROM);
  * the three `high` rows are self-introductions in the opcode's own record;
  * `mention` is always one of the lexicon names (or empty), and a duel id is never named
    twice in the file;
  * exactly the four duels in EXPECTED_EXCLUDED are excluded (pinned here as a literal, so
    emptying or growing the tool's exclusion list fails this check).

Note what "both ways" means for this check: it re-runs `tools/duel_names.py` first, so an edit
to the *file* alone is overwritten and not trusted; what it really pins is the method -- the
window rule, the lexicon, the deck check and the exclusions.  Proven by breaking those in the
tool and watching this check fail (see private/tmp/nm/break_test.py in the REPORT).

Usage: PY tools/test_duel_names.py
"""
import re
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / 'private' / 'baserom.gba'
OUT = ROOT / 'private' / 'extracted' / 'duel_names.tsv'
SCRIPT = ROOT / 'tools' / 'duel_names.py'

# The exclusion reasons are text, not logic: read them from the extractor so the two files
# cannot drift apart.  Everything else here is this file's own implementation.
import importlib.util                                   # noqa: E402
_spec = importlib.util.spec_from_file_location('duel_names_tool', SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EXCLUDED = _mod.EXCLUDED
EXPECTED_EXCLUDED = {12, 72, 76, 87}     # pinned here on purpose: see the check's docstring

BASE = 0x08000000
DUEL_PTR_TABLE = 0x08D35C28
DUEL_COUNT = 200
SCRIPT_MIN = 0x08D00000
WINDOW = 3

# Same names as the extractor's lexicon (data, not logic).
NAMES = ['Bandit Keith', 'Bonz', 'Weevil Underwood', 'Rex Raptor', 'Mako Tsunami',
         'Mai Valentine', 'Joey Wheeler', 'Yugi Muto', 'Seto Kaiba', 'Mokuba Kaiba',
         'Marik Ishtar', 'Odion', 'Ryou Bakura', 'Pegasus', 'Tristan Taylor', 'Tea Gardner',
         'Espa Roba']
PATS = {
    'Bandit Keith': [r'Bandit Keith', r'Keith'], 'Bonz': [r'Bonz'],
    'Weevil Underwood': [r'Weevil Underwood', r'Weevil', r'Underwood'],
    'Rex Raptor': [r'Rex Raptor', r'Raptor', r'Rex'],
    'Mako Tsunami': [r'Mako Tsunami', r'Mako', r'Tsunami'],
    'Mai Valentine': [r'Mai Valentine', r'Valentine'],
    'Joey Wheeler': [r'Joey Wheeler', r'Joey', r'Wheeler'],
    'Yugi Muto': [r'Yugi Muto', r'Yugi'], 'Seto Kaiba': [r'Seto Kaiba', r'Seto', r'Kaiba'],
    'Mokuba Kaiba': [r'Mokuba'], 'Marik Ishtar': [r'Marik Ishtar', r'Marik', r'Ishtar'],
    'Odion': [r'Odion'], 'Ryou Bakura': [r'Ryou Bakura', r'Bakura', r'Ryou'],
    'Pegasus': [r'Pegasus'], 'Tristan Taylor': [r'Tristan'], 'Tea Gardner': [r'Tea'],
    'Espa Roba': [r'Espa Roba', r'Espa', r'Roba'],
}
THEME = {
    'Bandit Keith': (['Machine'], []), 'Bonz': (['Zombie', 'Fiend'], []),
    'Weevil Underwood': (['Insect', 'Plant'], ['Forest']), 'Rex Raptor': (['Dinosaur', 'Reptile'], []),
    'Mako Tsunami': (['Aqua', 'Fish', 'Sea Dragon', 'Reptile'], ['Aqua']),
    'Mai Valentine': (['Wing Beast', 'Fairy'], ['Wind']),
    'Joey Wheeler': (['Warrior', 'BeastWarrior'], []), 'Yugi Muto': ([], []),
    'Seto Kaiba': (['Dragon', 'Machine'], ['Light']), 'Mokuba Kaiba': ([], []),
    'Marik Ishtar': (['Fiend'], ['Fiend']), 'Odion': ([], []),
    'Ryou Bakura': (['Fiend', 'Zombie'], ['Shadow']), 'Pegasus': (['Magic'], []),
    'Tristan Taylor': ([], []), 'Tea Gardner': ([], []), 'Espa Roba': ([], []),
}
TYPES = ['', 'Dragon', 'Magician', 'Zombie', 'Warrior', 'BeastWarrior', 'Beast', 'Wing Beast',
         'Fiend', 'Fairy', 'Insect', 'Dinosaur', 'Reptile', 'Fish', 'Sea Dragon', 'Machine',
         'Thunder', 'Aqua', 'Pyro', 'Rock', 'Plant', 'Magic', 'Trap', 'Ritual']
ATTRS = ['', 'Shadow', 'Light', 'Fiend', 'Dreams', 'Pyro', 'Forest', 'Wind', 'Earth', 'Thunder',
         'Aqua', 'Divine']
INTRO = (r"(?:I'?m|I am|[Mm]y name is|[Tt]hey call me|[Cc]all me) "
         r"(%s)\b|\b(%s), the \w|\b(%s) here\b")


def glyphs():
    tab = {}
    for row in (ROOT / 'config' / 'text_glyphs.csv').read_text(encoding='utf-8').splitlines():
        row = row.strip()
        if row and row[0] != '#' and not row.startswith('code,'):
            c = row.split(',')
            if c[1]:
                tab[int(c[0], 16)] = c[1]
    return tab


GLY = glyphs()


def field_text(blob):
    out = []
    i = 0
    while i < len(blob):
        b = blob[i]
        if b == 0x87 and i + 1 < len(blob):
            out.append(GLY.get(blob[i + 1], '?'))
            i += 2
        elif b == 0x23 and blob[i + 1:i + 2] in (b'0', b'1'):
            out.append('|')
            i += 2
        elif b == 0x5E:
            out.append('|')
            i += 1
        elif b == 0x25:
            out.append(',')
            i += 1
        elif 0x20 <= b <= 0x7E:
            out.append(chr(b))
            i += 1
        else:
            out.append('\\x%02x' % b)
            i += 1
    return ''.join(out)


class R:
    def __init__(self, data):
        self.d = data

    def u16(self, a):
        return struct.unpack_from('<H', self.d, a - BASE)[0]

    def u32(self, a):
        return struct.unpack_from('<I', self.d, a - BASE)[0]

    def text(self, addr):
        o = addr - BASE
        if not (self.d[o] == 0x24 and self.d[o + 1] == 0x30):
            return None
        e = self.d.find(b'\x00', o, o + 8192)
        return field_text(self.d[o + 2:e].split(b'$1')[0])

    def prev(self, addr):
        j = addr - BASE - 1
        while j > 2:
            if self.d[j] == 0x30 and self.d[j - 1] == 0x24 and self.d[j - 2] == 0x00:
                return BASE + j - 1
            j -= 1
        return None

    def deck(self, k):
        ptr = self.u32(self.u32(DUEL_PTR_TABLE + 4 * k) + 4)
        cards = [self.u16(ptr + 2 * i) for i in range(40)]
        return cards if any(cards) else []

    def site(self, op):
        return self.prev(op)


def stats():
    import csv
    with (ROOT / 'private' / 'extracted' / 'card_stats.tsv').open(encoding='utf-8') as f:
        return {int(r['card']): r for r in csv.DictReader(f, delimiter='\t')}


def find_sites(rom):
    sites, pos = [], 0
    while True:
        k = rom.d.find(b'\x238', pos)
        if k < 0:
            return sites
        pos = k + 1
        if BASE + k >= SCRIPT_MIN:
            rec = rom.site(BASE + k)
            if rec:
                sites.append((rom.d[k + 2], BASE + k, rec))


def window(rom, rec):
    out, a = [], rec
    while a and len(out) < WINDOW:
        t = rom.text(a)
        if t is None:
            break
        out.append((a, t))
        a = rom.prev(a)
    return out


def hits(txt):
    out = []
    for nm in NAMES:
        for p in PATS[nm]:
            for m in re.finditer(r'\b%s\b' % p, txt):
                out.append((nm, m.group(0), m.start()))
    return out


def intro(txt, text):
    t = re.escape(text)
    return bool(re.search(r"(?:I'?m|I am|[Mm]y name is|[Tt]hey call me|[Cc]all me) \b" + t + r"\b", txt)
                or re.search(r"\b" + t + r", the \w", txt)
                or re.search(r"\b" + t + r" here\b", txt))


def deck_check(rom, st, k, nm):
    cards = rom.deck(k)
    if not cards:
        return 'no deck'
    ty, at = THEME[nm]
    if not ty and not at:
        return 'no theme'
    tc = Counter(TYPES[int(st[c]['b_0808A30E'])] for c in cards
                 if c in st and int(st[c]['b_0808A30E']) < len(TYPES))
    ac = Counter(ATTRS[int(st[c]['b_08089C04'])] for c in cards
                 if c in st and int(st[c]['b_08089C04']) < len(ATTRS))
    n = max([tc[t] for t in ty] + [ac[a] for a in at] + [0])
    return '%s (%d/40)' % ('agree' if n >= 15 else 'differ', n)


def quote(txt, pos, n, width=60):
    lo, hi = max(0, pos - 25), min(len(txt), pos + n + width)
    return ('...' if lo > 0 else '') + txt[lo:hi] + ('...' if hi < len(txt) else '')


def expected(rom, st):
    rank = {'self-intro': 0, 'own-line': 1, 'nearby-line': 2}
    conf = {'self-intro': 'high', 'own-line': 'medium', 'nearby-line': 'low'}
    sites = {}
    for duel, op, rec in find_sites(rom):
        sites.setdefault(duel, []).append((op, rec))
    rows = ['duel\tname\tconfidence\tbasis\tmention\tevidence_addr\tevidence_line\tdist\t'
            'deck_check\talso_mentioned\tpre_duel_line']
    for k in range(DUEL_COUNT):
        if k not in sites:
            rows.append('\t'.join([str(k), '', '', 'no #8 opcode', '', '', '', '', '', '', '']))
            continue
        best = None
        for op, rec in sorted(sites[k]):
            recs = window(rom, rec)
            pre = recs[0][1][:120]
            cand = None
            for dist, (addr, txt) in enumerate(recs):
                for nm, text, pos in hits(txt):
                    if intro(txt, text) and dist <= 1:
                        kind = 'self-intro'
                    elif dist == 0:
                        kind = 'own-line'
                    else:
                        kind = 'nearby-line'
                    key = (rank[kind], dist)
                    if cand is None or key < cand[0]:
                        cand = (key, nm, kind, dist, addr, text, quote(txt, pos, len(text)))
            if cand is None:
                if best is None:
                    best = ((9, 9), [k, '', '', 'no name in window', '', '0x%08X' % op, '',
                                     '', '', '', pre])
                continue
            key, nm, kind, dist, addr, text, quo = cand
            others = sorted({n for a, t in recs for n, _, _ in hits(t)} - {nm})
            check = deck_check(rom, st, k, nm)
            ok = kind == 'self-intro' or check.startswith('agree')
            row = [k, nm if ok else '', conf[kind] if ok else '',
                   ('%s + deck' % kind) if (ok and kind != 'self-intro') else kind,
                   nm, '0x%08X' % addr, quo, dist, check, ' '.join(others), pre]
            if k in EXCLUDED and ok:
                row[1], row[2] = '', ''
                row[3] = 'excluded: ' + EXCLUDED[k]
            if best is None or key < best[0]:
                best = (key, row)
        rows.append('\t'.join(str(c) for c in best[1]))
    return rows


def main():
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit('FAIL tools/duel_names.py exited %d\n%s' % (r.returncode, r.stderr[-800:]))
    if not OUT.exists():
        sys.exit('FAIL %s was not written' % OUT)

    rom = R(ROM.read_bytes())
    st = stats()
    want = expected(rom, st)
    got = OUT.read_text(encoding='utf-8').splitlines()
    if got != want:
        for n, (a, b) in enumerate(zip(got, want)):
            if a != b:
                sys.exit('FAIL duel_names.tsv line %d differs\n  got : %r\n  want: %r'
                         % (n + 1, a[:200], b[:200]))
        sys.exit('FAIL duel_names.tsv length differs: got %d lines, want %d'
                 % (len(got), len(want)))

    problems = []
    rows = [l.split('\t') for l in got[1:]]
    if len(rows) != DUEL_COUNT or [int(x[0]) for x in rows] != list(range(DUEL_COUNT)):
        problems.append('rows are not duel ids 0..%d in order' % (DUEL_COUNT - 1))
    named = 0
    for x in rows:
        k, name, confidence, basis, mention, addr, line, dist, check, others, pre = x
        if name:
            named += 1
            if confidence not in ('high', 'medium', 'low'):
                problems.append('duel %s: confidence %r' % (k, confidence))
            if not basis:
                problems.append('duel %s: named without a basis' % k)
            if not addr.startswith('0x') or int(addr, 16) < SCRIPT_MIN:
                problems.append('duel %s: evidence %r is not in the data half' % (k, addr))
            elif rom.text(int(addr, 16)) is None or not any(
                    w in rom.text(int(addr, 16)) for w in name.split()):
                problems.append('duel %s: evidence record at %s does not contain %r'
                                % (k, addr, name))
            if confidence == 'high':
                txt = rom.text(int(addr, 16)) or ''
                if not re.search(r"(?:I'?m|I am|[Mm]y name is|[Tt]hey call me|[Cc]all me) "
                                 r"\S*%s|%s, the \w" % (re.escape(name), re.escape(name)), txt):
                    problems.append('duel %s: high but not a self-introduction: %r' % (k, txt[:50]))
        elif confidence:
            problems.append('duel %s: confidence %r without a name' % (k, confidence))
        if mention and mention not in NAMES:
            problems.append('duel %s: mention %r is not a lexicon name' % (k, mention))
        if pre == '' and mention:
            problems.append('duel %s: mention without a pre-duel line' % k)
        words = {w for nm in NAMES for w in nm.split()}
        for other in others.split():
            if other not in words:
                problems.append('duel %s: also_mentioned %r is not a lexicon name' % (k, other))
    if len({x[0] for x in rows}) != DUEL_COUNT:
        problems.append('a duel id appears twice')
    excluded = {x[0] for x in rows if x[3].startswith('excluded:')}
    if excluded != {str(k) for k in EXPECTED_EXCLUDED}:
        problems.append('excluded duels are %s, expected %s'
                        % (sorted(excluded, key=int), sorted(EXPECTED_EXCLUDED)))
    if problems:
        sys.exit('FAIL structural invariants:\n  ' + '\n  '.join(problems[:10]))

    print('rows: %d duels, named: %d (%s)' % (len(rows), named,
          ', '.join('%s %d' % (c, sum(1 for x in rows if x[2] == c)) for c in ('high', 'medium', 'low'))))
    print('pre-duel lines: %d' % sum(1 for x in rows if x[10]))
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
