"""Report DeepSeek spend from Hermes's token counts (read-only on state.db).

Usage: python deepseek_spend.py [--since YYYY-MM-DD] [--cwd D:\\Yugioh_DeComp_V2] [--json]
Hermes does not price most DeepSeek sessions, so cost is computed from tokens at the prices on Matter_Scatter's
own DeepSeek bill (usage export 2026-10-12, deepseek-flash, after the 2026-10-11 price change). Reasoning tokens
are counted as output (conservative: may double-count if Hermes already includes them).
"""
import argparse, datetime as dt, json, sqlite3, sys

DB = 'file:C:/Users/USER/AppData/Local/hermes/state.db?mode=ro'
PRICE_PER_M = {'miss': 0.30, 'hit': 0.006, 'out': 1.20}   # USD per million tokens
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def rows(since=None, cwd=None):
    c = sqlite3.connect(DB, uri=True)
    c.row_factory = sqlite3.Row
    q = ("select cwd, model, started_at, ended_at, last_activity_at, input_tokens, output_tokens, "
         "cache_read_tokens, reasoning_tokens from sessions "
         "where billing_provider='deepseek' or model like 'deepseek%'")
    out = []
    for r in c.execute(q):
        start = float(r['started_at'] or 0)
        if since and start < since:
            continue
        if cwd and (r['cwd'] or '').lower() != cwd.lower():
            continue
        end = float(r['ended_at'] or r['last_activity_at'] or start)
        tin, tcache = int(r['input_tokens'] or 0), int(r['cache_read_tokens'] or 0)
        tout = int(r['output_tokens'] or 0) + int(r['reasoning_tokens'] or 0)
        cost = (tin * PRICE_PER_M['miss'] + tcache * PRICE_PER_M['hit'] + tout * PRICE_PER_M['out']) / 1e6
        out.append({'cwd': r['cwd'] or '(desktop)', 'hours': max(0.0, end - start) / 3600, 'cost': cost,
                    'in': tin, 'out': tout, 'cache': tcache})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since')
    ap.add_argument('--cwd')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    since = dt.datetime.fromisoformat(a.since).timestamp() if a.since else None
    data = rows(since, a.cwd)
    total = sum(r['cost'] for r in data)
    if a.json:
        print(json.dumps({'sessions': len(data), 'cost_usd': round(total, 4)}))
        return
    by = {}
    for r in data:
        b = by.setdefault(r['cwd'], {'n': 0, 'hours': 0, 'cost': 0, 'in': 0, 'out': 0, 'cache': 0})
        b['n'] += 1
        for k in ('hours', 'cost', 'in', 'out', 'cache'):
            b[k] += r[k]
    for k, b in sorted(by.items(), key=lambda kv: -kv[1]['cost']):
        per_h = b['cost'] / b['hours'] if b['hours'] else 0
        print(f"{k[:40]:40} sessions={b['n']:3} hours={b['hours']:6.1f} cost=${b['cost']:7.2f} "
              f"(${per_h:.2f}/h) in={b['in']:,} cache={b['cache']:,} out={b['out']:,}")
    print(f'TOTAL ${total:.2f} over {len(data)} sessions')


if __name__ == '__main__':
    main()
