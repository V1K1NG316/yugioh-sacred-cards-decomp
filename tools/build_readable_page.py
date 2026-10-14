"""Build the Track B browser: a local, private web app to explore the readable game (Matter_Scatter, 2026-10-14).

Reads private/readable/<name>.c (first line: `// <proposed> — <purpose> [confidence: x]`), config/functions.csv,
private/asm/funcs/<name>.s (bl targets -> call graph) and src/funcs/ (Track A: byte-matched or not).
Writes private/extracted/readable/{index.html, index.json, c/<name>.c}. Game-derived: stays in private/, never
committed or published. View: launch config `extracted-pages` -> http://localhost:8765/readable/
Usage: PY tools/build_readable_page.py
"""
import csv
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('D:/Yugioh_DeComp_V2')          # private/ lives in the main checkout
READ = REPO / 'private' / 'readable'
OUT = REPO / 'private' / 'extracted' / 'readable'
HEAD = re.compile(r'^//\s*(\S+)\s*[—-]+\s*(.*?)\s*\[confidence:\s*(high|medium|low)\]', re.I)
BL = re.compile(r'^\s+bl\s+(\w+)', re.M)
# rough areas from the proposed name (first match wins); 'other' otherwise
AREAS = [('duel', r'duel|battle|attack|tribute|summon|field|lp_|life|turn|exodia|monster|trap|spell|graveyard|hand_'),
         ('cards & decks', r'card|deck|ante|prize|password|fusion|ritual|cost'),
         ('text & dialogue', r'text|glyph|string|font|message|dialog|name_'),
         ('menus & screens', r'menu|screen|cursor|window|title|shop|option|scene|map'),
         ('graphics', r'gfx|sprite|oam|bg_|palette|tile|vram|draw|render|lz77|decompress|fade|blend|dispcnt'),
         ('sound', r'sound|music|bgm|sfx|audio|m4a|song|voice'),
         ('save & system', r'save|sram|flash|irq|interrupt|timer|dma|input|key|reset|init|main|rng|random|math|div|mod|mem|copy|fill')]


def main():
    funcs = {r['name']: r for r in csv.DictReader(open(ROOT / 'config' / 'functions.csv'))}
    matched = {p.stem for p in (REPO / 'src' / 'funcs').glob('*.c')}
    (OUT / 'c').mkdir(parents=True, exist_ok=True)
    idx, calls = [], {}
    for p in sorted(READ.glob('*.c')):
        n = p.stem
        text = p.read_text(encoding='utf-8', errors='replace')
        m = HEAD.match(text.splitlines()[0] if text else '')
        prop, purpose, conf = (m.group(1), m.group(2), m.group(3).lower()) if m else (n, '', 'low')
        asm = REPO / 'private' / 'asm' / 'funcs' / (n + '.s')
        calls[n] = sorted(set(BL.findall(asm.read_text(errors='replace')))) if asm.exists() else []
        area = next((a for a, rx in AREAS if re.search(rx, prop, re.I)), 'other')
        f = funcs.get(n, {})
        idx.append({'n': n, 'p': prop, 'u': purpose, 'c': conf, 'a': f.get('address', ''), 's': int(f.get('size') or 0),
                    'm': n in matched, 'r': area})
        shutil.copyfile(p, OUT / 'c' / p.name)
    names = {e['n'] for e in idx}
    callers = {}
    for n, cs in calls.items():
        for c in cs:
            callers.setdefault(c, []).append(n)
    for e in idx:
        e['k'] = [c for c in calls.get(e['n'], []) if c in names]
        e['b'] = sorted(callers.get(e['n'], []))
    (OUT / 'index.json').write_text(json.dumps(idx, separators=(',', ':')), encoding='utf-8')
    shutil.copyfile(ROOT / 'tools' / 'readable_page.html', OUT / 'index.html')
    by = {}
    for e in idx:
        by[e['c']] = by.get(e['c'], 0) + 1
    print('wrote %s: %d functions, %d byte-matched, confidence %s' % (OUT, len(idx), sum(e['m'] for e in idx), by))


if __name__ == '__main__':
    main()
