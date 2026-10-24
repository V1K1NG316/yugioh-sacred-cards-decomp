#!/usr/bin/env bash
# Y5: fetch and set up the two community tools the matching loop uses. Run once:
#   bash scripts/decomp_tools.sh
#
# - private/tools/decomp-permuter  github.com/simonlindholm/decomp-permuter  (randomized search
#   for a function's C, used by scripts/permute_func.sh)
# - private/tools/asm-differ       github.com/simonlindholm/asm-differ       (the side-by-side
#   assembly diff, used by scripts/diff_func.sh)
# Both are pinned to a commit, so a run is reproducible; `git -C ... rev-parse HEAD` prints what
# is checked out. Licences and commit hashes are recorded in docs/credits.md.
#
# - private/venv: the Python the permuter and asm-differ need. pip is bootstrapped *into* the
#   venv with `python3 -m ensurepip` (part of the stdlib); only if the interpreter ships no
#   ensurepip does it fall back to https://bootstrap.pypa.io/get-pip.py, fetched with `curl -fsSL`.
#   The packages are pinned to the versions `private/venv/bin/pip freeze` reported on 2026-10-24,
#   so a run reproduces the same venv. Everything stays in private/; nothing is installed
#   system-wide.
#
# Safe to re-run: existing checkouts are fetched, the venv is reused.
set -euo pipefail
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
TOOLS=$REPO/private/tools
VENV=$REPO/private/venv
PERM_COMMIT=8556c81d80d1c1af98a858c8f4dc951357f29139
DIFF_COMMIT=0dd09af8f8008f1f880327cf0aca3b26d2562ea2
# pip freeze in private/venv, 2026-10-24 (rapidfuzz is Levenshtein's dependency):
DEPS=(toml==0.10.2 colorama==0.4.6 watchdog==6.0.0 Levenshtein==0.27.5 rapidfuzz==3.14.6 cxxfilt==0.3.0)

clone_at() {  # url directory commit
  local url=$1 dir=$2 commit=$3
  if [ -d "$TOOLS/$dir/.git" ]; then
    git -C "$TOOLS/$dir" fetch --quiet origin
  else
    git clone --quiet "$url" "$TOOLS/$dir"
  fi
  git -C "$TOOLS/$dir" checkout --quiet "$commit"
  printf 'decomp_tools: %-16s %s\n' "$dir" "$(git -C "$TOOLS/$dir" rev-parse HEAD)"
}

mkdir -p "$TOOLS"
clone_at https://github.com/simonlindholm/decomp-permuter.git decomp-permuter "$PERM_COMMIT"
clone_at https://github.com/simonlindholm/asm-differ.git asm-differ "$DIFF_COMMIT"

if [ ! -x "$VENV/bin/python3" ]; then
  echo "decomp_tools: creating $VENV"
  python3 -m venv --without-pip "$VENV"
fi
if ! "$VENV/bin/python3" -m pip --version > /dev/null 2>&1; then
  echo "decomp_tools: bootstrapping pip inside the venv (ensurepip)"
  if ! "$VENV/bin/python3" -m ensurepip --upgrade --default-pip > /dev/null 2>&1; then
    echo "decomp_tools: ensurepip unavailable; falling back to get-pip.py"
    curl -fsSL -o "$VENV/get-pip.py" https://bootstrap.pypa.io/get-pip.py
    "$VENV/bin/python3" "$VENV/get-pip.py" --no-cache-dir > /dev/null
  fi
fi

# toml      decomp-permuter's settings.toml
# colorama  asm-differ's colours (imported at startup even for --format=plain)
# watchdog  asm-differ's --watch
# levenshtein/cxxfilt  asm-differ's better diff algorithm and --source
"$VENV/bin/python3" -m pip install --no-cache-dir --quiet "${DEPS[@]}"
"$VENV/bin/python3" -c 'import toml, colorama, watchdog, Levenshtein, cxxfilt; print("decomp_tools: python deps OK in", __import__("sys").prefix)'
"$VENV/bin/python3" -m pip freeze --disable-pip-version-check
printf 'decomp_tools: permuter    %s\n' "$TOOLS/decomp-permuter/permuter.py"
printf 'decomp_tools: asm-differ  %s\n' "$TOOLS/asm-differ/diff.py"
printf 'decomp_tools: done -- next: tools/permute_func.sh <name> [minutes] / tools/diff_func.sh <name>\n'
