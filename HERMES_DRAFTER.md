# Brief for Hermes on DeepSeek as a parallel DRAFTER (written by Claude, 2026-10-14)

Several drafters run at the same time, each in its own worktree `D:/Yugioh_DeComp_V2/private/worktrees/ds-<batch>`
(a detached copy of `main`). You are one of them. `AGENTS.md` rules still apply. Your batch name and function list
are in your prompt.

## Do
For each function `<name>` in your list:
1. Read `D:/Yugioh_DeComp_V2/private/asm/funcs/<name>.s` (and `D:/Yugioh_DeComp_V2/private/ghidra/<name>.c` if present).
2. Write your best matching-C guess to `D:/Yugioh_DeComp_V2/private/drafts/<name>.c`: `#include "global.h"`, plain C,
   only that function, callees declared per their own epilogue (`pop {r0}; bx r0` = void), u8/u16 args from the
   `lsls/lsrs #0x18/#0x10` pairs, `gUnk_<8 hex>[]` symbols for fixed addresses. Read
   `D:/Yugioh_DeComp_V2/private/drafts/NOTES.txt` first: it lists every fix that worked so far (volatile, switch with
   empty cases, call-argument load order, extern arrays, `do {} while (0)`, b*32 not b>>3, ...).
3. Test it from YOUR worktree: copy it to `src/funcs/<name>.c` in your worktree, run
   `PY tools/match_func.py <name>`, then delete `src/funcs/<name>.c` again. Up to 2 tests; on a miss that is only
   register choice, stop (Claude runs the permuter on every miss); spend more tests only on structural misses.
4. Append one row per function to `D:/Yugioh_DeComp_V2/private/drafts/rows_<batch>.tsv`:
   `name<TAB>tested(y/n)<TAB>matched(y/n)<TAB>bytes differing` and keep the last diff of a miss in
   `D:/Yugioh_DeComp_V2/private/drafts/<name>.log`.
Generator scripts for one repeated shape are fine (as in batches 5-8) if they refuse anything outside that shape.

## Never
- Commit anything, create branches, edit `AI_Conversation.md`, `AGENTS.md`, `ops/`, `tools/`, `scripts/`, `config/`.
- Write into `D:/Yugioh_DeComp_V2/src` (the main checkout) or another drafter's worktree.
- Run `make compare` (Claude does it) or the permuter.

## Finish
Write `D:/Yugioh_DeComp_V2/private/drafts/report_<batch>.md`: matched count, the misses with bytes differing, shapes
that failed, minutes spent. Then stop. Your worktree's `git status --short` must be empty at the end.
