"""Ground truth run 2: compose two cards and dump each decompressed picture buffer,
so the picture->output byte mapping can be solved by matching both cards at once."""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / 'private' / 'tmp'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mgba_gdb import RSP

SCRATCH = 0x02030000
SCRATCH_LEN = 0x2000
PICBUF = 0x02018800
STUB = 0x02020200
SPIN = 0x02020214
CARDS = (1, 2)

r = RSP()
r.interrupt(0.5)
print('? ->', r.stop_reason())


def g():
    raw = bytes.fromhex(r.send('g').decode())
    return [int.from_bytes(raw[4 * i:4 * i + 4], 'little') for i in range(17)]


def arm_stub(dest, card):
    code = (bytes.fromhex('10009fe5' '10109fe5' '10e09fe5' '10209fe5' '12ff2fe1' 'feffffea')
            + dest.to_bytes(4, 'little') + card.to_bytes(4, 'little')
            + SPIN.to_bytes(4, 'little') + (0x08034AF9).to_bytes(4, 'little'))
    assert len(code) == 0x28
    return code


pattern = bytes(i & 0xFF for i in range(SCRATCH_LEN))
r.write(SCRATCH, pattern)
assert r.read(SCRATCH, 32) == pattern[:32]
r.write(0x04000208, b'\x00\x00')

for n, card in enumerate(CARDS):
    dest = SCRATCH + n * 0x1000
    r.write(STUB, arm_stub(dest, card))
    w = g()
    setup = list(w)
    setup[13] = 0x0203F000
    setup[14] = SPIN
    setup[15] = STUB
    for i in range(16):
        r.write_reg(i, setup[i])
    r.write_reg(25, 0x0000001F)
    assert g()[15] == STUB, 'pc did not take'
    r.s.sendall(b'$c#63')
    time.sleep(1.2)
    stop = r.interrupt(0.4)
    pc = g()[15]
    pic = r.read(PICBUF, 576)
    (HERE / ('emu_pic_%d.bin' % card)).write_bytes(pic)
    print('card %d: stop=%s pc=%#010x pic[0:24]=%s' % (card, stop, pc, pic[:24].hex()))

buf = r.read(SCRATCH, SCRATCH_LEN)
(HERE / 'emu_scratch2.bin').write_bytes(buf)
print('max read chunk:', r.max_read)
for n, card in enumerate(CARDS):
    region = buf[n * 0x1000:(n * 0x1000) + 0x1000]
    ref = pattern[n * 0x1000:(n * 0x1000) + 0x1000]
    changed = [i for i, (a, b) in enumerate(zip(region, ref)) if a != b]
    print('card %d: %d bytes changed, last %#x' % (card, len(changed), changed[-1]))
r.s.close()
print('done')
