"""Back up Hermes's config, secrets, skills and databases before an update (databases via the SQLite backup API)."""
import shutil, sqlite3, subprocess, sys, time
from pathlib import Path

H = Path(r'C:\Users\USER\AppData\Local\hermes')
dest = Path(r'C:\Users\USER\AppData\Local\hermes_backups') / time.strftime('%Y-%m-%d_%H%M')
dest.mkdir(parents=True, exist_ok=False)
for name in ['config.yaml', '.env', 'auth.json', 'SOUL.md', 'channel_directory.json']:
    if (H / name).exists():
        shutil.copy2(H / name, dest / name)
for name in ['skills', 'memories', 'plugins', 'hooks']:
    if (H / name).exists():
        shutil.copytree(H / name, dest / name)
for name in ['state.db', 'kanban.db', 'projects.db', 'shared-state.db', 'verification_evidence.db']:
    if (H / name).exists():
        src = sqlite3.connect(f'file:{H / name}?mode=ro', uri=True)
        dst = sqlite3.connect(dest / name)
        src.backup(dst)
        dst.close(); src.close()
commit = subprocess.run(['git', '-C', str(H / 'hermes-agent'), 'rev-parse', 'HEAD'],
                        capture_output=True, text=True).stdout.strip()
(dest / 'HERMES_COMMIT.txt').write_text(commit + '\n')
size = sum(p.stat().st_size for p in dest.rglob('*') if p.is_file())
print(f'backup: {dest}  files={sum(1 for p in dest.rglob("*") if p.is_file())}  {size / 1e6:.1f} MB  commit={commit}')
