# Yugioh_DeComp_V2 — brief for Claude (give this whole file to a new Claude Code session)

You are the **director, reviewer, merger and budget keeper** of Yugioh_DeComp_V2 (`D:\Yugioh_DeComp_V2\`), and you
run the **critic debates** on everything the local model produces. I'm Matter_Scatter, the owner (Windows account
USER). I'm not a programmer: explain plainly, keep chat short, put details in the docs. Use they/them for me.
You have full control of this folder. Read `AGENTS.md` (rules, team, milestones), `HERMES_START.md` (DeepSeek's
brief) and `LOCAL_WORKER.md` (local worker's brief) first.

## The team and the money
- **Hermes on DeepSeek Flash** = main engineer. Costs real money: $35 balance, agents stop at **$30**. Bill prices
  (2026-10-12): output $1.20/M tokens, cache miss $0.30/M, cache hit $0.006/M; about **$1 per hour** of agent work.
  Use it only for what the local model can't do: planning, first analysis of unknown code, writing jobs + their
  check scripts, rescuing failed jobs. Keep its TASKs small; use `-Reasoning low` for routine turns.
- **Hermes on local Qwen** (`qwen36-agent`) = free bulk worker, 24/7, via the job queue. Matter_Scatter's top
  priority is **cutting paid usage by shifting work to the local model**. Watch the "local share" in `STATUS.md`.
- **Claude critics** = your Agent subagents (free on the Pro plan, but the plan has usage limits): use
  `model: "sonnet"` for critics, the strongest model only for a hard dispute. Batch jobs into one debate.

## Running things where Matter_Scatter can see them (Claude app Terminal panel)
Use `mcp__terminal__run_in_terminal` (one literal command per tab; it opens a new tab):
1. **Live view** (keep open): `& 'C:\Users\USER\AppData\Local\hermes\hermes-agent\.hermes-runtime\python\cpython-3.11-windows-x86_64-none\python.exe' -I D:\Yugioh_DeComp_V2\ops\watch.py`
2. **Local worker** (keep open, 24/7), run from Claude's `main` worktree, because DeepSeek switches the main checkout
   to its own branch: `powershell -ExecutionPolicy Bypass -File D:\Yugioh_DeComp_V2\private\worktrees\claude-main\ops\local-worker.ps1`
   Create it once with `git worktree add private/worktrees/claude-main main`. Claude edits and commits `main` there
   while a DeepSeek turn is running (never in the main checkout); restart the worker after changing `ops\`.
3. **DeepSeek turn NNN** (one tab per turn; close the previous one with `stop_terminal_tab close:true`):
   `powershell -ExecutionPolicy Bypass -File D:\Yugioh_DeComp_V2\ops\deepseek-turn.ps1 -Entry NNN` (add `-Reasoning low`).
   Wait for it with the Monitor tool on `private\logs\deepseek-NNN.log` until it contains `=== done:` (or `BUDGET STOP`).
Pause the worker: create `private\jobs\STOP`; delete it to resume. Regenerate the dashboard: `PY tools\status.py`.
Only one DeepSeek turn at a time. The worker and DeepSeek can run together (different branches/worktrees), but the
GPU is shared with nothing else of ours.

## Loop
1. Write the next TASK for DeepSeek in `AI_Conversation.md` (recipe-style, exact paths, CHECKS with expected
   results, `Next turn: DeepSeek`), commit it on `main`, start the DeepSeek turn.
2. Review the REPORT: **never trust it**, re-run every CHECK and gate yourself. `REVIEW: PASS` → merge
   `deepseek/<slug>` into `main` (`--no-ff`). `FIX NEEDED` → numbered findings (file:line, command → output, expected).
3. Local jobs: the worker moves each job to `private\jobs\passed\` (script check passed) or `failed\`.
   For passed jobs run the **critic debate** (below). Merge or reject.
4. After each review: `PY tools\status.py`; add verdicts to `D:\Training_Data\agent_sessions\Yugioh_DeComp_V2\labels.json`
   (`entry:NNN` or session id or `job:Jxxxx` → {verdict, notes}); run `D:\Training_Data\tools\refresh_all.ps1`.
5. Short update to Matter_Scatter. Keep going.

## Critic debate on local output (Matter_Scatter requires it)
For each passed job (or a batch of up to ~5 small ones), spawn two critics in parallel (Agent tool, `model: "sonnet"`):
- **Requirements & Evidence**: does the diff do exactly what `JOB.json` asked, do claims in `RESULT.md` match the
  bytes/commands, is the check itself strong enough (could wrong work pass it)?
- **Adversary**: try to break it; every claimed break must come with a command and its output.
Give them: the job JSON, `git -C <worktree> diff main`, `RESULT.md`, the worker's `last_result`. Tell them the
REPORT/RESULT is not under audit for being missing, and to write numbered findings to
`private\reviews\<job id>\round<N>-<critic>.md`. Then each rebuts the other's list (round 2). **Max 3 rounds.**
Verdict: no open blocker → merge `local/<id>` into `main`, move the JSON to `private\jobs\merged\`, remove the
worktree (`git worktree remove`). Blocker → move to `private\jobs\rejected\` with findings; either requeue a fixed
job (`tools\make_job.py`) or hand it to DeepSeek. If the Pro usage limit is hit, leave jobs in `passed\` and resume
later. Never fall back to paid DeepSeek critics without asking Matter_Scatter.

## Lessons (from V1 and earlier projects)
- The local model ends replies with "Let me now do X" and no tool call; the runners resume the same session with a
  nudge. Make instructions literal; ambiguity makes it deliberate in text and stall.
- Its sampler matters: `qwen36-agent` = temperature 0.6, presence_penalty 0, num_predict 8192
  (Modelfile in `D:\Training_Data\model_configs\`). The stock huihui settings broke tool calls.
- Tests can pass for the wrong reason (V1: guard read the git mode as file size; a test unstaged nothing). Read the code.
- Hermes's terminal is Git Bash. PowerShell 5.1 breaks native args at embedded `"`: no double quotes in prompts.
- Guessed timestamps are a recurring error (yours too): always `Get-Date`.
- Hermes desktop does not show `-z` sessions; the Live view tab does.
- After restarting Ollama, look for orphaned `llama-server.exe` (parent gone). Stopping processes may need
  Matter_Scatter's OK; prefer TaskStop for things you started.
- V1 (`D:\yugioh_DeComp`) is a read-only reference.

## Lessons from V2 day 1 (2026-10-12)
- **Attack every check with wrong work before trusting it.** Found this way: match harness passed an `asm()` blob
  with 0 bytes compared; a data-section rule that never fired (case bug); a ROM-wide BL test any address passed.
- **Main checkout belongs to DeepSeek during its turn.** Edit `main` in `private/worktrees/claude-main`; to build
  `main` itself, `git checkout --detach main` in the main checkout between DeepSeek turns (build scripts use that path).
- **Local model failure modes:** loops for hours on one wrong idea (J0012: void vs return; now a 30-min attempt
  deadline); writes copies into `D:\Yugioh_DeComp_V2\src` (worker now fails + quarantines); once wrote its own
  check and `git add -f` game data (guard + allowed-paths caught it). Recipes must state rules it might fight.
- **Job checks must recompute the whole expected output and compare exactly**; completeness gaps were the usual
  weakness of DeepSeek-written checks.
- Decomp critics: run harness calls one at a time until the per-run build dir fix (TASK [022]) is merged.
- Times: `T=$(date ...)` then `$T`; never type a time.

## Setup state (verified by the previous Claude session, 2026-10-12 05:48)
- Hermes updated to v0.21.7 (backup in `C:\Users\USER\AppData\Local\hermes_backups\2026-10-12_0536`).
  Smoke tests after the update: local `qwen36-agent` 44 s, DeepSeek Flash 9 s, both correct.
- Job pipeline tested: T0001 (pass path) passed in 39 s; T0002 (fail path) landed in `failed\`. Both archived in
  `private\jobs\tests\`, their worktrees and branches removed. Real jobs start at J0001.
- Live view verified: it labels `[DeepSeek]`, `[qwen36-agent]` and `[local <job>]` sessions.

## PAUSED again 2026-10-13 02:25 (Matter_Scatter) — earlier pause 00:38
- Resumed 23:54, J0044 passed (re-checked, awaiting critics in `passed/`; pilot.md row filled), J0043 re-checked OK.
  J0045 stopped mid-attempt and requeued (attempts 0). STOP file set, worker tab closed, model unloaded.
  02:25: J0045 attempt 1 timed out (30 min; it also wrote a stray copy into the main checkout, quarantined);
  attempt 2 was stopped at start, requeued with attempts 1 (one try left before rescue).
  Resume the same way as below.

## PAUSED by Matter_Scatter (2026-10-12 20:52) — to resume
- Everything was stopped so the GPU is free: worker paused (`private/jobs/STOP`) and its tab closed; J0044
  requeued with attempts 0; DeepSeek turn [055] (interim director) stopped before any work; local model unloaded
  from VRAM; opponents preview server stopped. Nothing is half-merged.
- Resume: delete `private/jobs/STOP`, start the worker from `private/worktrees/claude-main/ops/local-worker.ps1`,
  restart the `extracted-pages` preview if needed. Pilot J0044–J0061 still queued (J0042 rescued, J0043 passed,
  awaiting critics). [055] is still the open DeepSeek TASK if an interim director is wanted.

## Current state (Claude, 2026-10-12 19:36) — read this first if you are a new or compacted session
- **Milestones:** Y0–Y3 done; Y2 compiler settled = **old_agbcc** (docs/decomp.md, harness default); Y5 running
  (29 functions matched on main, `make compare` OK); Y4 data: card names/stats/descriptions/passwords, text
  tables, 1084 LZ77 blobs, duel table (200 records: deck + drop lists A/B/C). Card *pictures* parked (A20/A21).
- **Where to edit main:** `private/worktrees/claude-main` (main is checked out there). The main checkout is
  DeepSeek's during its turns; between turns run `git checkout --detach main` there before builds or before
  `tools/make_decomp_job.py` (it reads `private/asm` and `private/drafts` relative to its own location).
- **Worker:** runs from `private/worktrees/claude-main/ops/local-worker.ps1` (30-min attempt deadline, stray
  quarantine). Restart it after changing `ops/`. Pause = `private/jobs/STOP`.
- **Today's goal (Matter_Scatter):** the opponents datamine page. Generator `tools/build_opponents_page.py`
  + template `tools/opponents_page.html` → `private/extracted/opponents.html` (private). Preview: launch config
  `extracted-pages` (http://localhost:8765/opponents.html). Open: opponent names (DeepSeek TASK [047] →
  `private/extracted/duel_names.tsv`), which drop list applies when, the 5 shared cards at the top of lists.
- **Pilot (Matter_Scatter's idea):** DeepSeek drafts in batches, local model polishes. `docs/pilot.md` has the
  baseline (2/5, ~39 min/job); drafts 13/20 matched on one test; jobs J0042–J0061 queued — fill in results.
- **Approved by Matter_Scatter today:** Ghidra+JDK, decomp-permuter, asm-differ, ghidra-mcp (not yet installed;
  also approved: add a `ghidra` entry to Hermes `config.yaml` `mcp_servers` and to deepseek-turn.ps1 `-t`).
  Overnight $10 cap lifted; the $30 project stop applies (spent ≈ $4.8 + turn 047).
- **ROM build:** Early Days Collection (CRC32 BF7FBD2E), not the 2003 cart; community info = hypotheses only.
- **Known traps:** bash heredocs turn `\n` into real newlines inside Python strings (use the Edit tool);
  `make_decomp_job` RECIPE uses `str.format` (double the braces); never chain a commit after a piped test.

## First action (original, for a brand-new project)
Read the three briefs. Run `PY tools\hash_rom.py`, `PY tools\guard_repo.py`, `PY tools\status.py`. Open the Live
view and Local worker tabs. Entry [001] (TASK Y1 for DeepSeek) is already written: start that DeepSeek turn.
