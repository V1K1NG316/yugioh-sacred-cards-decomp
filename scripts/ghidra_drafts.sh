#!/usr/bin/env bash
# Y5: Ghidra decompiler drafts for every function in config/functions.csv.
# Output: private/ghidra/<name>.c (one non-matching draft per function, untracked),
#         private/ghidra/project/ (the analysed Ghidra project, reused on re-runs).
#
# Run from anywhere:
#   bash scripts/ghidra_drafts.sh
#   ... --only sub_080016CC       # re-decompile one function (cheap: no re-import, no analysis)
#
# First run does three things: set up (scripts/ghidra_setup.sh) -> import the ROM raw as
# ARM:LE:32:v4t, disassemble and create every CSV function in its own mode -> auto-analyse, then
# decompile. Later runs reuse the analysed project; --only skips straight to one function.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ROOT="$PWD"
TOOLS="$ROOT/private/tools"
OUT="$ROOT/private/ghidra"
PROJ="$ROOT/private/ghidra/project"
HEADLESS="$TOOLS/ghidra/support/analyzeHeadless"
SCRIPTS="$ROOT/tools/ghidra"
CSV="$ROOT/config/functions.csv"
ROM="$ROOT/private/baserom.gba"
PROJECT=AY7E
PROGRAM=baserom.gba

ONLY=""
if [ "${1:-}" = "--only" ]; then
    ONLY="${2:?--only needs a function name}"
fi

[ -x "$HEADLESS" ] || { echo "missing $HEADLESS -- run scripts/ghidra_setup.sh first"; exit 1; }
[ -f "$CSV" ] || { echo "missing $CSV"; exit 1; }
export JAVA_HOME="$TOOLS/jdk"
export PATH="$JAVA_HOME/bin:$PATH"

run() {  # label + analyzeHeadless args
    local label="$1"; shift
    mkdir -p "$ROOT/private/logs"
    local log="$ROOT/private/logs/ghidra_$(echo "$label" | tr ' /' '__').log"
    echo "=== $label: $(date '+%H:%M:%S')  (log: $log)"
    local t0=$SECONDS rc=0
    "$HEADLESS" "$PROJ" "$PROJECT" "$@" \
        -scriptPath "$SCRIPTS" \
        -max-cpu 8 > "$log" 2>&1 || rc=$?
    echo "=== $label: headless exit $rc in $((SECONDS - t0))s"
    grep -vE '^(INFO|WARN) ' "$log" || true
    # surface the script's own summary lines (they are INFO-prefixed like everything else)
    grep -E 'GhidraScript\)|ERROR REPORT' "$log" | sed 's/^INFO  //' || true
    [ "$rc" = 0 ] || exit "$rc"
}

mkdir -p "$OUT" "$PROJ"

if [ -n "$ONLY" ]; then
    [ -f "$PROJ/$PROJECT.rep/project.prp" ] || { echo "no project yet: run without --only first"; exit 1; }
    run "drafts --only $ONLY" -process "$PROGRAM" -noanalysis \
        -postScript GbaDecompDrafts.java drafts "$CSV" "$OUT" --only "$ONLY"
    exit 0
fi

if [ -f "$PROJ/$PROJECT.rep/project.prp" ]; then
    run "drafts (project already analysed)" -process "$PROGRAM" -noanalysis \
        -postScript GbaDecompDrafts.java drafts "$CSV" "$OUT"
    exit 0
fi

# Phase 1: import + functions. Analysis is off: it would guess ARM everywhere (TMode 0) and
# disassemble the THUMB code the wrong way before we can set the mode per function.
run "import + functions" -import "$ROM" -processor ARM:LE:32:v4t \
    -loader BinaryLoader -loader-baseAddr 0x08000000 -noanalysis \
    -postScript GbaDecompDrafts.java funcs "$CSV" "$OUT"

# Phase 2: auto-analyse the project (function bodies, stack, cross references), then decompile.
# The analysis is time-boxed: on a raw 16 MiB blob the analyzers keep guessing functions inside
# the data (10 MB of it) and one pass ran >35 min without finishing (measured [020]). 600 s is
# enough for the code region; the decompiler works from the disassembly we set up in phase 1.
run "analyse + drafts" -process "$PROGRAM" -analysisTimeoutPerFile 600 \
    -postScript GbaDecompDrafts.java drafts "$CSV" "$OUT"
