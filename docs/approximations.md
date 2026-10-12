# Approximations

Every labelled guess (A1..An) and where it is marked.

- **A1** — `tools/find_functions.py` is a linear-scan heuristic, not a data-flow analysis: it decodes
  instructions from a function start and stops at a return or an unconditional branch, so a function
  that stores code in a jump table may be cut short. Function *starts* it reports are still backed
  by a real `BL`/`BLX` instruction or by an entry point. Marked in `docs/rom-map.md` §4 and in the
  script's docstring. (2026-10-12)
- **A2** — a target seen only as a pointer value loaded from a literal pool (`ldr rX,[pc,#imm]` … `bx
  rX`) is *not* written to `config/functions.csv` and is not walked into: such a word can be data.
  13 such values were skipped in the 2026-10-12 census. Marked in `tools/find_functions.py` and
  `docs/rom-map.md` §4. (2026-10-12)
- **A3** — the compiler that built the THUMB C code is guessed to be an old GNU/agbcc-class compiler
  (evidence: `pop {…}` + `bx rN` returns in 85 of 155 THUMB functions, only one `pop {…, pc}`; ARM
  startup stub; direct BIOS `svc` calls instead of a C library). Not proven — ARM's own `armcc` is
  not excluded. Decisive test: compile one function with `agbcc` and byte-compare (milestone Y5).
  Marked in `docs/rom-map.md` §3. (2026-10-12)
