#!/usr/bin/env bash
# Run one script against a freshly launched mGBA gdb-stub session.
# mGBA's stub takes one client per launch, so every run gets a new emulator.
#   bash scripts/emu_groundtruth.sh scripts/emu_card_image.py
# The mGBA copy lives in private/tmp/mgba and the ROM copy in private/tmp/ygo.gba
# (created with: cp -r <mGBA dir>/. private/tmp/mgba/ ; cp private/baserom.gba private/tmp/ygo.gba).
set -u
ROOT=/d/Yugioh_DeComp_V2
PY="C:/Users/USER/AppData/Local/hermes/hermes-agent/.hermes-runtime/python/cpython-3.11-windows-x86_64-none/python.exe"

kill_mgba() {
  for pid in $(powershell -NoProfile -Command "(Get-Process mGBA -ErrorAction SilentlyContinue).Id" 2>/dev/null | tr -d '\r'); do
    [ -n "$pid" ] && taskkill /F /PID "$pid" >/dev/null 2>&1
  done
}

cd "$ROOT" || exit 1
kill_mgba
sleep 2
( cd private/tmp/mgba && ./mGBA.exe -g -1 ../ygo.gba > ../mgba_run.log 2>&1 ) &
for _ in $(seq 1 25); do
  netstat -ano 2>/dev/null | grep -q '0.0.0.0:2345' && break
  sleep 1
done
sleep 6
"$PY" "$1"
rc=$?
kill_mgba
exit $rc
