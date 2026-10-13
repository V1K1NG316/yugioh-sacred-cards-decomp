#!/usr/bin/env bash
# Ghidra MCP server for this ROM: the ghidra-mcp *headless* server (Java, no Ghidra
# window) plus its MCP bridge (Python), both bound to 127.0.0.1 only.
#
#   wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/ghidra_mcp_server.sh start
#   ... stop      kill both by exact PID (nothing else is touched)
#   ... status    PIDs, ports, and the server's own /check_connection answer
#
# What `start` does:
#   1. private/tools/jdk + the ghidra-mcp headless jar built by
#      scripts/ghidra_mcp_build.sh, classpath = that jar + Ghidra's own jars
#      (exactly what the project's docker/entrypoint.sh builds);
#   2. the Java headless server on 127.0.0.1:8089, opening our analysed project
#      private/ghidra/project (AY7E) and the program baserom.gba;
#   3. the MCP bridge on 127.0.0.1:8081 as streamable-http, which is what an MCP
#      client (Hermes) connects to; the bridge translates MCP calls into HTTP
#      calls to the Java server on the same loopback.
# Both processes keep their PID in private/tmp/ and their output in
# private/tmp/*.log; both are untracked. Nothing is installed system-wide and
# no port is reachable off this machine (--bind 127.0.0.1, --mcp-host 127.0.0.1).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ROOT="$PWD"
TOOLS="$ROOT/private/tools"
SRC="$TOOLS/ghidra-mcp"
GHIDRA="$TOOLS/ghidra"
JAR="$SRC/target/GhidraMCP-7.0.0.jar"
VENV="$ROOT/private/venv"
TMP="$ROOT/private/tmp"
HOME_DIR="$TMP/ghidra-home"          # Ghidra's settings dir: inside the repo, not ~
PROJECT="$ROOT/private/ghidra/project"
PROGRAM=baserom.gba
HOST=127.0.0.1
PORT=8089                            # Java headless server
MCP_PORT=8081                        # MCP bridge (streamable-http)
PID_SERVER="$TMP/ghidra-mcp-server.pid"
PID_BRIDGE="$TMP/ghidra-mcp-bridge.pid"
LOG_SERVER="$TMP/ghidra-mcp-server.log"
LOG_BRIDGE="$TMP/ghidra-mcp-bridge.log"
START_TIMEOUT=300                    # the server opens a 16 MiB program on startup

log() { echo "[ghidra-mcp] $*"; }
alive() { [ -n "${1:-}" ] && kill -0 "$1" 2>/dev/null; }
read_pid() { [ -f "$1" ] && cat "$1" || true; }
port_open() { (exec 3<>"/dev/tcp/$HOST/$1") 2>/dev/null && exec 3>&- && return 0 || return 1; }

wait_for() {  # label timeout_s predicate...
    local label="$1" timeout="$2"; shift 2
    local t0=$SECONDS
    while [ $((SECONDS - t0)) -lt "$timeout" ]; do
        if "$@"; then return 0; fi
        sleep 2
    done
    log "TIMEOUT waiting for $label (${timeout}s)"
    return 1
}

server_classpath() {
    local cp="$JAR"
    local jar
    for jar in "$GHIDRA"/Ghidra/Framework/*/lib/*.jar \
               "$GHIDRA"/Ghidra/Features/*/lib/*.jar \
               "$GHIDRA"/Ghidra/Processors/*/lib/*.jar; do
        cp="$cp:$jar"
    done
    echo "$cp"
}

start() {
    [ -f "$JAR" ] || { log "missing $JAR -- run scripts/ghidra_mcp_build.sh"; exit 1; }
    [ -x "$TOOLS/jdk/bin/java" ] || { log "missing $TOOLS/jdk"; exit 1; }
    [ -x "$VENV/bin/python" ] || { log "missing $VENV/bin/python"; exit 1; }
    [ -f "$PROJECT/AY7E.rep/project.prp" ] || { log "missing analysed project $PROJECT -- run scripts/ghidra_drafts.sh"; exit 1; }
    mkdir -p "$TMP" "$HOME_DIR"

    local pid
    pid="$(read_pid "$PID_SERVER")"
    if alive "$pid"; then
        log "server already running (pid $pid)"
    else
        # Path endpoints (/import_file, /open_project, ...) are confined to the
        # repo; the server refuses anything outside GHIDRA_MCP_FILE_ROOT.
        export GHIDRA_MCP_FILE_ROOT="$ROOT"
        export JAVA_HOME="$TOOLS/jdk"
        nohup "$JAVA_HOME/bin/java" -Xmx4g \
            -Duser.home="$HOME_DIR" \
            -Dghidra.home="$GHIDRA" \
            -Dapplication.name=GhidraMCP \
            -classpath "$(server_classpath)" \
            com.xebyte.headless.GhidraMCPHeadlessServer \
            --bind "$HOST" --port "$PORT" --project "$PROJECT" \
            >> "$LOG_SERVER" 2>&1 &
        echo $! > "$PID_SERVER"
        log "started Java server pid $(cat "$PID_SERVER")  (log: $LOG_SERVER)"
        wait_for "the server to answer /check_connection" "$START_TIMEOUT" \
            curl -sf "http://$HOST:$PORT/check_connection" -o /dev/null \
            || { log "see $LOG_SERVER"; exit 1; }
        curl -s "http://$HOST:$PORT/check_connection"; echo
        # --project opens the project; the program inside it is opened on demand.
        curl -s -X POST -H 'Content-Type: application/json' \
            -d "{\"path\": \"$PROGRAM\"}" \
            "http://$HOST:$PORT/open_program"; echo
    fi

    pid="$(read_pid "$PID_BRIDGE")"
    if alive "$pid"; then
        log "bridge already running (pid $pid)"
    else
        export GHIDRA_MCP_URL="http://$HOST:$PORT"
        export PYTHONPATH="$SRC/python"
        nohup "$VENV/bin/python" -m bridge_mcp_ghidra \
            --transport streamable-http --mcp-host "$HOST" --mcp-port "$MCP_PORT" \
            >> "$LOG_BRIDGE" 2>&1 &
        echo $! > "$PID_BRIDGE"
        log "started MCP bridge pid $(cat "$PID_BRIDGE")  (log: $LOG_BRIDGE)"
        wait_for "the bridge to listen on $MCP_PORT" 60 port_open "$MCP_PORT" \
            || { log "see $LOG_BRIDGE"; exit 1; }
    fi
    log "MCP endpoint: http://$HOST:$MCP_PORT/mcp"
}

stop() {
    local name pid
    for name in bridge server; do
        local file="$PID_BRIDGE" ; [ "$name" = server ] && file="$PID_SERVER"
        pid="$(read_pid "$file")"
        if alive "$pid"; then
            log "killing $name pid $pid (SIGTERM, exact PID)"
            kill -TERM "$pid"
            local t0=$SECONDS
            while alive "$pid" && [ $((SECONDS - t0)) -lt 30 ]; do sleep 1; done
            if alive "$pid"; then log "$name pid $pid still alive after 30s"; exit 1; fi
            log "$name stopped"
        else
            log "$name not running"
        fi
        rm -f "$file"
    done
    port_open "$PORT" && { log "port $PORT still listening"; exit 1; } || true
    port_open "$MCP_PORT" && { log "port $MCP_PORT still listening"; exit 1; } || true
}

status() {
    local name pid
    for name in server bridge; do
        local file="$PID_SERVER" ; [ "$name" = bridge ] && file="$PID_BRIDGE"
        pid="$(read_pid "$file")"
        if alive "$pid"; then log "$name: running pid $pid"; else log "$name: not running"; fi
    done
    log "ports: $PORT $(port_open "$PORT" && echo listening || echo closed), $MCP_PORT $(port_open "$MCP_PORT" && echo listening || echo closed)"
    curl -s "http://$HOST:$PORT/check_connection" 2>/dev/null || log "no answer on $HOST:$PORT"
    echo
}

case "${1:-status}" in
    start) start ;;
    stop) stop ;;
    status) status ;;
    *) echo "usage: $0 {start|stop|status}" >&2; exit 2 ;;
esac
