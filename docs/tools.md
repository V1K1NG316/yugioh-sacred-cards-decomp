# Tools

The toolchain of the Arch PC (since 2026-10-24; the Windows/WSL setup is gone — no `D:\`, no WSL,
no Windows Python). Project-specific tools live under `private/` (untracked); the only system-wide
pieces are the two pacman packages the owner installed.

- `python3` (3.14) — runs `tools/*.py` and `scripts/*.py`. No extra Python packages are needed for
  the gates; `scripts/decomp_tools.sh` puts the two community tools' dependencies in `private/venv/`.
- `arm-none-eabi-as/ld/objcopy/objdump/nm` (GNU binutils 2.47, pacman `arm-none-eabi-binutils`) —
  assemble, link and inspect the ROM build.
- Host `cpp` and `gcc` (16.2.1) — `cpp` preprocesses each C function before agbcc sees it.
- **agbcc** and **old_agbcc** — `private/tools/agbcc/` (`bin/`, `include/`, `lib/`), built from
  `pret/agbcc` commit `da598c1d918402c42c0c0d7128ba14567f3175e9` (source in
  `private/tools/agbcc-src/`); commit, commands and licence in `docs/credits.md`. Which one compiles
  a file is decided per file (approximation A37, `scripts/match_func.sh`).
- **gbadisasm** — `private/tools/gbadisasm/gbadisasm`, clone of `jiangzhengwenjz/gbadisasm` at
  commit `940def2c91d678ee671716b8b44a2223c0ff2c62`, built with `make CAPSTONE_ARCHS="arm"`. Turns
  `private/baserom.gba` + `private/asm/rom.cfg` into `private/asm/rom.s` (`scripts/disasm.sh`).
- **decomp-permuter**, **asm-differ** — `private/tools/`, pinned commits, set up by
  `scripts/decomp_tools.sh` into `private/venv/`. Only `permute_func`/`diff_func` need them.
- **mGBA** — `mgba-qt` 0.10.5 (pacman, `/usr/bin/mgba-qt`, installed 2026-10-24). The emulator
  ground-truth scripts (`scripts/emu_groundtruth.sh`, `scripts/emu_*.py`, `scripts/mgba_gdb.py`) are
  ported to Linux but have not been run since the port, and `emu_groundtruth.sh` still launches a
  portable copy (`private/tmp/mgba/mGBA`): point it at `mgba-qt` before first use.
- **Ghidra 12.1.4** + **Temurin JDK 21** — downloaded into `private/tools/` by
  `scripts/ghidra_setup.sh` when decompiler drafts are wanted (they are optional: `make compare`,
  `match_func`, `diff_func` and the permuter do not need them).
