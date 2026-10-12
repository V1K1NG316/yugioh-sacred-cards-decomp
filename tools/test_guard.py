"""Prove guard_repo.py works via 3 test cases in a throwaway repo."""
import subprocess, sys, pathlib, time

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def main():
    # Determine paths 
    project = pathlib.Path(r"D:\Yugioh_DeComp_V2")
    guard_script = project / "tools" / "guard_repo.py"
    baserom = project / "private" / "baserom.gba"

    # Create throwaway test repo: D:\Yugioh_DeComp_V2\private\tmp\guardtest-<unix time>
    u = str(int(time.time()))
    test_dir = project / "private" / "tmp" / f"guardtest-{u}"
    if not test_dir.exists():
        test_dir.mkdir(parents=True)
    
    # git init
    r = run(["git", "-C", str(test_dir), "init"])
    assert r.returncode == 0, "git init failed"
    run(["git", "-C", str(test_dir), "config", "user.name", "Hermes"])
    run(["git", "-C", str(test_dir), "config", "user.email", "hermes@test"])

    results = []
    
    # Case 1: ok.txt with text "hello\n" -> expect exit 0
    (test_dir / "ok.txt").write_text("hello")
    run(["git", "-C", str(test_dir), "add", "ok.txt"])
    r = run([sys.executable, str(guard_script), "--repo", str(test_dir)])
    c1 = "PASS" if r.returncode == 0 else "FAIL"
    results.append(f"case 1: {c1}")
    
    # Case 2: fake.dat = first 0xC0 bytes of baserom.gba -> expect exit 1 with "GBA header"
    first_c0 = baserom.read_bytes()[:0xC0]
    (test_dir / "fake.dat").write_bytes(first_c0)
    run(["git", "-C", str(test_dir), "add", "fake.dat"])
    r = run([sys.executable, str(guard_script), "--repo", str(test_dir)])
    c2 = "PASS" if r.returncode == 1 and "GBA header" in r.stdout else "FAIL"
    results.append(f"case 2: {c2}")
    
    # Case 3: big.txt of 1048577 bytes -> expect exit 1 (large file)
    # Remove fake.dat from index, create and add big.txt
    unstaged = run(["git", "-C", str(test_dir), "rm", "--cached", "-q", "fake.dat"]).returncode == 0
    (test_dir / "big.txt").write_bytes(b"x" * int(1048577))
    run(["git", "-C", str(test_dir), "add", "big.txt"])
    r = run([sys.executable, str(guard_script), "--repo", str(test_dir)])
    c3 = ("PASS" if unstaged and r.returncode == 1 and "large file" in r.stdout
          and "GBA header" not in r.stdout else "FAIL")
    results.append(f"case 3: {c3}")
    
    for line in results:
        print(line)
    
    ok = all("PASS" in l for l in results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
