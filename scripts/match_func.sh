#!/usr/bin/env bash
# Y5: compile one C function with agbcc and link it at its ROM address.
# Called by tools/match_func.py (never by hand -- the arguments are generated):
#   wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/match_func.sh <name> <0xADDR> <srcdir>
# <srcdir> is a WSL path holding <name>.c (the checkout under test; usually a job worktree).
# Everything else (agbcc, the ROM, the build dir) is the main checkout, /mnt/d/Yugioh_DeComp_V2.
# Writes into private/build/match/<name>/:
#   <name>.i/.s/.o   preprocessed, agbcc asm, object
#   size.txt         the function's length in bytes (gcc's .size: body + literal pool)
#   sections.txt     .text/.data/.bss sizes of the object (a non-empty .data is unsupported)
#   <name>.bin       the object's bytes, linked at ADDR
#   <name>.unresolved <name>.ld.log   from scripts/link_at.sh
#   rom.bin          the same number of bytes taken from the ROM at ADDR
#   disasm_ours.txt disasm_rom.txt  one instruction per line, for the caller's diff
# Exit 0 only if the whole pipeline ran; the byte comparison is the caller's job.
set -euo pipefail
NAME=$1
ADDR=$2
SRCDIR=$3

REPO=/mnt/d/Yugioh_DeComp_V2
A=$REPO/private/tools/agbcc
W=$REPO/private/build/match/$NAME
OFF=$(( ADDR - 0x08000000 ))

rm -rf "$W"
mkdir -p "$W"
cp "$SRCDIR/$NAME.c" "$W/$NAME.c"

# pokefirered's agbcc invocation, minus its charmap preprocessor (we have no charmap yet).
cpp -nostdinc -undef -std=gnu89 -I "$A/include" -I "$A" -I "$REPO/include" -o "$W/$NAME.i" "$W/$NAME.c"
"$A/bin/agbcc" -mthumb-interwork -Wimplicit -Wparentheses -Werror -O2 -fhex-asm -o "$W/$NAME.s" "$W/$NAME.i"
arm-none-eabi-as -mcpu=arm7tdmi -mthumb-interwork -o "$W/$NAME.o" "$W/$NAME.s"

arm-none-eabi-objdump -h "$W/$NAME.o" | awk '/^ *[0-9]+ \./{printf "%s %s\n", $2, toupper($3)}' > "$W/sections.txt"

SIZE=$(arm-none-eabi-objdump -t "$W/$NAME.o" | awk -v n="$NAME" '$3 == "F" && $NF == n {print $5}')
[ -n "$SIZE" ] || { echo "match_func.sh: no function symbol '$NAME' in $NAME.o" >&2; exit 3; }
printf '%s\n' "$(( 0x$SIZE ))" > "$W/size.txt"
LEN=$(( 0x$SIZE ))

# Everything else the compiled code needs (calls, data addresses) is resolved by scripts/link_at.sh.
bash "$REPO/scripts/link_at.sh" "$W" "$NAME" "$W/$NAME.o" "$ADDR"

dd if="$REPO/private/baserom.gba" of="$W/rom.bin" bs=1 skip="$OFF" count="$LEN" status=none

arm-none-eabi-objdump -d "$W/$NAME.elf" > "$W/disasm_ours.txt"
arm-none-eabi-objdump -D -b binary -m armv4t -M force-thumb --adjust-vma=$ADDR \
    "$W/rom.bin" > "$W/disasm_rom.txt" 2>/dev/null || true
exit 0
