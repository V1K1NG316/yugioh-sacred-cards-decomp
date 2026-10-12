#!/usr/bin/env bash
# Y3: generate private/asm/rom.s (whole-ROM disassembly, one file per function) and build it.
# Run inside WSL from the repo root: wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/disasm.sh
# Output: private/asm/rom.cfg, rom_raw.s, rom_full.s, funcs/*.s, data/*.s, rom.s
# (all generated, all untracked) and the tracked function list config/functions.csv.
set -euo pipefail
cd /mnt/d/Yugioh_DeComp_V2

PY=python3
GBADISASM=private/tools/gbadisasm/gbadisasm
MAX_LOOPS=5

[ -x "$GBADISASM" ] || { echo "missing $GBADISASM -- build it: (cd private/tools/gbadisasm && make)"; exit 1; }

mkdir -p private/asm

# Fixpoint loop (TASK [013] item 1): the function list drives the disassembler, and the
# disassembler finds function starts the list does not have (BL targets the Y2 census
# missed).  Run cfg -> gbadisasm -> csv until the function set stops changing.
for i in $(seq 1 "$MAX_LOOPS"); do
  $PY tools/make_disasm_cfg.py
  "$GBADISASM" private/baserom.gba -c private/asm/rom.cfg > private/asm/rom_raw.s
  $PY tools/post_disasm.py private/asm/rom_raw.s private/asm/rom_full.s
  rm -f private/asm/rom_raw.s   # 107 MB intermediate; gbadisasm re-makes it in seconds
  cp config/functions.csv private/asm/functions.prev.csv
  $PY tools/functions_from_rom_s.py private/asm/rom_full.s config/functions.csv
  rows=$(( $(wc -l < config/functions.csv) - 1 ))
  if cmp -s private/asm/functions.prev.csv config/functions.csv; then
    echo "disasm.sh: loop $i: function list stable at $rows rows"
    break
  fi
  echo "disasm.sh: loop $i: function list changed -> $rows rows, disassembling again"
  if [ "$i" = "$MAX_LOOPS" ]; then
    echo "disasm.sh: function list still changing after $MAX_LOOPS loops -- giving up"; exit 1
  fi
done

$PY tools/split_disasm.py
echo "disasm.sh: wrote private/asm/rom.s ($(wc -l < private/asm/rom.s) lines, $(ls private/asm/funcs | wc -l) function files)"