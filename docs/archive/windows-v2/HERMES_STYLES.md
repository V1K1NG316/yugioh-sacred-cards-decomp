# Brief for Hermes on DeepSeek: STYLE VARIANTS (Matter_Scatter's idea, written by Claude, 2026-10-14)

You get medium functions (64-160 bytes) whose first draft did NOT match. The permuter is good at small rewrites
(operand order, temporaries, statement order) but cannot change the *shape* of the code. Your job is to give it
different shapes to start from. `HERMES_DRAFTER.md` rules (worktree, never commit, never write into the main
checkout's src/) still apply.

For each function `<name>` in your list:
1. Read `D:/Yugioh_DeComp_V2/private/asm/funcs/<name>.s`, the current draft `D:/Yugioh_DeComp_V2/private/drafts/<name>.c`
   and its last diff `D:/Yugioh_DeComp_V2/private/drafts/<name>.log` if present, and `private/drafts/NOTES.txt`.
2. Write **3 to 5 variants** `D:/Yugioh_DeComp_V2/private/drafts/<name>.v1.c` ... `.v5.c`, each a complete matching-C
   candidate in a genuinely DIFFERENT style, e.g.:
   - if/else chain vs `switch` (with explicit empty cases) vs early returns
   - `for` vs `while` vs `do/while` loops; index vs pointer walking
   - a struct for a block of related fields vs an array vs separate globals
   - one expression vs named temporaries; signed vs unsigned types; u8/u16 locals vs int
   - helper values computed before vs inside the call
   Each must keep the asm's behaviour exactly. Test each once from your worktree (`PY tools/match_func.py <name>`
   after copying it to your worktree's `src/funcs/<name>.c`; delete it afterwards). If a variant MATCHes, also copy it
   to `D:/Yugioh_DeComp_V2/private/drafts/<name>.c` (keep the old one as `<name>.c.orig` if that does not exist yet).
3. Append rows `name<TAB>variant<TAB>matched(y/n)<TAB>bytes differing` to
   `D:/Yugioh_DeComp_V2/private/drafts/rows_<batch>.tsv`.

Finish with `D:/Yugioh_DeComp_V2/private/drafts/report_<batch>.md` (matched functions, which style won, minutes). Stop.
Claude then runs the permuter on every variant of every function that still misses.
