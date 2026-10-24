#!/usr/bin/env bash
# Run one script against a freshly launched mGBA gdb-stub session.
# mGBA's stub takes one client per launch, so every run gets a new emulator.
#   bash scripts/emu_groundtruth.sh scripts/emu_card_image.py
#
# The emulator is the system mGBA (`/usr/bin/mgba-qt`, 0.10.5; `-g` opens the GDB stub on
# port 2345 — `mgba-qt --help`). Override it with MGBA=/path/to/emulator. It runs on a copy of
# the ROM at private/tmp/ygo.gba (made from private/baserom.gba when missing), so nothing is
# written next to the original.
#
# A GUI window opens on the desktop while the script runs: that is expected.
# Only the emulator this script started is killed (its PID), never anything else.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
PY=python3
MGBA=${MGBA:-/usr/bin/mgba-qt}
ROM=$ROOT/private/tmp/ygo.gba
LOG=$ROOT/private/tmp/mgba_run.log
PORT=2345

cd "$ROOT" || exit 1
[ -x "$MGBA" ] || { echo "emu_groundtruth: $MGBA is not executable (set MGBA=...)" >&2; exit 2; }
mkdir -p "$ROOT/private/tmp"
[ -f "$ROM" ] || cp private/baserom.gba "$ROM" || exit 1

PID=""
kill_mgba() {
  [ -n "$PID" ] || return 1
  kill "$PID" >/dev/null 2>&1 || return 1
  wait "$PID" 2>/dev/null
  PID=""
}
trap 'kill_mgba' EXIT INT TERM

"$MGBA" -g "$ROM" > "$LOG" 2>&1 &
PID=$!

for _ in $(seq 1 25); do
  kill -0 "$PID" 2>/dev/null || break
  ss -ltn 2>/dev/null | grep -q ":$PORT " && break
  sleep 1
done
if ! kill -0 "$PID" 2>/dev/null; then
  echo "emu_groundtruth: $MGBA exited at startup; log: $LOG" >&2
  sed -n '1,20p' "$LOG" >&2
  exit 1
fi
if ! ss -ltn 2>/dev/null | grep -q ":$PORT "; then
  echo "emu_groundtruth: the gdb stub is not listening on port $PORT; log: $LOG" >&2
  exit 1
fi
sleep 6
"$PY" "$1"
rc=$?
kill_mgba
exit $rc
