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

- **A22** — duel-record fields `+0x00` (two u16), `+0x14` (8000/8000 in all 200 records),
  `+0x18`, `+0x1C` (a life-point-like pair), `+0x20` (a 0..15 switch) and `+0x24` (32..42 and 139)
  of the 200 duel records at `0x08D35C28` are read back exactly (reproducible with
  `PY tools/duel_table.py`) but their **meaning is not established**; only `+0x18` has a code
  reader found so far (`sub_08016254` copies it to `0x02020D30+0x0C`). Worth noting: `sub_080164EC`
  uses the `+0x20` byte to choose between steps of 10 / 100 / 1000 / 10000, which reads like
  life-point display animation, but that screen was never driven in the emulator.
  (DeepSeek, 2026-10-12)
- **A23** — opponent *identity* for every duel except 59, 79 (Bonz) and 93 (Bandit Keith) is
  inferred from deck content, not read from a name field: e.g. duels 40/57/58 are called
  "insect" duellists because the game's own pre-duel line says so and their decks are 17/40 and
  28/40 Insect; duel 69 is called a sea/aqua deck because 30 of its 40 cards are Aqua/Fish/Sea
  Dragon/Reptile typed; "no Blue-Eyes deck exists in this table" and "Red-Eyes B. Dragon appears
  once in duels 19 and 27" are exact ROM facts, but attaching the *names* Joey/Kaiba/Mako to those
  duels is a fan-knowledge mapping, not a ROM lookup. (DeepSeek, 2026-10-12)
- **A24** — the 129 `#8 <id>` opcodes were found by scanning for the byte pair `23 38` at or above
  `0x08D00000` with the id byte after it and the enclosing text record taken as the nearest `$0`
  preceded by `00`. Every hit satisfies "byte after the id is 0x00" and "id < 200", and the
  opcode's meaning is read from `sub_08031E40` case 8, but no *negative* scan for false positives
  (an ordinary text string reading "#8…" inside a message) was done, and a second duel-start path
  (e.g. the opcode at case 9, `0x08032004`) was not decoded. The 92 distinct ids are a lower bound
  on how many of the 200 records the story uses. (DeepSeek, 2026-10-12)
- **A25** — the deck interpretation (word `+0x04` = the opponent's 40-card deck) rests on the
  structure (40 u16, all ids 1..900 or all zero) and on content agreement with the duel's own
  dialogue (Bonz zombie deck + zombie drops, Bandit Keith machine deck + machine drops), *not* on
  having read the code that loads the deck at duel start. If that turns out to be, e.g., a card
  *pool* rather than a deck, the file layout is unaffected but the wording in `docs/game-data.md`
  is. (DeepSeek, 2026-10-12)
- **A26** — which of the three weighted lists (`+0x08` / `+0x0C` / `+0x10`) the game reads *for
  what*. Verified from the code: the record's 10 words are copied verbatim into `0x02020D30+0x2C`
  by `sub_08017F54` (so RAM `+0x34/+0x38/+0x3C` = record `+0x08/+0x0C/+0x10`); `sub_08016768`
  (roll 0..29999) reads `+0x0C` and runs 50 times at duel start only; `sub_0801649C` (roll
  0..2047) reads `+0x08` or `+0x10` depending on whether the id in `0x02020B34` is one of the 49
  ids in `0x080BA280`. Not verified: what each pool *is* in game terms (the opponent's hand, the
  ante, the cards the player can win), and that `0x02020B34` really holds "the card being
  resolved" — that reading comes from `sub_0800475C(2)` being stored there in the card path and
  `sub_08007604` zeroing it, which fits but was never watched in the emulator. (DeepSeek,
  2026-10-12, [048])
- **A27** — the opponent names in `private/extracted/duel_names.tsv` (tool `tools/duel_names.py`).
  Only the three `confidence=high` rows (59, 79, 93) are read straight out of the text: the line
  that starts the duel is the opponent's own and he says who he is. The six `low` rows are "a
  name is used within two records of the duel *and* the duel's own deck matches that character's
  card theme": duels 39/40/57 rest on lines spoken *by* Weevil Underwood's insect crew, so those
  rows are leads, not facts. The window rule itself (the `#8` record plus the two records before
  it) is a heuristic: on duel 93 a 16-record window runs back into Bonz's lines, a different
  character. Also a correction to A24: this turn finds **130** `#8` sites covering **93** duel
  ids, one more than the 129/92 recorded there — the extra site is `0x08DD2695` (duel 24), whose
  enclosing record is 3147 bytes long and was missed by the older 3000-byte back-search; every
  site in `duel_scripts.tsv` is in this set. (DeepSeek, 2026-10-12, [048])

- **A-pack1 (Claude, from Matter_Scatter's memory of the game, 2026-10-12 19:48)**: after a won duel the player picks one of
  **3 packs** and receives about 5–7 cards. Hypothesis: the per-duel pools (record +0x08 / +0x0C / +0x10, read at
  duel start per [048]) are the **reward-pack generator**, pre-rolled at duel start and shown after the duel:
  pool A = the opponent's themed cards, pool B = occasional rare card from the 885-card list (~50%), pool C =
  shared special case (49-id set). To verify: find the routine that fills 3 × N reward slots with
  `sub_0801649C` / `sub_08016768` rolls, and the post-duel 3-pack screen. Not yet verified.

- **A-pack1 update (Claude, 2026-10-12 19:54, community sources — weak: that LP page recaps OTHER series games; our ROM is the Early Days Collection build):** Sacred Cards uses the **ante** rule (winner takes the loser's
  wagered card) and gives **random drops from each opponent's loot table "as low as 1/2048"** plus a fixed card
  per 10 wins against an opponent (Let's Play Archive, Update 05). 1/2048 = one slot of the 0..2047 roll →
  pool A (+0x08) is most likely the per-opponent **loot table**. No source mentions a 3-pack choice screen (may be
  another Yu-Gi-Oh title). Speedrun notes (TASVideos 17496): fixed RNG seed at new game; RNG advances on deck
  shuffle, NPC movement, ante wins, monster destruction; draw-order logic not found by runners. To verify in code:
  the post-duel reward routine and a 10-win fixed-reward table.

- **A26 — RESOLVED (DeepSeek, 2026-10-12, [054])**: the pools are read **only after a duel**, in the
  won handler `sub_08016254` (reached from `0x08017D6C` → `sub_08016234`), never during one. `+0x08` /
  `+0x10` give the **one** card the player wins (`+0x28` = 1, set at `0x08017CDA`): `+0x08` (the duel's
  own list) when the ante card `0x02020B34` is *not* one of the 49 ids at `0x080BA280`, `+0x10` (the
  shared 57-id list at `0x080B80CC`) when it is; with no ante card set (`0x02020B34 == 0`) no card is
  given at all. `+0x0C` is rolled 50× into a *second* array (`0x02020DB0`, see A28) and is not part of
  the visible reward. `0x02020B34` is **not** "the card being resolved": it is the player's **ante
  card**, set by the trunk menu's "Use as Ante" action (`sub_08007750`: it checks the count for the
  highlighted card in the collection array `0x02020770` first — `sub_080043C0` at `0x0800775E` — then
  stores the id at `0x08007794` or `0x080077A6`) and zeroed by `sub_08007604` — and on a loss
  `sub_08004348` removes one copy of it from the collection (`0x0801636E`). Details and
  the four hypothesis verdicts: `docs/game-data.md`, "What the three lists actually do".

- **A28 — the purpose of the per-card count array at `0x02020DB0`** (DeepSeek, 2026-10-12, [054]).
  Verified: it is one byte per card id 1..900 (cap 250 copies, `sub_0801BED4` at `0x0801BED4`), it is
  zeroed at the start of a new game (`sub_0801BFB8`, called only from the new-game init `sub_08006314`),
  its writers are the 50 win rolls (`0x08016756`) and the "enter the card's code" machine
  (`0x080342C6`), and it is copied to/from a menu working copy `0x02021140` by `sub_0801B77C` /
  `sub_0801B85C`. Not established: what the game shows it for. It is *not* the card collection — that
  is `0x02020770` (the array the ante loss decrements at `0x0801636E`, the story's gift opcode writes
  at `0x08032004`, and the win adds to at `0x0801647A`). Candidates: (a) an "obtained at least once"
  log used by the card-list / trade screens, (b) the shop's stock. Everything above is read off the
  code; the cheap decisive test is an in-game spot check (win a duel in mGBA, then compare the Trunk
  entry for the won card against the card-detail screen's count), which needs the emulator, so it is
  left open. Also unverified for the same reason: the 50 rolls' *effect* is invisible in the win
  screen, so nothing in the code yet says whether the player sees those 50 cards anywhere.

- **A29 — "the opponent's loot table" vs "the opponent's ante card"** (DeepSeek, 2026-10-12, [054]).
  The code fixes the mechanics (one roll 0..2047 from a per-duel weighted list, card added to the
  collection, announced as "#2 was obtained!") and the ante rule for the *player's* own card (lost on
  a defeat). Whether the card won is fictionally the opponent's ante card or a "drop" cannot be decided
  from the code: nothing picks or stores an opponent-side ante card at duel start. Labelled, not
  resolved; the odds are identical either way.

- **A30 — the 10-slot reward array** (DeepSeek, 2026-10-12, [054]). `0x02020D30+0x12` is ten u16 card
  slots and the win screen loops over all ten (`0x0801630C`, stopping at the first 0), but the count
  byte `+0x28` is only ever written as 1 (`0x08017CDA`) or 0 (`0x08017F86`), so in this build at most
  one card can appear. Read as: the reward list is a general "cards obtained" list (up to 10) that
  this build only ever fills with one entry — for example a leftover from a design where a win could
  give several cards. Not verifiable from the ROM alone.
- **A31 `volatile` as a matching idiom** (Claude, 2026-10-13). Some matched C uses `volatile` only because
  old_agbcc then picks the ROM's registers / load order: `extern volatile u8 gUnk_02020B00[]` (sub_08018150), a
  `volatile u8 *p` alias (sub_0801C324/C344/C378), `*(volatile u16 *)0x04000000` (sub_0801371C, a hardware
  register, where volatile is the real thing). For RAM globals it is NOT evidence that the memory is volatile.
  If those symbols move into a shared header later, declarations must be reconciled.
- **A32 raw thumb function-pointer literals** (Claude, 2026-10-13). Matched C may store a thumb function's address as
  the raw odd literal (`0x08003B95` = sub_08003B94 | 1, in sub_08003B58) because C linking `sub_08003B94` gives the even
  address. Correct for this ROM; breaks silently if code ever moves. A `global.h` convention can replace it later.
- **A33 call-through prototypes** (Claude, 2026-10-13). `sub_08038E24` is a bare `bx r0` (call the pointer in r0);
  its `void sub_08038E24(u32)` prototype is a guess, the pointer slot `gUnk_0201CB24` is set by sub_08003B58.
- **A34 per-file prototypes** (Claude, 2026-10-13). Each `src/funcs/*.c` declares its own callees and externs, so the
  same symbol can carry different types in different files (e.g. `sub_080061A8` is `u32` where defined, `void` in
  sub_08006220.c; `gUnk_0201FCC0` is `u8[]` in most files, `u16[]` in sub_080044A4/FC). Byte-safe today (separate
  compilation units, unused results); to unify when a shared header is introduced (follow-up, not started).
- **A35 unlisted functions inside an extent** (critic, batch J0134–J0143). `config/functions.csv` gives sub_080073E4 an
  extent of 32 bytes, but bytes 0x080073F4..0x08007403 are another small table-lookup function with no row of its own
  (`0004 0249 800b 4018 0068 7047 …`). Matching is unaffected (build_matched copies the tail with `.incbin`); the
  function list should be split there (follow-up: scan extents for a second `bx lr`/`push` start). Also: two bare
  `bx lr` stubs at 0x08009248 and 0x0800924C inside sub_08009224's extent (critic, batch J0144–J0153).
