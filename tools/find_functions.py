#!/usr/bin/env python3
"""Find function starts in private/baserom.gba (THUMB/ARM) with their extents.

Method (worklist over seeds, then BL closure):
  * seeds: the entry points from scripts/dis_range.sh evidence (reset, crt0,
    IRQ handler, main);
  * the interrupt-handler table at 0x0807F420 read by the crt0 dispatcher
    (source `irq_table`);
  * a whole-ROM sweep of 4-aligned words holding an odd 0x08xxxxx1 pointer into
    the ROM whose target starts with a THUMB `push {..., lr}` prologue (source
    `ptr_prologue`): function-pointer tables / jump tables that no BL reaches.
    Such a candidate is accepted only when its target head decodes as valid
    THUMB (thumb_ok / A4) and its target lies within PTR_MAX_DIST of a function
    already found by the BL closure (A6, measured separation evidence);
  * BL closure: every THUMB `BL`/`BLX` and ARM `BL` target of an accepted
    function is added and walked in turn.  A BL target is accepted on the
    strength of the BL instruction itself, with no decode filter - real
    functions that do not begin with a prologue (e.g. the one-instruction
    `bx lr` interrupt stubs) must not be dropped.

This is a heuristic sweep, not a data-flow analysis (A1).

For each accepted function the walker records where it stopped; `size` in the
CSV is `min(walk_end, next_function_start) - address`, i.e. the function's own
end bounded by the next function start so that extents never overlap (A5).

Output: config/functions.csv, header `address,name,mode,size,source`.
"""
import bisect
import struct
from array import array
from pathlib import Path

REPO = Path(r'D:\Yugioh_DeComp_V2')
ROM = REPO / 'private' / 'baserom.gba'
OUT = REPO / 'config' / 'functions.csv'

BASE = 0x08000000
MAX_FUNC = 0x4000     # stop a runaway scan
VALID_N = 8           # instructions a candidate's head must decode as (A4)
PTR_MAX_DIST = 0x10000  # ptr_prologue target must be this close to BL-closure code (A6)

SEEDS = [
    (0x08000000, 'arm',   'reset',       'reset_vector'),
    (0x080000C0, 'arm',   'crt0',        'reset_branch'),
    (0x080000FC, 'arm',   'irq_handler', 'crt0_writes_0x03007FFC'),
    (0x08016928, 'thumb', 'main',        'crt0_bx_literal_0x0800021C'),
]
IRQ_TABLE = 0x0807F420  # dispatcher at irq_handler loads handler ptrs from here

rom = ROM.read_bytes()


def u16(a):
    return struct.unpack_from('<H', rom, a - BASE)[0]


def u32(a):
    return struct.unpack_from('<I', rom, a - BASE)[0]


def in_rom(a):
    return BASE <= a < BASE + len(rom)


def sext(v, bits):
    m = 1 << (bits - 1)
    return (v ^ m) - m


def thumb_ok(addr, n=VALID_N):
    """True if the next n THUMB instructions at addr decode as defined ARMv4T
    THUMB.  Rejects a BL/BLX low half with no high half, the undefined
    0xE800-0xEFFF and 0xDE00-0xDEFF blocks, bkpt/unused halves of the 0xBxxx
    group (0xB1xx-0xB3xx, 0xBE00-0xBEFF), and 0x0000 padding (A4)."""
    i = addr
    seen = 0
    while seen < n:
        if not in_rom(i + 1):
            return False
        hw = u16(i)
        if (hw & 0xF800) == 0xF000:                     # BL / BLX pair
            if not in_rom(i + 3):
                return False
            if (u16(i + 2) & 0xF800) not in (0xF800, 0xE800):
                return False
            i += 4
        elif (hw & 0xF800) == 0xF800:                   # lone BL low half
            return False
        elif 0xE800 <= hw <= 0xEFFF or 0xDE00 <= hw <= 0xDEFF:
            return False
        elif 0xB000 <= hw <= 0xBFFF:
            if not (hw <= 0xB0FF or 0xB400 <= hw <= 0xB5FF
                    or 0xBC00 <= hw <= 0xBDFF or (hw & 0xFF80) == 0xBF00):
                return False
        elif hw == 0x0000:
            return False
        else:
            i += 2
        seen += 1
    return True


def scan(addr, mode):
    """Walk one function from `addr`.  Returns (targets, walk_end): `targets` is
    a list of (address, mode, source) for BL/BLX/BX targets, `walk_end` the
    address just past the last instruction visited."""
    targets = []
    i = addr
    last = {}          # reg -> value of the last `ldr rX,[pc,#imm]`
    stop = addr + MAX_FUNC
    while i < stop and in_rom(i):
        if mode == 'thumb':
            hw = u16(i)
            if (hw & 0xF800) == 0xF000 and in_rom(i + 3):
                hw2 = u16(i + 2)
                if (hw2 & 0xF800) == 0xF800:            # BL
                    off = sext(((hw & 0x7FF) << 12) | ((hw2 & 0x7FF) << 1), 23)
                    targets.append(((i + 4 + off) & ~1, 'thumb', 'bl_thumb'))
                    i += 4
                    continue
                if (hw2 & 0xF800) == 0xE800:            # BLX imm -> ARM
                    off = sext(((hw & 0x7FF) << 12) | ((hw2 & 0x7FF) << 1), 23)
                    targets.append(((i + 4 + off) & ~3, 'arm', 'blx_thumb'))
                    i += 4
                    continue
            if (hw & 0xF800) == 0x4800:                 # ldr rX,[pc,#imm]
                last[(hw >> 8) & 7] = u32(((i + 4) & ~3) + ((hw & 0xFF) * 4))
                i += 2
                continue
            if (hw & 0xFF07) in (0x4700, 0x4780):       # bx/blx reg (Rm=bits 6-3)
                rm = (hw >> 3) & 0xF
                if rm == 14 or rm not in last:
                    return targets, i + 2
                p = last[rm]
                m = 'thumb' if p & 1 else 'arm'
                targets.append(((p & ~1) if m == 'thumb' else (p & ~3), m,
                                'bx_reg_thumb'))
                return targets, i + 2
            if (hw & 0xFF00) == 0x4600:                 # mov with a high register
                rd = ((hw >> 4) & 8) | (hw & 7)
                if rd == 15 and ((hw >> 3) & 0xF) == 14:
                    return targets, i + 2               # mov pc, lr
                i += 2
                continue
            if (hw & 0xFF00) == 0xBD00 and (hw & 0x0100):   # pop {..,pc}
                return targets, i + 2
            if (hw & 0xF800) == 0xE000:                 # b (uncond)
                return targets, i + 2
            if (hw & 0xF800) == 0xF800:
                i += 4
                continue
            i += 2
        else:
            ins = u32(i)
            if (ins & 0xFFFFFFF0) in (0xE12FFF10, 0xE12FFF30):
                rd = ins & 0xF                            # bx/blx reg
                if rd == 14 or rd not in last:
                    return targets, i + 4
                p = last[rd]
                m = 'thumb' if p & 1 else 'arm'
                targets.append(((p & ~1) if m == 'thumb' else (p & ~3), m,
                                'bx_reg_arm'))
                return targets, i + 4
            if (ins & 0x0F000000) == 0x0B000000:         # BL
                off = sext((ins & 0xFFFFFF) << 2, 26)
                t = i + 8 + off
                m = 'thumb' if t & 1 else 'arm'
                targets.append(((t & ~1) if m == 'thumb' else (t & ~3), m, 'bl_arm'))
                i += 4
                continue
            if (ins & 0xFF7F0000) == 0xE51F0000:          # ldr rX,[pc,#imm]
                last[(ins >> 12) & 0xF] = u32(i + 8 + (ins & 0xFFF))
                i += 4
                continue
            if (ins & 0xFFFFFFF0) == 0xE1A0F00E:          # mov pc, lr
                return targets, i + 4
            if (ins & 0xFF900000) == 0xE8900000 and ((ins >> 16) & 0xF) == 13 \
                    and (ins & 0x200000) and (ins & 0x8000):    # ldm sp!,{..,pc}
                return targets, i + 4
            if (ins & 0x0F000000) == 0x0A000000:          # b (uncond)
                return targets, i + 4
            i += 4
    return targets, i


def ptr_candidates():
    """4-aligned ROM words holding an odd 0x08xxxxx1 pointer whose target starts
    with a THUMB `push {..., lr}` (0xB5xx) and lies in the ROM.  Sorted, unique.
    The decode filter (A4) and the proximity filter (A6) are applied by main()."""
    words = array('I')
    words.frombytes(rom[:len(rom) // 4 * 4])
    out = set()
    for w in words:
        if not (w & 1):
            continue
        t = w & ~1
        if not in_rom(t + 2) or t < 0x08000100:
            continue
        if (u16(t) & 0xFF00) == 0xB500:      # push {...} with LR set
            out.add(t)
    return sorted(out)


def main():
    if not ROM.exists():
        raise SystemExit(f'missing {ROM}')
    found = {}        # address -> (mode, name, source)
    walk_end = {}
    skipped = set()   # pointer values seen via `bx rX` but not accepted (A2)
    far = []          # ptr_prologue candidates rejected by the A6 proximity rule

    def run(queue):
        while queue:
            a, m, name, src = queue.pop(0)
            if a not in found:
                found[a] = (m, name, src)
            if a in walk_end:
                continue
            targets, end = scan(a, m)
            walk_end[a] = end
            for t, tm, ts in targets:
                if not in_rom(t):
                    continue
                if ts in ('bx_reg_thumb', 'bx_reg_arm'):
                    # a pointer read from a literal pool: not proof of code (A2)
                    if t not in found:
                        skipped.add(t)
                    continue
                if t not in found:
                    queue.append((t, tm, None, ts))

    # phase 1: seeds, IRQ table, and everything the BL closure reaches from them
    queue = [(a, m, n, s) for a, m, n, s in SEEDS]
    for k in range(14):      # interrupt-handler table: word k -> handler bit k-1
        p = u32(IRQ_TABLE + 4 * k)
        if in_rom(p & ~1) and (p & ~1) >= 0x08000100:
            queue.append((p & ~1, 'thumb' if p & 1 else 'arm', None, 'irq_table'))
    run(queue)

    # filter the function-pointer table candidates against the phase-1 code (A6)
    bl_starts = sorted(found)
    bad_head = []

    def nearest_bl(a):
        i = bisect.bisect_left(bl_starts, a)
        best = 1 << 40
        if i < len(bl_starts):
            best = min(best, bl_starts[i] - a)
        if i:
            best = min(best, a - bl_starts[i - 1])
        return best

    queue = []
    for t in ptr_candidates():
        if t in found:
            continue
        if not thumb_ok(t):
            bad_head.append(t)
            continue
        d = nearest_bl(t)
        if d > PTR_MAX_DIST:
            far.append((t, d))
            continue
        queue.append((t, 'thumb', None, 'ptr_prologue'))
    run(queue)               # phase 2: pointer tables + their BL closure

    starts = sorted(found)
    rows = []
    for idx, a in enumerate(starts):
        m, name, src = found[a]
        unit = 2 if m == 'thumb' else 4
        end = walk_end.get(a, a + unit)
        nxt = starts[idx + 1] if idx + 1 < len(starts) else None
        stop = end if (nxt is None or nxt >= end) else nxt
        size = max(stop - a, unit)         # extents never overlap (A5)
        rows.append((a, name or f'sub_{a:08X}', m, size, src))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='ascii', newline='\n') as f:
        f.write('address,name,mode,size,source\n')
        for a, n, m, sz, s in rows:
            f.write(f'0x{a:08X},{n},{m},{sz},{s}\n')

    per_source = {}
    for r in rows:
        per_source[r[4]] = per_source.get(r[4], 0) + 1
    print(f'functions: {len(rows)}')
    print(f'thumb: {sum(1 for r in rows if r[2] == "thumb")}  '
          f'arm: {sum(1 for r in rows if r[2] == "arm")}')
    print(f'lowest: 0x{rows[0][0]:08X}  highest: 0x{rows[-1][0]:08X}')
    for s in sorted(per_source):
        print(f'  source {s}: {per_source[s]}')
    print(f'pointer values seen via bx rX but not accepted (A2): {len(skipped)} '
          f'(of which now in the census anyway: {len(skipped & set(found))})')
    print(f'ptr_prologue candidates rejected by the A4 decode rule: {len(bad_head)}')
    print(f'ptr_prologue candidates rejected by the A6 proximity rule: {len(far)}')
    for t, d in sorted(far):
        print(f'  far 0x{t:08X} nearest BL-closure function 0x{d:X} away')


if __name__ == '__main__':
    main()
