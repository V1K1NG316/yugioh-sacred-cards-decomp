#!/usr/bin/env bash
# Run the permuter on many functions at once (Claude, 2026-10-14; Matter_Scatter: "use ~20 cores").
#   bash tools/permute_many.sh <minutes> <parallel> name1 name2 ...      (from anywhere)
# Each function runs tools/permute_func.sh with --jobs 2 and its draft private/drafts/<name>.c as the base
# (or private/drafts/<name>.<tag>.c files, see STYLE below). A candidate the permuter scores 0 is re-checked
# with the real gate (tools/match_func.py, in the scratch worktree private/worktrees/claude-draftcheck) and,
# only if it MATCHes, saved as private/drafts/<name>.perm.c for Claude to tidy and queue.
# Results: private/permuter/many.tsv (name, base, score, match). Never touches src/ or git.
#
# STYLE: if PERMUTE_BASES="v1 v2 ..." is set, each name runs once per base private/drafts/<name>.<v>.c
# (the style-variant experiment); the result rows say which base won.
set -uo pipefail
MIN=$1; PAR=$2; shift 2
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
PY=python3
W=$R/private/worktrees/claude-draftcheck
OUT=$R/private/permuter/many.tsv
cd "$R"
touch "$OUT"

one() {  # name base_file tag
  local n=$1 base=$2 tag=$3 dir score res
  dir=$R/private/permuter/$n${tag:+.$tag}
  bash "$R/tools/permute_func.sh" "$n" "$MIN" --base "${base#$R/}" --jobs 2 > "$R/private/permuter/log_$n${tag:+.$tag}.txt" 2>&1
  # permute_func.sh always writes into private/permuter/<name>; keep a per-variant copy
  if [ -n "$tag" ] && [ -d "$R/private/permuter/$n" ]; then rm -rf "$dir"; cp -r "$R/private/permuter/$n" "$dir"; fi
  score=$(grep -o 'best score [0-9]*' "$R/private/permuter/log_$n${tag:+.$tag}.txt" | tail -1 | grep -o '[0-9]*$')
  res=none
  if [ "${score:-x}" = 0 ] && [ -f "$dir/best.c" ]; then
    # flock-free: the gate builds in a per-pid dir, but the source file name is shared -> serialise via mkdir lock
    until mkdir "$R/private/permuter/.gate.lock" 2>/dev/null; do sleep 1; done
    cp "$dir/best.c" "$W/src/funcs/$n.c"
    if (cd "$W" && "$PY" tools/match_func.py "$n" | head -1 | grep -q '^MATCH'); then
      res=MATCH; cp "$dir/best.c" "$R/private/drafts/$n.perm.c"
    else res=gate-fail; fi
    rm -f "$W/src/funcs/$n.c"; rmdir "$R/private/permuter/.gate.lock"
  fi
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date +%H:%M)" "$n" "${tag:-draft}" "${score:-error}" "$res" >> "$OUT"
}

jobs_list=()
for n in "$@"; do
  if [ -n "${PERMUTE_BASES:-}" ]; then
    for v in $PERMUTE_BASES; do [ -f "$R/private/drafts/$n.$v.c" ] && jobs_list+=("$n|$R/private/drafts/$n.$v.c|$v"); done
  else
    jobs_list+=("$n|$R/private/drafts/$n.c|")
  fi
done
# Variants of the same function cannot run at once (permute_func.sh shares private/permuter/<name>), so run
# them name by name inside one slot; different names run in parallel.
declare -A byname=()
for j in "${jobs_list[@]}"; do n=${j%%|*}; byname[$n]+="$j "; done
running=0
for n in "${!byname[@]}"; do
  ( for j in ${byname[$n]}; do IFS='|' read -r nn base tag <<< "$j"; one "$nn" "$base" "$tag"; done ) &
  running=$((running + 1))
  if [ "$running" -ge "$PAR" ]; then wait -n; running=$((running - 1)); fi
done
wait
echo "permute_many done: $(date +%H:%M)"
