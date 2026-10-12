#!/usr/bin/env bash
# Y5: `tools/diff_func.sh <name>` -- side-by-side diff of src/funcs/<name>.c against the ROM.
# The real thing is tools/diff_func.py (docstring there); this wrapper exists because the task and
# docs/decomp.md name it as a .sh. Works from the repo root or from a job worktree.
cd "$(dirname "$0")" || exit 1
exec "C:/Users/USER/AppData/Local/hermes/hermes-agent/.hermes-runtime/python/cpython-3.11-windows-x86_64-none/python.exe" diff_func.py "$@"
