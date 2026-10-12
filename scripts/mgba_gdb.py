"""Minimal GDB remote-serial-protocol client for mGBA's gdb stub (Windows, stdlib only)."""
import socket
import time


class RSP:
    def __init__(self, host='127.0.0.1', port=2345, timeout=10.0):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.s.settimeout(timeout)
        self.buf = b''
        self.packets = []
        self.max_read = 1024

    def qsupported(self):
        return self.send('qSupported:multiprocess+;swbreak+;hwbreak+')

    # --- low level -------------------------------------------------------
    def _read_byte(self):
        while not self.buf:
            self.buf = self.s.recv(65536)
            if not self.buf:
                raise EOFError('stub closed')
        b, self.buf = self.buf[:1], self.buf[1:]
        return b

    def send(self, payload, wait=True):
        if isinstance(payload, bytes):
            data = payload
        else:
            data = payload.encode()
        if data in (b'\x03',):
            self.s.sendall(data)
            return None
        csum = sum(data) & 0xFF
        self.s.sendall(b'$' + data + b'#%02x' % csum)
        # consume the ack, skipping any async notification packets
        while True:
            b = self._read_byte()
            if b == b'+':
                break
            if b in (b'$', b'\x03'):
                if b == b'\x03':
                    continue
                pkt = self._read_raw_packet()
                self.packets.append(pkt)
                self.s.sendall(b'+')
                continue
            if b == b'-':
                self.s.sendall(b'$' + data + b'#%02x' % csum)
        if not wait:
            return None
        return self.recv()

    def _read_raw_packet(self):
        out = bytearray()
        while True:
            b = self._read_byte()
            if b == b'#':
                self._read_byte(); self._read_byte()
                return bytes(out)
            out += b

    def recv(self):
        while True:
            b = self._read_byte()
            if b == b'+':
                continue
            if b == b'$':
                pkt = self._read_raw_packet()
                self.s.sendall(b'+')
                return pkt
            if b == b'\x03':
                return b'\x03'

    def interrupt(self, settle=0.5):
        self.s.sendall(b'\x03')
        time.sleep(settle)
        return self.recv()

    # --- commands --------------------------------------------------------
    def stop_reason(self):
        return self.send('?')

    def regs(self):
        hexs = self.send('g').decode()
        raw = bytes.fromhex(hexs)
        return dict(r=[int.from_bytes(raw[4 * i:4 * i + 4], 'little') for i in range(16)],
                    fpscpsr=raw[4 * 16:], cpsr=int.from_bytes(raw[25 * 4:26 * 4], 'little'))

    def write_reg(self, n, value):
        return self.send('P%x=%s' % (n, value.to_bytes(4, 'little').hex()))

    def read(self, addr, length):
        out = bytearray()
        step = self.max_read
        while len(out) < length:
            n = min(length - len(out), step)
            resp = self.send('m%x,%x' % (addr + len(out), n))
            if resp.startswith(b'E'):
                if step > 16:
                    step //= 4
                    continue
                raise RuntimeError('mem read error at %#x: %s' % (addr + len(out), resp))
            self.max_read = step
            out += bytes.fromhex(resp.decode())
        return bytes(out)

    def write(self, addr, data):
        for i in range(0, len(data), 512):
            chunk = data[i:i + 512]
            resp = self.send('M%x,%x:%s' % (addr + i, len(chunk), chunk.hex()))
            if resp != b'OK':
                raise RuntimeError('mem write failed at %#x: %s' % (addr + i, resp))
        return True

    def set_break(self, addr, kind=2):
        return self.send('Z0,%x,%d' % (addr, kind))

    def clear_break(self, addr, kind=2):
        return self.send('z0,%x,%d' % (addr, kind))

    def cont(self, settle=0.0):
        self.s.sendall(b'$c#63')
        time.sleep(0)  # ack handled by recv()
        b = self._read_byte()
        if b == b'+':
            pass
        elif b == b'\x03':
            return b'\x03'
        else:
            self.buf = b + self.buf
        return self.recv()

    def step(self):
        return self.send('s')

    def kill(self):
        try:
            self.s.sendall(b'$k#6b')
        except OSError:
            pass
        self.s.close()
