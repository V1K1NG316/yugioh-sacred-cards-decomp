#!/usr/bin/env bash
# Link one compiled object at one ROM address, with the ROM's other symbols stubbed out.
# Called by scripts/match_func.sh and scripts/build_matched.sh from the repo root:
#   bash scripts/link_at.sh <workdir> <base> <object> <0xADDR>
# Writes <workdir>/<base>.elf, <base>.bin (the object's .text bytes only), <base>.unresolved
# (undefined symbols that are not NAME_<8 hex digits>) and <base>.ld.log.
#
# ld must see each callee as a real Thumb function, or it inserts a Thumb->ARM interworking veneer
# and the call bytes come out wrong. `ld --defsym` cannot say "thumb": an absolute symbol is taken
# for ARM code. So every NAME_<8 hex digits> symbol the object leaves undefined is *defined* here
# by a two-byte stub in a section of its own, placed at that address by the linker script. The
# CSV's mode column decides whether the stub is a .thumb_func (the address keeps the low bit the
# CPU needs) or plain data.
set -euo pipefail
WORK=$1
BASE=$2
OBJ=$3
ADDR=$4
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)

declare -A MODE
while IFS=, read -r _ n m _rest; do MODE["$n"]=$m; done < <(tail -n +2 "$REPO/config/functions.csv")

: > "$WORK/$BASE.unresolved"
: > "$WORK/$BASE.stubs.s"
STUB_LD=()
STUBS=0
while read -r s; do
  [ -n "$s" ] || continue
  if ! [[ $s =~ ^[A-Za-z_][A-Za-z0-9_]*_([0-9A-Fa-f]{8})$ ]]; then
    printf '%s\n' "$s" >> "$WORK/$BASE.unresolved"
    continue
  fi
  sec=".stub_$s"
  if [ "${MODE[$s]:-}" = thumb ]; then
    { echo "	.section $sec, \"ax\", %progbits"
      echo "	.thumb"
      echo "	.thumb_func"
      echo "	.globl $s"
      echo "$s:"
      echo "	bx lr"; } >> "$WORK/$BASE.stubs.s"
  else
    { echo "	.section $sec, \"a\", %progbits"
      echo "	.globl $s"
      echo "$s:"
      echo "	.byte 0, 0, 0, 0"; } >> "$WORK/$BASE.stubs.s"
  fi
  STUB_LD+=("  $sec 0x${BASH_REMATCH[1]} : { \"$WORK/$BASE.stubs.o\"($sec) }")
  STUBS=$(( STUBS + 1 ))
done < <(arm-none-eabi-nm -u "$OBJ" | awk '{print $NF}')

{
  echo 'SECTIONS'
  echo '{'
  echo "  .text $ADDR : { \"$OBJ\"(.text) }"
  for l in ${STUB_LD[@]+"${STUB_LD[@]}"}; do echo "$l"; done
  echo '  /DISCARD/ : { *(.ARM.attributes) *(.comment) *(.note*) }'
  echo '}'
} > "$WORK/$BASE.ld"

LINK_OBJS=("$OBJ")
if [ "$STUBS" -gt 0 ]; then
  arm-none-eabi-as -mcpu=arm7tdmi -mthumb-interwork -o "$WORK/$BASE.stubs.o" "$WORK/$BASE.stubs.s"
  LINK_OBJS+=("$WORK/$BASE.stubs.o")
fi

# ld refuses to place a section at an address its alignment forbids, and gcc's .text asks for 4;
# thumb functions may start at ADDR % 4 == 2, so relax the alignment to 2 first.
if [ $(( $ADDR % 4 )) -ne 0 ]; then
  arm-none-eabi-objcopy --set-section-alignment .text=2 "$OBJ"
fi

# --no-check-sections: a stub can sit inside the address range of the function we are matching.
arm-none-eabi-ld -T "$WORK/$BASE.ld" --no-check-sections -o "$WORK/$BASE.elf" \
    "${LINK_OBJS[@]}" "$REPO/private/tools/agbcc/lib/libgcc.a" 2> "$WORK/$BASE.ld.log" || {
  cat "$WORK/$BASE.ld.log" >&2; exit 4; }

# -j .text: only the object's own bytes, not the stubs and not anything pulled from libgcc.
arm-none-eabi-objcopy -j .text -O binary "$WORK/$BASE.elf" "$WORK/$BASE.bin"
