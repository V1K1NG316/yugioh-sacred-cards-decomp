#!/usr/bin/env bash
# Y5: `tools/permute_func.sh <name> [minutes] [--base file.c] [--jobs N]` -- time-boxed search
# for a near-miss function with decomp-permuter. The work happens in scripts/permute_func.sh,
# which explains the whole setup; this wrapper only carries the call there.
#
# The best candidate lands in private/permuter/<name>/best.c -- never in src/. A candidate that
# scores 0 still has to pass `python3 tools/match_func.py <name>` before it is copied in.
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
exec bash "$REPO/scripts/permute_func.sh" "$@"
