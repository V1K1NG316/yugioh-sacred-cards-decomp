"""Regenerate STATUS.md: budget, job queue, local vs DeepSeek share, latest conversation entries.

Run after every review (Claude) and whenever you like:  PY D:\\Yugioh_DeComp_V2\\tools\\status.py
"""
import json, re, sqlite3, subprocess, sys, time
from pathlib import Path

REPO = Path(r'D:\Yugioh_DeComp_V2')
JOBS = REPO / 'private' / 'jobs'
BUDGET_START, STOP, BALANCE = '2026-10-12T05:40', 30.0, 35.0
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def spend():
    out = subprocess.run([sys.executable, '-I', str(REPO / 'tools' / 'deepseek_spend.py'), '--since', BUDGET_START,
                          '--json'], capture_output=True, text=True).stdout
    return json.loads(out)


def local_sessions():
    c = sqlite3.connect('file:C:/Users/USER/AppData/Local/hermes/state.db?mode=ro', uri=True)
    r = c.execute("select count(*), coalesce(sum(output_tokens),0) from sessions where lower(cwd) like ? "
                  "and model not like 'deepseek%'", ('d:\\yugioh_decomp_v2%',)).fetchone()
    d = c.execute("select count(*), coalesce(sum(output_tokens),0) from sessions where lower(cwd) like ? "
                  "and model like 'deepseek%'", ('d:\\yugioh_decomp_v2%',)).fetchone()
    return r, d


def main():
    s = spend()
    (loc_n, loc_out), (ds_n, ds_out) = local_sessions()
    counts = {k: len(list((JOBS / k).glob('J*.json'))) if (JOBS / k).exists() else 0
              for k in ['queue', 'running', 'passed', 'merged', 'rejected', 'failed']}
    total_out = loc_out + ds_out
    share = f'{100 * loc_out / total_out:.0f}%' if total_out else 'n/a'
    conv = (REPO / 'AI_Conversation.md').read_text(encoding='utf-8') if (REPO / 'AI_Conversation.md').exists() else ''
    heads = re.findall(r'^## \[\d{3}\].*$', conv, re.M)[-6:]
    worker = 'PAUSED (private/jobs/STOP)' if (JOBS / 'STOP').exists() else 'running or idle'
    lines = [
        '# STATUS — Yugioh_DeComp_V2', '',
        f"_Generated {time.strftime('%Y-%m-%d %H:%M')} by `tools/status.py`. Do not edit by hand._", '',
        '## DeepSeek budget',
        f"- Spent since {BUDGET_START}: **${s['cost_usd']:.2f}** of the ${STOP:.0f} stop "
        f"(balance ${BALANCE:.0f}, ${BALANCE - STOP:.0f} reserve). Remaining before stop: **${max(0, STOP - s['cost_usd']):.2f}**.",
        '- Computed from Hermes token counts at the 2026-10-12 bill prices (out $1.20/M, miss $0.30/M, hit $0.006/M).', '',
        '## Who did the work (agent output tokens in this project)',
        f'- Local Qwen: {loc_n} sessions, {loc_out:,} tokens · DeepSeek: {ds_n} sessions, {ds_out:,} tokens · '
        f'**local share {share}**', '',
        f'## Local job queue (worker: {worker})',
        '| queued | running | passed, awaiting critics | merged | rejected by critics | failed → DeepSeek |',
        '|---:|---:|---:|---:|---:|---:|',
        f"| {counts['queue']} | {counts['running']} | {counts['passed']} | {counts['merged']} | {counts['rejected']} | {counts['failed']} |", '',
        '## Latest conversation entries', *[f'- {h[3:]}' for h in heads], '',
        'Milestones and their status: see `README.md`.',
    ]
    (REPO / 'STATUS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
