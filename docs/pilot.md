# Pilot: DeepSeek drafts, local model polishes (started 2026-10-12 18:58)

Matter_Scatter's idea: the local model works as DeepSeek's "hands" (exact instructions) instead of solving
functions itself. DeepSeek writes a draft C for each function in one cheap batch turn; the local job copies it,
tests it, and may only make small diff-guided fixes.

## Baseline (local model alone, same size class: 30..60 code bytes, real logic)
| job | function | result | GPU time |
|---|---|---|---|
| J0026 | sub_08000CD8 | pass, attempt 1 | ~9 min |
| J0027 | sub_08001690 | fail (2 attempts, 1 timeout), Claude rescue | ~60 min |
| J0028 | sub_08003118 | fail (2 attempts, 1 timeout), Claude rescue | ~60 min |
| J0029 | sub_08003F28 | pass, attempt 1 (first job with the argument-type rule) | ~8 min |
| J0030 | sub_080045C4 | fail (2 attempts, 2 timeouts; also wrote a stray into main) | ~60 min |
Baseline: **2/5 = 40% pass**, mean **~39 min GPU per job**, DeepSeek cost $0 (rescues by Claude).

## Pilot set (20 functions, same size class)
Listed in `private/jobs/drafts/pilot_functions.txt` (5 formerly held jobs J0036–J0040 + 15 new).

## Measures
Per function: draft matched as written (y/n), local job pass (y/n), attempts, GPU minutes, rescue needed, and the
DeepSeek drafting cost per function (turn cost / 20). Results table filled in as jobs finish.

## Results
| job | function | draft as written | local result | GPU time | notes |
|---|---|---|---|---|---|
| J0042 | sub_0800595C | 2/32 bytes off | fail (2 attempts) → Claude rescue (1 edit) | ~55 min | model misread `#0x80 lsl 7` as 0x80, made it worse; draft fix was `b < a` → `a > b`. Two reading rules added to the remaining pilot recipes. |
| J0043 | sub_08005D0C | yes (0 bytes off) | pass, attempt 1 (copy only, no fix) | ~3 min | first pilot job where the draft matched as written. C identical to `private/drafts/sub_08005D0C.c`; types verified from the asm epilogues (`pop {r0}; bx r0` = void for the function and for `sub_08021E50` / `sub_0800465C`; `lsls/lsrs #0x18` = u8 arg). Merged on `main` by DeepSeek (interim director). GPU time = session `20261012_202426_380718` → result `20:26:59` (no worker transcript keeps start times, so this is session-id-to-result). |
| J0044 | sub_08006188 | no (13/32 bytes off) | before the pause: no answer (output-token limit). After requeue: **pass**, attempt 1 | ~18 min (23:54→00:12) | model's fix: move `0x0E000040` into a local first, so the literal loads happen in the ROM's order. A real polish of a near-miss draft. Return type u32 (`pop {r1}; bx r1`). |
