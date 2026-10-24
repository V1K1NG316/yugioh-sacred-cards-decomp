#!/usr/bin/env bash
# Y5: the ROM's own bytes for one function, as an object file.
# Run from the repo root (tools/diff_func.py and scripts/permute_func.sh do):
#   bash scripts/rom_func_obj.sh <name> <outdir>
#
# <outdir>/<name>.o is the thing that matters: an arm-none-eabi object whose .text is that
# function's code, assembled from the ROM's own disassembly (private/asm/rom_full.s, the file
# gbadisasm produced from private/baserom.gba). It is what asm-differ diffs our C against and
# what the permuter scores its candidates against -- so "does this C match?" is answered against
# the ROM's real instructions, not against another compiler's idea of them.
#
# The object is checked before it is used, both ways:
#   1. linked at the function's address with scripts/link_at.sh (calls resolved to stubs placed at
#      their real ROM addresses) and compared, byte for byte, with the ROM;
#   2. when the object has no relocations at all, its raw .text is compared with the ROM too,
#      because that is exactly what the permuter and asm-differ see.
# Exit 0 only if check 1 passes.
#
# Intermediates, all inside <outdir>: <name>.rom.s (the extracted asm), <name>.target.s (the same
# wrapped for the assembler), verify.* and <name>.o -- the object itself.
set -euo pipefail
NAME=$1
OUT=$2
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)

ROW=$(awk -F, -v n="$NAME" 'NR > 1 && $2 == n {print $1, $3}' "$REPO/config/functions.csv")
[ -n "$ROW" ] || { echo "rom_func_obj: $NAME is not in config/functions.csv" >&2; exit 2; }
read -r ADDR MODE <<< "$ROW"
[ "$MODE" = thumb ] || { echo "rom_func_obj: $NAME is $MODE code; only THUMB is supported" >&2; exit 2; }

mkdir -p "$OUT"
OFF=$(( ADDR - 0x08000000 ))

# The function's own asm: from `thumb_func_start <name>` up to the next function, or to the first
# .incbin. Bytes past the function belong to the next function or to data that is not ours.
awk -v n="$NAME" '
  inf && /^[ \t]*(arm|thumb|non_word_aligned_thumb)_func_start/ { exit }
  inf && /^[ \t]*\.incbin/ { exit }
  /^[ \t]*thumb_func_start[ \t]+[A-Za-z_]/ && $2 == n { inf = 1 }
  inf { print }
' "$REPO/private/asm/rom_full.s" > "$OUT/$NAME.rom.s"
[ -s "$OUT/$NAME.rom.s" ] || {
  echo "rom_func_obj: no asm for $NAME in private/asm/rom_full.s (run scripts/disasm.sh first?)" >&2; exit 2; }

# A trailing `.align` is the ROM's own zero padding up to the next function's start, and it IS
# part of this function's extent in config/functions.csv (`size` = distance to the next start).
# It must stay, and it must say what it fills with: the disassembly writes `.align 2, 0`, which
# emits `00 00` like the ROM. Trimming the line instead makes the assembler round the section up
# on its own, and it fills that with `c0 46` (mov r8,r8 -- the Thumb nop), so the last bytes come
# out as `c0 46` where the ROM has `00 00` and every padded function fails its compare (seen on
# sub_080045C4). So: drop trailing blank lines only, and make any trailing bare `.align N`
# explicit about its zero fill.
awk '{ lines[NR] = $0 }
     END { last = NR
           while (last > 0 && lines[last] ~ /^[ \t]*$/) last--
           if (last > 0 && lines[last] ~ /^[ \t]*\.align[ \t]+[0-9]+[ \t]*$/) {
             sub(/[ \t]*$/, "", lines[last]); lines[last] = lines[last] ", 0"
           }
           for (i = 1; i <= last; i++) print lines[i] }' \
  "$OUT/$NAME.rom.s" > "$OUT/$NAME.rom.s.trim"
mv "$OUT/$NAME.rom.s.trim" "$OUT/$NAME.rom.s"

{
  echo '	.include "asm/macros.inc"'
  echo '	.syntax unified'
  echo '	.text'
  cat "$OUT/$NAME.rom.s"
} > "$OUT/$NAME.target.s"

if ! bash "$REPO/scripts/asm_with_defsyms.sh" "$OUT/$NAME.target.s" "$OUT/$NAME.o" "$REPO" \
      2> "$OUT/$NAME.as.log"; then
  echo "rom_func_obj: the ROM asm for $NAME does not assemble:" >&2
  cat "$OUT/$NAME.as.log" >&2
  exit 1
fi

# 1. Linked at its address, the object's bytes must be the ROM's bytes.
cp "$OUT/$NAME.o" "$OUT/verify.o"
bash "$REPO/scripts/link_at.sh" "$OUT" verify "$OUT/verify.o" "$ADDR"
if [ -s "$OUT/verify.unresolved" ]; then
  echo "rom_func_obj: $NAME references symbols that are not NAME_<8 hex digits>:" >&2
  cat "$OUT/verify.unresolved" >&2
  exit 1
fi
LEN=$(stat -c%s "$OUT/verify.bin")
dd if="$REPO/private/baserom.gba" of="$OUT/verify.rom.bin" bs=1 skip="$OFF" count="$LEN" status=none
if ! cmp -s "$OUT/verify.bin" "$OUT/verify.rom.bin"; then
  echo "rom_func_obj: $NAME: the assembled ROM asm is NOT the ROM's bytes:" >&2
  od -An -tx1 "$OUT/verify.bin" >&2
  od -An -tx1 "$OUT/verify.rom.bin" >&2
  exit 1
fi

# 2. Same bytes straight out of the object, when nothing in it needs relocating.
RELS=$(arm-none-eabi-objdump -r "$OUT/$NAME.o" | grep -c 'R_ARM_' || true)
if [ "$RELS" -eq 0 ]; then
  arm-none-eabi-objcopy -j .text -O binary "$OUT/$NAME.o" "$OUT/$NAME.raw.bin"
  RAW=$(stat -c%s "$OUT/$NAME.raw.bin")
  dd if="$REPO/private/baserom.gba" of="$OUT/$NAME.raw.rom.bin" bs=1 skip="$OFF" count="$RAW" status=none
  if ! cmp -s "$OUT/$NAME.raw.bin" "$OUT/$NAME.raw.rom.bin"; then
    echo "rom_func_obj: $NAME: the object's raw .text is not the ROM's bytes" >&2
    exit 1
  fi
  RAW_NOTE="raw .text also identical"
else
  RAW_NOTE="$RELS relocation line(s): the bytes only become the ROM's after linking, same as for any candidate object"
fi

printf 'rom_func_obj: %s @ %s: %s bytes, linked bytes identical to the ROM (%s)\n' \
  "$NAME" "$ADDR" "$LEN" "$RAW_NOTE"
