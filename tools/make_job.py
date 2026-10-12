"""Create a job for the local worker (the only supported way to add jobs).

Usage (one line):
  PY tools/make_job.py --title "Name function 0x08001234" --kind name \
      --allowed config/symbols.csv --check "PY tools/check_symbols.py" \
      --instructions-file private/jobs/drafts/name_0x08001234.md [--max-attempts 2]
A job must be small (one function / one table / one file), name every file it may change (--allowed, glob ok),
and carry a check command that exits 0 ONLY when the work is right (run with Git Bash inside the job's worktree).
A word `PY` in --check is expanded to the full quoted Python path. Every .py file the check names must already be
committed on `main` (the worktree starts from main): get Claude to merge your branch first, or the job is refused.
Each worktree gets a read-only copy of the ROM at private/baserom.gba.
Prints the new job id. Jobs land in private/jobs/queue/ and the local worker picks them up oldest first.
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path

REPO = Path(r'D:\Yugioh_DeComp_V2')
JOBS = REPO / 'private' / 'jobs'
PY = 'C:/Users/USER/AppData/Local/hermes/hermes-agent/.hermes-runtime/python/cpython-3.11-windows-x86_64-none/python.exe'
KINDS = ['decompile', 'name', 'extract', 'doc', 'script', 'test', 'other']
PREFIXES = ('d:/yugioh_decomp_v2/', '/d/yugioh_decomp_v2/', '/mnt/d/yugioh_decomp_v2/')


def fix_check(check):
    """Expand PY; refuse .py files in the check that are not committed on main."""
    check = re.sub(r'(?<![\w/.-])PY(?![\w/.-])', '"%s"' % PY, check)
    for tok in re.findall(r'[\w:/\\.-]+\.py\b', check):
        rel = tok.replace('\\', '/')
        if rel.lower().startswith(PREFIXES):
            rel = rel.split('/', 3 if rel.startswith('/d/') else 2)[-1]
            if rel.lower().startswith('yugioh_decomp_v2/'):
                rel = rel.split('/', 1)[1]
        r = subprocess.run(['git', '-C', str(REPO), 'cat-file', '-e', 'main:' + rel], capture_output=True)
        if r.returncode != 0:
            sys.exit(f'check names {tok} ({rel}), which is not committed on main: ask Claude to merge it first')
    return check


def next_id():
    ids = [int(m.group(1)) for p in JOBS.rglob('J*.json') if (m := re.match(r'J(\d+)\.json$', p.name))]
    return f'J{(max(ids) + 1) if ids else 1:04d}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', required=True)
    ap.add_argument('--kind', required=True, choices=KINDS)
    ap.add_argument('--allowed', required=True, action='append', help='file or glob the job may change (repeatable)')
    ap.add_argument('--check', required=True, help='command that exits 0 only when the job is done right')
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--instructions')
    group.add_argument('--instructions-file')
    ap.add_argument('--max-attempts', type=int, default=2)
    ap.add_argument('--created-by', default='deepseek')
    a = ap.parse_args()
    text = a.instructions if a.instructions else Path(a.instructions_file).read_text(encoding='utf-8')
    if len(text) > 6000:
        sys.exit('instructions too long (> 6000 chars): split the job')
    job = {'id': next_id(), 'title': a.title, 'kind': a.kind, 'instructions': text,
           'allowed_paths': a.allowed, 'check': fix_check(a.check), 'max_attempts': a.max_attempts, 'attempts': 0,
           'status': 'queued', 'created_by': a.created_by, 'created_at': time.strftime('%Y-%m-%dT%H:%M:%S')}
    (JOBS / 'queue').mkdir(parents=True, exist_ok=True)
    out = JOBS / 'queue' / f"{job['id']}.json"
    out.write_text(json.dumps(job, indent=2), encoding='utf-8')
    print(job['id'])


if __name__ == '__main__':
    main()
