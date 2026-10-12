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
- **A3** — the compiler that built the THUMB C code is guessed to be an old GNU/agbcc-class compiler
  (evidence: `pop {…}` + `bx rN` returns in 85 of 155 THUMB functions, only one `pop {…, pc}`; ARM
  startup stub; direct BIOS `svc` calls instead of a C library). Not proven — ARM's own `armcc` is
  not excluded. Decisive test: compile one function with `agbcc` and byte-compare (milestone Y5).
  Marked in `docs/rom-map.md` §3. (2026-10-12)
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
