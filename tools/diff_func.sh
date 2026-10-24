#!/usr/bin/env bash
# Y5: `tools/diff_func.sh <name>` -- side-by-side diff of src/funcs/<name>.c against the ROM.
# The real thing is tools/diff_func.py (docstring there); this wrapper exists because the task and
# docs/decomp.md name it as a .sh. Works from the repo root or from a job worktree.
exec python3 "$(dirname "$0")/diff_func.py" "$@"
