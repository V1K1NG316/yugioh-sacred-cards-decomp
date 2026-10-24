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
## 2026-10-12 06:32 — Y3 part 1: gbadisasm pipeline, `make compare` builds the disassembly (DeepSeek, branch `deepseek/y3-disasm`)
- New: `tools/make_disasm_cfg.py` (config/functions.csv → `private/asm/rom.cfg`),
  `tools/post_disasm.py` (raw gbadisasm → `private/asm/rom.s`), `scripts/disasm.sh` (the whole
  pipeline), `asm/macros.inc` (pret-style `thumb_func_start` / `arm_func_start` /
  `non_word_aligned_thumb_func_start`). Updated: `Makefile` (`compare` now builds
  `private/asm/rom.s`, the Y1 shell build moved to `compare-shell`), `docs/credits.md`
  (gbadisasm + bundled Capstone 3.0.5-rc2, commit, licence).
- Tool: `git clone https://github.com/jiangzhengwenjz/gbadisasm private/tools/gbadisasm`
  → commit `940def2c91d678ee671716b8b44a2223c0ff2c62`; `make -j4` in WSL builds Capstone 3.0.5-rc2
  (arm only) + `gbadisasm`, `make exit=0`. `https://github.com/pret/gbadisasm` does not exist (404).
- Command: `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/disasm.sh` →
  `functions.csv: 1034 rows (thumb 1031, arm 3)` / `raw -> rom_raw.s : 1139194 lines, 12315 labels,
  last label 0x0803B61C` / `wrote private/asm/rom.s: 4 trailing bytes appended, 1 branches narrowed
  to .n`. Generation 16 s, assembly 4 s.
- `wsl ... make compare` → `private/build/yugioh.gba: OK`, exit 0. Byte-identical.
- Functions disassembled: 1977 (1034 census rows + 943 extra entry points gbadisasm's own BL
  analysis found; 4 ARM incl. a previously unknown ARM subroutine `sub_08036C74` reached by a
  Thumb `add r2, pc, #0; bx r2` thunk). Bytes: instructions 177622 (82029 lines, 1.06% of the ROM),
  data 16599594 (98.94%: `.byte` 16565922, `.4byte` 30372 = 7593 literals/jump-table words,
  `.align` padding 3300). Line-by-line replay lands on `0x09000000` with 0 drift: the split is exact.
  Inside the code block `0x08000000-0x0803B5D0`: 177554 instruction bytes, 65598 data/pad.
- Two authored post-processing steps were needed (both in `tools/post_disasm.py`, both first
  discovered by the byte diff): (1) gbadisasm drops the bytes after its final label — the sentinel
  `data_label 0x08FFFFFC` in the cfg pins it, post_disasm appends the last 4 bytes;
  (2) `b <sym>` to a `non_word_aligned_thumb_func_start` symbol assembles as a 4-byte `b.w` (the
  symbol's Thumb bit makes GNU as refuse the 2-byte form) — post_disasm rewrites exactly those
  branches to `b.n`. First diff before the fix: `0x0803714C` orig `ED E7 00 00` vs built
  `FF F7 ED BF`.
- Falsification: `mov r0, #0x12` → `#0x13` on line 27 of `private/asm/rom.s` → `make compare` FAILED
  (`sha1sum: WARNING: 1 computed checksum did NOT match`); restored → `OK`, exit 0. Fork-copy
  `asm/rom.s` path: `make compare-shell` → `private/build/yugioh_shell.gba: OK`, exit 0.
- Gates: `make clean && make compare` → OK, exit 0; `guard_repo.py` 41 files, 0 failures;
  `hash_rom.py` ORIGINAL+BASEROM OK; new files check-ignore = 1 (tracked).
- Note: `docs/credits.md` was the one file in the repo with mixed LF/CRLF endings; it is now
  uniformly CRLF like the rest of `docs/`.

## 2026-10-12 06:50 — Y3 part 2: true function list, per-function files, data as `.incbin` (DeepSeek, branch `deepseek/y3-split`)

- New tools: `tools/functions_from_rom_s.py` (refresh `config/functions.csv` from the generated asm),
  `tools/split_disasm.py` (one file per function + data files + the `.include` list that is
  `private/asm/rom.s`). Changed: `tools/post_disasm.py` (`.byte` runs → `.incbin`, with address
  tracking that must land on the sentinel), `scripts/disasm.sh` (fixpoint loop + split step),
  `Makefile` (the assembly now depends on `private/asm/funcs/*.s` and `private/asm/data/*.s`),
  `tools/test_functions_csv.py` (check 9: the CSV must equal the asm's function starts; MIN_ROWS
  1900; `source=disasm` rule), `tools/code_map.py` (reports the instruction/`.incbin` split; the old
  extent-sum report became meaningless once extents tile the ROM), `docs/rom-map.md` §4/§5,
  `docs/approximations.md` A5 (rewritten) + A8 (new).
- Fixpoint, from scratch with the Y2 list of 1034 rows
  (`wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/disasm.sh`):
  `functions.csv: 1034 rows` → `functions_from_rom_s: 1977 functions (thumb 1973, arm 4) / kept 1034,
  new 943 (source=disasm), stale 0` → `loop 1: function list changed -> 1977 rows, disassembling
  again` → `loop 2: function list stable at 1977 rows` → `split_disasm: 1977 function files, 253
  data files`. exit 0. The 4 ARM rows are the startup stub plus `sub_08036C74`, found by the loop.
- `wsl ... make compare` → `private/build/yugioh.gba: OK`, exit 0;
  `sha1sum private/build/yugioh.gba` = `d3710031520d9cdae70d870c60b1667285fe5230`.
- `PY tools/test_functions_csv.py` → `fixpoint: the CSV equals the 1977 function starts of
  rom_full.s` / `rows: 1977  thumb: 1973  arm: 4` / `ptr_prologue rows: 681  bl_thumb rows: 347` /
  `ALL CHECKS PASSED`, exit 0.
- Byte split (same as part 1, only the representation changed): `.incbin` 16565922 (98.74%),
  `.4byte` 30372 (7593 words: 626 jump-table words + 6967 literal-pool words), instructions 177622,
  `.align` padding 3300; `non-.incbin bytes: 211298` from `post_disasm.py`. `rom_full.s` is 1.84 MB /
  103897 lines where part 1's `rom.s` was 107 MB / 1139204 lines; `private/asm` is 7.8 MB total
  (`rom_raw.s` is now deleted after `post_disasm`).
- Falsification (C4): `movs r0, #1` → `#2` in `private/asm/funcs/main.s` → `make compare` rebuilt
  (the wildcard dependency works) and `private/build/yugioh.gba: FAILED` / `1 computed checksum did
  NOT match`, exit 2; restored → `OK`, exit 0.
- Determinism: `split_disasm.py` run twice leaves `sha1(private/asm/rom.s)` =
  `cec316d594834af70eed166413cee71c27f41fa4` unchanged; `sha1(config/functions.csv)` =
  `4f5975431d609ff9e1e7bf56d21f73f88ced6b56`.
- Gates: `guard_repo.py` 48 files, 0 failures; `hash_rom.py` ORIGINAL+BASEROM OK; both new tools
  `git check-ignore` = 1 (tracked).
- Finding for Y2/Y3: the disassembler emits no label at or above `0x0803B61C`, so 16533984 bytes
  (98.6% of the ROM) are one unlabelled data run — recorded as open (A8), not as "no code there".

## 2026-10-12 07:23 — Y5 part 1: agbcc match harness, first three functions matched (DeepSeek)
- Branch `deepseek/y5-harness` (from `main` `3315d0d`). agbcc copied (not modified) from
  `D:\Custom_Pokemon\private\base\pokefirered\tools\agbcc\` to `private\tools\agbcc\` — 13 MB, bin/
  include/ lib/; recorded in `docs\credits.md`.
- New: `tools\match_func.py` (the check: compile one C file with agbcc, link it at the function's
  ROM address, compare the bytes), `scripts\match_func.sh` (cpp/agbcc/as pipeline),
  `scripts\link_at.sh` (stub symbols + linker script, one place that knows how to link at an
  address), `scripts\build_matched.sh` (the C goes into the ROM build), `include\global.h`,
  `src\funcs\{sub_08004750,sub_08007604,sub_0800AF94}.c`, `tools\{progress,pick_decomp_targets,
  make_decomp_job,romcode}.py`, `docs\decomp.md`. `Makefile`: the rom.o rule now runs
  `scripts\build_matched.sh` and depends on `src/funcs/*.c` plus the three scripts.
- Three functions matched byte for byte, so **approximation A3 is settled**: agbcc
  (gcc 2.9-arm-000512, `-mthumb-interwork -Wimplicit -Wparentheses -Werror -O2 -fhex-asm`) is the
  compiler. Updated `docs\approximations.md` (A3 now SETTLED, A9 added) and `docs\rom-map.md` §3.
  `PY tools\match_func.py sub_08004750` →
  `MATCH sub_08004750 @ 0x08004750: 12 bytes identical, 12 bytes of room in the ROM (next start 0x0800475C)`;
  same for `sub_08007604` (12) and `sub_0800AF94` (10).
- From scratch: `rm -rf private/asm private/build` + `wsl ... bash scripts/disasm.sh` → 1977
  functions, list stable at loop 1; `wsl ... make compare` → `build_matched: 3 C function(s), 34
  bytes compiled from C` … `private/build/yugioh.gba: OK`; `sha1sum` =
  `d3710031520d9cdae70d870c60b1667285fe5230` (the original).
- `PY tools\progress.py` → `3/1977 functions matched (0.15%)`, `34/211294 code bytes linked from C`.
  The 211294 denominator comes from `tools\romcode.py` (extent minus `.incbin`), cross-checked
  against Y3's `non-.incbin bytes: 211298`.
- Falsification: `*(u16 *)0x02020B34 = 1` (one wrong constant) → `FAIL ... first difference at +0x2
  (rom 00, ours 01)`, exit 1; the same in a scratch worktree copy of the C, then restored → MATCH.
- Two traps found and written up in `docs\decomp.md` §6: (1) rom.s is `.syntax unified` while agbcc
  writes divided syntax, so `mov r0, #0` assembled to the 4-byte `mov.w` and the ROM came out 4
  bytes too long — the fragment is now bracketed with `.syntax divided`/`.syntax unified`; (2) `ld
  --defsym` makes an *absolute* symbol, which ld takes for ARM code and answers with a Thumb→ARM
  veneer (`bl 800afa0 <__sub_0800AF3C_from_thumb>`), so undefined symbols are now real `.thumb_func`
  stubs placed at their addresses.
- Gates: `guard_repo.py` 65 files, 0 failures; `hash_rom.py` ORIGINAL OK / BASEROM OK;
  `git check-ignore -q` = 1 on each of the 13 new files.

## 2026-10-12 07:51 — Claude: approvals from Matter_Scatter (overnight)
- 07:50: Ghidra + portable JDK download approved (TASK [019]).
- 07:51: decomp-permuter and asm-differ download approved; DeepSeek installs them after [019] (portable, under
  `private/tools/`, recorded in `docs/credits.md`).
- Overnight: Matter_Scatter asked Claude to accept what the agents need while they sleep; Claude caps overnight
  DeepSeek spend at project total $4.20 (was $1.19 at 07:47) and keeps the project rules (no system installs).
- 07:53: Matter_Scatter raised the overnight cap: keep project DeepSeek spend under $10 total.

## 2026-10-12 08:58 — DeepSeek: Ghidra headless decompiler drafts (TASK [019])
- `scripts/ghidra_setup.sh` (new): downloads the Java runtime and Ghidra into `private/tools/`, each
  checked against the SHA-256 its project publishes.
  `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/ghidra_setup.sh`
  → `OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz: OK`,
  `ghidra_12.1.4_PUBLIC_20260921.zip: OK`, `openjdk version "21.0.12.1"`.
- `tools/ghidra/GbaDecompDrafts.java` (new) + `scripts/ghidra_drafts.sh` (new): headless import of
  `private/baserom.gba` as raw `ARM:LE:32:v4t` at 0x08000000, `TMode` set per row of
  `config/functions.csv`, one function created per row, analysis, then the decompiler writes
  `private/ghidra/<name>.c`.
  `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/ghidra_drafts.sh`
  → `funcs: 1977 created, 0 renamed, 0 failed, of 1977 rows`;
  `drafts: 1977 written, 0 had no function, 0 decompile failures, 1295595 C chars`.
  Analysis is time-boxed (`-analysisTimeoutPerFile 600`); re-run for one function:
  `... bash scripts/ghidra_drafts.sh --only sub_080016CC` → `drafts: 1 written` in 45 s.
- `tools/make_decomp_job.py`: a job's recipe quotes the draft's path when `private/ghidra/<name>.c`
  exists. `PY tools/make_decomp_job.py sub_080016CC --dry-run` → the recipe now contains
  "A decompiler DRAFT of this function is at `D:/Yugioh_DeComp_V2/private/ghidra/sub_080016CC.c`".
- Docs: `docs/decomp.md` §8 (the loop), `docs/credits.md` (Temurin JDK 21, Ghidra 12.1.4 + hashes).
- Gates: `tools/guard_repo.py` 66 files, 0 failures; `tools/hash_rom.py` OK; `git check-ignore -q` = 1
  for each new file; `make compare` → `private/build/yugioh.gba: OK`.

## 2026-10-12 14:18 — Y5 tooling 2: parallel-safe harness, asm-differ, decomp-permuter (DeepSeek, branch `deepseek/permuter`)

TASK [022]. New files: `scripts/asm_with_defsyms.sh`, `scripts/rom_func_obj.sh`,
`scripts/permute_func.sh`, `scripts/diff_func.sh`, `scripts/decomp_tools.sh`, `tools/diff_func.py`,
`tools/diff_func.sh`, `tools/permute_func.sh`. Changed: `tools/match_func.py` (per-run build dir,
`--keep`/`--workdir`), `scripts/match_func.sh` (optional 4th argument = that dir),
`scripts/build_matched.sh` (reads the symrefs list, below), `tools/make_decomp_job.py` (recipe),
`docs/decomp.md` §2/§9/§10, `docs/credits.md`.

- **Parallel-safe harness.** Every `match_func.py` run builds in `private/build/match/<name>.<pid>`
  and deletes that directory when it ends, so overlapping runs cannot collide; `--keep`/`--workdir`
  keep it instead (`tools/diff_func.py` uses both). `scripts/build_matched.sh` is the one caller
  that still uses the shared `private/build/match/<name>`.
  C1, 8 runs at once (task asked for 4): `bash private/tmp/c1_parallel.sh` →
  `8 match_func.py runs launched at once, wall clock 864 ms`, then eight lines of
  `exit=0  MATCH <name> @ 0x...: N bytes identical`, and
  `leftover per-run build dirs (the runs delete their own): 0`. The same 8 runs also passed while
  `make compare` was building in the same checkout.
- **asm-differ** (commit `0dd09af`, MIT) — `tools/diff_func.sh <name>`, i.e.
  `PY tools/diff_func.py <name>`: builds `src/funcs/<name>.c` exactly as the check does, builds the
  ROM's own bytes for that function as a second object (`scripts/rom_func_obj.sh`, verified against
  the ROM) and prints the two side by side. `tools/diff_func.sh sub_08004750` → `CURRENT (0)`, no
  differences; on the perturbed copy below → `CURRENT (10)` with `i`/`|` on the two differing lines
  (`ldrb r0, [r0, #3]` vs `ldrb r0, [r0, #0]`; `.word 0x0201fcc0` vs `.word 0x0201fcc3`), which is
  exactly what the check says: `FAIL ... 2/12 bytes differ`.
- **decomp-permuter** (commit `8556c81`, MIT) — `tools/permute_func.sh <name> [minutes]
  [--base file.c] [--jobs N]`: sets up `private/permuter/<name>/` (ROM bytes as `target.o`, the C
  as `base.c`, generated `compile.sh`), runs time-boxed with `--stop-on-zero` and copies the best
  candidate to `private/permuter/<name>/best.c` — never into `src/`. Demo: `sub_08004750`
  (`return gUnk_0201FCC0[3];`) perturbed into `unsigned char *p = &gUnk_0201FCC0[3]; return *p;`
  → `[sub_08004750] base score = 10`, `found new best score! (0 vs 10)`, 119 candidates, 2.7 s wall
  clock including the setup (first run: 170 candidates, 3 s). That `best.c` through the real check:
  `MATCH sub_08004750 @ 0x08004750: 12 bytes identical, 12 bytes of room in the ROM`.
  Setup: `bash scripts/decomp_tools.sh` → both clones at their pinned commits + `private/venv`
  (pip bootstrapped into the venv from bootstrap.pypa.io because Ubuntu 24.04's `python3` has none;
  nothing system-wide, nothing under `private/` committed).
- **Assembly with `--defsym`** (`scripts/asm_with_defsyms.sh`): every undefined symbol named
  `NAME_<8 hex digits>` is defined as the address in its own name, so a constant the C names by a
  symbol and the ROM's inline constant read the same for the two tools. It also writes
  `<name>.o.symrefs`, which `build_matched.sh` now reads instead of `nm -u` — after `--defsym`
  those symbols are no longer undefined. Without that, `make compare` failed once with
  `arm-none-eabi-ld: private/build/rom.o: in function 'sub_08004750': (.text+0x4758): undefined
  reference to 'gUnk_0201FCC0'`.
- Measured in passing: `extern signed char gUnk_0201FCC0[]` returned as `unsigned char` compiles to
  the ROM's `ldrb` **byte-identically** (permuter base score 0, `cmp` against the ROM) — gcc 2.9
  drops the sign-extending load when the value is only used as an unsigned char. Recorded in
  `docs/decomp.md` §9 so a future "signed vs unsigned" near miss is not misread.
- Gates: `tools/guard_repo.py` 82 files, 0 failures; `tools/hash_rom.py` → `ORIGINAL` and `BASEROM`
  both `sha1=d3710031520d9cdae70d870c60b1667285fe5230 OK`; `git check-ignore -q` = 1 for all 8 new
  files; `make compare` → `private/build/yugioh.gba: OK`.

## 2026-10-12 — Y4 part 1: graphics and text survey (DeepSeek, `deepseek/y4-survey`)

Compression families found and turned into jobs; text tables mapped; the `0x87` accent table decoded.
Evidence: `private/tmp/refroot/` (a scratch root holding reference implementations + the ROM copy) and
`private/tmp/break_checks.sh`; commands and output in REPORT `[026]` of `AI_Conversation.md`.

- New check scripts (committed, they define three local jobs whose tools the local model still writes):
  `tools/test_lz77.py`, `tools/test_text_tables.py`, `tools/test_find_text_tables.py`.
  All three were verified both ways: exit 0 against a reference implementation in `private/tmp/refs_good/`,
  exit 1 (with the mismatching line printed) against a deliberately broken one and against a missing tool.
  `PY tools/test_lz77.py` in `private/tmp/refroot` → `blobs: 1084 / out bytes: 3398277 / ALL CHECKS PASSED`.
- `tools/test_lz77.py` also caught a real bug in my first reference decompressor: the overlapping back-reference
  copy (`bytes(out[-dist] for _ in range(count))` evaluates one byte `count` times) — fixed to append byte by
  byte, mirroring the BIOS. First run of the check: `FAIL blob 0x0803C44C differs: 16384 bytes, want 16384`.
- Job recipes written (not queued: their checks must be merged to `main` first):
  `private/jobs/drafts/lz77_extract.md`, `private/jobs/drafts/text_tables.md`,
  `private/jobs/drafts/text_table_map.md`. `docs/jobs.md` has the batch entry.
- Docs: `docs/game-data.md` gained §Compression, §Text, §`0x87` accented letters; `docs/approximations.md`
  gained A10 (LZ77 blob rule), A11 (text-pointer-table rule), A12 (description index is still unknown).
- Gates: `PY tools/guard_repo.py` → `guard: 87 files checked, 0 failures`; `PY tools/hash_rom.py` → ORIGINAL and
  BASEROM both `OK` (exit 0); `make compare` (WSL) → `private/build/yugioh.gba: OK`; `git check-ignore -q` = 1
  for each of the three new check scripts; nothing under `private/` staged.


## 2026-10-12 14:50 — Y4 part 2: the card-description index is found; text decoder + description extractor jobs (DeepSeek, branch `deepseek/y4-text`)

TASK `[028]`, budget ~$1.00. Files: new `config/text_glyphs.csv`, `tools/test_decode_text.py`,
`tools/test_card_descriptions.py`; recipes `private/jobs/drafts/decode_text.md` and `card_descriptions.md`;
references in `private/tmp/refs_good/`; `docs/game-data.md` §Text rewritten, `docs/approximations.md` (A12
RESOLVED, new A13, A14), `docs/jobs.md` batch 4.

- **A12 solved.** Cards are 1..900; the description index is the 900-word table at `0x08E94E7C`, read by the
  card-database loader `sub_08006BE4` at `0x08006CA0` (`ldr r0, =0x08E94E78` = table - 4, `adds r0, r6, r0`
  with `r6 = 4*cardId`) because the game's card ids are 1-based - the same trick as the name reader
  `sub_080073E4` (`=0x08D310E0` for the table at `0x08D310E4`). The description pointer lands at struct
  `0x02020B00 + 8`; when the card's cost exceeds the Duelist Level the game stores `0x08D30F40` instead
  ("Your Duelist Level is below the Cost...").
- `0x08DFC054` is not a card table: searching the whole 16 MiB for the word gives exactly one hit
  (`PY` scan -> `0x8dfc054 word occurrences in whole ROM: ['0x8024f90'] count 1`), the literal pool of the
  effect-message renderer `sub_08024F64`. The old "2 load sites" note was wrong. `0x08E94E78` likewise has
  exactly one hit (`0x8006cb0`).
- Description records: `81 40` + `$0`..`$5` + `00 00`, cards 1/2/3 padded to 126/132/112 bytes per field, all in
  `0x08DFCE68`..`0x08E94E75`; the 900 pointers are strictly increasing, the table ends `0x08E95C8C` before a run
  of `0xFFFFFFFF`.
- Five famous cards decoded through the rule (C1) and the whole 30..40 name block lines up with its
  descriptions; card 2's effect line matches `word[0x08DFC054 + 4*2]` = "...on the own field will be powered up".
- Glyph table re-swept over the Latin fields of all 900 name records: 28 codes, `0x74` `0x75` = OE/oe are new
  (`Gros OEil`, `Boeuf de combat`, `Changement de coeur`), `0x64` still unknown.
- Two new checks, each validated both ways with `bash private/tmp/break_checks2.sh`: reference -> exit 0,
  three broken variants per tool -> exit 1, tool absent -> exit 1, restored -> exit 0.
  `PY tools/test_decode_text.py` -> `records: 920 / fields: 5520 / bytes: 207046 / ALL CHECKS PASSED`;
  `PY tools/test_card_descriptions.py` -> `cards: 900 / bytes: 152373 / ALL CHECKS PASSED`.
- Gates: `PY tools/guard_repo.py` -> `guard: 89 files checked, 0 failures` (exit 0); `PY tools/hash_rom.py` ->
  ORIGINAL and BASEROM `OK` (exit 0); `make compare` (WSL) -> `private/build/yugioh.gba: OK` (exit 0);
  `git check-ignore -q` = 1 for each new file; nothing under `private/` staged.

## 2026-10-12 — Y4 part 3: card property columns named, card pictures decoded (DeepSeek, branch `deepseek/y4-cards`)

- Card struct `0x02020B00` (loader `sub_08006BE4`) now has every `card_stats.tsv` column named. Two are
  proved by the code that *prints* them: struct `+0x16` = card type (`sub_08007380` -> name getter
  `sub_0802319C`, table `0x08D4BC3C`, 24 names) and struct `+0x17` = attribute (`sub_080073A8` ->
  `sub_0801A624`, table `0x08D419E0`, 12 names).
  `PY private/tmp/y4c3_c1.py` -> `type table (0x08D4BC3C, 24): 0=, 1=Dragon, 2=Magician, ... 23=Ritual`,
  `attr table (0x08D419E0, 12): 0=, 1=Shadow, 2=Light, 3=Fiend, ... 11=Divine`,
  `type column: matches the TCG type in all 11 cases` (BEWD Dragon, Mystical Elf/Dark Magician Magician,
  Hitotsu-Me Giant BeastWarrior, Griffore Beast, Summoned Skull/Kuriboh Fiend, Celtic Guardian Warrior, ...).
- Other columns: `+0x19` = card-frame graphics id (the picture loader indexes the 10-word table `0x08D536C8`;
  it is 3 for every Magic card, 4 for every Trap, 5 for every Ritual); `+0x1b` = optional unique-effect
  routine id, nonzero for 79 cards (Mystical Elf, whose description says it powers up BEWD, is one of them)
  indexed into **code**-pointer tables `0x08D353A0`/`0x080FB79C`; `+0x1a` = effect/script id (2 for all 773
  monsters, one distinct value per Magic/Ritual/Trap card) indexing the code table `0x08D34B80`; `+0x1c` =
  per-trap id, nonzero for exactly the 19 Trap cards. `0x0808B4A7` is **not** a per-card column: the loader
  does `+0x1d = 0x0808B4A7[+0x1a]`. Guesses A16-A18; the attribute-scheme caveat is A15.
- Card pictures: table `0x08D536F0` holds **901** words and **entry n = card n** (entry 0 = an all-zero dummy
  picture). The loader `sub_08034AF8`/`sub_080351A4` reads `u32[0x08D536F0 + 4*cardId]` with the 1-based id
  (no "-4" trick, unlike `sub_080073E4`), which matches the LZ77 census (901 pointed 576-byte blobs).
- Format: each blob is BIOS LZ77 -> exactly 576 bytes = **8bpp palette indices in 8x8 tiles of 64 bytes**,
  9 tiles row-major = **24x24 pixels**; palette = the 256-entry BGR555 table at **`0x089C54B0`** (the card
  screen loads 0xa0 halfwords = 160 colours of it; `0x9f` = `#292929` is the background of 864 of 900
  pictures). The 10 card frames at `0x0894BCB4 + k*0x400` (1024 B = 16 tiles = 32x32) are the same format and
  are the same image with three palette indices remapped (204 byte substitutions per variant).
- New check `tools/test_card_images.py` + reference `private/tmp/refs_good_img/extract_card_images.py`,
  verified both ways with `bash private/tmp/break_card_images.sh`: reference -> `cards: 900` /
  `bytes: 1085114` / `ALL CHECKS PASSED` (exit 0), tool absent -> exit 1, and four broken variants -> exit 1
  (`FAIL card 1: pixel (9,0) is 115, expected 159`, `FAIL card 1: PLTE is not the 256 colours of 0x089C54B0`,
  `FAIL 1.png: 600 raw bytes, expected 575`, `FAIL 1.png: 599 raw bytes, expected 600`).
- Card 1 (Blue-Eyes White Dragon) and card 35 (Dark Magician) decoded by hand: `private/tmp/card_001.png`,
  `private/tmp/card_035.png` (24x24, 8bpp, 37 / 70 palette indices, background `0x9f` = `#292929`).
- Job recipe for the local worker: `private/jobs/drafts/card_images.md`; check must be merged on `main` first.

## 2026-10-12 15:5x - Y4 part 4: card picture ground truth from mGBA (gdb stub), Cost column, card 40

Tool: `D:\Custom_Pokemon\private\tools\mGBA\mGBA-0.10.5-win64`, run from a copy in `private/tmp/mgba`
(nothing written next to the original) on a ROM copy `private/tmp/ygo.gba`, with `-g` (gdb stub, port 2345).
Neither front end can run a Lua script from the command line (`--help` has no `--script`, no autoload setting
in the binary), so the stub is driven by our own client: `scripts/mgba_gdb.py`. One client per launch - a
second connection is refused, so every measurement is a fresh emulator (`scripts/emu_groundtruth.sh` does the
launch-wait-run-kill cycle).

Method: a small ARM trampoline in EWRAM calls the game's own routines (the stub cannot set Thumb state from a
CPSR write, so the trampoline `bx`es to an odd address and passes arguments in r0-r3). Called:
* `sub_08034AF8(dest, card)` - the card picture loader. Left in EWRAM: the decompressed picture at 0x02018800.
* `sub_08034B40(dest, picture, frame)` - the composition, first with the real sources, then with synthetic
  patterns (one 4-byte chunk index per chunk) to measure which source byte lands where.

Results (all in `docs/game-data.md` "Card pictures"):
- LZ77 decode verified against the game: 576 bytes at 0x02018800 for cards 1 and 2 byte-for-byte equal my
  decode (`PY scripts/emu_anchors.py` -> `ANCHORS OK`, exit 0).
- The composed card image is 32x32 8bpp, 8x8 tiles row-major, = frame asset + art in a 24x24 window at (4,2).
  Every composed byte outside that window equals the frame asset: 448 of 448, cards 1 and 2. Written at
  destination byte `i + 768*(i//256)`. 144 art chunks + 112 frame chunks = exactly 1024 bytes per card.
- SHA-256 anchors taken from the emulator dumps, now embedded in `tools/test_card_images.py`: composed
  `380f8482...7160` / art `a3079443...492d` (card 1), composed `254f9f94...81ba` / art `78351907...b060`
  (card 2); the ROM alone reproduces all four.
- Palette: the card screen's code at `0x08028130` does `CpuFastSet(0x089C54B0 -> 0x02000200, 160 words)`
  (SWI 0x0B). Correction: Y4 part 3's `sub_08034658` is that same wrapper (destination comes from the caller),
  it does not write palette RAM; calling it with a dummy argument left palette RAM all-zero, measured.
- NOT verified: how it looks on screen - the card screen was never displayed, so the on-screen colour/scale is
  open (A20/A21). The art data is high-frequency, so the 24x24 decode looks dithered at 1:1.

Cost column, the [033] doubt (`docs/game-data.md` "Card Cost"):
- u32 table `0x08088DF0`, entry n = card n: BEWD 95, Mystical Elf 319, Dark Magician 183, Red-Eyes 207,
  Celtic Guardian 260, Blue-Eyes Ultimate Dragon 20, Dragon Piper 86 (`[033]`'s 12/20 came from a shifted read).
- `sub_08006BE4` stores it at `struct+0x0C`, calls `sub_08014110` (Duelist Level), and when Cost > level it
  replaces the card's description pointer (`struct+0x08`) with `0x08D30F40`, which decodes to "Your Duelist
  Level is below the Cost. This can't be put in the Deck." Plain deck Cost, used unscaled.
Card 40: `PY` + the Y4 part 2 decoder, cards 38..42 - each name has its own description; "A being that dwells
inside a curiously decorated vase" is Dragon Piper's own text, no off-by-one.

New tracked files: `scripts/mgba_gdb.py`, `scripts/emu_groundtruth.sh`, `scripts/emu_card_image.py`,
`scripts/emu_picture_map.py`, `scripts/emu_anchors.py`; `tools/test_card_images.py` gains the anchors and the
composed-image rule. Break tests `bash private/tmp/break_card_images2.sh`:
```
=== tool absent (must fail)                      FAIL tools/extract_card_images.py does not exist   exit=1
=== good reference tool in place (must pass)     anchors: 2 cards match the emulator dump / cards: 900 /
                                                 bytes: 1085114 / ALL CHECKS PASSED               exit=0
=== broken: window moved to (5,2) (must fail)    FAIL card 1: the 32x32 image in the emulator's tile buffer
                                                 hashes 380f8482...7160, this composition hashes 9563ec2e... exit=1
=== broken: column-major tiles (must fail)       FAIL card 1: pixel (9,0) is 115, expected 159        exit=1
=== broken: wrong palette (must fail)            FAIL card 1: PLTE is not the 256 colours of 0x089C54B0 exit=1
=== restored good reference (must pass again)    ALL CHECKS PASSED                                   exit=0
```
- 2026-10-12 15:58: Matter_Scatter lifted the overnight $10 cap (awake and watching); the $30 project stop still applies.

## 2026-10-12 16:12 — Y5 probe: cost-table index settled, two 100+-instruction functions attempted (DeepSeek, branch `deepseek/y5-large`)
Cost column, the `[037]` dispute (is `w_08088DF0` indexed `+4*k` or `+4*(k-1)`?): new `tools/cost_index.py` settles
it from the loader's own registers. `sub_08006BE4` @ 0x08006BE4 zero-extends its argument into **r4**
(`lsls r4,r4,#0x10; lsrs r4,r4,#0x10`) and indexes *every* column with that one register — `u16 @ 0x080886E6 +
2*r4` (ATK), `u16 @ 0x08087FDC + 2*r4` (DEF), `u32 @ 0x08088DF0 + 4*r4` (Cost), the byte rows `+r4`, and
`sub_080073E4(r4)` = `*(u32 *)(0x08D310E0 + 4*r4)` for the card-name pointer. So name index = stat index = card id,
**1-based with entry 0 a dummy** (ATK/DEF `0xFFFF`, Cost 0, empty name), and the answer is **`+4*k`** — the same
rule `tools/extract_card_stats.py` (J0005) uses, so no fix is needed there. Command `PY tools/cost_index.py`, exit 0:
```
  id   0                             atk=65535 def=65535 W=    0 lvl=  0
  id   1  Blue-Eyes White Dragon     atk= 3000 def= 2500 W=   95 lvl=  8
  id   2  Mystical Elf               atk=  800 def= 2000 W=  319 lvl=  4
  id  35  Dark Magician              atk= 2500 def= 2100 W=   20 lvl=  7
  id  82  Red-Eyes B. Dragon         atk= 2400 def= 2000 W=   12 lvl=  7
  id 366  Labyrinth Wall             atk=    0 def= 3000 W=  585 lvl=  5
  Blue-Eyes White Dragon id   1 -> +4*id =    95 , +4*(id-1) =     0
  Dark Magician          id  35 -> +4*id =    20 , +4*(id-1) =   183
  Red-Eyes B. Dragon     id  82 -> +4*id =    12 , +4*(id-1) =   207
  Labyrinth Wall         id 366 -> +4*id =   585 , +4*(id-1) =   255
  DEF + 2*901 -> 0x080886E6 OK / ATK + 2*901 -> 0x08088DF0 OK
  W   + 4*901 -> 0x08089C04 OK / byte0 + 901 -> 0x08089F89 OK
  RESULT: the loader index is +4*id with id = the card number 1..900 (entry 0 unused)
```
`docs/game-data.md` "Card Cost and the Duelist-Level gate" carried four wrong values and now carries the corrected
list (Dark Magician 20, Red-Eyes B. Dragon 12, Celtic Guardian 161, Blue-Eyes Ultimate Dragon 255 — the "20" it
printed is Dark Magician's — Dragon Piper 260, Labyrinth Wall 585) plus an index paragraph. The `[036]` section
above this one repeats the old list (183/207/260/86 are entries 34/81/40/39, i.e. the previous card); this entry
supersedes it.

Matching C at 100+ instructions (TASK `[038]` item 2) — both attempted, neither matched, nothing committed for them:
- `sub_080066D0` (232 B, ~106 instructions): transcribed from `private/asm/rom_full.s` into a C file with named
  structs (`Unk_02023120`, `Unk_02023140`, `Unk_02023160`+0xF0, `Unk_02023270`+0x14/0x28, `Unk_0202347C`,
  `Unk_02020B00`) — struct fields are what make agbcc pool the bare symbol and use a displacement; raw `u8 *` math
  folds `+0x28` into the pool (measured). Four builds, `PY tools/match_func.py sub_080066D0`:
  `FAIL ... first difference at +0xA (rom 81, ours 06); 188/232 bytes differ`. Best build is 224 B against the ROM's
  232; of 106 instruction lines 59 are byte-identical, 32 differ only in register names, 11 in operands, 4 are
  ROM-only; the literal pool is identical (6 words, same order). The whole gap is gcc 2.9's register allocation
  (the ROM keeps the constant 1 in r7, the long-lived bases in sl/r9, arg0 in r8 and spills arg1 to the stack).
  C shapes tried without moving it: named `u8` locals for both params, a `tab` pointer variable, struct fields vs
  raw pointer math, a named constant variable.
- `sub_08012B70` (extent 260 = 258 B code + 2 B alignment, ~120 instructions): one transcription, two 12-iteration
  loops. `PY tools/match_func.py sub_08012B70` → `FAIL ... first difference at +0x2 (rom 57, ours 4f); 207/220 bytes
  differ` (our build 220 B). Both loops' instruction sequences match the ROM's one for one; again only the
  allocation differs.
- Kept out of the tree (an unmatched `src/funcs/*.c` would break `make compare`): `private/tmp/y5-attempts/`.
- `tools/diff_func.py sub_08012B70` refuses the function (`rom_func_obj: sub_08012B70: the assembled ROM asm is NOT
  the ROM's bytes`) because the A5 extent ends with 2 bytes of `mov r0,r0` alignment padding; `sub_080066D0` (no
  trailing padding) diffs fine. Reported to Claude as a small tool fix.

Gates: `PY tools/guard_repo.py` → `guard: 109 files checked, 0 failures` (exit 0); `PY tools/hash_rom.py` →
ORIGINAL + BASEROM `OK` (exit 0); `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- make compare` →
`build_matched: 23 C function(s), 230 bytes from C linked into the ROM` … `private/build/yugioh.gba: OK` (exit 0,
29 s); `PY tools/progress.py` → `23/1977 functions matched (1.16%)`; `git check-ignore -q tools/cost_index.py` →
exit 1 (tracked) and `git check-ignore -q private/tmp/y5-attempts/sub_080066D0.c` → exit 0 (ignored).
- 2026-10-12 18:48: Matter_Scatter approved downloading ghidra-mcp (github.com/bethington/ghidra-mcp, Apache-2.0) for agent-driven Ghidra; portable under private/tools/.
- 2026-10-12 18:50: Matter_Scatter approved adding a ghidra-mcp entry to Hermes global config (C:/Users/USER/AppData/Local/hermes/config.yaml, mcp_servers).

## 2026-10-12 20:08 — Claude: ghidra-mcp wired into Hermes (approved by Matter_Scatter)
- Hermes global config `C:/Users/USER/AppData/Local/hermes/config.yaml` (backup `config.yaml.bak-pre-ghidra-mcp-20261012_2007`):
  added `mcp_servers.ghidra` (url http://127.0.0.1:8081/mcp, timeout 120, connect_timeout 15) with **enabled: false**.
  Reason: with the server down, `hermes mcp test ghidra` waited 15.1 s ("timed out after 15s"); every Hermes
  session (worker, other projects) would pay that. `hermes mcp list` → ghidra "✗ disabled".
- `ops/deepseek-turn.ps1 -Ghidra`: starts `scripts/ghidra_mcp_server.sh`, flips enabled→true, adds toolset
  `mcp-ghidra` (Hermes names MCP toolsets `mcp-<name>`), and in `finally` flips it back and stops the server.
  Toggle tested on a copy: ON→"enabled: true", OFF→"enabled: false", file identical after ON+OFF.
- Verified ghidra-mcp itself (Claude re-ran DeepSeek's smoke test): 75→86 tools, decompile, xrefs to
  0x08D35C28 (3 in sub_08017CA8), rename in a throwaway copy; server stopped, ports closed.
- 2026-10-12 20:11: Claude corrected deepseek-turn -Ghidra toolset to `ghidra` (hermes -z validates MCP toolsets by server name, hermes_cli/oneshot.py); `mcp-ghidra` was ignored ("unknown --toolsets entries"). Turn 053 restarted.

## 2026-10-12 20:24 — DeepSeek [054]: what the duel card pools do (branch `deepseek/pools`)

Tools this turn: the ghidra-mcp bridge (one `load_tool_group("xref")` call, then `get_functions` /
`get_xrefs_to`) plus the already-generated disassembly `private/asm/rom_full.s` and `objdump`
(`scripts/dis_range.sh`). Every address below was read from the ROM's own code.

Chain (callers, `grep -nE 'bl sub_080(17CA8|17D6C|16234|16254|16360|1644C|16748|164EC|1649C|16768)' private/asm/rom_full.s`):

```
37710:	bl sub_08016254      37715:	bl sub_08016360      37732:	bl sub_08014094
37733:	bl sub_0801644C      37734:	bl sub_08016748      37735:	bl sub_080164EC
37887:	bl sub_08016408      37971:	bl sub_0801649C      38324:	bl sub_08016768
40505:	bl sub_08017CA8      40616:	bl sub_08017D6C      40728:	bl sub_08016234
```
(the 40505/40616 sites are inside `sub_08017B84`, 40616 at `0x08017C9C`) and, from
`dis_range.sh 0x08016234 0x08016770 thumb`, the exact call sites: `0x08016240` → `sub_08016254`,
`0x0801624C` → `sub_08016360` (**lost**), `0x08016268` → `sub_08014094`, `0x0801626C` →
`sub_0801644C`, `0x08016270` → `sub_08016748`, `0x08016274` → `sub_080164EC`, `0x0801636E` →
`sub_08004348` (ante removal), `0x08016468` → `sub_0801649C`, `0x0801647A` → `sub_0800431C`,
`0x080164A2` → `sub_0801823C`, `0x080164C0` → `sub_08034628(0, 0x7FF)`, `0x0801664C` →
`sub_08034628(rec+0x1C, rec+0x1E)`, `0x0801674C` → `sub_08016768`, `0x08016756` → `sub_0801BED4`,
`0x08017D90` → `sub_08016234`.

Result (details in `docs/game-data.md`, "What the three lists actually do"): a won duel gives **one**
card (count byte `0x02020D30+0x28` = 1, written at `0x08017CDA`), rolled 0..2047 from record `+0x08`
(or record `+0x10` = the shared 57-id list at `0x080B80CC` when the player's **ante card**
`0x02020B34` is one of the 49 ids at `0x080BA280`), added to the collection `0x02020770` and printed
as duel message 5 "#2 was obtained!"; with no ante card set the win gives no card. The same handler
adds Deck Capacity (`record+0x18`) and Domino (`sub_08034628(record+0x1C, record+0x1E)` ×
10^`record+0x20`). A **lost** duel removes one copy of the ante card from the collection
(`0x0801636E`). The 50 rolls from `+0x0C` go into a second array `0x02020DB0` (open question A28).
`0x02020B34` is the ante card, not "the card being resolved" ([048] corrected).

Gates: `PY tools/guard_repo.py` → `guard: 133 files checked, 0 failures` (exit 0); `PY tools/hash_rom.py`
→ ORIGINAL + BASEROM `OK` (exit 0); `wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- make compare`
→ `private/build/yugioh.gba: OK` (exit 0). No new files, so `check-ignore` is unchanged (the four edited
files are all tracked).

## 2026-10-13 08:07 — Claude: build_matched installs a function's .s only after its self-check
- Found: a stray `src/funcs/sub_080013D8.c` (local job J0062 wrote into the main checkout) made `make compare`
  rewrite `private/asm/funcs/sub_080013D8.s` with wrong code; the self-check failed but the file stayed, so the next
  build (stray gone) produced a ROM with 13 wrong bytes at 0x13DF.
- Repair: `PY tools/split_disasm.py` (regenerates private/asm/funcs) → `make compare` OK.
- Fix: `scripts/build_matched.sh` writes `private/build/match/<name>/gen.s`, checks it, then copies it into place.
- Attack test: wrong 32-byte C for sub_0801C324 → "does NOT reproduce", md5 of private/asm/funcs/sub_0801C324.s
  unchanged (013feb58…); after restoring the C, `make compare` → `private/build/yugioh.gba: OK`.

## 2026-10-14 04:43 — Claude: published on GitHub (Matter_Scatter's request, public)
- Repo: https://github.com/V1K1NG316/yugioh-sacred-cards-decomp (main = 93455da, 555 commits, 296 files).
- Scrubbed copy: `wsl ... bash private/publish/make_public.sh` (bare clone of main + git-filter-repo 2.47.0 replacing the
  Windows username with `USER` in all files and commit messages) → "objects containing the username: 0",
  "game-derived paths: 0". Pushed with `git -C private/publish/yugioh.git push https://github.com/V1K1NG316/yugioh-sacred-cards-decomp.git main`;
  `git ls-remote` → 93455da2d9cda840f592a6dcd6a18cfb7c215b36 refs/heads/main.
- Update later: run make_public.sh again, then the same push with `--force` (history is re-written each time, same ids
  for unchanged commits).

## 2026-10-24 06:34 — Linux port: toolchain built here, `make compare` OK natively (Hermes/DeepSeek)
- Why: the project runs on the owner's Arch PC since 2026-10-24; no `D:\`, `/mnt/d`, WSL or Windows Python may
  be left in `tools/`, `scripts/` or the `Makefile`.
- Toolchain check: `arm-none-eabi-as --version` → GNU assembler 2.47.20260726 (target arm-none-eabi);
  `python3 --version` → 3.14.9; host `cpp`/`gcc` 16.2.1.
- agbcc: `git clone https://github.com/pret/agbcc private/tools/agbcc-src` → commit
  `da598c1d918402c42c0c0d7128ba14567f3175e9`; `./build.sh` exit 0 (log `private/tools/agbcc-build.log`);
  `./install.sh <repo>/private` → `private/tools/agbcc/{bin,include,lib}`.
  `ls private/tools/agbcc/bin` → `agbcc` (3798352 B), `agbcc_arm` (4953848 B), `old_agbcc` (3798088 B).
- gbadisasm (Y3 disassembler, not in git): clone `jiangzhengwenjz/gbadisasm` at
  `940def2c91d678ee671716b8b44a2223c0ff2c62`, `make CAPSTONE_ARCHS="arm"` → exit 0,
  `private/tools/gbadisasm/gbadisasm` (758896 B).
- Ported — repo root is now found from each script's own location, `wsl ... -- bash x.sh` is a plain
  `bash x.sh`, `wsl_path()` is gone: `scripts/{match_func,build_matched,link_at,rom_func_obj,diff_func,
  permute_func,disasm,build,dis_range,decomp_tools,emu_groundtruth}.sh`, `tools/{diff_func,permute_func,
  permute_many}.sh`, `Makefile` (missing-rom.s hint); `tools/{match_func,diff_func,hash_rom,guard_repo,
  test_guard,test_functions_csv,test_rom_header,rom_header,census,code_map,find_functions,xmatch,siblings,
  sibling_drafts,gen_wrapper_drafts,build_readable_page,make_job,make_decomp_job}.py`; `PY tools/x.py`
  in usage/docstrings → `python3 tools/x.py`. `make_job.py`'s `PY` token is now `sys.executable`.
- Not ported, left untouched (Windows-only per the brief): `tools/{backup_hermes,newest_session,
  deepseek_spend,deepseek_balance,status,cost_index}.py`.
- `bash scripts/disasm.sh` → `loop 1: function list stable at 1977 rows`, 1977 function files + 253 data files,
  `.incbin` 16565922 B, exit 0; `config/functions.csv` unchanged (git status clean under `config/`).
- `make compare` (cold: all 1025 C functions compiled) → `build_matched: 1025 C function(s), 48120 bytes from C
  linked into the ROM` → `private/build/yugioh.gba: OK`, real 1m23.166s. Second run, nothing to rebuild → `OK`,
  real 0m0.054s.
- Gates: `python3 tools/hash_rom.py` → ORIGINAL+BASEROM `sha1=d3710031520d9cdae70d870c60b1667285fe5230`
  `sha256=12d28e09…a411  OK`, exit 0. `python3 tools/guard_repo.py` → `guard: 1147 files checked, 0 failures`,
  exit 0.
- `tools/test_*.py`, run one by one with `python3`: 15 pass. `test_card_images.py` exits 1 with
  `FAIL tools/extract_card_images.py does not exist` — that extractor was never committed
  (`git log --all -- tools/extract_card_images.py` is empty), so the failure predates the port.
- `tools/match_func.py` on `sub_08004750`, `sub_0800AF94`, `sub_08014480` → MATCH, 12 / 10 / 28 bytes identical,
  exit 0. Discrimination test in `private/scratch/matchtest/` (its own `tools/match_func.py` + a copy of
  `sub_08014480.c` with `p[8] - 1` → `p[8] - 2`): `FAIL … first difference at +0xC (rom 01, ours 02);
  1/28 bytes differ`, exit 1; `git status --short src/` empty.
- Residual grep (`tools/ scripts/ Makefile`) for `D:[\/]`, `/mnt/d`, `wsl `, `wsl_path`, `Ubuntu-24.04`:
  only `tools/status.py` and `tools/deepseek_spend.py`, the two not ported.
- Follow-ups: `README.md` still says "Building (WSL, Ubuntu 24.04)" (outside this brief's allowed paths); mGBA is
  not installed, so `scripts/emu_*` are ported but have not been run; agbcc commit and build recorded in
  `docs/credits.md`, toolchain list rewritten in `docs/tools.md`.

## 2026-10-24 (Claude) — correction to the Linux port entry
- "mGBA is not installed" above is wrong: `mgba-qt` 0.10.5-5 was installed by the owner at 06:27 (`pacman -Q mgba-qt`).
  The emulator scripts are still unrun; `scripts/emu_groundtruth.sh` expects a portable `private/tmp/mgba/mGBA` and
  needs pointing at `/usr/bin/mgba-qt` first.
- Review of the port (3 Sonnet reviewers): `make compare` re-run from an empty `private/build` → `OK` in 1m22s, every
  function built from agbcc output (no asm fallback); deliberate wrong C → `FAIL`, exit 1.
