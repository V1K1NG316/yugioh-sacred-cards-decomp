#!/usr/bin/env bash
# Run one script against a freshly launched mGBA gdb-stub session.
# mGBA's stub takes one client per launch, so every run gets a new emulator.
#   bash scripts/emu_groundtruth.sh scripts/emu_card_image.py
#   bash scripts/emu_groundtruth.sh <script.py> [args]      (args go to the script)
#
# The stub binds 0.0.0.0:2345 and `mgba-qt --help` offers no way to change that, so by default
# both the emulator and the script run inside a private network namespace
# (`unshare --user --map-root-user --net`, loopback brought up): the port never reaches the LAN.
# Set EMU_NO_NETNS=1 to run in the normal namespace instead — the stub is then reachable from
# the whole network for the length of the run (see docs/tools.md).
#
# The emulator is the system mGBA (`/usr/bin/mgba-qt`, 0.10.5; `-g` opens the GDB stub on
# port 2345 — `mgba-qt --help`). Override it with MGBA=/path/to/emulator. It runs on a copy of
# the ROM at private/tmp/ygo.gba (made from private/baserom.gba when missing), so nothing is
# written next to the original.
#
# A GUI window opens on the desktop while the script runs: that is expected.
# Only the emulator this script started is killed (its PID: SIGTERM, up to 3 s, then SIGKILL),
# never anything else. Exit codes: 0/script's own, 1 for a failed launch, 2 for a usage error.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
PY=python3
MGBA=${MGBA:-/usr/bin/mgba-qt}
ROM=$ROOT/private/tmp/ygo.gba
LOG=$ROOT/private/tmp/mgba_run.log
PORT=2345

if [ "$#" -lt 1 ]; then
  echo "usage: emu_groundtruth.sh <script.py> [args]" >&2
  exit 2
fi

# Who, if anyone, holds $PORT in *this* network namespace?  `ss -ltnp` names the owning pid
# only for sockets of processes we may inspect, which is all we need: our own mGBA.
port_busy() {
  ss -ltn -H 2>/dev/null | awk '{print $4}' | grep -qE "[:.]$PORT\$"
}
port_owner() {
  ss -ltnp -H 2>/dev/null | grep -E "[:.]$PORT[[:space:]]" \
    | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2
}

# Refuse before launching: mGBA cannot take the stub port, and a second emulator would just wait
# for a script that can only ever reach one of them.
refuse_if_busy() {  # $1 = where we looked
  if port_busy; then
    echo "emu_groundtruth: port $PORT is already in use$1; mGBA's gdb stub needs it free." >&2
    ss -ltnp 2>/dev/null | grep -E "[:.]$PORT[[:space:]]" >&2 || true
    exit 1
  fi
}

# The port is checked on the real machine and again inside the private namespace: a leftover
# listener on the host is invisible from inside a namespace, but it still means a stale emulator
# (or another run) is around, so the run is refused either way.
refuse_if_busy " (checked on the host)"

if [ "${EMU_NO_NETNS:-0}" != 1 ] && [ "${EMU_IN_NETNS:-0}" != 1 ]; then
  if ! command -v unshare >/dev/null 2>&1; then
    echo "emu_groundtruth: unshare not found; re-run with EMU_NO_NETNS=1 (the stub will then be reachable from the LAN)" >&2
    exit 1
  fi
  if ! unshare --user --map-root-user --net true >/dev/null 2>&1; then
    echo "emu_groundtruth: cannot create a private network namespace (unshare --user --map-root-user --net failed);" >&2
    echo "emu_groundtruth: re-run with EMU_NO_NETNS=1 (the stub will then be reachable from the LAN)" >&2
    exit 1
  fi
  # Re-enter this script inside the namespace, loopback up, all arguments unchanged.
  exec unshare --user --map-root-user --net \
    bash -c 'ip link set lo up || exit 1; EMU_IN_NETNS=1 exec bash "$@"' _ "$0" "$@"
fi

refuse_if_busy " (checked inside the private network namespace)"
cd "$ROOT" || exit 1
[ -x "$MGBA" ] || { echo "emu_groundtruth: $MGBA is not executable (set MGBA=...)" >&2; exit 2; }
mkdir -p "$ROOT/private/tmp"
[ -f "$ROM" ] || cp private/baserom.gba "$ROM" || exit 1

PID=""
kill_mgba() {
  [ -n "$PID" ] || return 0
  kill -TERM "$PID" >/dev/null 2>&1
  local i
  for i in $(seq 1 30); do          # up to 3 s for a clean exit
    kill -0 "$PID" 2>/dev/null || break
    sleep 0.1
  done
  if kill -0 "$PID" 2>/dev/null; then
    echo "emu_groundtruth: pid $PID ignored SIGTERM for 3 s; sending SIGKILL" >&2
    kill -KILL "$PID" >/dev/null 2>&1
  fi
  wait "$PID" 2>/dev/null
  PID=""
}
trap 'kill_mgba' EXIT
trap 'kill_mgba; exit 130' INT TERM

"$MGBA" -g "$ROM" > "$LOG" 2>&1 &
PID=$!

ready=0
for _ in $(seq 1 25); do
  kill -0 "$PID" 2>/dev/null || break
  owner=$(port_owner)
  if [ "$owner" = "$PID" ]; then ready=1; break; fi
  if [ -n "$owner" ]; then
    echo "emu_groundtruth: port $PORT is owned by pid $owner, not by our mGBA (pid $PID); log: $LOG" >&2
    exit 1
  fi
  sleep 1
done
if ! kill -0 "$PID" 2>/dev/null; then
  echo "emu_groundtruth: $MGBA exited at startup; log: $LOG" >&2
  sed -n '1,20p' "$LOG" >&2
  exit 1
fi
if [ "$ready" != 1 ]; then
  echo "emu_groundtruth: the gdb stub is not listening on port $PORT with pid $PID; log: $LOG" >&2
  exit 1
fi
sleep 6                              # the stub accepts connections before the game has booted

"$PY" "$@"
rc=$?
kill_mgba
exit $rc
