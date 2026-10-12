"""Check indexed (staged/committed) files against guard rules."""
import subprocess, sys, pathlib


def main():
    repo = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--repo" and i + 1 < len(sys.argv):
            repo = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    if not repo:
        repo = r"D:\Yugioh_DeComp_V2"

    result = subprocess.run(
        ["git", "-C", repo, "ls-files", "-s", "-z"],
        capture_output=True,
    )
    entries = result.stdout.split(b"\x00") if result.stdout.strip() else []

    # Read baserom for GBA header check (bytes 0x4..0xA0)
    baserom_path = pathlib.Path(r"D:\Yugioh_DeComp_V2\private\baserom.gba")
    if not baserom_path.exists():
        print("FAIL: private/baserom.gba missing")
        return 2
    logo_section = b""
    data = baserom_path.read_bytes()
    if len(data) >= 0xC0:
        logo_section = data[0x4 : 0xA1]

    checked = 0
    failures = []
    BAD_SUFFIXES = (".gba", ".GBA", ".sav", ".SAV", ".sa1", ".SA1",
                    ".srm", ".SRM", ".elf", ".ELF", ".bin", ".BIN", ".o", ".O")

    for raw in entries:
        if not raw.strip():
            continue
        parts = raw.split(b"\t")
        meta = parts[0].decode()
        fpath = parts[1].decode()

        # Parse mode/sha/stage from first portion before any extra tabs
        header = meta.split(" ")[-3]  # stage is last
        sha = meta.split(" ")[1]

        blob = subprocess.run(
            ["git", "-C", repo, "cat-file", "blob", sha],
            capture_output=True,
        )
        raw_bytes = blob.stdout
        sz = len(raw_bytes)
        checked += 1

        # (a) size > 1 MiB
        if sz > 1048576:
            failures.append(f"FAIL {fpath}: large file ({sz} bytes)")
            continue

        # (b) bad suffix
        for suffix in BAD_SUFFIXES:
            if fpath.endswith(suffix):
                failures.append(f"FAIL {fpath}: has suffix {suffix}")
                break

        # (c) ELF magic
        if raw_bytes[:4] == b"\x7fELF":
            failures.append(f"FAIL {fpath}: ELF magic")
            continue

        # (d) GBA header check
        if len(raw_bytes) >= 0xC0 and logo_section:
            byte_b2 = raw_bytes[0xB2] if len(raw_bytes) > 0xB2 else b"\x00"
            if byte_b2 == 0x96:
                section_check = raw_bytes[0x4 : 0xA1]
                if section_check == logo_section[:len(section_check)] and len(section_check) == min(len(logo_section), len(raw_bytes) - 4):
                    failures.append(f"FAIL {fpath}: GBA header")

    msg = f"guard: {checked} files checked, {len(failures)} failures"
    for f in failures:
        print(f)
    print(msg)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
