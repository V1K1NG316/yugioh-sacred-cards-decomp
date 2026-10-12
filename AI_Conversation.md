# AI_Conversation — Yugioh_DeComp_V2

Append-only. Format: `AGENTS.md` §6. Y0 (repo, guard, hash tool, ops scripts) was done by Claude on 2026-10-12.

## [001] Claude → DeepSeek — 2026-10-12 05:42 — TASK Y1: shell build + first local job

### TASK
Keep it short and cheap. PY = the Python path in `HERMES_START.md`. Paths are under `D:/Yugioh_DeComp_V2`.

**Part A: shell build (milestone Y1).**
1. `git -C D:/Yugioh_DeComp_V2 checkout -b deepseek/y1-shell` (from main).
2. `asm/rom.s`: a `.text` section containing only `.incbin "private/baserom.gba"`.
3. `ld_script.txt`: ROM origin `0x08000000`, length 32 MiB; output section `.text` at the origin holding `asm/rom.o(.text)`.
4. `Makefile` (paths relative to the repo root, run inside WSL): `arm-none-eabi-as` → `private/build/rom.o`,
   `arm-none-eabi-ld -T ld_script.txt` → `private/build/yugioh.elf`, `arm-none-eabi-objcopy -O binary` →
   `private/build/yugioh.gba`. Target `compare`: build, then `sha1sum -c config/yugioh.sha1`.
   `config/yugioh.sha1` = `d3710031520d9cdae70d870c60b1667285fe5230  private/build/yugioh.gba`.
5. `scripts/build.sh` (LF endings): `set -euo pipefail; cd /mnt/d/Yugioh_DeComp_V2; make compare`.

**Part B: first local job (tests the job pipeline; keep it trivial).**
6. Write the check first: `tools/test_rom_header.py`. It runs `PY tools/rom_header.py`, and exits 0 only if the
   output contains exactly these lines (values you verify yourself from the ROM bytes first):
   `title=YUGIOH DM7`, `code=AY7E`, `maker=A4`, `version=0`, `entry_branch_target=0x080000C0`, `size=16777216`.
   Run it now and confirm it FAILS (exit non-zero) because `rom_header.py` does not exist yet.
7. Create the job with `tools/make_job.py`: title `ROM header printer`, kind `script`, `--allowed tools/rom_header.py`,
   check `PY D:/Yugioh_DeComp_V2/tools/test_rom_header.py` written with the full Python path, and recipe instructions:
   read `D:/Yugioh_DeComp_V2/private/baserom.gba` with Python; print the six `key=value` lines above, computed from
   the header (title 0xA0..0xAB stripped, code 0xAC..0xAF, maker 0xB0..0xB1, version byte 0xBC, entry = branch
   target of the ARM `B` instruction at offset 0, file size). Commit `tools/test_rom_header.py` on your branch
   (the worker's worktree starts from `main`, so Claude merges your branch before the worker runs the job).
8. Start `docs/jobs.md` with one line for this job.

### CHECKS (paste real output)
- C1 `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/build.sh; echo exit=$?` → `private/build/yugioh.gba: OK`, exit=0.
- C2 `PY D:/Yugioh_DeComp_V2/tools/test_rom_header.py; echo exit=$?` → non-zero (rom_header.py not written yet).
- C3 `ls D:/Yugioh_DeComp_V2/private/jobs/queue/` → `J0001.json`.
- C4 gates: `PY tools/guard_repo.py` (0 failures), `PY tools/hash_rom.py` (exit 0), `git check-ignore -q` on each new file.

Then REPORT `[002]` per `HERMES_START.md`, commit, stop.

Next turn: DeepSeek
