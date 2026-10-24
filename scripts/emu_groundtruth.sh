#!/usr/bin/env bash
# Run one script against a freshly launched mGBA gdb-stub session.
# mGBA's stub takes one client per launch, so every run gets a new emulator.
#   bash scripts/emu_groundtruth.sh scripts/emu_card_image.py
# The mGBA copy lives in private/tmp/mgba and the ROM copy in private/tmp/ygo.gba
# (created with: cp -r <mGBA dir>/. private/tmp/mgba/ ; cp private/baserom.gba private/tmp/ygo.gba).
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
PY=python3

kill_mgba() {
  pkill -f 'private/tmp/mgba' >/dev/null 2>&1
  sleep 1
}

cd "$ROOT" || exit 1
kill_mgba
sleep 2
( cd private/tmp/mgba && ./mGBA -g -1 ../ygo.gba > ../mgba_run.log 2>&1 ) &
for _ in $(seq 1 25); do
  ss -ltn 2>/dev/null | grep -q '0.0.0.0:2345\|\[::\]:2345\|\*:2345' && break
  sleep 1
done
sleep 6
"$PY" "$1"
rc=$?
kill_mgba
exit $rc
