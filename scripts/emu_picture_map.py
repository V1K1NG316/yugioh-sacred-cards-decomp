"""Impulse test 3 (clean): prefill 0xCC, mask one source with 0xFF, index the other by chunk.

Run P: frame = 0xFF everywhere, picture = chunk index -> 0xCC = not written, 0xFF = frame, j = picture chunk j
Run F: picture = 0xFF everywhere, frame = chunk index -> j = frame chunk j
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / 'private' / 'tmp'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mgba_gdb import RSP

PIC, FRM, LEN = 0x02021000, 0x02022000, 4096
STUB = 0x02020200
SPIN = STUB + 0x18
TARGET = 0x08034B41
DEST_P, DEST_F = 0x02030000, 0x02031000

r = RSP()
r.interrupt(0.5)
print('? ->', r.stop_reason())


def g():
    raw = bytes.fromhex(r.send('g').decode())
    return [int.from_bytes(raw[4 * i:4 * i + 4], 'little') for i in range(17)]


def arm_stub(dest, pic, frm):
    code = (bytes.fromhex('18009fe5' '18109fe5' '18209fe5' '18e09fe5' '18309fe5' '13ff2fe1')
            + bytes.fromhex('feffffea') + bytes(4)
            + dest.to_bytes(4, 'little') + pic.to_bytes(4, 'little') + frm.to_bytes(4, 'little')
            + SPIN.to_bytes(4, 'little') + TARGET.to_bytes(4, 'little'))
    assert len(code) == 0x34
    return code


def call(dest, pic_pat, frm_pat):
    r.write(PIC, pic_pat)
    r.write(FRM, frm_pat)
    r.write(STUB, arm_stub(dest, PIC, FRM))
    w = g()
    setup = list(w)
    setup[13] = 0x0203F000
    setup[14] = SPIN
    setup[15] = STUB
    for i in range(16):
        r.write_reg(i, setup[i])
    r.write_reg(25, 0x0000001F)
    r.s.sendall(b'$c#63')
    time.sleep(1.2)
    r.interrupt(0.4)
    return g()[15] == SPIN


def chunked(n, cap=250):
    out = bytearray()
    for i in range(n // 4):
        out += bytes([i % cap]) * 4
    return bytes(out)


r.write(0x04000208, b'\x00\x00')
r.write(DEST_P, b'\xCC' * 0x1000)
r.write(DEST_F, b'\xCC' * 0x1000)
ok_p = call(DEST_P, chunked(LEN), b'\xFF' * LEN)
xp = r.read(DEST_P, 0x1000)
(HERE / 'emu_map2_pic.bin').write_bytes(xp)
ok_f = call(DEST_F, b'\xFF' * LEN, chunked(LEN))
xf = r.read(DEST_F, 0x1000)
(HERE / 'emu_map2_frm.bin').write_bytes(xf)
print('run P ok=%s  run F ok=%s' % (ok_p, ok_f))
print('run P: 0xCC left %d, 0xFF %d, indexed %d' % (xp.count(0xCC), sum(1 for o in range(0, 0x1000, 4) if xp[o:o + 4] == b'\xff\xff\xff\xff'), sum(1 for o in range(0, 0x1000, 4) if xp[o] != 0xCC and xp[o:o + 4] == bytes([xp[o]]) * 4)))
print('run F: 0xCC left %d, 0xFF %d, indexed %d' % (xf.count(0xCC), sum(1 for o in range(0, 0x1000, 4) if xf[o:o + 4] == b'\xff\xff\xff\xff'), sum(1 for o in range(0, 0x1000, 4) if xf[o] != 0xCC and xf[o:o + 4] == bytes([xf[o]]) * 4)))
r.s.close()
print('done')
