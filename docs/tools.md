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
  `scripts/decomp_tools.sh` into `private/venv/`. Only `permute_func`/`diff_func` need them. Both
  were first run on this PC on 2026-10-24: `diff_func sub_08014480` → `CURRENT (0)` (no differing
  lines), and the permuter turned a deliberately broken copy (base score 5) into a score-0
  candidate.
- **mGBA** — `mgba-qt` 0.10.5 (pacman, `/usr/bin/mgba-qt`, installed 2026-10-24). `-g` opens the
  gdb stub on **`0.0.0.0:2345`** (`mgba-qt --help`); the stub cannot be told to bind another
  address or port. `scripts/emu_groundtruth.sh <script.py> [args]` starts it on the ROM copy
  `private/tmp/ygo.gba` (or `$MGBA` if set), waits until `ss -ltnp` shows *its own* PID on port
  2345, runs one `scripts/emu_*.py`, then stops it with SIGTERM and, after 3 s, SIGKILL (an
  already-stopped emulator really does ignore the TERM). No argument → usage on stderr, exit 2;
  anything already listening on 2345 → one-line refusal, exit 1.
  **The port never reaches the LAN by default:** the emulator and the script both run inside a
  private network namespace (`unshare --user --map-root-user --net`, with `ip link set lo up`
  inside), so 2345 exists only on that namespace's loopback. `EMU_NO_NETNS=1` runs them in the
  normal namespace instead; the stub is then open on all interfaces for the length of the run and
  ufw is what keeps it private, so only set that when the namespaces are unavailable.
  First Linux run 2026-10-24: `emu_groundtruth.sh scripts/emu_anchors.py` → `ANCHORS OK`, exit 0,
  and `emu_card_image.py` reads the game's RAM through the stub. A window opens on the desktop
  while it runs, which is expected.
- **Ghidra 12.1.4** + **Temurin JDK 21** — downloaded into `private/tools/` by
  `scripts/ghidra_setup.sh` when decompiler drafts are wanted (they are optional: `make compare`,
  `match_func`, `diff_func` and the permuter do not need them).
