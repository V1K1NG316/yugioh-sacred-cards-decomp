"""Live view of every Hermes agent working in D:\\Yugioh_DeComp_V2 (DeepSeek main + local worker jobs).

Run it in the Claude app's "Live view" terminal tab:  PY D:\\Yugioh_DeComp_V2\\ops\\watch.py
Read-only on Hermes's state.db. Blue = tool call, grey = tool result, green = what the agent says.
"""
import json, os, sqlite3, sys, time

DB = 'file:C:/Users/USER/AppData/Local/hermes/state.db?mode=ro'
ROOT = 'd:\\yugioh_decomp_v2'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
C = {'ds': '\033[95m', 'loc': '\033[93m', 'call': '\033[96m', 'say': '\033[92m', 'res': '\033[90m', 'end': '\033[0m'}


def short(s, n):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n] + ' ...'


def tag(s):
    cwd = (s['cwd'] or '').lower()
    if 'worktrees' in cwd:
        return f"{C['loc']}[local {cwd.rsplit(chr(92), 1)[-1]}]{C['end']}"
    who = 'DeepSeek' if 'deepseek' in (s['model'] or '') else (s['model'] or '?')
    return f"{C['ds']}[{who}]{C['end']}"


def main():
    os.system('')
    seen, last_status = {}, {}
    print(f"Watching Hermes agents in D:\\Yugioh_DeComp_V2 (Ctrl+C to close)")
    while True:
        try:
            c = sqlite3.connect(DB, uri=True, timeout=5)
            c.row_factory = sqlite3.Row
            live = c.execute("select * from sessions where lower(cwd) like ? and (ended_at is null or ended_at > ?) "
                             "order by started_at", (ROOT + '%', time.time() - 120)).fetchall()
            for s in live:
                sid, t = s['id'], tag(s)
                if sid not in seen:
                    seen[sid] = 0
                    print(f"\n{t} ===== session {sid}: {s['title'] or ''}")
                for m in c.execute('select * from messages where session_id=? and id>? order by id', (sid, seen[sid])):
                    seen[sid] = m['id']
                    if m['role'] == 'user':
                        print(f"{t} {C['res']}[prompt] {short(m['content'], 150)}{C['end']}")
                    elif m['role'] == 'assistant':
                        if m['content']:
                            print(f"{t} {C['say']}{short(m['content'], 600)}{C['end']}")
                        for call in json.loads(m['tool_calls'] or '[]'):
                            fn = call.get('function', {})
                            print(f"{t} {C['call']}-> {fn.get('name')} {short(fn.get('arguments', ''), 200)}{C['end']}")
                    elif m['role'] == 'tool':
                        print(f"{t} {C['res']}   <- {short(m['content'], 220)}{C['end']}")
                st = 'finished' if s['ended_at'] else (s['last_activity_description'] or 'working')
                if last_status.get(sid) != st:
                    last_status[sid] = st
                    print(f"{t} {C['res']}[{time.strftime('%H:%M:%S')}] {st}{C['end']}")
            c.close()
        except sqlite3.Error as e:
            print(f'(db busy: {e})')
        time.sleep(3)


if __name__ == '__main__':
    main()
