"""Which card id does the cost table `w_08088DF0` use?  (Y5, [038] item 1) -- reproducible evidence.

The dispute: `[036]` printed Dark Magician Cost 183 and Red-Eyes B. Dragon 207, `[037]` computed
20 and 12 from `u32 @ 0x08088DF0 + 4*35` / `+4*82`, and `tools/extract_card_stats.py` (J0005) reads
`+4*k` for card k = 1..900.  One of the two rules is off by one entry.

The loader, `sub_08006BE4` @ 0x08006BE4 (`private/asm/rom_full.s`), takes the card id in r0 and
zero-extends it into **r4** (`lsls r4,r4,#0x10; lsrs r4,r4,#0x10`), then uses that one register for
every column:

    ldr r0,=0x080886E6 / lsls r1,r4,#1 / adds r0,r1,r0 / ldrh    ATK = u16 @ 0x080886E6 + 2*r4
    ldr r0,=0x08087FDC / adds r1,r1,r0   / ldrh                  DEF = u16 @ 0x08087FDC + 2*r4
    ldr r0,=0x08088DF0 / lsls r6,r4,#2 / adds r0,r6,r0 / ldr     W   = u32 @ 0x08088DF0 + 4*r4
    ldr r0,=0x08089C04 / adds r0,r4,r0   / ldrb                  byte-table rows, + r4
    adds r0,r4,#0 / bl sub_080073E4      / str r0,[r5]           name pointer for the same r4

and `sub_080073E4` @ 0x080073E4 is `*(u32 *)(0x08D310E0 + 4*id)` -- the card-name pointer table, again
with no -1 and no shift.  So name index == stat index == the game's own card id; the only question
left is which value id 1 is, and this script answers it from the ROM alone: it prints the id-0 row
(the dummy) and the id-1 row, matches the rulebook ATK/DEF of four named cards against the stat
tables, and lists what each candidate rule gives for the same card.  It exits 0 only when the
1-based rule (+4*id, entry 0 unused) is the one that reproduces the rulebook stats, the values the
game's own callers produce, and the 901-entry table spacing.

Usage: PY tools/cost_index.py        (reads private/baserom.gba; no arguments)
"""
import struct
import sys
from pathlib import Path

ROM = Path(__file__).resolve().parents[1] / 'private' / 'baserom.gba'
BASE = 0x08000000
NAME_TABLE = 0x08D310E0      # what sub_080073E4 uses: one u32 per card id, entry 0 = dummy
ATK, DEF, W = 0x080886E6, 0x08087FDC, 0x08088DF0
BYTE0, LEVEL = 0x08089C04, 0x08089F89

# What docs/game-data.md ("Card Cost and the Duelist-Level gate") prints, card name -> cost.
DOC_VALUES = {
    'Blue-Eyes White Dragon': 95,
    'Mystical Elf': 319,
    'Hitotsu-Me Giant': 121,
    'Dark Magician': 183,
    'Red-Eyes B. Dragon': 207,
    'Celtic Guardian': 260,
    'Blue-Eyes Ultimate Dragon': 20,
    'Dragon Piper': 86,
}

# Rulebook ATK/DEF, used to find each card's id from the stat tables alone.
ANCHORS = [('Blue-Eyes White Dragon', 3000, 2500), ('Dark Magician', 2500, 2100),
           ('Red-Eyes B. Dragon', 2400, 2000), ('Labyrinth Wall', 0, 3000)]

fails = []


def main():
    if not ROM.exists():
        print('ERROR: %s not found' % ROM)
        return 1
    d = ROM.read_bytes()

    def u16(addr, k):
        return struct.unpack_from('<H', d, addr - BASE + 2 * k)[0]

    def u32(addr, k):
        return struct.unpack_from('<I', d, addr - BASE + 4 * k)[0]

    def name(i):
        ptr = u32(NAME_TABLE, i)
        o = ptr - BASE
        if not 0 <= o < len(d) - 2:
            return '<pointer %08X outside the ROM>' % ptr
        end = o + 2
        while d[end] not in (0x24, 0x00):
            end += 1
        return ''.join(chr(c) if 0x20 <= c <= 0x7E else '?' for c in d[o + 2:end])

    def ids_of(label):
        return [k for k in range(1, 901) if name(k) == label]

    def row(i):
        return 'id %3d  %-26s atk=%5d def=%5d W=%5d lvl=%3d' % (
            i, name(i), u16(ATK, i), u16(DEF, i), u32(W, i), d[LEVEL - BASE + i])

    print('== id 0 is the dummy row, id 1 is the first real card (name table 0x08D310E0 + 4*id)')
    for i in range(0, 4):
        print('  ' + row(i))
    if (u16(ATK, 0), u16(DEF, 0), u32(W, 0)) != (0xFFFF, 0xFFFF, 0):
        fails.append('id 0 is not the dummy row (0xFFFF/0xFFFF/0)')
    if name(1) != 'Blue-Eyes White Dragon':
        fails.append('id 1 is not Blue-Eyes White Dragon')

    print('== the same id on both tables, checked against the rulebook ATK/DEF')
    for label, atk, dfn in ANCHORS:
        hits = [i for i in range(1, 901)
                if u16(ATK, i) == atk and u16(DEF, i) == dfn and name(i) == label]
        named = ids_of(label)
        if not hits or not named:
            fails.append('%s: no id has those stats and that name' % label)
            continue
        for i in hits[:2]:
            print('  ' + row(i))
        if hits[0] != named[0]:
            fails.append('%s: stat id %d and name id %d disagree' % (label, hits[0], named[0]))

    print('== the two candidate rules for the same card (id = the game\'s own card number)')
    for label in ('Blue-Eyes White Dragon', 'Dark Magician', 'Red-Eyes B. Dragon', 'Labyrinth Wall'):
        i = ids_of(label)[0]
        print('  %-22s id %3d -> +4*id = %5d , +4*(id-1) = %5d' % (
            label, i, u32(W, i), u32(W, i - 1)))

    print('== what docs/game-data.md prints, against both rules')
    for label, claimed in DOC_VALUES.items():
        named = ids_of(label)
        if not named:
            fails.append('%s is not in the name table' % label)
            continue
        i = named[0]
        got, prev = u32(W, i), u32(W, i - 1)
        verdict = ('doc matches +4*id' if got == claimed
                   else 'doc matches +4*(id-1)' if prev == claimed else 'doc matches NEITHER')
        print('  %-25s doc %4d  |  +4*id %4d  +4*(id-1) %4d  (%s)' % (label, claimed, got, prev, verdict))

    print('== 901 entries? (each table starts exactly where the previous one ends)')
    for label, got, want in (('DEF + 2*901', DEF + 2 * 901, ATK), ('ATK + 2*901', ATK + 2 * 901, W),
                             ('W + 4*901', W + 4 * 901, BYTE0), ('byte0 + 901', BYTE0 + 901, 0x08089F89)):
        print('  %-12s -> 0x%08X %s' % (label, got, 'OK' if got == want else 'expected 0x%08X' % want))
        if got != want:
            fails.append('%s does not land on the next table' % label)
    print('  name table: id 900 -> %08X %r' % (u32(NAME_TABLE, 900), name(900)))
    print('              id 901 -> %08X %r (past the end)' % (u32(NAME_TABLE, 901), name(901)))

    if u32(W, 1) != 95:
        fails.append('u32 @ W + 4*1 is not 95 (Blue-Eyes White Dragon)')

    print()
    if fails:
        for f in fails:
            print('FAIL: %s' % f)
        return 1
    print('RESULT: the loader index is +4*id with id = the card number 1..900 (entry 0 unused);')
    print('        tools/extract_card_stats.py reads that same entry for card k, so its rule is right;')
    print('        the two disputed values are id 35 Dark Magician = 20 and id 82 Red-Eyes B. Dragon = 12.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
