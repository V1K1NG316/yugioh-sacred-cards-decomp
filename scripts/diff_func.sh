#!/usr/bin/env bash
# Y5: side-by-side diff of one function's C against the ROM's own bytes (asm-differ).
# Run inside WSL from the repo root; tools/diff_func.sh (Git Bash) and tools/diff_func.py drive it:
#   bash scripts/diff_func.sh <name> <0xADDR> <srcdir> [rundir]
#
# 1. scripts/match_func.sh builds <srcdir>/<name>.c with agbcc and links it at ADDR -- the same
#    build tools/match_func.py compares, so the diff shows what the check sees.
# 2. scripts/rom_func_obj.sh turns the ROM's own asm for that function into an object, checked
#    against the ROM.
# 3. private/tools/asm-differ/diff.py prints the two objects side by side (-o: two object files,
#    ours as -f, the ROM's as -F; no map file is needed in that mode).
# Both objects go through scripts/asm_with_defsyms.sh, so a constant the C names by a symbol
# (`gUnk_0201FCC0`) and the ROM's inline constant read the same: the diff shows real differences,
# not toolchain bookkeeping.
#
# Exit 0 whenever a diff was produced; whether the C matches is match_func.py's verdict, not this.
set -euo pipefail
NAME=$1
ADDR=$2
SRCDIR=$3
REPO=/mnt/d/Yugioh_DeComp_V2
WORK=${4:-$REPO/private/build/match/$NAME.diff}
DIFF=$REPO/private/tools/asm-differ/diff.py
PY=$REPO/private/venv/bin/python3

[ -f "$DIFF" ] || { echo "diff_func: $DIFF is missing -- run scripts/decomp_tools.sh first" >&2; exit 2; }
[ -x "$PY" ] || { echo "diff_func: $PY is missing -- run scripts/decomp_tools.sh first" >&2; exit 2; }

bash "$REPO/scripts/match_func.sh" "$NAME" "$ADDR" "$SRCDIR" "$WORK"
bash "$REPO/scripts/rom_func_obj.sh" "$NAME" "$WORK/ref" > /dev/null

# asm-differ reads diff_settings.py from the directory it is started in, so one is written there.
STAGE=$REPO/private/build/diff/$NAME
mkdir -p "$STAGE"
cat > "$STAGE/diff_settings.py" <<'SETTINGS'
# Written by scripts/diff_func.sh -- asm-differ loads this from the directory it runs in.
def apply(config, args):
    config["arch"] = "arm32"
    config["objdump_executable"] = "arm-none-eabi-objdump"
SETTINGS

cd "$STAGE"
set +e
"$PY" "$DIFF" "$NAME" -o -f "$WORK/$NAME.o" -F "$WORK/ref/$NAME.o" --format=plain --no-pager
STATUS=$?
set -e
if [ "$STATUS" -ne 0 ]; then
  echo "diff_func: asm-differ exited with status $STATUS (objects: $WORK)" >&2
fi
exit "$STATUS"
