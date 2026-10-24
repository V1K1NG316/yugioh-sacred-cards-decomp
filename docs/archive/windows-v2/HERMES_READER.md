# Brief for Hermes on DeepSeek as a READER (Track B: readable game; written by Claude, 2026-10-14)

Matter_Scatter wants two results: the byte-perfect matching decomp (Track A, other briefs) AND a readable, explained
version of the whole game (Track B, this brief) — "understand it fully, mod it, rebuild it". Track B does NOT need to
match bytes. It must be faithful to what the code does and honest about what is a guess.

You get a list of functions. Your worktree is in your prompt (`HERMES_DRAFTER.md` rules: never commit, never write
into `D:/Yugioh_DeComp_V2/src`, never touch ops/tools/scripts/config).

For each function `<name>`:
1. Read Ghidra's decompilation `D:/Yugioh_DeComp_V2/private/ghidra/<name>.c` and, when it is unclear, the asm
   `D:/Yugioh_DeComp_V2/private/asm/funcs/<name>.s`. Use what is already known: `docs/game-data.md` (card tables,
   duel table, text tables, prize rules), `docs/rom-map.md`, existing readable files of callers/callees in
   `D:/Yugioh_DeComp_V2/private/readable/`, and GBA hardware registers (0x04000000 DISPCNT, 0x04000130 KEYINPUT,
   0x040000D4 DMA3, ...).
2. Write `D:/Yugioh_DeComp_V2/private/readable/<name>.c`:
   - first line: `// <proposed_name> — <one-line purpose> [confidence: high|medium|low]`
   - then the function as clean, readable C: real variable names, structs/enums where obvious, comments for magic
     numbers and GBA registers, Ghidra noise removed (`undefined4`, `in_lr`, casts that do nothing). Keep the
     original `<name>` as the function name and put the proposed name in the comment, so files stay linkable.
3. Append `<name><TAB><proposed_name><TAB><confidence><TAB><one-line purpose>` to
   `D:/Yugioh_DeComp_V2/private/readable/names_<batch>.tsv`.
Proposed names: lower_snake_case, verb first (`load_card_name`, `draw_duel_field`), unique; `unknown_<addr>` is fine
when you cannot tell. Never invent game facts: if a purpose is a guess, say so and use low confidence.

Work fast: tiny wrappers need one line of thought. Spend effort on the functions that hold game logic.
Finish with `D:/Yugioh_DeComp_V2/private/readable/report_<batch>.md`: counts per confidence, the 5 most interesting
findings (game rules, data formats), minutes spent. Then stop.
