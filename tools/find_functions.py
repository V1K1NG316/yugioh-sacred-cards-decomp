#!/usr/bin/env python3
"""Find function starts in private/baserom.gba by following THUMB BL and ARM BL/BX targets.

Method (linear scan, worklist): start from the entry points found in
scripts/dis_range.sh evidence (reset vector, crt0, IRQ handler, main) plus the
interrupt-handler table the crt0's dispatcher reads at 0x0807F420.  For every
function start, decode instructions until the function ends (return: thumb
`pop {..,pc}` / `bx lr` / `mov pc,lr`; arm `bx lr` / `mov pc,lr` /
`ldm sp!,{..,pc}`; or an unconditional branch out of the function).  Registers
loaded by `ldr rX,[pc,#imm]` are tracked so that `bx rX` / `blx rX` targets
(the crt0 -> main interworking jump) are recovered.

This is a heuristic sweep, not a full data-flow analysis: it is an
approximation (docs/approximations.md A1).  Output: config/functions.csv with
header `address,name,mode,source` (address 0x08xxxxxx, sorted, unique).
"""
import struct
from pathlib import Path

REPO = Path(r'D:\Yugioh_DeComp_V2')
ROM = REPO / 'private' / 'baserom.gba'
OUT = REPO / 'config' / 'functions.csv'

BASE = 0x08000000
END = 0x09000000
MAX_FUNC = 0x4000  # stop a runaway scan

# step-1 entries: (address, mode, name, source)
SEEDS = [
    (0x08000000, 'arm',   'reset',       'reset_vector'),
    (0x080000C0, 'arm',   'crt0',        'reset_branch'),
    (0x080000FC, 'arm',   'irq_handler', 'crt0_writes_0x03007FFC'),
    (0x08016928, 'thumb', 'main',        'crt0_bx_literal_0x0800021C'),
]
IRQ_TABLE = 0x0807F420  # dispatcher at irq_handler loads handler ptrs from here

rom = ROM.read_bytes()
ENDS = {}      # function address -> last instruction address visited by scan()


def u16(addr):
    o = addr - BASE
    return struct.unpack_from('<H', rom, o)[0]


def u32(addr):
    o = addr - BASE
    return struct.unpack_from('<I', rom, o)[0]


def in_rom(a):
    return BASE <= a < BASE + len(rom)


def sext(v, bits):
    m = 1 << (bits - 1)
    return (v ^ m) - m


def scan(addr, mode):
    """Walk one function; yield (target, mode, source) for BL/BX targets found."""
    i = addr
    last = {}          # reg -> value of the last `ldr rX,[pc,#imm]`
    stop = addr + MAX_FUNC
    while i < stop and in_rom(i):
        ENDS.setdefault(addr, []).append(i)   # every instruction address scanned
        if mode == 'thumb':
            hw = u16(i)
            if (hw & 0xF800) == 0xF000 and in_rom(i + 2):
                hw2 = u16(i + 2)
                if (hw2 & 0xF800) == 0xF800:      # BL
                    off = ((hw & 0x7FF) << 12) | ((hw2 & 0x7FF) << 1)
                    off = sext(off, 23)
                    yield ((i + 4 + off) & ~1, 'thumb', 'bl_thumb')
                    i += 4
                    continue
                if (hw2 & 0xF800) == 0xE800:      # BLX imm -> ARM
                    off = ((hw & 0x7FF) << 12) | ((hw2 & 0x7FF) << 1)
                    off = sext(off, 23)
                    yield ((i + 4 + off) & ~3, 'arm', 'blx_thumb')
                    i += 4
                    continue
            if (hw & 0xF800) == 0x4800:            # ldr rX,[pc,#imm]
                last[(hw >> 8) & 7] = u32(((i + 4) & ~3) + ((hw & 0xFF) * 4))
                i += 2
                continue
            if (hw & 0xFF07) in (0x4700, 0x4780):  # bx/blx reg (Rm = bits 6-3)
                rm = (hw >> 3) & 0xF
                if rm == 14 or rm not in last:
                    return
                p = last[rm]
                m = 'thumb' if p & 1 else 'arm'
                yield ((p & ~1) if m == 'thumb' else (p & ~3), m, 'bx_reg_thumb')
                return
            if (hw & 0xFF00) == 0x4600:            # mov with a high register
                rd = ((hw >> 4) & 8) | (hw & 7)
                rm = (hw >> 3) & 0xF
                if rd == 15 and rm == 14:          # mov pc, lr
                    return
                i += 2
                continue
            if (hw & 0xFF00) == 0xBD00 and (hw & 0x0100):            # pop {..,pc}
                return
            if (hw & 0xF800) == 0xE000:                              # b (uncond)
                return
            if (hw & 0xF800) == 0xF800 and in_rom(i + 2):            # second half
                i += 4
                continue
            i += 2
        else:
            ins = u32(i)
            if (ins & 0xFFFFFFF0) in (0xE12FFF10, 0xE12FFF30):
                rd = ins & 0xF                          # bx/blx reg
                if rd == 14 or rd not in last:
                    return
                p = last[rd]
                m = 'thumb' if p & 1 else 'arm'
                yield ((p & ~1) if m == 'thumb' else (p & ~3), m, 'bx_reg_arm')
                return
            if (ins & 0x0F000000) == 0x0B000000:        # BL
                off = sext((ins & 0xFFFFFF) << 2, 26)
                t = i + 8 + off
                m = 'thumb' if t & 1 else 'arm'
                yield ((t & ~1) if m == 'thumb' else (t & ~3), m, 'bl_arm')
                i += 4
                continue
            if (ins & 0xFF7F0000) == 0xE51F0000:        # ldr rX,[pc,#imm]
                last[(ins >> 12) & 0xF] = u32(i + 8 + (ins & 0xFFF))
                i += 4
                continue
            if (ins & 0xFFFFFFF0) == 0xE1A0F00E:        # mov pc, lr
                return
            if (ins & 0xFF900000) == 0xE8900000 and ((ins >> 16) & 0xF) == 13 \
                    and (ins & 0x200000) and (ins & 0x8000):   # ldm sp!,{..,pc}
                return
            if (ins & 0x0F000000) == 0x0A000000:        # b (unconditional, cond=AL)
                return
            i += 4


def main():
    if not ROM.exists():
        raise SystemExit(f'missing {ROM}')
    found = {}      # address -> (mode, name, source)
    bl_hit = set()  # addresses that a real BL/BLX instruction targets
    skipped = set() # targets seen only through `bx rX` after a literal load
    queue = []
    for a, m, n, s in SEEDS:
        queue.append((a, m, n, s))
    for k in range(14):   # interrupt-handler table: word k -> handler for bit k-1
        p = u32(IRQ_TABLE + 4 * k)
        if in_rom(p & ~1) and (p & ~1) >= 0x08000100:
            m = 'thumb' if p & 1 else 'arm'
            queue.append((p & ~1, m, None, 'irq_table_entry'))

    while queue:
        a, m, name, src = queue.pop(0)
        if a in found:
            continue
        found[a] = (m, name, src)
        for t, tm, ts in scan(a, m):
            if not in_rom(t):
                continue
            if ts in ('bx_reg_thumb', 'bx_reg_arm'):
                # a pointer value read from a literal pool: not proof of code, so
                # do not walk into it (docs/approximations.md A2)
                if t not in found:
                    skipped.add(t)
                continue
            bl_hit.add(t)
            if t not in found:
                queue.append((t, tm, None, ts))

    rows = []
    for a in sorted(found):
        m, name, src = found[a]
        rows.append((a, name or f'sub_{a:08X}', m, src))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='ascii', newline='\n') as f:
        f.write('address,name,mode,source\n')
        for a, n, m, s in rows:
            f.write(f'0x{a:08X},{n},{m},{s}\n')
    print(f'functions: {len(rows)}')
    print(f'thumb: {sum(1 for r in rows if r[2] == "thumb")}  '
          f'arm: {sum(1 for r in rows if r[2] == "arm")}')
    print(f'lowest: 0x{rows[0][0]:08X}  highest: 0x{rows[-1][0]:08X}')
    print(f'pointer-only targets not walked into (unverified): {len(skipped)}')


if __name__ == '__main__':
    main()
