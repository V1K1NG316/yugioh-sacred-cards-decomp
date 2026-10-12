"""Match one decompiled C function against the ROM bytes (Y5).

Usage (Git Bash, from the repo root or from a job worktree):
  PY tools/match_func.py sub_0800AF94

Reads the function's address from config/functions.csv (main checkout), compiles
src/funcs/<name>.c with agbcc inside WSL (scripts/match_func.sh), links it at that address,
and compares the linked bytes -- the whole function, literal pool included -- with the ROM.
Exit 0 only on an exact match. On a mismatch it prints the first differing offset and a
side-by-side disassembly of the ROM bytes and ours.

  src/funcs/<name>.c comes from *this* checkout (a job worktree counts); the compiler, the
  ROM and all build output come from the main checkout, D:\\Yugioh_DeComp_V2, so that a job
  can never corrupt them.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

MAIN = Path(r'D:\Yugioh_DeComp_V2')
WSL_DISTRO = 'Ubuntu-24.04'
WSL_MAIN = '/mnt/d/Yugioh_DeComp_V2'
CSV = 'config/functions.csv'
DIS_LINE = re.compile(r'^\s*([0-9a-f]+):\s+([0-9a-f ]+?)\s\s+(.*)$')


def wsl_path(p):
    """D:\\Yugioh_DeComp_V2\\src -> /mnt/d/Yugioh_DeComp_V2/src (for the WSL side)."""
    p = Path(p).resolve()
    parts = p.parts
    drive = parts[0][0].lower()
    return '/mnt/%s/%s' % (drive, '/'.join(parts[1:]))


def load_functions(csv_path):
    """name -> {'addr': int, 'mode': str, 'next': int}; the CSV's `size` is the distance to
    the next function's start (approximation A5), so `next` is where this one must end."""
    rows = {}
    line_iter = iter(csv_path.read_text(encoding='utf-8').splitlines())
    header = next(line_iter).split(',')
    for line in line_iter:
        if not line.strip():
            continue
        f = dict(zip(header, line.split(',')))
        addr, size = int(f['address'], 16), int(f['size'])
        rows[f['name']] = {'addr': addr, 'mode': f['mode'], 'next': addr + size}
    return rows


def disasm_lines(path, base):
    """objdump text -> {offset: (bytes, instruction)}."""
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        m = DIS_LINE.match(line)
        if not m:
            continue
        off = int(m.group(1), 16) - base
        if off < 0:
            continue
        out[off] = (m.group(2).replace(' ', ''), m.group(3).strip())
    return out


def side_by_side(rom, ours, rom_lines, our_lines, size):
    """One line per instruction, ROM left, ours right. A line is marked when the bytes under it
    differ -- the two disassemblies can group a pool word differently, so the verdict comes from
    the bytes, never from the text."""
    print('    offset  rom                          ours')
    for off in sorted(set(rom_lines) | set(our_lines)):
        if off >= size:
            continue
        rb, rt = rom_lines.get(off, ('', ''))
        ob, ot = our_lines.get(off, ('', ''))
        step = max(len(rb), len(ob)) // 2 or 2
        flag = '  <-- differs' if rom[off:off + step] != ours[off:off + step] else ''
        print('    +%-5d  %-28s %s%s' % (off, rb or '?', ot or '?', flag))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('name', help='function name, e.g. sub_0800AF94 (also the .c file name)')
    ap.add_argument('--main', default=str(MAIN), help='main checkout (default: %(default)s)')
    ap.add_argument('--quiet', action='store_true', help='print only the verdict')
    a = ap.parse_args()

    main_dir = Path(a.main)
    root = Path(__file__).resolve().parents[1]
    name = a.name

    funcs = load_functions(main_dir / CSV)
    if name not in funcs:
        sys.exit('match_func: %s is not in %s' % (name, CSV))
    row = funcs[name]
    if row['mode'] != 'thumb':
        sys.exit('match_func: %s is %s code; only THUMB C functions are supported' % (name, row['mode']))
    src = root / 'src' / 'funcs' / (name + '.c')
    if not src.exists():
        sys.exit('match_func: no such file: %s' % src)

    cmd = ['wsl', '-d', WSL_DISTRO, '--cd', WSL_MAIN, '--', 'bash', 'scripts/match_func.sh',
           name, '0x%08X' % row['addr'], wsl_path(src.parent)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        if r.stdout:
            print(r.stdout, end='')
        if r.stderr:
            print(r.stderr, end='')
        sys.exit('match_func: the agbcc pipeline failed (exit %d)' % r.returncode)

    work = main_dir / 'private' / 'build' / 'match' / name
    size = int((work / 'size.txt').read_text().strip())
    sections = dict(l.split() for l in (work / 'sections.txt').read_text().split('\n') if l.strip())
    unresolved = [s for s in (work / (name + '.unresolved')).read_text().split() if s]

    for sec in ('.DATA', '.RODATA', '.BSS'):
        if sections.get(sec, '0') not in ('0', '00000000'):
            sys.exit('match_func: %s is not empty (%s bytes): this function needs data placed at a '
                     'second address, which the harness cannot do yet' % (sec, sections[sec]))
    if unresolved:
        sys.exit('match_func: undefined symbols that are not NAME_<8 hex digits>: %s'
                 % ', '.join(unresolved))

    ours = (work / (name + '.bin')).read_bytes()[:size]
    rom = (work / 'rom.bin').read_bytes()
    if len(rom) != size or len(ours) != size:
        sys.exit('match_func: got %d ROM bytes and %d compiled bytes, expected %d'
                 % (len(rom), len(ours), size))

    hexs = lambda b: ' '.join('%02x%02x' % (b[i + 1], b[i]) for i in range(0, len(b) - 1, 2))
    room = row['next'] - row['addr']
    if ours == rom:
        print('MATCH %s @ 0x%08X: %d bytes identical, %d bytes of room in the ROM (next start 0x%08X)'
              % (name, row['addr'], size, room, row['next']))
        if not a.quiet:
            print('      %s' % hexs(rom))
        return 0

    first = next(i for i in range(size) if rom[i] != ours[i])
    print('FAIL  %s @ 0x%08X: first difference at +0x%X (rom %02x, ours %02x); %d/%d bytes differ'
          % (name, row['addr'], first, rom[first], ours[first],
             sum(1 for i in range(size) if rom[i] != ours[i]), size))
    if not a.quiet:
        print('      rom  %s' % hexs(rom))
        print('      ours %s' % hexs(ours))
        side_by_side(rom, ours,
                     disasm_lines(work / 'disasm_rom.txt', row['addr']),
                     disasm_lines(work / 'disasm_ours.txt', row['addr']), size)
        if (work / (name + '.ld.log')).exists() and (work / (name + '.ld.log')).read_text().strip():
            print('ld said: %s' % (work / (name + '.ld.log')).read_text().strip())
    return 1


if __name__ == '__main__':
    sys.exit(main())
