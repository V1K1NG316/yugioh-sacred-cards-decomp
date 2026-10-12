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
| `0x08089C04` + 901·i, i=0..7 | u8[901] each | i=1 (`0x08089F89`) = **level**; i=0 = **attribute**, i=2 = **card type**; i=3..6 named in §"Card property columns"; i=7 (`0x0808B4A7`) is *not* per-card data, it is a lookup table addressed by i=5 |
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

## Card property columns, named (DeepSeek 2026-10-12, Y4 part 3)
The loader `sub_08006BE4` copies every column of `card_stats.tsv` into the card struct at `0x02020B00`, so
column = struct field. Two fields are named by the *code that prints them*: `sub_08007380` loads struct `+0x16`
and calls the 24-name getter `sub_0802319C` (`0x08D4BC3C`: Dragon, Magician, Zombie, …, Magic, Trap, Ritual),
and `sub_080073A8` loads struct `+0x17` and calls the 12-name getter `sub_0801A624` (`0x08D419E0`: Shadow,
Light, Fiend, Dreams, Pyro, Forest, Wind, Earth, Thunder, Aqua, Divine). Values: type 1..23 (`+0x16`), attribute
0..11 (`+0x17`), level 1..12 (`+0x18`).
| `card_stats.tsv` column | struct | meaning | evidence |
|---|---|---|---|
| `w_08088DF0` | `+0x0c` | cost (Duelist Level the card needs) | loader compares it with `sub_08014110` (Duelist Level) to pick the real description |
| `b_08089C04` | `+0x17` | **attribute** index into the 12-name table `0x08D419E0` | `sub_080073A8` -> `sub_0801A624`; values 0..11 |
| `b_08089F89` | `+0x18` | level | `sub_08006BE4` (`strb` to `+0x18`); BEWD 8, Kuriboh 1 |
| `b_0808A30E` | `+0x16` | **card type** index into the 24-name table `0x08D4BC3C` | `sub_08007380` -> `sub_0802319C`; values 1..23 |
| `b_0808A693` | `+0x19` | card-frame graphics id (0..8) | the picture loader `sub_08034AF8`/`sub_080351A4` uses it to pick one of 10 frame graphics (see below); 3 = every Magic card, 4 = every Trap, 5 = every Ritual |
| `b_0808AA18` | `+0x1b` | optional unique-effect routine id, `0` = none | nonzero for 79 of 900 cards - among them card 2 Mystical Elf, whose own description says it powers up Blue-Eyes White Dragon; the card screens store it to `0x0201CB3C`, index the **code**-pointer tables `0x08D353A0` / `0x080FB79C` and tail-call through the `bx r0` stub `sub_08038E24` |
| `b_0808AD9D` | `+0x1a` | effect/script id | `2` for all 773 monsters, otherwise one value per non-monster card (Magic 3..125, Ritual 65..113, Trap 55..131, 127 distinct); the card screens store it to `0x0201CB34` and index the code-pointer table `0x08D34B80` |
| `b_0808B122` | `+0x1c` | per-trap id | nonzero for exactly the 19 Trap cards (values 1..19, all different); `sub_0802AB2C` runs `sub_08028308` only when it is nonzero |
| `b_0808B4A7` | `+0x1d` | **not a per-card column**: a lookup table indexed by `+0x1a` | the loader does `ldrb r0,[+0x1a]; ldrb r0,[0x0808B4A7 + r0]; strb r0,[+0x1d]`; `sub_0800BB9C` then does `ldrb r4,[struct+0x1d]; lsls r4,#3; ldrh r0,[0x08D3632A + 8*r4]` and loads the card id it finds there |
Checked against famous cards (C1): the type column matches the real type in **11 of 11** - 1 BEWD 1=Dragon,
2 Mystical Elf 2=Magician, 3 Hitotsu-Me Giant 5=BeastWarrior, 4 Baby Dragon 1=Dragon, 22 Summoned Skull 8=Fiend,
35 Dark Magician 2=Magician, 41 Celtic Guardian 4=Warrior, 46 Griffore 6=Beast, 58 Kuriboh 8=Fiend,
82 Red-Eyes B. Dragon 1=Dragon, 866 Blue-Eyes Ultimate Dragon 1=Dragon. The attribute column is the game's own
scheme, *not* the TCG attribute: it agrees with the TCG for Light cards (BEWD, Mystical Elf both 2=Light) and
Dark ones (Dark Magician, Kuriboh 1=Shadow) but calls Celtic Guardian "Light" (TCG: Earth), Griffore "Forest",
Baby Dragon "Earth", Red-Eyes and Summoned Skull "Fiend" (A15).

## Card pictures (DeepSeek 2026-10-12; format **ground-truthed in mGBA**, Y4 part 4)
* **Pointer table `0x08D536F0`, 901 words, entry n = card n** (1-based; entry 0 points to an all-zero picture and
  is never used). The loader reads `u32[0x08D536F0 + 4*cardId]` with its 1-based card id and does *not* use the
  "-4" trick of the name/description readers, which is why the table carries the extra word; word 901 is outside
  the table. Consistent with the LZ77 census: 901 of the 576-byte blobs are pointed at by a ROM word.
* Each entry is BIOS **LZ77** (`0x10` + 24-bit size) decompressing to exactly **576 bytes**. **Verified in the
  emulator**: `sub_08034AF8` decompresses card 1 / card 2 into `0x02018800`, and the 576 bytes there are
  byte-for-byte the Python LZ77 decode (`scripts/emu_anchors.py` re-checks it; SHA-256 in
  `tools/test_card_images.py`).
* Those 576 bytes are **8 bits per pixel** palette indices in **8x8-pixel tiles of 64 bytes**, nine tiles in
  **row-major** order = **24x24 pixels** (`tile = (y//8)*3 + (x//8)`, byte `(y%8)*8 + (x%8)`). 864 of 900 pictures
  use one background index (`0x9f`) and carry a 1-pixel `0x9f` border on all four sides.
* **Card frames**: `struct[+0x19]` picks one of the 10 pointers at `0x08D536C8` -> `0x0894BCB4 + k*0x400`,
  1024 bytes each = 16 tiles = **32x32, same 8bpp tile format** (row-major, 4 tiles per row); entries 0..8 are the
  *same* frame with three palette indices remapped (204 byte substitutions: `0x07`->`0x1D` etc.), entry 9 is all
  zeros. Index 0 renders as a 2-pixel black border with a 1-pixel `0x9f` + frame-colour inner line - a card frame.
  The frame id comes from the byte table `0x0808A693`, entry n = card n (card 1 -> 0, card 2 -> 1, card 35 -> 0,
  card 866 -> 5); check it with `PY scripts/emu_anchors.py`.
* **The card image the game builds (`sub_08034AF8` -> `sub_08034B40`), measured in mGBA**: a **32x32, 8bpp** image,
  8x8 tiles of 64 B, row-major, that is the **frame asset with the 24x24 art pasted into a window at (4,2)**
  (4-pixel margins left/right, 2 above, 6 below). 576 art bytes + 448 frame bytes = 1024 = one 32x32 8bpp tile
  image exactly. The frame's own border pixels prove the window: every composed byte outside (4,2)..(27,25) equals
  the frame asset, 448 of 448, for cards 1 and 2.
* **Where it goes**: the caller (`sub_08034684`) passes `0x02010400 + table[slot]*32` as the destination; the
  routine writes image byte `i` at destination byte **`i + 768*(i//256)`** - i.e. the destination is a screen tile
  buffer whose tile rows are **768 bytes (12 tiles)** apart and the card's 4 tiles sit at the start of four
  consecutive rows. Measured by calling `sub_08034B40` with pattern sources (one 4-byte chunk index per chunk) and
  reading back which chunk landed where: 144 picture chunks + 112 frame chunks = exactly 1024 bytes written.
* **Palette: the BGR555 table at `0x089C54B0`** (512 bytes for the first 256 colours; entries `0xa6`..`0xff` are
  zero, which fits the art, whose indices stop at `0x9f`). The card screen's own code confirms the address: the
  routine at `0x08028130` does `CpuFastSet(0x089C54B0 -> 0x02000200, 160 words = 640 bytes)` (SWI `0x0B`)
  before it fills its 5 card slots. (Correction to Y4 part 3: `sub_08034658`/`sub_0803466C` are *that same*
  CpuFastSet wrapper - they copy 160 **words** from `0x089C54B0` to a destination the caller passes in `r0`; they
  do not write palette RAM themselves, and calling `sub_08034658` with a dummy argument leaves palette RAM
  untouched, as measured.) Index `0x9f` = `#292929` (art background), index 0 = `#FFFFF6`.
* **Not verified: how it looks on screen.** mGBA's front ends give no way to script input or reach a screen, so the
  card screen was never displayed: the *bytes* the game produces are measured (hashes above), but the on-screen
  colour/scale is not. The art data itself is high-frequency (only 22% of neighbouring pixels are equal, RGB
  distance to the neighbour ~160/765) - it reads as dithered/noisy at 1:1, which is exactly the appearance the
  Y4 part 3 review rejected. Composed PNGs for the reviewer: `private/tmp/card_composed_001.png` (Blue-Eyes),
  `_002.png`, `_035.png` (Dark Magician), `_866.png`.
* Extractor / decoder: `tools/extract_card_images.py` (job `card_images`, still queued - the file does not exist
  yet) writes one 8-bit indexed PNG per card, `private/extracted/cards/<n>.png`, 24x24, with the palette above;
  check `tools/test_card_images.py` (`anchors: 2 cards match the emulator dump` / `cards: 900` /
  `bytes: 1085114` / `ALL CHECKS PASSED`; it fails if the window moves, if the tile order changes, or if the PLTE
  is not `0x089C54B0`).
* Emulator harness (all tracked): `scripts/mgba_gdb.py` (gdb-stub client, no gdb needed),
  `scripts/emu_groundtruth.sh` (launch mGBA on a ROM copy + run one script; mGBA 0.10.5 accepts one client per
  launch), `scripts/emu_card_image.py` (call the game's routine, dump what it wrote), `scripts/emu_picture_map.py`
  (the impulse test that measured the byte mapping), `scripts/emu_anchors.py` (re-derive the anchors from the ROM
  and compare with the dumps). mGBA here is `D:\Custom_Pokemon\private\tools\mGBA\mGBA-0.10.5-win64`, run from a
  copy under `private/tmp/` so nothing is written next to the original.

## Card Cost and the Duelist-Level gate (verified, DeepSeek 2026-10-12, Y4 part 4; index fixed Y5 [039])
Closes the doubt in `[033]`. The card row's **Cost** is a 32-bit value from the table `0x08088DF0`
(entry = card id; entry 0 unused): Blue-Eyes White Dragon 95, Mystical Elf 319, Hitotsu-Me Giant 121,
Dark Magician 20, Red-Eyes B. Dragon 12, Celtic Guardian 161, Blue-Eyes Ultimate Dragon 255,
Dragon Piper 260, Labyrinth Wall 585.
`sub_08006BE4` (the row loader) stores it at `struct+0x0C` and then, at `0x08006C5E`..`0x08006C6A`:
```
bl 0x8014110            ; returns the player's Duelist Level
ldr r1,[r5,#12]         ; the card's Cost
cmp r1, r0
bls 0x8006CA0           ; Cost <= level: fall through and store the card's own description
ldr r0,=0x08D30F40      ; Cost >  level: store this pointer instead
str r0,[r5,#8]          ; struct+0x08 = description pointer
```
`0x08D30F40` decodes (with the text tables of Y4 part 2) to **"Your Duelist Level is below the Cost. This
can't be put in the Deck."** So the column is a plain deck Cost used **unscaled**, compared directly against the
Duelist Level.

**Index (settled in `[039]`, reproducible with `PY tools/cost_index.py`)**: `sub_08006BE4` takes the card id in
`r0`, zero-extends it into **r4**, and indexes *every* column with that one register -- ATK `u16 @ 0x080886E6 +
2*r4`, DEF `+2*r4` from `0x08087FDC`, Cost `u32 @ 0x08088DF0 + 4*r4`, the byte rows `+r4`, and the name pointer via
`sub_080073E4` = `*(u32 *)(0x08D310E0 + 4*r4)`. Name index, stat index and card id are therefore the same number:
id 0 is the dummy row (ATK/DEF `0xFFFF`, Cost 0, name = the empty string) and id 1 is Blue-Eyes White Dragon
(3000/2500, level 8, Cost 95). Each table is exactly **901 entries** (DEF ends where ATK starts, ATK where Cost
starts, Cost where the byte rows start, and the byte rows are 901 bytes apart), which is what a 0-based dummy plus
900 cards needs. So the rule is `+4*id` with id = the card number, as `tools/extract_card_stats.py` (J0005) and
`[036]`'s first three values use. The values `[036]` printed for Dark Magician (183), Red-Eyes B. Dragon (207),
Celtic Guardian (260) and Dragon Piper (86) are the **previous** entry's, i.e. cards 34, 81, 40 and 39; and the
"Blue-Eyes Ultimate Dragon 20" it printed is Dark Magician's Cost (`+4*35`). The current values are in the list
above.


## Card 40 "Dragon Piper" description (checked, DeepSeek 2026-10-12, Y4 part 4)
No off-by-one. Cards 38..42, name then description, decoded with the Y4 part 2 text decoder:
```
 38 Gaia The Fierce Knight    A powerful knight that rides a horse faster than the wind.
 39 Curse of Dragon           A yellow dragon that breathes the very flames of hell.
 40 Dragon Piper              A being that dwells inside a curiously decorated vase.
 41 Celtic Guardian           An elf that has been given training in the ways of the sword.
 42 Illusionist Faceless Mage An odd being without a face but with heads on both its shoulders.
```
Every line describes its own card, the names are monotonic, and "A being that dwells inside a curiously decorated
vase" is Dragon Piper's own text (the card is drawn as a creature in a pot).


## Other leads (unverified)
- THUMB→ARM thunks (`add rX, pc, #imm; bx rX`) in the code region: `0x08036C70`→`0x08036C74`,
  `0x08036D0A`→`0x08036D10`, `0x08036E96`→`0x08036E9C`. The last two ARM targets may be missing from the census.

## Card passwords (found by Claude, 2026-10-12, from Matter_Scatter's hint)
- **Table**: 8 bytes per card, one decimal digit per byte, card k at `0x08D4F43C + 8*k` (card 1 Blue-Eyes at
  `0x08D4F444` = `08 09 06 03 01 01 03 09` = 89631139). Verified against the real passwords of cards 1, 22, 35,
  58, 82 (Blue-Eyes 89631139, Summoned Skull 70781052, Dark Magician 46986414, Kuriboh 40640057, Red-Eyes 74677422).
- Cards **1..831** have digits; slot 0 and cards **832..900** hold `0F 0F 0F 0F 0F 0F 0F 0E` (no password:
  game-exclusive cards such as 866 Blue-Eyes Ultimate Dragon).
- Base `0x08D4F43C` is referenced once, at `0x080341FC` (likely the password-entry screen).
- Open (A-n pending): Matter_Scatter recalls a password purchase had a **cost**; test whether the code near
  `0x080341FC` reads the `w_08088DF0` column (now called "cost") as the price.

## Opponents, decks and drops (verified, DeepSeek 2026-10-12)

**The table**: `0x08D35C28` is a pointer table of **exactly 200** little-endian words; word k is the
address of duel record k, and the records are 40 bytes each starting at `0x080B4B5C`
(`record(k) = 0x080B4B5C + 0x28*k` for every k in 0..199 — checked for all 200, `PY
tools/test_duel_table.py`).

**What indexes it** (this is the "opponent table" of the TASK): the story-script bytecode
interpreter `sub_08031E40` dispatches on `#<digit>`; case 8 (`#8 <id>`) at `0x08031FC6` does
`ldrb r0,[r0,#1]` (the byte after the `8`) and `strh r0,[0x02020D30 + 0x10]`. The duel code
`sub_080164EC` then reads exactly that word as the table index:
`ldrh r0,[0x02020D30+0x10]; lsls r0,#2; ldr r0,[0x08D35C28 + r0]`; `sub_08016254` and
`sub_08016408` use the same index. So `<id>` = duel number = table index, and the same byte is the
index into the deck/record data. **129 `#8 <id>` opcodes** exist in the ROM's data half
(`>= 0x08D00000`, every one followed by the record's `00` terminator), covering **92 distinct duel
ids (1..102)**; each sits in the pre-duel dialogue record, which is extracted with its English
line in `private/extracted/duel_scripts.tsv`.

**Record layout** (40 bytes = 10 words, `+0x00`..`+0x24`), all fields read back from the ROM and
cross-checked against the three code sites that read them:
| offset | type | meaning | evidence |
|---|---|---|---|
| `+0x00` | u16, u16 | duel id in the low half, a second id/flag in the high half (values 0..95 / 0..6) | unverified beyond the values themselves (A22) |
| `+0x04` | u32 | pointer to the opponent's **deck**: 40 × u16 card ids (id 0 = empty slot; all-zero = "no deck", e.g. records 0, 48, 50-53) | record 1 → `0x080E7CC0` = 40 ids; content matches the duelist (below) |
| `+0x08` | u32 | weighted list A: `u16 card id, u16 cumulative weight`, ends at the first id 0; rolled 0..2047 | `sub_0801649C` |
| `+0x0C` | u32 | weighted list B, same shape; rolled 0..29999 | `sub_08016768` (random 0x752F) |
| `+0x10` | u32 | weighted list C, same shape; rolled 0..2047 | `sub_0801649C` (the other of `+0x34`/`+0x3C` in the duel struct) |
| `+0x14` | u16, u16 | written `0x1F40/0x1F40` (8000/8000) in all 200 records | unverified (A22) |
| `+0x18` | u32 | small count; read into `0x02020D30+0x0C` by `sub_08016254` (values 0, 5, 10, 30) | unverified (A22) |
| `+0x1C` | u16, u16 | life-point-like pair: 2000/2000, 7000/7000, 8000/8000, 500/500, 1000/1000 … | unverified (A22) |
| `+0x20` | u8 | switch value 0..15 used by `sub_080164EC` to pick a step of 10/100/1000/10000 | purpose unverified (A22) |
| `+0x24` | u16 | values 32..42 and 139 | unverified (A22) |

**The drop model** (verified by the two readers, and by content): a list entry is chosen when the
roll is *below* its cumulative weight, so entry i covers `(w[i-1], w[i]]` of the roll space and its
chance is `(w[i] - w[i-1]) / (R+1)` with R = 2047 (`+0x08`, `+0x10`) or 29999 (`+0x0C`). That is
also the invariant the check enforces on all 200 records: every non-empty `+0x08`/`+0x10` list ends
on weight **2047** (93 / 102 lists), every non-empty `+0x0C` list ends on **29999** (103 lists), all
ids are 1..900 and weights strictly increase. Decoded example — duel 59 (Bonz), list `+0x08`,
6 entries, 16.65% each: The Snake Hair (36), Armored Zombie (96), Dragon Zombie (97), Clown Zombie
(98), Stop Defense (320), Yami (335). Duel 93 (Bandit Keith), list `+0x08`, 15 entries: 7.18% The
Snake Hair, then ~7.1% each Armored Zombie, Dragon Zombie, Clown Zombie, Stop Defense, Pendulum
Machine, Launcher Spider, Zoa, Metalzoa, Metalmorph, … (`private/tmp/opp/drops.py`). The list at
`+0x0C` is an 885-entry near-uniform pool over the whole card list (~0.02% each) — the shared
"random card" table.

**Identified opponents** (deck content, checked against the game's own dialogue):
- **duel 93 = Bandit Keith** — his own line (in the record that carries the `#8` opcode) says "I'm
  Bandit Keith. However far I fall, I'll keep crawling back up." Deck: Machine Conversion Factory,
  Pendulum Machine, Zoa, Metalzoa, Yaiba Robo, Giga-Tech Wolf, Dharma Cannon, Patrol Robo,
  Metalmorph, Slot Machine, Space Drone, Blast Sphere, Barrel Dragon, 7 Completed — a machine deck,
  and his drops are Zoa/Metalzoa/Metalmorph/Machine Conversion Factory.
- **duel 59 (and 79) = Bonz** — "I'm Bonz, the undying"; "Bonz, the undead, shall duel forever!"
  Deck: 16 Zombie + 33/40 Fiend-attribute cards (Skull Servant, Pumpking the King of Ghosts, Mech
  Mole Zombie, Phantom Ghost, Bone Mouse, Thousand-Eyes Idol, Shadow Specter), drops all zombie
  cards.
- **insect decks (A23)**: duels 40/57 ("the insect army", "I'll show you how strong an insect deck
  can be") run 17/40 Insect + 12 Plant + 9 Beast with 26/40 Forest attribute; duel 58 ("My insect
  deck is the strongest") runs **28/40 Insect**, 34/40 Forest.
- **duel 69 (A23)**: 3× Water Element, 3× The Furious Sea King, 3× Kanikabuto, 3× Turtle Raccoon,
  3× Penguin Soldier, 3× Liquid Beast, 3× Boneheimer, 3× Twin Long Rods — a pure sea/aqua deck
  (the game's own text names Mako Tsunami as the sea-deck duelist).
- No record in this table contains Blue-Eyes White Dragon (1) at all; Red-Eyes B. Dragon (82)
  appears once each in duels 19 and 27 (A23).

**Opponent names: there is no name table** (negative result, checked two ways). The rule-A11 scan
for `$0`-record pointer tables finds 15 tables, all identified (card names, descriptions, credits,
duel messages, type/attribute names, effect texts, NPC dialogue lists, location labels) and none
holds opponent names; repeating the scan at every byte alignment (not only 4-aligned) and with a
64-byte gap allowance adds nothing new (35 runs, same set). The 200 duel records have no name field
either. Opponent names exist only *inside* dialogue text — either as the addressee in a line
("Joey Wheeler% you just wait…") or, usefully, as a self-introduction in the duel's own pre-duel
line (that is how duels 59/79/93 were identified above). Finding the full duel → NPC → name map
needs the map/NPC tables, which is a separate job.

**Which of the three lists is read, and what decides it** (DeepSeek 2026-10-12, [048]; code
evidence, not a guess). At duel start `sub_08017F54` copies the 10 words of `record(duel id)`
into RAM `0x02020D30+0x2C` word for word, so RAM `+0x34` *is* the record's `+0x08`, `+0x38` is
`+0x0C` and `+0x3C` is `+0x10` (`sub_08017CA8` re-copies them when a duel is entered). The two
readers then differ:
* `+0x0C` (RAM `+0x38`) is read by `sub_08016768` (roll `sub_08034628(0, 0x752F)` = 0..29999),
  which only `sub_08016748` calls and which only the duel-start routine `sub_08016254` calls;
  it runs **50 times** at the start of every duel. Its content is not per-duel at all: 103 of
  the 200 records point at the single shared table `0x080C65D4` (885 ids, uniform ~34 weight
  each), the other 97 at `0x080C65D0` — the same address 4 bytes lower, where the first id is 0,
  i.e. an empty list. So `+0x0C` is the tournament-wide "any card" pool.
* `+0x08` and `+0x10` are read by `sub_0801649C` (roll `sub_08034628(0, 0x7FF)` = 0..2047) and
  **which of the two it uses is decided by the card id in `0x02020B34`**: it calls
  `sub_0801823C(id)`, which returns 0 when the id is one of the **49 ids in the table at
  `0x080BA280`** and 1 otherwise; `r0 == 1` (not in the table) loads RAM `+0x34` = record
  `+0x08`, `r0 == 0` (in the table) loads RAM `+0x3C` = record `+0x10`. `0x02020B34` is written
  by the card-resolution path from `sub_0800475C(2)` (the id of the card being resolved,
  `0x080077xx` region) and zeroed by `sub_08007604`, so at the start of a duel it is 0 — a value
  that is not in the table — and the opening hand (`sub_0801644C`, 10 cards into RAM `+0x12`)
  comes from `+0x08`.
* Content confirms which is which: `+0x08` is per-duel (49 distinct pointers across the 200
  records; 93 records have a list of 1..74 entries, 107 are empty; duel 59's six zombie cards,
  duel 93's 15 machine cards), while `+0x10` is one shared list of **57 ids** at `0x080B80CC`
  in 102 of the records — nearly the same card set as the 49-id table `0x080BA280` (that table
  has 24, 318, 655, 658, 672, 870 that the list lacks; the list has 14 ids the table lacks),
  i.e. a curated "special cards" pool.
So: **`+0x0C` is always read at the start of a duel; `+0x08` versus `+0x10` depends on whether
the card being resolved in that moment is one of the 49 special cards.** What the two pools are
*for* in game terms (which one feeds the opponent's hand, which one the card the player wins)
is not established — labelled A26.

**Tools**: extractor `tools/duel_table.py` → `private/extracted/duel_table.tsv` (200 rows, one per
record), `duel_decks.tsv` (card ids + names per duel, 42 distinct decks) and `duel_scripts.tsv`
(129 opcode sites). Check `tools/test_duel_table.py` (full recompute of all three files plus the
structural invariants above; `ALL CHECKS PASSED`). A second check `tools/test_duel_rewards.py` is
in place for the local job that writes `tools/duel_rewards.py` (raw lists with card names and
`chance_ppm`); recipe `private/jobs/drafts/duel_rewards.md`.

## Opponent names from the story scripts (DeepSeek 2026-10-12, [048])

Plain answer first: the game says an opponent's name out loud for only a few of the 200 duels.
What the text does support is in `private/extracted/duel_names.tsv` (200 rows), produced by
`tools/duel_names.py` and checked by `tools/test_duel_names.py`. Everything the game does not
say is **left blank** rather than filled in from the deck or from general knowledge.

Method (all of it reproducible from the ROM):
* The `#8 <id>` opcode is the last thing in the line an NPC says before a duel, and the duel
  code uses the byte after the `8` as the record index — so **the speaker of that record is the
  opponent**. 130 such sites exist in the data half (`0x08D00000` up), covering 93 distinct
  duel ids. (The older extraction lists 129: it misses `0x08DD2695` (duel 24), whose enclosing
  record is 3147 bytes long. Every site in `duel_scripts.tsv` is in this tool's set.)
* Dialogue records are stored back to back — each ends with `00`, the next starts with `$0` — so
  the record before the opcode's record is the *same NPC's* earlier line; the usual pattern is
  "What? Are you challenging me? Sure, I accept." / "Heh, don't whine and cry if you lose!"
  (duel 35). The window is the opcode's record plus the two before it. Looking further back
  leaves the conversation: a 16-record window picks up Bonz eleven records before duel 93
  (a different character).
* A name is written only when the game backs it *twice over*: the speaker introduces himself
  ("I'm …", "My name is …", "<Name>, the …"), **or** the name is used in the window and the
  duel's own 40 cards match that character's card theme (the game's own type/attribute columns
  in `card_stats.tsv`; agreement = 15+ of 40 cards). The deck is a check, never a source.
* Only **three characters** ever introduce themselves in the whole data half: Bonz, Bandit
  Keith, and Marik ("My name is Marik Ishtar" — and that record is not next to any duel, so no
  row rests on it). Four mentions that a read showed are not the opponent are excluded
  with a reason (`EXCLUDED` in `tools/duel_names.py`): duel 12 (the line asks "why are they after
  us?" *about* Marik), 72 (a simile — "I'm kind of like Mako Tsunami"), 76 (someone looking for
  Kaiba), 87 (the line *addresses* Marik — "Master Marik Ishtar… I beg your forgiveness").

| duel | name | confidence | the line it rests on (evidence_addr) |
|---|---|---|---|
| 21 | Bonz | low | "Bonz, the undead, shall duel forever!" (0x08DD2E7F) + zombie deck 16/40 |
| 26 | Weevil Underwood | low | "Not I, but Mr. Underwood himself will duel you." (0x08D7B8EA) + insect deck 34/40 |
| 39 | Weevil Underwood | low | "challenging Mr. Underwood? You'll have to beat me first." (0x08D798B4) + 26/40 |
| 40 | Weevil Underwood | low | "Mr. Underwood has no time to deal with dregs like you." (0x08D7A213) + 26/40 |
| 57 | Weevil Underwood | low | "Mr. Underwood is the toughest duelist." (0x08D7ADA5) + 26/40 |
| 59 | Bonz | high | "Bonz, the undead, shall duel forever!" (0x08DD2E7F) |
| 79 | Bonz | high | "Duel? I'm Bonz, the undying." (0x08D60837) |
| 90 | Bandit Keith | low | "I'll take the Ghouls. #5, Keith is yours." (0x08D84C16) + machine deck 20/40 |
| 93 | Bandit Keith | high | "I'm Bandit Keith. However far I fall, I'll keep crawling back up." (0x08DD792A) |

The three `high` rows are facts: the speaker of the duel-starting line says who he is (duels 59
and 79 are Bonz's ghost, 93 is Keith). The `low` rows are leads, not facts: the name is used in
the duel's own neighbourhood and the deck matches, but the speaker may be the character's
follower ("Mr. Underwood has no time to deal with dregs like you" is spoken *by* one of Weevil's
insect crew, not by Weevil). Each row carries its quote, so the reader decides. Everything else
is blank: of the 93 duel ids a script starts, only these 9 have a supported name; the duel 84
that are unnamed keep no name and no guess. In addition each of the 93 rows carries
`pre_duel_line`, the game's own line for that duel ("All right. I'll take you on."), so a duel
without a name still has its own label for the opponents page. Duel ids 103..199 have no `#8`
opcode at all (107 rows) and nothing to name.

Limits worth knowing: the window rule assumes the records around a duel line belong to the same
NPC, which holds for the "challenge → duel" pairs but not for a record whose Japanese field is
huge (it swallows the records around it); and the lexicon only holds names the game itself
spells out (17 characters — names like Arkana, Strings, Lumis, Umbra, Rebecca, Solomon, Serenity,
Duke never appear in the ROM's dialogue at all, checked by word-boundary search).
