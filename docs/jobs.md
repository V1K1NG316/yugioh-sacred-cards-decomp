# Local job log

DeepSeek logs each batch of local jobs here (ids, purpose).

## 2026-10-12 — batch 1 (pipeline warm-up, created by DeepSeek on `deepseek/y1-shell`)
- `J0001` — ROM header printer. Kind `script`. Writes `tools/rom_header.py`, which prints the six GBA
  header fields (`title`, `code`, `maker`, `version`, `entry_branch_target`, `size`) as `key=value` lines.
  Check: `PY tools/test_rom_header.py` (exact-stdout compare against the values read from the ROM).
  Allowed: `tools/rom_header.py`. Purpose: first real job through the worker; also gives later jobs a
  reusable header report.

## 2026-10-12 — batch 2 (created by DeepSeek on `deepseek/y2-census`)
- `J0002` — ROM ASCII string extractor. Kind `script`. Writes `tools/rom_strings.py`, which dumps every
  maximal run of >= 6 printable ASCII bytes as `0xADDR<TAB>text` to `private/extracted/strings.txt`.
  Check: `PY tools/test_rom_strings.py` (written and validated by DeepSeek *before* the job: it
  re-reads the ROM and round-trip checks every line, its maximality, the known strings and a minimum
  row count; the real result is 57622 rows — the check was verified to pass against a reference
  implementation and to fail when the script is absent). Allowed: `tools/rom_strings.py`,
  `private/extracted/strings.txt`. Purpose: gives the "any library strings?" question of Y2 part 1 an
  answerable dataset without spending DeepSeek tokens on the scan.

## 2026-10-12 — Y5 decomp batch: not queued yet (DeepSeek, `deepseek/y5-harness`)
No job was queued this turn, on purpose: the check every decomp job needs is
`PY tools/match_func.py <name>`, and `tools/make_job.py` refuses a check whose .py file is not
committed on `main` yet. `PY tools/make_decomp_job.py <name> --dry-run` prints the whole recipe
and the exact make_job.py command without queueing anything (verified this turn); run it without
`--dry-run` once this branch is merged. Targets for the first batch come from
`PY tools/pick_decomp_targets.py 10`: `sub_080243A0`, `sub_080016CC`, `sub_08005FFC`,
`sub_08006270`, `sub_080095B4`, `sub_08009680`, `sub_0800ABE0`, `sub_0800ABEC`, `sub_0800ABF8`,
`sub_0800AC04` (8-12 code bytes each).
