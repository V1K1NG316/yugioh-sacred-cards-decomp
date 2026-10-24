"""Print the DeepSeek account balance (GET https://api.deepseek.com/user/balance).

Reads DEEPSEEK_API_KEY from Hermes's own .env (never prints it). Usage: PY tools/deepseek_balance.py [--json]
Added 2026-10-14 at Matter_Scatter's request: the real balance next to tools/deepseek_spend.py's estimate.
"""
import json
import sys
import urllib.request
from pathlib import Path

ENV = Path.home() / 'AppData' / 'Local' / 'hermes' / '.env'


def key():
    for line in ENV.read_text(encoding='utf-8').splitlines():
        if line.strip().startswith('DEEPSEEK_API_KEY='):
            return line.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit('DEEPSEEK_API_KEY not found in %s' % ENV)


def main():
    req = urllib.request.Request('https://api.deepseek.com/user/balance',
                                 headers={'Authorization': 'Bearer ' + key(), 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    if '--json' in sys.argv:
        print(json.dumps(data))
        return
    print('available: %s' % data.get('is_available'))
    for b in data.get('balance_infos', []):
        print('%s total %s (granted %s, topped up %s)' % (b.get('currency'), b.get('total_balance'),
                                                         b.get('granted_balance'), b.get('topped_up_balance')))


if __name__ == '__main__':
    main()
