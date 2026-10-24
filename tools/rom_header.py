"""ROM header printer for Yu-Gi-Oh! The Sacred Cards (GBA cartridge header)."""
import struct
from pathlib import Path

ROM_PATH = str(Path(__file__).resolve().parents[1] / 'private' / 'baserom.gba')

def main():
    with open(ROM_PATH, "rb") as f:
        data = f.read()

    # title: bytes 0xA0 up to but NOT including 0xAC, decoded as ASCII,
    #         trailing 0x00 removed
    title = data[0xA0:0xAC].rstrip(b"\x00").decode("ascii")

    # code: bytes 0xAC up to but NOT including 0xB0, decoded as ASCII
    code = data[0xAC:0xB0].decode("ascii")

    # maker: bytes 0xB0..0xB2, decoded as ASCII
    maker = data[0xB0:0xB2].decode("ascii")

    # version: unsigned byte at offset 0xBC, printed in decimal
    version = data[0xBC]

    # entry_branch_target: 32-bit little-endian word at offset 0 (ARM branch)
    #   word = struct.unpack('<I, data[0:4])[0]
    word0 = struct.unpack("<I", data[0:4])[0]
    off = (word0 & 0x00FFFFFF) * 4
    target = 0x08000000 + off + 8

    # size: length of the file in bytes
    size = len(data)

    print(f"title={title}")
    print(f"code={code}")
    print(f"maker={maker}")
    print(f"version={version}")
    print(f"entry_branch_target=0x{target:08X}")
    print(f"size={size}")


if __name__ == "__main__":
    main()
