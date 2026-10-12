# Credits

Community tools and sources used (name, URL, version/commit, licence).

- **gbadisasm** — GBA disassembler. https://github.com/jiangzhengwenjz/gbadisasm
  commit `940def2c91d678ee671716b8b44a2223c0ff2c62` (2023-07-14). Used for Y3: it turns
  `private/baserom.gba` plus the config written by `tools/make_disasm_cfg.py` into the assembly
  that `make compare` builds back into the ROM. Cloned (not vendored) into
  `private/tools/gbadisasm/`; nothing under `private/` is committed.
  **Licence: the repository carries no LICENSE file and its README states no licence** — flagged
  in AI_Conversation [011], QUESTION 1. Private use only until that is settled.
  (The URL the task named first, `github.com/pret/gbadisasm`, does not exist: HTTP 404 on
  2026-10-12. The task's fallback URL above is the one used.)
- **Capstone 3.0.5-rc2** — disassembly framework, bundled inside gbadisasm as
  `capstone-3.0.5-rc2.tar.gz` and built from source by gbadisasm's Makefile with
  `CAPSTONE_ARCHS="arm"`. Licence: BSD-3-Clause (`capstone-3.0.5-rc2/LICENSE.TXT`).
