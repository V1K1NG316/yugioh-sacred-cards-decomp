# Approximations

Every labelled guess (A1..An) and where it is marked.

- **A1** — `tools/find_functions.py` is a linear-scan heuristic, not a data-flow analysis: it decodes
  instructions from a function start and stops at a return or an unconditional branch, so a function
  that stores code in a jump table may be cut short. Function *starts* it reports are still backed
  by a real `BL`/`BLX` instruction or by an entry point. Marked in `docs/rom-map.md` §4 and in the
  script's docstring. (2026-10-12)
- **A2** — a target seen only as a pointer value loaded from a literal pool (`ldr rX,[pc,#imm]` … `bx
  rX`) is *not* walked into: such a word can be data. 13 such values were skipped in the part-1
  census; 26 in the part-2 census, of which 3 are in `config/functions.csv` anyway because a
  pointer *table* word also points at them (the A6 sweep sees tables, not literal pools). Marked in
  `tools/find_functions.py` and `docs/rom-map.md` §4. (2026-10-12)
- **A3 — SETTLED (2026-10-12, milestone Y5):** the guess was an old GNU/agbcc-class THUMB compiler
  rather than ARM's own `armcc` (evidence: `pop {…}` + `bx rN` returns in 85 of 155 THUMB
  functions, only one `pop {…, pc}`; ARM startup stub; direct BIOS `svc` calls instead of a C
  library). The decisive test the guess named has now been run: **agbcc** (gcc 2.9-arm-000512,
  `-mthumb-interwork -Wimplicit -Wparentheses -Werror -O2 -fhex-asm`) reproduces ROM functions
  byte for byte — `sub_08004750`, `sub_08007604` and `sub_0800AF94` match exactly, literal pool and
  return shape included, and `make compare` stays byte-identical with their C linked
  (`tools/match_func.py`; `docs/decomp.md` §5). Marked in `docs/rom-map.md` §3. (2026-10-12, Y5)
- **A9** — what "a function is matched" means in Y5: the ROM's bytes for the function's whole A5
  extent equal the compiled C's bytes over gcc's `.size` (code + literal pool), followed by `.space`
  zeros for the remaining bytes of the extent. `scripts/build_matched.sh` compares that whole extent
  with the ROM per function before the ROM is rebuilt, so a non-zero tail fails loudly rather than
  being absorbed; the assumption being checked is that those tail bytes are padding and not part of
  the function. Marked in `scripts/build_matched.sh`, `docs/decomp.md` §7. (2026-10-12, Y5)
- **A4** — the decode-validity rule used to reject a function-table candidate: the first 8 THUMB
  instructions at the target must decode as **defined ARMv4T THUMB**. Rejected by the rule
  (`thumb_ok` in `tools/find_functions.py`): a `BL`/`BLX` low half with no matching high half, the
  undefined `0xE800`–`0xEFFF` and `0xDE00`–`0xDEFF` blocks, the unused/bkpt halves of the `0xBxxx`
  group (`0xB1xx`–`0xB3xx`, `0xBE00`–`0xBEFF`), and `0x0000` padding. It is applied **only** to
  `ptr_prologue` candidates, never to a `BL` target: a real function need not begin with a
  prologue (the interrupt stubs at `0x08003B94` are a single `bx lr`), and a real `BL` is stronger
  evidence than any decode heuristic. 0 of the 833 `ptr_prologue` candidates were refused by it.
  Marked in `tools/find_functions.py`, `docs/rom-map.md` §4. (2026-10-12)
- **A5** — the `size` column, since Y3: the distance from the row's address to the **next row's
  address** (the last row runs to the sentinel `0x08FFFFFC`). The extents tile the ROM and are
  disjoint by construction, which is what `tools/test_functions_csv.py` verifies; they are address
  ranges, **not** "code only" — a literal pool or a data table between two functions is inside the
  earlier row's extent. Before Y3 it was `min(walk_end, next_function_start) - address` with
  `walk_end` from the finder's linear walk (the Y2 rule below, kept for the record: a function cut
  short by a jump table got a short size, capped by the next start). Sizes are still **not** verified
  against the real function boundaries. Marked in `tools/functions_from_rom_s.py`,
  `docs/rom-map.md` §4. (2026-10-12, Y3)
  - Y2 rule, superseded: `min(walk_end, next_function_start) - address`, `walk_end` = where the
    linear walk stopped, or `address + 16 KiB` if the walk hit `MAX_FUNC`
    (`tools/find_functions.py`).
- **A6** — a pointer-table (`ptr_prologue`) candidate is accepted only if its target lies within
  `PTR_MAX_DIST` = 64 KiB (`0x10000`) of a function the BL closure already found. Rationale is
  measured, not tuned: of the 833 candidates, every rejected one was at least 312 660 bytes
  (`0x4C554`) from BL-closure code and every accepted one at most 22 564 (`0x5824`) — the 64 KiB
  line sits in a two-order-of-magnitude empty band. 20 candidates were refused by it, all pointing
  into the data half of the ROM; if the game really has a second code block far from the first, this
  rule would hide it. Marked in `tools/find_functions.py`, `docs/rom-map.md` §4. (2026-10-12)
- **A7** — the 1 MiB data-block table in `docs/rom-map.md` §5 is read from three crude statistics
  only (zero-byte share, printable-ASCII share, count of odd `0x08xxxxxx` words); every "guess"
  column of that table is a guess, not a finding. (2026-10-12)
- **A8** — what makes a data run "data" in the Y3 disassembly: the disassembler's own decision. A run
  of bytes is emitted as `.incbin` when gbadisasm has no label and no instruction there, which means
  the function list, a `BL`, a pointer table or the `data_label` sentinel did not reach it. Nothing
  verifies that no code hides inside such a run — in particular the whole tail
  `0x0803B61C`–`0x08FFFFFC` (16 533 984 bytes, 98.6 % of the ROM) is one unlabelled data run, and the
  626 `.4byte` pointer words kept as symbols would not show a code block that is only reached by a
  computed jump. Marked in `tools/post_disasm.py`, `tools/split_disasm.py`, `docs/rom-map.md` §5.
  (2026-10-12, Y3)
- **A10** — what counts as an LZ77 blob in `tools/find_lz77.py` / `tools/test_lz77.py`: any file offset whose
  byte is `0x10` and whose following 24-bit little-endian size (1..`0x40000`) is produced *exactly* by the BIOS
  LZ77 stream at +4. Two deliberate choices, both visible in the output: (1) overlapping candidates are resolved
  left to right (a candidate starting inside an accepted blob's compressed range is dropped), and (2) no pointer
  word is required, so 112 of the 1084 blobs are unreferenced — 102 of them declare 72 bytes or less and are
  almost certainly coincidences inside data (a valid-looking header whose stream accidentally completes), the
  rest are 576-byte blobs inside the card-picture region. A blob also may not overshoot its declared size with
  its last copy, which is a choice, not a BIOS rule: the BIOS would keep writing. Marked in
  `tools/test_lz77.py`, `docs/game-data.md` §Compression. (2026-10-12, Y4)
- **A11** — what counts as a text-pointer table in `tools/find_text_tables.py` / `tools/test_find_text_tables.py`:
  a run of 4-aligned words whose value is a ROM address starting with `$0` (0x24 0x30), where consecutive hits
  are at most 8 bytes apart and a run needs at least 4 hits. Evidence for the rule: run over the whole ROM it
  returns 15 runs and reproduces every table found by hand, entry counts included (`0x08D310E4` ×900,
  `0x08D30310` ×140, `0x08D36130` ×124, `0x08D4BC3C` ×24, `0x08D419E0` ×12) — with the strict "exactly 4 bytes
  apart" variant, the duel-message table came back as two runs (23 + 47) instead of 124, which is why the 8-byte
  gap is in the rule. It cannot see a table whose records start differently, and it will split a table that has
  two or more consecutive non-`$0` entries. Marked in `tools/test_find_text_tables.py`, `docs/game-data.md`
  §Text. (2026-10-12, Y4)
- **A12** — the card-description index is *not* found, only the text: the records live in
  `0x08DE0000`–`0x08E40000` (a boundary read off the region where `$0…$5` records with `^` line breaks sit, not
  a verified limit) and the 901-word sorted table at `0x08DFC054` was assumed to be the card→description table
  and is not (entries 0 and 1 point one byte apart, entry 1's target is a duel message). Until the mapping is
  found, descriptions must be harvested by scanning, not by card number. Marked in `docs/game-data.md` §Text.
  (2026-10-12, Y4)
- **A12 — RESOLVED** (2026-10-12, Y4 part 2, DeepSeek). The index is the 900-word pointer table at
  `0x08E94E7C`, one entry per card number (entry `k` = card `k+1`), read by the card-database loader
  `sub_08006BE4` with a literal 4 bytes below the table (`0x08E94E78`) because the game's card ids are 1-based
  (`sub_080073E4` does the same for the name table at `0x08D310E4` via `0x08D310E0`). Verified on cards 1-2, 30-40,
  35, 58, 82, 866 and 887 (names line up with their descriptions), and card 2's description effect line matches
  `word[0x08DFC054 + 4*2]`. `0x08DFC054` is *not* a card table at all (one reader, `sub_08024F64`, effect
  messages). The old text above is kept as the record of what was wrong. Evidence in `docs/game-data.md` §Text.
- **A13** — the text-decoding rules of `tools/decode_text.py` are read off the *shape* of the data, not from the
  renderer: `^` and `#0` are rendered as a line break, `%` as a comma, `$<digit>` starts a language field, and a
  record ends at the first `0x00`. Facts: every Latin description field has the shape `^2<line1>^<line2>^`
  (4505 / 4506 have the leading `^2`, so the `2` is a per-field constant, not a line number) and duel messages use
  `#0`/`#1`… where descriptions use `^`. What `^<digit>` selects and whether `^` really is a line break for the
  renderer is unverified. Marked in `tools/test_decode_text.py`, `tools/test_card_descriptions.py`,
  `config/text_glyphs.csv`. (2026-10-12, Y4 part 2)
- **A14** — the table at `0x08DFC054` (901 words, entry 0 an empty string) holds duel-time effect-message
  templates and is indexed by something other than the card number: the callers of `sub_08024F64` pass constants
  (0x54, 0x59, 0x21C), Blue-Eyes' slot 1 reads "…will be summoned", and slots 35/58/865/887 are empty, yet
  `word[0x08DFC054 + 4*2]` is exactly Mystical Elf's effect line. Reading it as an *effect id* is a guess.
  Marked in `docs/game-data.md` §Text. (2026-10-12, Y4 part 2)
- **A15** — the attribute column of `card_stats.tsv` (`0x08089C04` -> struct `+0x17`) holds an index into the
  game's own 12-entry attribute table (`0x08D419E0`: Shadow, Light, Fiend, Dreams, Pyro, Forest, Wind, Earth,
  Thunder, Aqua, Divine). That it *is* the attribute is verified by code (`sub_080073A8` prints it via the name
  getter `sub_0801A624`), but the game's attribute is **not** the TCG attribute: it agrees for Light (BEWD,
  Mystical Elf) and Dark (Dark Magician "Shadow", Kuriboh "Shadow") and disagrees for Celtic Guardian
  (game "Light", TCG Earth), Griffore ("Forest", TCG Earth), Baby Dragon ("Earth", TCG Wind), Red-Eyes B.
  Dragon and Summoned Skull ("Fiend", TCG Dark), Blue-Eyes Ultimate Dragon ("Divine", TCG Light). Reading the
  12 values as the old Game Boy Duel Monsters attribute set is a guess; the byte values themselves are data.
  Marked in `docs/game-data.md`. (2026-10-12, Y4 part 3)
- **A16** — struct `+0x1a` (`0x0808AD9D`) and `+0x1b` (`0x0808AA18`) are read as "effect/script ids": the card
  screens `sub_080113EC` / `sub_080285E8` store them to RAM (`0x0201CB3C`, `0x0201CB34`) and index tables of
  **code** pointers (`0x08D353A0`, `0x080FB79C`, `0x08D34B80`) that are tail-called through the `bx r0` stub
  `sub_08038E24`. The value *ranges* are solid data (`+0x1a` = 2 for all 773 monsters, one distinct value per
  Magic/Ritual/Trap card; `+0x1b` nonzero for 79 cards, including Mystical Elf, whose description says it powers
  up Blue-Eyes White Dragon), but "which routine the game then runs" is not traced, so the *name* is a guess.
  (2026-10-12, Y4 part 3)
- **A17** — struct `+0x19` (`0x0808A693`) selects one of the 10 card-frame graphics at `0x08D536C8` (the picture
  loader reads it), and it is 3 for every Magic card, 4 for every Trap and 5 for every Ritual - solid. What
  1 (75 cards), 6 (1 card), 7 (1 card) and 8 (1 card) mean is unknown; "frame colour variant" is a guess from
  the frame data (the 9 frames are one shape with three palette indices remapped). Marked in `docs/game-data.md`.
  (2026-10-12, Y4 part 3)
- **A18** — the loader does `struct[+0x1d] = table[0x0808B4A7 + struct[+0x1a]]`, and `sub_0800BB9C` then reads
  `u16[0x08D3632A + 8*struct[+0x1d]]` and loads the **card id** it finds there. The 8-byte records at
  `0x08D36328` look like pairs of card ids (record 0 all zero, record 1 = 38,364), i.e. it behaves like a
  "related card" table, but which game mechanic uses it (fusion? transformation? deck helper?) is a guess.
  Marked in `docs/game-data.md`. (2026-10-12, Y4 part 3)
- **A19** - the card image composition is *measured*, but one part of it is still an interpretation: the game
  writes image byte `i` of the 32x32 card image at destination byte `i + 768*(i//256)` (impulse test in
  `scripts/emu_picture_map.py`). 768 bytes = 12 8bpp tiles, and calling the destination "a screen tile buffer
  whose rows are 12 tiles wide, with the card in the first 4 tiles of four consecutive rows" fits the caller
  (`0x02010400 + table[slot]*32`) but is not proved - only the byte arithmetic is. What matters for extraction
  (frame + art at (4,2), 32x32 8bpp row-major tiles) is proved by the emulator anchors. (2026-10-12, Y4 part 4)
- **A20** - the art's *appearance* is unverified. mGBA 0.10.5 has no scripted input and no headless screen path,
  so the card screen was never displayed; the bytes the game produces were read out with its gdb stub instead.
  The art data is high-frequency (22% of neighbouring pixels equal, RGB neighbour distance ~160/765), so the
  24x24 decode looks dithered/noisy at 1:1 - the same appearance the Y4 part 3 review called "noise". Either the
  art really is dithered at 24x24 (and the reviewer's upscale exaggerates it) or the picture index space maps to
  the palette through something not yet found (a per-card palette does not exist: a scan for a 900-entry table
  with constant 32-byte or 512-byte stride over the ROM found nothing). Check `private/tmp/card_composed_*.png`.
  (2026-10-12, Y4 part 4)
- **A21** - the palette address `0x089C54B0` is confirmed as the one the card screen copies (routine at
  `0x08028130`: `CpuFastSet(0x089C54B0 -> 0x02000200, 160 words)`, SWI `0x0B`), but the palette RAM that the BG
  ends up using (BG palette 0x05000000 and/or OBJ palette 0x05000200, and at which bank) was not read, because
  that needs the card screen to be displayed. The 256-colour BGR555 reading and the `+0x1F`-scaled RGB
  conversion are unchanged from Y4 part 3. (2026-10-12, Y4 part 4)

- **A-disp1 (Claude, 2026-10-12 15:47)** — card picture layout/palette (A20/A21) and the cost-table indexing are DISPUTED; see
  AI_Conversation [037]. Do not rely on `docs/game-data.md` picture or Dark Magician/Red-Eyes cost values yet.
