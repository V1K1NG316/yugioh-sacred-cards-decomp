#!/usr/bin/env bash
# Y5: `tools/permute_func.sh <name> [minutes] [--base file.c] [--jobs N]` -- time-boxed search
# for a near-miss function with decomp-permuter. The work happens in WSL
# (scripts/permute_func.sh, which explains the whole setup); this wrapper only carries the call
# across and translates Windows-style paths to /mnt/d/... ones.
#
# The best candidate lands in private/permuter/<name>/best.c -- never in src/. A candidate that
# scores 0 still has to pass `PY tools/match_func.py <name>` before it is copied in.
set -euo pipefail
ARGS=()
for a in "$@"; do
  case "$a" in
    [A-Za-z]:[\\/]*) ARGS+=("$(echo "$a" | sed -E 's|^([A-Za-z]):[\\/]|/mnt/\L\1/|; s|\\|/|g')") ;;
    *) ARGS+=("$a") ;;
  esac
done
exec wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/permute_func.sh "${ARGS[@]}"
