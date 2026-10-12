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

## Compression (verified, DeepSeek 2026-10-12)
The game calls the BIOS directly through one-instruction wrappers, and the whole disassembly
(`private/asm/rom_full.s`, 211 294 bytes of code) holds only **four `svc` instructions**:
| wrapper | instruction | call sites | purpose |
|---|---|---|---|
| `sub_08036934` | `svc 0x11` LZ77UnCompWram | 27 in 19 functions | **LZ77 decompression of assets** |
| `sub_08036930` | `svc 0x13` HuffUnComp | 4 in 4 (`sub_08009100`, `sub_08009118`, `sub_08024980`, `sub_08028018`) | Huffman, 4 places |
| `sub_0803692C` | `svc 0x0B` CpuSet | 336 in 143 | memory copy |
| `sub_08036928` | `svc 0x0C` CpuFastSet | 4 in 4 | memory fill/copy |
No call to RLE (`0x14`/`0x15`), BitUnPack (`0x10`) or the diff filters (`0x16`–`0x18`) exists anywhere, and no
custom decompressor was found: **LZ77 + Huffman is the whole compression story** (leads still open: what the 4
Huffman call sites decompress — the blobs themselves have not been scanned for yet).

Following the `r0` argument back from the 27 LZ77 call sites resolves 20 distinct source pointers, e.g.
`0x0803C44C` (16384 out), `0x08056D28` (49152 out), `0x0807F458` (16384 out, 3 sites) — but most assets are
loaded through *tables*, not one-site-per-blob: `0x082B26AC` (a 3616-byte blob) is the source at 4 sites and
`0x08D536F0` (the 900-word table itself) at 2.

**LZ77 inventory** (scan of the whole ROM for a `0x10` + 24-bit-size header that decompresses to exactly that
many bytes; rule and caveats in A10): **1084 blobs, 3 398 277 bytes out from 2 381 036 bytes in**; 972 of them
are pointed at by a ROM word, 112 are not. Families:
| declared size | count | pointed | where / what |
|---|---|---|---|
| 576 B | 909 | 901 | `0x0894E4B4`..`0x08E9E6F0`, pointed at by the **900-word table at `0x08D536F0`** (one per card) |
| 44 544 B | 58 | 58 | `0x082B3088`..`0x0848CF78`, table at `0x08D514D0` (58 words) |
| 16 384 B | 7 | 6 | code-block graphics, referenced from literal pools (`0x08000330`, `0x08000634`, …) |
| 24 576 / 32 768 / 49 152 B | 2 / 2 / 1 | 2 / 2 / 1 | same |
| 4096 / 3616 B | 1 / 1 | 1 / 1 | same |
| ≤ 72 B | 102 | 0 | smaller than any real asset and unreferenced — coincidences inside data (A10) |
The 9 unreferenced 576-byte blobs are inside the card-picture region (`0x0899BFEC`..`0x089C03F8`), so they are
probably reached by arithmetic (`table + k`), not by their own word. The 576-byte per-card blobs decompress to
**binary** (card 1 and card 900 both start with long zero runs), so they are per-card pictures, not text.
Extractor: `tools/find_lz77.py` (job `lz77_extract`, recipe `private/jobs/drafts/lz77_extract.md`), check
`tools/test_lz77.py`.

## Text (verified + one open lead)
Record shape everywhere: `$0<English>$1<French>$2<German>$3<Italian>$4<Spanish>$5<Japanese>` + `00`
(card records at `0x08D419E0`/`0x08D4BC3C` add a `$6`). Inside a record: `%` = comma, `#0` = line break in
duel messages, `^` = line break in card descriptions, `0x87 <code>` = one accented letter (table below).
`0x08D36130` is untranslated: all five Western fields hold the same English text.

Whole-ROM pointer-table map (`tools/find_text_tables.py`, job `text_table_map`, output
`private/extracted/text_table_map.tsv`; rule in A11) — **15 tables**, the largest:
| table | entries | contents |
|---|---|---|
| `0x08D310E4` | 900 | card names |
| `0x08D30310` | 140 | credits (`Original character design`, `Original monster design`) |
| `0x08D36130` | 124 | duel messages (`It's #5's turn.`, `Duel victory!`, `Lost the duel...`) |
| `0x08D4BC3C` | 24 | card-type names (`Dragon`, `Magician`, `Zombie`) |
| `0x08D419E0` | 12 | attribute names (`Light`, `Shadow`, `Fiend`) |
| `0x08DFC508` / `0x08DFCA80` / `0x08DFCC88` / `0x08DFCDEC` / `0x08DFCE3C` | 50/49/10/8/11 | effect/duel message texts (`#2#0was activated.#1…`) |
Extractor for the middle four: `tools/extract_text_tables.py` (job `text_tables`), check `tools/test_text_tables.py`.

**Card descriptions are indexed by card number — found** (2026-10-12, Y4 part 2). Cards are numbered 1..900 and
the description index is the **900-word pointer table at `0x08E94E7C`** (entry `k` = card `k+1`; records run in
card order, the table ends at `0x08E95C8C` followed by `0xFFFFFFFF`). The descriptions are uncompressed `$0`…`$5`
records in `0x08DFCE68`..`0x08E94E75` — the first record starts exactly where the 901-word table at `0x08DFC054`
ends. `0x08DE6578`..`0x08DFBF2E`, which *that* table points at, holds **duel-time effect messages**, not
descriptions.

The game's reader is the card-database loader `sub_08006BE4` (it fills the card struct at `0x02020B00`); the
description text pointer is stored at struct `+8`:
```asm
0x08006C88  bl sub_08014110        @ r0 = Duelist Level
0x08006C8C  ldr r1, [r5, #0xc]     @ r1 = card cost, word at 0x08088DF0 + 4*cardId
0x08006C90  cmp r1, r0
0x08006C92  bls 0x08006CA0         @ cost <= Duelist Level -> the real description
0x08006C94  ldr r0, =0x08D30F40    @ else: "Your Duelist Level is below the Cost. This can't be put in the Deck."
...
0x08006CA0  ldr r0, =0x08E94E78    @ the description table, 4 bytes low
0x08006CA4  adds r0, r6, r0        @ r6 = 4 * cardId
0x08006CA6  ldr r0, [r0]
0x08006CA8  str r0, [r5, #8]
```
**Card ids are 1-based**: the literal sits 4 bytes *below* the table (`0x08E94E78` = `0x08E94E7C` - 4), exactly the
trick the name reader `sub_080073E4` uses for the name table (`0x08D310E0` for `0x08D310E4`). The word at
`0x08E94E78` is `0x08D2A6E4`, a per-card byte array — not a text record — so id 0 means "no card" and is never
looked up. Whole-ROM read counts: exactly **one** word equals `0x08DFC054` (the literal pool at `0x08024F90`, the
only reader being `sub_08024F64`, an effect-message renderer) and exactly one equals `0x08E94E78` (pool at
`0x08006CB0`). The earlier "loaded at 2 sites" was wrong.

Record layout: `81 40` + `$0`…`$5` + `00 00`. Latin fields are padded to the record's own fixed width (126 / 132 /
112 bytes for cards 1 / 2 / 3), the Japanese `$5` field is raw Shift-JIS (~2 bytes per character), and every Latin
field has the shape `^2<line 1>^<line 2>^` — in 4505 of the 4506 fields the leading `^2` is present, and the `2`
is a constant, not a line number (A13). Card 1 (`0x08DFCE68`), raw decoded:
```
$0^2A legendary dragon that   takes pride inits enormous  power.      ^Its powers  of destructionfar exceed    comprehension.^
```

**Checked against the game's own data** (C1, Y4 part 2) — card number → decoded English description:
| # | name | description (padding collapsed for reading) |
|---|---|---|
| 1 | Blue-Eyes White Dragon | A legendary dragon that takes pride in its enormous power. Its powers of destruction far exceed comprehension. |
| 2 | Mystical Elf | An elf with blue skin, yellow hair, and light of element. It can powerup Blue-Eyes White Dragons on the own field. |
| 35 | Dark Magician | A sinister spell caster that possesses both power and defense. It is among the best of all magicians. |
| 58 | Kuriboh | A small and furry fiend that is not much of a threat. However, it can be a pain if they appear in numbers in darkness. |
| 82 | Red-Eyes B. Dragon | A sinister black dragon with eyes that shine a deep scarlet. It furiously … |
| 866 | Blue-Eyes Ultimate Dragon | The ultimate of all dragons that has three awe-inspiring heads … |
The tools keep the ROM's padding spaces; only this table collapses them. Two further confirmations that the index
is right: cards 30..40 line up name-for-name with their description (Zombie Warrior → "A skeletal warrior … with a
sword and shield", Dark Magician → "A sinister spell caster …", Gaia the Dragon Champion → "A powerful knight that
sits astride its dragon steer"), and card 2's description effect line matches `word[0x08DFC054 + 4*2]` = "…on the
own field will be powered up". Five names exist twice in the 900 slots (Blue-Eyes White Dragon, Dark Magician,
Red-Eyes B. Dragon, Blue-Eyes Ultimate Dragon, Red-Eyes Black Metal Dragon — the promo reprints); each slot has its
own name record and its own description text, so the mapping is per *slot*, not per name.

Decoder / extractor: `tools/decode_text.py` (job `decode_text`) decodes any record address, six languages;
`tools/extract_card_descriptions.py` (job `card_descriptions`) writes card number → name → description to
`private/extracted/card_descriptions.tsv` (900 lines, 152 373 bytes). Glyph table `config/text_glyphs.csv`;
checks `tools/test_decode_text.py`, `tools/test_card_descriptions.py`.

## `0x87` accented letters (verified, DeepSeek 2026-10-12; re-swept 2026-10-12 Y4 part 2)
Two bytes: `0x87` then a code byte, rendering one accented letter. The code byte is a look-alike letter, so the
table is a lookup, not a formula. Verified by reading the byte pairs in known words of the 900 card names (each
code below is quoted with the word it was read from). The sweep over the Latin fields (`$0`…`$4`, i.e. everything
before the `$5` marker) of all 900 name records finds exactly **28 codes**; the same byte values inside `$5` are
not escapes at all, they are Shift-JIS lead/second bytes. The machine-readable copy of this table is
`config/text_glyphs.csv` (27 codes with a letter, `0x64` without), consumed by `tools/decode_text.py`.
| code | letter | evidence |
|---|---|---|
| `0x54` `0x56` `0x58` `0x59` | Ö Ú Ü ß | `Ödland`, `Último día`, `Übersinnlicher`, `Großer Weißer` |
| `0x5A` `0x5B` `0x5C` | à á â | `Oscurità`, `Lutin à corne`, `Cráneo`, `Crâne` |
| `0x5F` `0x60` `0x61` `0x62` | ä è é ê | `Blauäugiger`, `ténèbres`, `Géant`, `Tête` |
| `0x65` `0x66` `0x67` `0x68` | í î ï ñ | `místico`, `Chaîne`, `humanoïde`, `montaña` |
| `0x6A` `0x6B` `0x6D` | ó ô ö | `Dragón`, `fantômes`, `Zweiköpfiger` |
| `0x6F` `0x70` `0x71` `0x73` | ú û ü ç | `Músico`, `envoûtante`, `Geflügelter`, `Garçon` |
| `0x74` `0x75` | Œ œ | `Gros Œil`, `Œil de feu`; `Bœuf de combat`, `Changement de cœur` |
`0x61` is also used for the capital `É` (`Garçon-Étoile`). The capitals, with the count the sweep gives:
`0x43` Á (2 words: `Águila de ala`, `Árbol antiguo`), `0x48` É (23, e.g. `Baron de l'Épée infernale`,
`Masque de l'Éclat et de la Nuit`), `0x4C` Í (**1**: `Ídolo mil ojos`). Unknown: `0x64` (`Ultimo D?d della
Strega`, Italian). Three codes appear for a second letter that is certainly a typo in the game's own text:
`0x56` for í in `día`, `0x6B` for é in `météo` (`mêtaêo`). The codes `0x82`/`0x83`/`0x89`/`0x90` never occur
in the Latin fields: everything inside a `$5` field is raw Shift-JIS, so those bytes are not escapes at all.

## Other leads (unverified)
- THUMB→ARM thunks (`add rX, pc, #imm; bx rX`) in the code region: `0x08036C70`→`0x08036C74`,
  `0x08036D0A`→`0x08036D10`, `0x08036E96`→`0x08036E9C`. The last two ARM targets may be missing from the census.
