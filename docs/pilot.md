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
(pending)
