#!/usr/bin/env bash
# Y5: run decomp-permuter on one function, time-boxed, and keep the best candidate it finds.
# Run from anywhere (tools/permute_func.sh wraps this):
#   bash scripts/permute_func.sh <name> [minutes] [--base <file.c>] [--jobs N]
#
# Sets up private/permuter/<name>/ from scratch:
#   target.o    the ROM's own bytes for this function (scripts/rom_func_obj.sh, which checks them
#               against the ROM) -- the permuter scores every candidate against this
#   base.c      src/funcs/<name>.c, or --base <file.c> to start from something else
#               (e.g. a deliberately perturbed copy, to see what the permuter can find)
#   global.h    a copy of include/global.h, because the permuter preprocesses base.c itself with
#               `cpp -P -nostdinc`, which only finds a quoted include next to the file
#   compile.sh  a generated copy of the harness pipeline (agbcc -> as), so a candidate is compiled
#               by the same compiler with the same flags as the real check
#   function.txt/settings.toml   which function the permuter is looking at
# The permuter then runs for <minutes> (default 5) and its best candidate is copied to
# private/permuter/<name>/best.c. Nothing is ever written into src/: a candidate that scores 0
# still has to pass `tools/match_func.py <name>` and be copied in by hand.
#
# This is a search tool for near misses, run by a human/agent -- deliberately NOT something a
# local job runs: it is slow, it is opaque about what it tried, and the score is not the check.
set -euo pipefail
NAME=$1
shift
MINUTES=5
if [ $# -gt 0 ] && [[ $1 =~ ^[0-9]+$ ]]; then
  MINUTES=$1
  shift
fi
BASE=""
JOBS=8
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE=$2; shift 2 ;;
    --jobs) JOBS=$2; shift 2 ;;
    *) echo "permute_func: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
PERM=$REPO/private/tools/decomp-permuter/permuter.py
PY=$REPO/private/venv/bin/python3
DIR=$REPO/private/permuter/$NAME

[ -f "$PERM" ] || { echo "permute_func: $PERM is missing -- run scripts/decomp_tools.sh first" >&2; exit 2; }
[ -x "$PY" ] || { echo "permute_func: $PY is missing -- run scripts/decomp_tools.sh first" >&2; exit 2; }

if [ -z "$BASE" ]; then
  BASE=$REPO/src/funcs/$NAME.c
  [ -f "$BASE" ] || { echo "permute_func: no such file: $BASE (pass --base to use another .c)" >&2; exit 2; }
else
  [ -f "$BASE" ] || { echo "permute_func: no such file: $BASE" >&2; exit 2; }
fi

mkdir -p "$DIR"
# Old candidates from a previous run would otherwise be mistaken for this run's best.
rm -rf "$DIR"/output-*
cp "$BASE" "$DIR/base.c"
cp "$REPO/include/global.h" "$DIR/global.h"
printf '%s\n' "$NAME" > "$DIR/function.txt"
{
  echo "# decomp-permuter settings for $NAME (private/tools/decomp-permuter/README.md)."
  echo "func_name = \"$NAME\""
  echo "compiler_type = \"gcc\"   # agbcc is gcc 2.9; picks this project's pass weights"
} > "$DIR/settings.toml"

cat > "$DIR/compile.sh" <<'COMPILE'
#!/usr/bin/env bash
# Written by scripts/permute_func.sh; the permuter calls it as `compile.sh <in.c> -o <out.o>`.
# The harness pipeline and flags (scripts/match_func.sh) minus -Werror: a warning does not change
# the bytes, and the winner is re-checked by tools/match_func.py, which keeps -Werror.
set -euo pipefail
IN=$1
OUT=$3
REPO=@REPO@
A=$REPO/private/tools/agbcc
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
# Compiler per file (A37): a C file whose first line is `/* compiler: agbcc ... */` was built by the
# newer agbcc (most of 0x0802B000-0x08035FFF matches only with it); every other file uses old_agbcc.
# AGBCC=<name> in the environment overrides both (experiments only).
CC=${AGBCC:-}
if [ -z "$CC" ]; then
  if head -1 "$IN" | grep -q "^/\* compiler: agbcc\b"; then CC=agbcc; else CC=old_agbcc; fi
fi
cpp -nostdinc -undef -std=gnu89 -I "$A/include" -I "$A" -I "$REPO/include" -o "$T/c.i" "$IN"
"$A/bin/$CC" -mthumb-interwork -Wimplicit -Wparentheses -O2 -fhex-asm -o "$T/c.s" "$T/c.i"
bash "$REPO/scripts/asm_with_defsyms.sh" "$T/c.s" "$OUT"
COMPILE

# compile.sh is generated inside private/permuter/<name>/, so its own location says nothing about
# the repo root: the @REPO@ placeholder above is replaced here with this checkout's root.
sed -i "s|^REPO=@REPO@\$|REPO=$REPO|" "$DIR/compile.sh"

bash "$REPO/scripts/rom_func_obj.sh" "$NAME" "$DIR"
cp "$DIR/$NAME.o" "$DIR/target.o"

echo "permute_func: base.c   = $BASE"
echo "permute_func: target.o = the ROM's bytes for $NAME (checked), $DIR"
echo "permute_func: running for ${MINUTES} min with $JOBS jobs; log: $DIR/run.log"

cd "$DIR"
set +e
timeout --signal=INT --kill-after=60 "$(( MINUTES * 60 ))" \
  "$PY" "$PERM" "$DIR" -j "$JOBS" --stop-on-zero 2>&1 \
  | tr '\r' '\n' | tee "$DIR/run.log" | grep --line-buffered -v -E '^iteration'
STATUS=${PIPESTATUS[0]}
set -e
case "$STATUS" in
  0)   echo "permute_func: the permuter finished on its own (score 0, or all candidates exhausted)" ;;
  124) echo "permute_func: time is up after ${MINUTES} min; keeping the best candidate so far" ;;
  *)   echo "permute_func: the permuter exited with status $STATUS (see $DIR/run.log)" ;;
esac

ITER=$(grep -o 'iteration [0-9]*' "$DIR/run.log" | awk '{print $2}' | sort -n | tail -1 || true)
BASE_SCORE=$(sed -n 's/.*base score = \([0-9]*\).*/\1/p' "$DIR/run.log" | head -1)
echo "permute_func: base.c scores ${BASE_SCORE:-?}; ${ITER:-0} candidates compiled (full log: $DIR/run.log)"
grep -E 'found new best score|tied best score|Found zero score' "$DIR/run.log" | tail -3 || true
if [ "${BASE_SCORE:-}" = 0 ]; then
  echo "permute_func: base.c already scores 0 -- it compiles to the target, there is nothing to search for"
  exit 0
fi

BEST=$(ls -d "$DIR"/output-* 2>/dev/null | sed 's/.*output-\([0-9]*\)-.*/\1/' | sort -n | head -1)
if [ -z "$BEST" ]; then
  echo "permute_func: no candidate was better than base.c; nothing written to best.c" >&2
  exit 1
fi
BESTDIR=$(ls -d "$DIR"/output-$BEST-* | head -1)
cp "$BESTDIR/source.c" "$DIR/best.c"
printf 'permute_func: best score %s -> %s/best.c\n' "$BEST" "$DIR"
if [ "$BEST" = 0 ]; then
  printf 'permute_func: score 0 -- check it before trusting it:\n'
  printf '  python3 tools/match_func.py %s   # with best.c copied to src/funcs/%s.c\n' "$NAME" "$NAME"
fi
