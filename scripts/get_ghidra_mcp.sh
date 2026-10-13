#!/usr/bin/env bash
# Fetch bethington/ghidra-mcp into private/tools/ghidra-mcp (untracked, portable).
# Run inside WSL from the repo root:
#   wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/get_ghidra_mcp.sh [commit]
# The commit is pinned: what ships is fetched, recorded in docs/credits.md, and never updated
# silently. Re-running with the same commit only checks it is the same checkout.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
TOOLS="private/tools"
PIN="${1:-}"
REPO="$TOOLS/ghidra-mcp"
mkdir -p "$TOOLS"
if [ ! -d "$REPO/.git" ]; then
    git clone --quiet https://github.com/bethington/ghidra-mcp "$REPO"
fi
git -C "$REPO" fetch --quiet --tags origin
if [ -z "$PIN" ]; then
    PIN="$(git -C "$REPO" rev-parse origin/HEAD 2>/dev/null || git -C "$REPO" rev-parse origin/main)"
fi
git -C "$REPO" checkout --quiet "$PIN"
echo "ghidra-mcp: $(git -C "$REPO" rev-parse HEAD)"
git -C "$REPO" log -1 --format='date: %ci   subject: %s'
