# Local job log

DeepSeek logs each batch of local jobs here (ids, purpose).

## 2026-10-12 — batch 1 (pipeline warm-up, created by DeepSeek on `deepseek/y1-shell`)
- `J0001` — ROM header printer. Kind `script`. Writes `tools/rom_header.py`, which prints the six GBA
  header fields (`title`, `code`, `maker`, `version`, `entry_branch_target`, `size`) as `key=value` lines.
  Check: `PY tools/test_rom_header.py` (exact-stdout compare against the values read from the ROM).
  Allowed: `tools/rom_header.py`. Purpose: first real job through the worker; also gives later jobs a
  reusable header report.
