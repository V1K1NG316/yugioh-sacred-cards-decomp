#!/usr/bin/env bash
# Build the ROM in WSL and compare it with the original (milestone Y1).
set -euo pipefail
cd /mnt/d/Yugioh_DeComp_V2
make compare
