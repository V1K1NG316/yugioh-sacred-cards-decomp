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

## 2026-10-12 — batch 3 (Y4 part 1: graphics and text, by DeepSeek on `deepseek/y4-survey`)
Not queued yet: `tools/make_job.py` refuses a check whose `.py` is not yet on `main`, and all three checks below
are new on this branch. Claude merges, then the three `make_job.py` lines listed in REPORT `[026]` can be run.
Each job writes **one** tool and nothing else; every check recomputes the full expected output from the ROM and
was verified to exit 0 against a reference implementation and non-zero against a broken one.
- `tools/find_lz77.py` — every LZ77 blob (BIOS format) in the ROM → `private/extracted/lz77/<ADDRESS>.bin` +
`index.tsv` (1084 blobs, 3 398 277 bytes out, 2 381 036 bytes in). Check: `PY tools/test_lz77.py` (compares
the index, every blob's bytes, the file set and stdout against its own decompressor). Recipe:
`private/jobs/drafts/lz77_extract.md`. Purpose: the graphics half of Y4 without spending DeepSeek tokens on a
16 MiB scan.
- `tools/extract_text_tables.py` — the four multi-language tables (credits ×140, duel messages ×124, attributes
×12, card types ×24) → `private/extracted/text_tables.tsv` (300 records, 89 636 bytes of raw record hex).
Check: `PY tools/test_text_tables.py`. Recipe: `private/jobs/drafts/text_tables.md`. Purpose: the non-card
text Y4 needs, and the raw material for a glyph decoder.
- `tools/find_text_tables.py` — whole-ROM map of pointer tables aimed at `$0` text records →
`private/extracted/text_table_map.tsv` (15 tables). Check: `PY tools/test_find_text_tables.py`. Recipe:
`private/jobs/drafts/text_table_map.md`. Purpose: the systematic version of the hand survey; it reproduces
every table found by hand, entry counts included.

## 2026-10-12 — batch 4 (Y4 part 2: text decoder + card descriptions, by DeepSeek on `deepseek/y4-text`)
Not queued yet (same rule: `tools/make_job.py` refuses a check whose `.py` is not on `main`). Claude merges, then
the two lines in REPORT `[029]` can be run. Both jobs write one tool; both checks recompute the whole expected
output from the ROM and were verified to exit 0 against a reference implementation and non-zero against three
broken variants each plus a missing tool (`private/tmp/break_checks2.sh`).
- `tools/decode_text.py` — decode any text record address, one line per language field (`$0`..`$5`), accents via
`config/text_glyphs.csv`, `^`/`#0` line breaks and `%` commas. Check: `PY tools/test_decode_text.py` (920
addresses = all 900 card names + 20 card descriptions, 5520 lines, 207 046 bytes compared exactly against the
check's own decoder). Recipe: `private/jobs/drafts/decode_text.md`. Purpose: Y4 text, reusable by every later
text tool, without spending DeepSeek tokens on five languages of byte rules.
- `tools/extract_card_descriptions.py` — card number (1..900) → name → description, English, both tables read
from the ROM (`0x08D310E4`, `0x08E94E7C`) → `private/extracted/card_descriptions.tsv` (900 lines, 152 373
bytes). Check: `PY tools/test_card_descriptions.py`. Recipe: `private/jobs/drafts/card_descriptions.md`. Purpose:
the A12 result as data, one line per card, ready for the in-game spot checks.
