#!/usr/bin/env bash
# Assemble one Thumb .s for the matching tools, with every undefined symbol turned into the
# absolute address its name spells.
#   bash scripts/asm_with_defsyms.sh <in.s> <out.o> [include_dir]
#
# Why: the C asks for a constant address as a symbol (`extern u8 gUnk_0201FCC0[]`), so agbcc
# writes `.word gUnk_0201FCC0` and the assembler leaves a relocation behind, while the ROM's own
# asm for the same bytes writes the constant inline (`.4byte 0x0201FCC0`). Tools that compare
# assembly *text* -- decomp-permuter, asm-differ -- would then report a difference that is not
# there. Defining each such symbol as an absolute value (`--defsym gUnk_0201FCC0=0x0201FCC0`) makes
# both sides read the same, and the value is exactly the address in the symbol's own name, so no
# guess is involved. Calls to other functions keep their relocation, which is what the ROM's asm
# has too, and the address in the name is what the linker would have used anyway.
#
# The bytes are unaffected: scripts/rom_func_obj.sh checks the result against the ROM, and
# tools/match_func.py is still the gate for any C.
set -euo pipefail
IN=$1
OUT=$2
INC=${3:-}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

AS_FLAGS=(-mcpu=arm7tdmi -mthumb-interwork)
[ -n "$INC" ] && AS_FLAGS+=(-I "$INC")

arm-none-eabi-as "${AS_FLAGS[@]}" -o "$TMP/pass1.o" "$IN"

# The names the assembled code refers to but does not define, saved next to the object: build_matched.sh
# needs them to decide which ones `make` must `.set` (see its comment), and after --defsym they are
# no longer visible as undefined symbols in the finished object.
DEFS=()
: > "$OUT.symrefs"
while read -r s; do
  [ -n "$s" ] || continue
  if [[ $s =~ ^[A-Za-z_][A-Za-z0-9_]*_([0-9A-Fa-f]{8})$ ]]; then
    addr=0x${BASH_REMATCH[1]}
  else
    # A named function (reset, crt0, irq_handler, main): its address is its row in config/functions.csv
    # (2026-10-14; before, every function referring to one of them could not be permuted or diffed).
    addr=$(awk -F, -v n="$s" '$2 == n { print $1; exit }' "$(dirname "$0")/../config/functions.csv")
    if [ -z "$addr" ]; then
      echo "asm_with_defsyms: $s is neither NAME_<8 hex digits> nor a named function in config/functions.csv; refusing to guess" >&2
      exit 2
    fi
  fi
  printf '%s\n' "$s" >> "$OUT.symrefs"
  DEFS+=(--defsym "$s=$addr")
done < <(arm-none-eabi-nm -u "$TMP/pass1.o" | awk '{print $NF}')

arm-none-eabi-as "${AS_FLAGS[@]}" ${DEFS[@]+"${DEFS[@]}"} -o "$OUT" "$IN"
