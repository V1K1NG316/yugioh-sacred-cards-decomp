# Rules for Yugioh_DeComp_V2 (all agents)

Owner: **Matter_Scatter** (Windows account `USER`; **not a programmer**; use they/them; plain language).
Hermes cannot write this file (protected-file guard). Propose changes in a REPORT; Claude edits.

## 0. Team
| Role | Who | Brief |
|---|---|---|
| Director, reviewer, merger, budget keeper; runs the critic debates | **Claude Code** | `CLAUDE_START.md` |
| Main engineer: hard reverse engineering, plans and creates local jobs | **Hermes on DeepSeek Flash** (`deepseek-v4-flash-vision-exp`) | `HERMES_START.md` |
| Bulk worker: small, script-checked jobs, 24/7 | **Hermes on local Qwen** (`qwen36-agent` in Ollama) | `LOCAL_WORKER.md` |
| Judge of anything checkable | **check scripts** (byte match, hash, round trip, tests) | job `check` field |
| Critics on every local output | **Claude subagents** (two critics + rebuttal, max 3 rounds) | `CLAUDE_START.md` |

**Cost rule:** local first. DeepSeek costs real money ($35 balance; agents stop at $30 spent, see `STATUS.md`).
DeepSeek does only what the local model cannot: planning, first analysis of unknown code, splitting work into jobs,
and rescuing jobs the local model failed twice. Anything repeatable becomes a local job.

## 1. Hard rules
1. `rom\sacred_cards_usa.gba` is the read-only original (SHA-1 `d3710031520d9cdae70d870c60b1667285fe5230`).
   Work from `private\baserom.gba`. `tools\hash_rom.py` must pass after every task and job.
2. **No game-derived file in git**: ROM, saves, generated disassembly, extracted graphics/text/tables, builds.
   They live in `private\`. Git holds authored files only: scripts that generate things, symbol/function lists in
   `config\`, docs, hand-written asm/C. `.gitignore` is a whitelist; check new files with
   `git check-ignore -q <file>; echo $?` (0 = ignored, 1 = tracked). `tools\guard_repo.py` checks the index.
3. Agents write **only inside `D:\Yugioh_DeComp_V2\`** (local jobs: only inside their own worktree, only the job's
   `allowed_paths`). Other folders on the PC are read-only.
4. **No system-wide installs** without Matter_Scatter's approval (one batched QUESTION: name, version, size, path).
   Python packages may go in `private\venv`.
5. Kill processes by exact PID only. No `--yolo`. No wiping folders.
6. **Numbers, not vibes.** Every claim has the command and its real output. Times come from `date` / `Get-Date`.
7. Small edits (files written in pieces under ~150 lines). Prefer a script to reasoning about bytes in your head.
8. Nothing is shared or published. Community open-source tools are allowed; record them in `docs\credits.md`.

## 2. Branches and flow
- `main` is Claude's. DeepSeek works on `deepseek/<task-slug>`; local jobs on `local/<job-id>` in
  `private\worktrees\<job-id>`. Claude merges.
- DeepSeek turn: read the last TASK in `AI_Conversation.md`, do it, append REPORT, commit, stop.
- Local job: `ops\local-worker.ps1` runs it; the worker's own check decides pass/fail; passed jobs then face the
  Claude critic debate; Claude merges or rejects.

## 3. Milestones
| ID | Goal | Done test |
|----|------|-----------|
| Y0 | Repo, guard, hashes, ops scripts | guard + hash pass (done by Claude 2026-10-12) |
| Y1 | Shell build: `make compare` rebuilds the ROM byte-identical | SHA-1 of `private\build\yugioh.gba` = original |
| Y2 | ROM census: entry, code vs data ranges, libraries, compiler identified with evidence | `docs\rom-map.md`, first `config\functions.csv` |
| Y3 | Disassembly: generated asm per function in `private\asm\`, data `.incbin`, still byte-identical | `make compare` passes; function count |
| Y4 | Game data: cards, text, decks, graphics decoded by `tools\` extractors into `private\extracted\` | round-trip tests + in-game spot checks |
| Y5 | Matching C: functions decompiled to C that compile byte-identical | `make compare` with C linked; % matched |

## 4. Layout
```
AGENTS.md CLAUDE_START.md HERMES_START.md LOCAL_WORKER.md README.md STATUS.md MODLOG.md AI_Conversation.md
docs\      rom-map.md credits.md tools.md approximations.md jobs.md
config\    functions.csv symbols.csv
tools\     hash_rom.py guard_repo.py test_guard.py make_job.py status.py deepseek_spend.py ...
ops\       deepseek-turn.ps1 local-worker.ps1 watch.py common.ps1   (how agents are run)
scripts\   build / compare / check scripts (.sh, LF endings)
asm\ src\ include\   hand-written asm / C
rom\       original ROM (read-only, untracked)
private\   untracked: baserom.gba, build, generated asm, extracted data, jobs, worktrees, logs, reviews, venv
```

## 5. Gates (before every REPORT; report any gate not run as "not run")
1. `PY tools\guard_repo.py` → 0 failures.  2. `PY tools\hash_rom.py` → exit 0.
3. From Y1 on: `make compare` (WSL) passes.  4. `git check-ignore -q` on every new file.

## 6. Log formats
- `AI_Conversation.md` (append-only): `## [NNN] Author → Recipient — YYYY-MM-DD HH:MM — subject`; sections
  TASK / REPORT / REVIEW / QUESTION; last line `Next turn: X`. Authors: Claude, DeepSeek, Matter_Scatter.
- `MODLOG.md`: dated, append-only: change + exact command + pasted output.
- `docs\approximations.md`: every labelled guess (A1..An), also marked where used.
- `docs\jobs.md`: DeepSeek keeps a short log of job batches it created (ids, purpose).
