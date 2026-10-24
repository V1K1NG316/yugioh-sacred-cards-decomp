#!/usr/bin/env bash
# Y5: fetch the Java runtime and Ghidra used for headless decompiler drafts.
# Portable by design: everything lands under private/tools/ (untracked) -- no apt, no
# system-wide install, no PATH changes outside this project.
# Run from anywhere:
#   bash scripts/ghidra_setup.sh
# Idempotent: a file that is already there is re-verified, not re-downloaded.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ROOT="$PWD"
TOOLS="$ROOT/private/tools"
DL="$TOOLS/dl"

# Pinned versions (URLs + the SHA-256 each project publishes for that file).
JDK_NAME=OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz
JDK_URL="https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/$JDK_NAME"
JDK_SHA=ce79869e1307ed8ee1e2baa86a412b1eb5b75d10a01006d788a6f968bcfaee94

GHIDRA_NAME=ghidra_12.1.4_PUBLIC_20260921.zip
GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.4_build/$GHIDRA_NAME"
GHIDRA_SHA=ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db

mkdir -p "$DL" "$TOOLS/jdk" "$TOOLS/ghidra"

fetch() {  # url sha  -> verified file in $DL
    local url="$1" sha="$2" out
    out="$DL/$(basename "${url%%\?*}")"
    if [ ! -f "$out" ]; then
        echo "downloading $out"
        curl -L --fail --retry 3 --retry-delay 5 -o "$out.part" "$url"
        mv "$out.part" "$out"
    else
        echo "already have $out"
    fi
    echo "$sha  $out" | sha256sum -c -
}

fetch "$JDK_URL" "$JDK_SHA"
fetch "$GHIDRA_URL" "$GHIDRA_SHA"

if [ ! -x "$TOOLS/jdk/bin/java" ]; then
    echo "unpacking jdk -> private/tools/jdk"
    tar xzf "$DL/$JDK_NAME" -C "$TOOLS/jdk" --strip-components=1
fi
if [ ! -x "$TOOLS/ghidra/support/analyzeHeadless" ]; then
    echo "unpacking ghidra -> private/tools/ghidra"
    rm -rf "$TOOLS/ghidra.tmp"
    python3 -m zipfile -e "$DL/$GHIDRA_NAME" "$TOOLS/ghidra.tmp"
    inner="$(find "$TOOLS/ghidra.tmp" -maxdepth 1 -mindepth 1 -type d | head -1)"
    mv "$inner"/* "$TOOLS/ghidra/"
    rm -rf "$TOOLS/ghidra.tmp"
fi

"$TOOLS/jdk/bin/java" -version
chmod +x "$TOOLS/ghidra/support/analyzeHeadless"
echo "OK: $TOOLS/jdk/bin/java , $TOOLS/ghidra/support/analyzeHeadless"
