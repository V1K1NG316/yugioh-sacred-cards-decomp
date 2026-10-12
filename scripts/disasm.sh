#!/usr/bin/env bash
# Y3: generate private/asm/rom.s (whole-ROM disassembly) and build it.
# Run inside WSL from the repo root: wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/disasm.sh
set -euo pipefail
cd /mnt/d/Yugioh_DeComp_V2

PY=python3
GBADISASM=private/tools/gbadisasm/gbadisasm

[ -x "$GBADISASM" ] || { echo "missing $GBADISASM -- build it: (cd private/tools/gbadisasm && make)"; exit 1; }

mkdir -p private/asm
$PY tools/make_disasm_cfg.py
"$GBADISASM" private/baserom.gba -c private/asm/rom.cfg > private/asm/rom_raw.s
$PY tools/post_disasm.py private/asm/rom_raw.s private/asm/rom.s
echo "disasm.sh: wrote private/asm/rom.s ($(wc -l < private/asm/rom.s) lines)"
