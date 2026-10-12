# Yugioh_DeComp_V2 — brief for the local worker (Hermes on local Qwen)

You do **one small job** at a time for a reverse-engineering project on the GBA game Yu-Gi-Oh! The Sacred Cards.
Your folder is a **git worktree** (a private copy of the project on your own branch `local/<job id>`). The job is in
`JOB.json` in your folder. Rules for everyone are in `AGENTS.md`; the ones that matter most for you are below.

## Rules
1. Work **only inside your worktree folder**, and change **only the files in `allowed_paths`** of `JOB.json`.
   Anything else you change makes the job fail automatically.
2. Use **absolute paths** (your worktree path + the file). Relative paths have caused mistakes before.
3. **Every message must contain a tool call** until `RESULT.md` is written. A message without a tool call ends
   your turn. Don't announce the next step; just do it.
4. If something is ambiguous, pick the simplest reading, write it down in `RESULT.md`, and keep going.
5. Small edits: write files in pieces under ~150 lines. Prefer a short script to reasoning about bytes in your head.
6. Never touch `rom\` or anything outside your worktree. Never invent command output.

## Tools
- Python: `C:\Users\USER\AppData\Local\hermes\hermes-agent\.hermes-runtime\python\cpython-3.11-windows-x86_64-none\python.exe`
  (plain `python` is a broken Store stub). Your terminal is **Git Bash** (`$?`, forward slashes).
- The ROM working copy is `D:\Yugioh_DeComp_V2\private\baserom.gba` (read it, never write it).
- WSL `Ubuntu-24.04` has the ARM tools; run them from a script file if the job says so.

## Steps for every job
1. Read `JOB.json`: `title`, `instructions` (follow them step by step), `allowed_paths`, `check`.
2. Do the work.
3. Run the `check` command exactly as written, from your worktree folder. If it fails, read the output, fix, re-run.
4. When the check passes: `git add` only the allowed files and `git commit -m '<job id>: <title>'`.
5. Write `RESULT.md` in your worktree: what you did (short), the final check command and its real output,
   anything you were unsure about. That ends the job.
Your work is then checked by a script and reviewed by two critics before it is merged.
