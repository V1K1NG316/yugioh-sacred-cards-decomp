# MODLOG — Yugioh_DeComp_V2

## 2026-10-12 05:42 — Y0 setup (Claude)
- Copied the ROM from V1 (`D:\yugioh_DeComp\Yu-Gi-Oh! - The Sacred Cards (USA) (Early Days Collection)\...gba`) to
  `rom\sacred_cards_usa.gba` (set read-only) and `private\baserom.gba`. Both SHA-1 `D3710031520D9CDAE70D870C60B1667285FE5230`.
- Ported from V1 (paths updated): `tools\hash_rom.py`, `tools\guard_repo.py`, `tools\test_guard.py`.
  `hash_rom.py` → both OK, exit 0. `test_guard.py` → case 1/2/3 PASS, exit 0.
- New: `ops\` (deepseek-turn, local-worker, watch, common), `tools\` make_job, status, deepseek_spend,
  newest_session, backup_hermes. Hermes backed up to `C:\Users\USER\AppData\Local\hermes_backups\2026-10-12_0536`
  (478 files, 143.3 MB, Hermes commit 93f108e) before `hermes update`.
- DeepSeek prices taken from Matter_Scatter's usage export (2026-09-13..10-12): after the 2026-10-11 change, flash =
  output $1.20/M, cache miss $0.30/M, cache hit $0.006/M.

## 2026-10-12 05:54 — Y1 shell build (DeepSeek, branch `deepseek/y1-shell`)
- New: `asm/rom.s` (`.incbin "private/baserom.gba"`), `ld_script.txt`, `Makefile`, `config/yugioh.sha1`,
  `scripts/build.sh`, `tools/test_rom_header.py`; `docs/jobs.md` started with job `J0001` (ROM header printer).
- Command: `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/build.sh`
  → `arm-none-eabi-as` / `arm-none-eabi-ld -T ld_script.txt` / `arm-none-eabi-objcopy -O binary`,
  then `sha1sum -c config/yugioh.sha1` → `private/build/yugioh.gba: OK`, exit 0 (16777216 bytes, after `make clean` too).
- Gates: `guard_repo.py` 25 files, 0 failures; `hash_rom.py` ORIGINAL+BASEROM OK; new files tracked (check-ignore = 1).
- Job `J0001` queued (`private/jobs/queue/J0001.json`), max 2 attempts. Worker is paused while `private/jobs/STOP` exists.

## 2026-10-12 06:03 — Claude: worker judged jobs against current main (J0001 false fail)
- Symptom: J0001 check passed (`test_rom_header: OK`) but both attempts failed with `outside allowed: AI_Conversation.md`.
- Cause: `ops/local-worker.ps1` line 56 used `git diff --name-only main`; Claude committed [004] to main while the job ran.
- Evidence: `git diff --name-only main...local/J0001` → `tools/rom_header.py` only.
- Fix: `git diff --name-only --merge-base main` (commit 2663546). Test on the J0001 worktree → `tools/rom_header.py`.
- J0001 requeued (attempts reset; failed copy archived as `private/jobs/tests/J0001.failed-judge-bug.json`);
  rerun 06:03 → pass. Worker now runs from `private/worktrees/claude-main` (main checkout is on DeepSeek's branch).
## 2026-10-12 06:04 — Y2 part 1: entry, compiler, function finder (DeepSeek, branch `deepseek/y2-census`)
- New: `scripts/dis_range.sh` (range disassembler), `tools/find_functions.py` (BL/BX worklist finder →
  `config/functions.csv`), `tools/test_functions_csv.py` (check, exit 0), `tools/test_rom_strings.py`
  (check for job `J0002`), `docs/rom-map.md`. Updated: `docs/approximations.md` (A1-A3), `docs/jobs.md`
  (batch 2), `config/functions.csv` (158 rows: 155 THUMB, 3 ARM).
- Entry path: reset `0x08000000` `ea00002e b 0x80000c0` → crt0 `0x080000C0` (ARM: IRQ stack
  `0x03007FA0`, system stack `0x03007F00`, writes handler `0x080000FC` to `0x03007FFC`, `bx` into
  `0x08016929` = `main`) → IRQ handler `0x080000FC` (ARM dispatcher, handler table `0x0807F420`:
  default `0x08003B70`, all interrupts `0x08003B94`). Command:
  `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/dis_range.sh 0x080000C0 0x08000200`.
- Finder: `PY tools/find_functions.py` → `functions: 158 / thumb: 155 arm: 3 / lowest: 0x08000000
  highest: 0x0803B5AC / pointer-only targets not walked into (unverified): 13`;
  `PY tools/test_functions_csv.py` → `rows: 158 thumb: 155 arm: 3 / ALL CHECKS PASSED`, exit 0.
- Build gate: `wsl ... bash scripts/build.sh` → `private/build/yugioh.gba: OK`, exit 0.
  Other gates: `guard_repo.py` 31 files, 0 failures; `hash_rom.py` ORIGINAL+BASEROM OK; all new
  tracked files check-ignore = 1, `private/jobs/queue/J0002.json` = 0 (ignored).
- Job `J0002` queued (ROM string extractor, check `PY tools/test_rom_strings.py`, verified against a
  reference implementation before queuing: 57622 rows pass, missing script fails).

## 2026-10-12 06:13 — Claude: job pipeline hardening after J0002
- J0002 (DeepSeek-made) failed twice: check `PY tools/test_rom_strings.py` → `PY: command not found` (exit 127);
  test not on main when the worktree was cut; model wrote its own copy of the test (caught: outside allowed) and
  `git add -f private/extracted/strings.txt` (caught only by size: 2443254 bytes).
- 72611ff: `make_job.py` expands `PY`, refuses checks whose .py files are not on main; worktrees get a read-only,
  SHA-1-checked `private/baserom.gba`.
- eff76e3: `guard_repo.py` fails paths under `private/`/`rom/` and force-added ignored files. Tests: J0002 worktree
  → 2 failures; small force-added `zz_forced.txt` → FAIL; main → 0 failures; `test_guard.py` cases 1–3 PASS.
- J0002 requeued: check expanded, allowed only `tools/rom_strings.py`, explicit commit rules; old branch deleted
  (it held the ROM strings); failed record in `private/jobs/tests/J0002.failed-ops-bug.json`.
- Briefs: HERMES_START (job rules), LOCAL_WORKER rule 7.
## 2026-10-12 06:16 — Y2 part 2: census 158 → 1034, extents, code/data map (DeepSeek, branch `deepseek/y2-census2`)
- New: `tools/code_map.py` (read-only code/data report). Updated: `tools/find_functions.py`
  (pointer-table seeds, A4/A6 filters, `size` column), `tools/test_functions_csv.py` (stronger check),
  `config/functions.csv` (header `address,name,mode,size,source`, 1034 rows), `docs/rom-map.md`
  (§4 census, §5 code/data map), `docs/approximations.md` (A2 updated, A4–A7 added).
- `PY tools/find_functions.py` → `functions: 1034 / thumb: 1031 arm: 3 / lowest: 0x08000000
  highest: 0x0803B5AC / source bl_thumb: 347, crt0_bx_literal: 1, crt0_writes_0x03007FFC: 1,
  irq_table: 2, ptr_prologue: 681, reset_branch: 1, reset_vector: 1 / pointer values seen via bx rX
  but not accepted (A2): 26 (of which now in the census anyway: 3) / ptr_prologue rejected by A4: 0 /
  by A6: 20`. The 20 A6 rejections are all data-half addresses ≥ 0x4C554 bytes from BL-closure code.
- `PY tools/test_functions_csv.py` → `rom THUMB BL pairs: 38338 distinct targets: 32440 /
  rows: 1034 thumb: 1031 arm: 3 / ptr_prologue rows: 681 bl_thumb rows: 347 / ALL CHECKS PASSED`, exit 0.
  Falsification of the new check: appending `0x080FFF00,sub_080FFF00,thumb,4,bl_thumb` to the CSV →
  `FAIL 0x080FFF00 bl_thumb: no THUMB BL into it from inside another extent`, exit 1; restored → exit 0.
- `PY tools/code_map.py` → code bytes 64170 (0.38% of the ROM), code region
  `0x08000000..0x0803B5D0` (26.39% of it function extents), 5 gaps > 4 KiB (43646 B) inside the code
  region, two of them code-like (`0x08004318`, `0x08031DA4`); 1 MiB data-block table in `docs/rom-map.md` §5.
- Gates: `wsl ... bash scripts/build.sh` → `private/build/yugioh.gba: OK`, exit 0;
  `guard_repo.py` 38 files, 0 failures; `hash_rom.py` ORIGINAL+BASEROM OK; all changed/new files
  check-ignore = 1. Job `J0002` (string extractor) passed at 06:14 on main.
