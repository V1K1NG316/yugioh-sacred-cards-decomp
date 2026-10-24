#!/usr/bin/env bash
# Build the ROM and compare it with the original (milestone Y1).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
make compare
