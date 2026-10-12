"""Print the id of the newest Hermes one-shot session for a working folder (read-only on state.db).

Usage: python newest_session.py <cwd> [--after <unix time>]
"""
import argparse, sqlite3

ap = argparse.ArgumentParser()
ap.add_argument('cwd')
ap.add_argument('--after', type=float, default=0)
a = ap.parse_args()
c = sqlite3.connect('file:C:/Users/USER/AppData/Local/hermes/state.db?mode=ro', uri=True)
r = c.execute("select id from sessions where source='oneshot' and lower(cwd)=? and started_at>=? "
              "order by started_at desc limit 1", (a.cwd.lower().rstrip('\\'), a.after)).fetchone()
print(r[0] if r else '')
