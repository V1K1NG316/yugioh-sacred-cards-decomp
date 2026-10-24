#!/usr/bin/env bash
# Ghidra MCP (bethington/ghidra-mcp): build the headless server jar.
# Portable by design: Maven and the built jar land under private/tools/ (untracked),
# nothing is installed system-wide and no PATH outside this project changes.
# Run from anywhere:
#   bash scripts/ghidra_mcp_build.sh
# Needs private/tools/jdk (scripts/ghidra_setup.sh), private/tools/ghidra, and the
# ghidra-mcp checkout (scripts/get_ghidra_mcp.sh). Idempotent: an existing jar is kept
# unless you pass --force.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ROOT="$PWD"
TOOLS="$ROOT/private/tools"
DL="$TOOLS/dl"
SRC="$TOOLS/ghidra-mcp"
GHIDRA="$TOOLS/ghidra"
JAVA_HOME_DIR="$TOOLS/jdk"
MVN_VERSION=3.9.9
MVN_DIR="$TOOLS/maven/apache-maven-$MVN_VERSION"
FORCE="${1:-}"

# --- checks -------------------------------------------------------------------
[ -x "$JAVA_HOME_DIR/bin/java" ] || { echo "missing $JAVA_HOME_DIR (run scripts/ghidra_setup.sh)" >&2; exit 1; }
[ -d "$SRC/src/main/java" ] || { echo "missing $SRC (run scripts/get_ghidra_mcp.sh)" >&2; exit 1; }
[ -d "$GHIDRA/Ghidra/Framework" ] || { echo "missing $GHIDRA (run scripts/ghidra_setup.sh)" >&2; exit 1; }

export JAVA_HOME="$JAVA_HOME_DIR"
export PATH="$JAVA_HOME/bin:$PATH"

# --- portable Maven (verified against the digest Apache publishes) -------------
if [ ! -x "$MVN_DIR/bin/mvn" ]; then
    name="apache-maven-$MVN_VERSION-bin.tar.gz"
    base="https://archive.apache.org/dist/maven/maven-3/$MVN_VERSION/binaries"
    mkdir -p "$DL" "$TOOLS/maven"
    if [ ! -f "$DL/$name" ]; then
        echo "downloading $name"
        curl -L --fail --retry 3 --retry-delay 5 -o "$DL/$name.part" "$base/$name"
        mv "$DL/$name.part" "$DL/$name"
    fi
    echo "verifying $name against $base/$name.sha512"
    curl -sL --fail "$base/$name.sha512" -o "$DL/$name.sha512"
    ( cd "$DL" && sed 's/$/  '"$name"'/' "$name.sha512" | sha512sum -c - )
    tar xzf "$DL/$name" -C "$TOOLS/maven"
fi
MVN="$MVN_DIR/bin/mvn"
"$MVN" -v | head -3

# Maven's local repository lives inside the project too: nothing is written to
# ~/.m2, so the whole toolchain can be deleted by removing private/tools/.
M2="$TOOLS/maven/repo"
GV=12.1.4                                  # pom.xml <ghidra.version>
JARS="Base:Features/Base Decompiler:Features/Decompiler Docking:Framework/Docking \
Generic:Framework/Generic Project:Framework/Project SoftwareModeling:Framework/SoftwareModeling \
Utility:Framework/Utility Gui:Framework/Gui FileSystem:Framework/FileSystem Graph:Framework/Graph \
DB:Framework/DB Emulation:Framework/Emulation PDB:Features/PDB FunctionID:Features/FunctionID \
Help:Framework/Help Debugger-api:Debug/Debugger-api \
Framework-TraceModeling:Debug/Framework-TraceModeling Debugger-rmi-trace:Debug/Debugger-rmi-trace"
mkdir -p "$M2"
# Ghidra's jars are not on Maven Central; the build needs them under the
# coordinates ghidra:<Artifact>:12.1.4. This is the same install-file step the
# project's own `python -m tools.setup ensure-prereqs` performs, pointed at
# private/tools/maven/repo instead of the user's cache.
for entry in $JARS; do
    id="${entry%%:*}"; rel="${entry#*:}"
    jar="$GHIDRA/Ghidra/$rel/lib/$id.jar"
    [ -f "$jar" ] || { echo "missing Ghidra jar $jar" >&2; exit 1; }
    if [ -f "$M2/ghidra/$id/$GV/$id-$GV.jar" ]; then
        echo "already installed: ghidra:$id:$GV"
        continue
    fi
    echo "installing ghidra:$id:$GV  <- ${jar#$ROOT/}"
    "$MVN" -q -B install:install-file -Dmaven.repo.local="$M2" \
        "-Dfile=$jar" -DgroupId=ghidra -DartifactId="$id" -Dversion="$GV" \
        -Dpackaging=jar -DgeneratePom=true
done

# --- build --------------------------------------------------------------------
cd "$SRC"
# -P headless is the profile that makes the jar runnable on its own (main class
# com.xebyte.headless.GhidraMCPHeadlessServer + lib/ classpath prefix).
if [ "$FORCE" = "--force" ] || [ ! -f "target/GhidraMCP-7.0.0.jar" ]; then
    "$MVN" -B -P headless -DskipTests -Dmaven.repo.local="$M2" package
fi
ls -l target/GhidraMCP-*.jar

# --- Python side of the bridge (into private/venv, never system-wide) ----------
# The bridge is a thin MCP<->HTTP multiplexer; its only runtime deps are the MCP
# SDK and pydantic (pyproject [project].dependencies). Installed into the project
# venv so nothing is added to the system Python.
VENV="$ROOT/private/venv"
[ -x "$VENV/bin/python" ] || { echo "missing $VENV (run scripts/decomp_tools.sh)" >&2; exit 1; }
"$VENV/bin/pip" install -q -r <("$VENV/bin/python" - <<'PY'
import tomllib
with open("pyproject.toml", "rb") as fh:
    print("\n".join(tomllib.load(fh)["project"]["dependencies"]))
PY
)
"$VENV/bin/python" -c "import mcp, pydantic; print('bridge deps OK: mcp', mcp.__version__ if hasattr(mcp,'__version__') else 'n/a', '/ pydantic', pydantic.VERSION)"
echo "OK: $SRC/target/GhidraMCP-7.0.0.jar"
