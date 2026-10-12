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

**Card descriptions are uncompressed and found** (region ≈ `0x08DE0000`–`0x08E40000`), e.g. at `0x08DFE3D0`:
```
$0^2A ghostly   spirit of a   wild animal   that roams in wastelands. ^This card   could become
troublesome   if encounteredin number.^$1^2A ghostly   spirit of a   wild animal   that roams …
```
Note the space padding (the text is pre-wrapped for a fixed-width font) and that every language holds the same
untranslated text. **Not yet indexed:** the 901-word table at `0x08DFC054` is sorted, unique and points into
`0x08DE6578`..`0x08DFBF2E`, but it is *not* card→description (entry 0 and 1 point one byte apart, and entry 1
targets a duel message). How the game finds a card's description is the open item (A12).

## `0x87` accented letters (verified, DeepSeek 2026-10-12)
Two bytes: `0x87` then a code byte, rendering one accented letter (`0x87` itself never appears otherwise). The
code byte is a look-alike letter, so the table is a lookup, not a formula. Verified by reading the byte pairs in
known words of the 900 card names (each code below is quoted with the word it was read from):
| code | letter | evidence |
|---|---|---|
| `0x54` `0x56` `0x58` `0x59` | Ö Ú Ü ß | `Ödland`, `Último día`, `Übersinnlicher`, `Großer Weißer` |
| `0x5A` `0x5B` `0x5C` | à á â | `Oscurità`, `Lutin à corne`, `Cráneo`, `Crâne` |
| `0x5F` `0x60` `0x61` `0x62` | ä è é ê | `Blauäugiger`, `ténèbres`, `Géant`, `Tête` |
| `0x65` `0x66` `0x67` `0x68` | í î ï ñ | `místico`, `Chaîne`, `humanoïde`, `montaña` |
| `0x6A` `0x6B` `0x6D` | ó ô ö | `Dragón`, `fantômes`, `Zweiköpfiger` |
| `0x6F` `0x70` `0x71` `0x73` | ú û ü ç | `Músico`, `envoûtante`, `Geflügelter`, `Garçon` |
`0x61` is also used for the capital `É` (`Garçon-Étoile`). Very likely but only read once: `0x43` Á (`Árbol`,
`Águila`), `0x48` É (`Épée de dragon`), `0x4C` Í (`Ídolo mil ojos`). Unknown: `0x64` (`Ultimo D?d della
Strega`, Italian). Three codes appear for a second letter that is certainly a typo in the game's own text:
`0x56` for í in `día`, `0x6B` for é in `météo` (`mêtaêo`). The codes `0x82`/`0x83`/`0x89`/`0x90` only ever occur
inside the Shift-JIS `$5` fields, so they are not escapes at all — they are second bytes of Shift-JIS
characters that follow a `0x87` kanji byte.

## Other leads (unverified)
- THUMB→ARM thunks (`add rX, pc, #imm; bx rX`) in the code region: `0x08036C70`→`0x08036C74`,
  `0x08036D0A`→`0x08036D10`, `0x08036E96`→`0x08036E9C`. The last two ARM targets may be missing from the census.
