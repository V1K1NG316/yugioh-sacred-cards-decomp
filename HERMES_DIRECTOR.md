# Interim director rules for Hermes on DeepSeek (while Claude is unavailable)

Written by Claude, 2026-10-12, at Matter_Scatter's request. These rules apply ONLY to a turn whose TASK says
"interim director". Everything in `AGENTS.md` and `HERMES_START.md` still applies. When in doubt: do less, write
it down, stop. Claude reviews everything you did when back.

## Your job in this mode
Keep the local pipeline moving: review finished local jobs, merge the good ones, park the rest. Nothing else.

## The loop (repeat until no job is left in `private/jobs/passed/` or the budget below is reached)
For the oldest JSON in `D:/Yugioh_DeComp_V2/private/jobs/passed/` (job `Jxxxx`, worktree `private/worktrees/Jxxxx`):
1. `git -C private/worktrees/Jxxxx diff --name-only --merge-base main` must list ONLY the job's `allowed_paths`.
   `git -C private/worktrees/Jxxxx ls-files private JOB.json RESULT.md` must print nothing.
2. Re-run the job's `check` yourself from inside the worktree → must exit 0 (paste the last line).
3. Decompile jobs only: read the C. Plain C, no `asm`, only that one function, `#include "global.h"`; return type
   and every callee's declared type match the epilogues (`pop {r0}; bx r0` = void). If a type is wrong but a
   corrected version still MATCHes, fix it in the worktree, re-check, commit there.
4. Merge in Claude's worktree (never in the main checkout):
   `git -C D:/Yugioh_DeComp_V2/private/worktrees/claude-main merge --no-ff local/Jxxxx -m "Merge local/Jxxxx (interim review by DeepSeek)"`
5. Clean up: copy `RESULT.md` to `private/reviews/Jxxxx/RESULT.md`, delete it from the worktree,
   `git worktree remove private/worktrees/Jxxxx`, `git -C private/worktrees/claude-main branch -d local/Jxxxx`,
   move the JSON to `private/jobs/merged/`.
6. Anything that fails 1–3 and you cannot fix with a one-line type change: move the JSON to `private/jobs/rejected/`
   with a short `review_note` field. Do not rescue functions yourself in this mode.
After every 5 merges, from the main checkout (`git checkout --detach main` first, only if no other DeepSeek work is
on it): `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- make compare` must print `OK`. If not: stop, write it up.

## Pilot bookkeeping
For every pilot job (`[pilot]` in the title) add a row to the Results table in `docs/pilot.md` (in claude-main):
job, function, draft as written (see `private/drafts/summary.tsv`), local result, GPU minutes (worker log times),
notes. Failed pilot jobs: list them, do not fix them.

## Hard limits in this mode
- Budget: stop when this turn has spent about **$1.50**, or the project total reaches **$9**.
- Do NOT: edit `ops/`, `tools/match_func.py`, `scripts/`, `config/`, `AGENTS.md`, `CLAUDE_START.md`, Hermes's
  `config.yaml`; download anything; start or stop the worker; queue new jobs; touch `rom/`; delete folders;
  `git push`; `--force` anything; kill processes except your own by exact PID.
- Times come from `date`, never typed.

## At the end
Append REPORT `[NNN] DeepSeek → Claude — <date> — REPORT interim director` to `AI_Conversation.md` (in
claude-main): jobs merged / rejected (ids + one line each), pilot table status, `make compare` result, spend,
anything odd. Commit it in claude-main. Stop.
