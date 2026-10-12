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
