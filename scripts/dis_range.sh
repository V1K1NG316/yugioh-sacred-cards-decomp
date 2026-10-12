#!/usr/bin/env bash
# Disassemble a range of the ROM (milestone Y2).
#   scripts/dis_range.sh 0x08000000 0x08000010          -> ARM
#   scripts/dis_range.sh 0x080000C0 0x08000120 thumb    -> THUMB
# $1 start address (0x08......), $2 stop address, $3 optional literal "thumb".
set -euo pipefail
cd /mnt/d/Yugioh_DeComp_V2
extra=()
if [ "${3:-}" = "thumb" ]; then extra=(-M force-thumb); fi
arm-none-eabi-objdump -D -b binary -m armv4t --adjust-vma=0x08000000 \
    --start-address="$1" --stop-address="$2" "${extra[@]}" private/baserom.gba
