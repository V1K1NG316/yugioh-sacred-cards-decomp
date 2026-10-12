# Game data (milestone Y4)

Verified facts about where the game keeps its data. Extractors live in `tools/`, their output in `private/extracted/`.

## Card names (found by Claude, 2026-10-12)
- **Pointer table**: 900 little-endian words at `0x08D310E4`..`0x08D31EF4`. Entry k → card number k+1
  (1 = Blue-Eyes White Dragon, 2 = Mystical Elf, 3 = Hitotsu-Me Giant, 900 = "7 Completed").
- **Record**: `$0<English>$1<French>$2<German>$3<Italian>$4<Spanish>$5<Japanese>` then `00`.
  Japanese is Shift-JIS. In the European names an accented letter is `0x87` + a letter
  (seen: `87 61` = é in "Géant"/"terminées", `87 5F` = ä in "Blauäugiger", `87 65` = í in "místico").
  Unverified: the full `0x87` table.
- Cards 584–587 ("Spirit Message I/N/A/L") use Shift-JIS `81 68` (”) as quote marks inside the English name.
- The word just before the table (`0x080A6838`) points to a Shift-JIS string, not a `$0` record: not part of it.
- Extractor: `tools/extract_card_names.py` (job J0004) → `private/extracted/card_names.tsv`;
  check `tools/test_card_names.py`.

## Card properties (found by Claude, 2026-10-12)
Parallel arrays indexed by card number (0..900; entry 0 is a dummy). Base addresses are loaded together from the
literal pool at `0x08006C70`..`0x08006C98` (DEF base also at `0x080208F8` and 4 more places).
| address | type | meaning |
|---|---|---|
| `0x08087FDC` | u16[901] | DEF (spell/trap = 65535) |
| `0x080886E6` | u16[901] | ATK (spell/trap = 65535) |
| `0x08088DF0` | u32[901] | unknown (BEWD 95, Mystical Elf 319) |
| `0x08089C04` + 901·i, i=0..7 | u8[901] each | i=1 (`0x08089F89`) = **level**; others unknown |
Verified against known cards: 1 BEWD 3000/2500 L8, 4 Baby Dragon 1200/700 L3, 22 Summoned Skull 2500/1200,
35 Dark Magician 2500/2100, 41 Celtic Guardian 1400/1200, 46 Griffore 1200/1500, 82 Red-Eyes B. Dragon 2400/2000.
In names, `%` stands for a comma ("Winged Dragon% Guardian of the Fortress #1").
Extractor: `tools/extract_card_stats.py` (job J0005) → `private/extracted/card_stats.tsv`; check `tools/test_card_stats.py`.

## Other leads (unverified)
- THUMB→ARM thunks (`add rX, pc, #imm; bx rX`) in the code region: `0x08036C70`→`0x08036C74`,
  `0x08036D0A`→`0x08036D10`, `0x08036E96`→`0x08036E9C`. The last two ARM targets may be missing from the census.
