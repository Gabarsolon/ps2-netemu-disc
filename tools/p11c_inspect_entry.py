import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
off = 0x10100
for i in range(0, 48, 4):
    w, = struct.unpack('>I', data[off+i:off+i+4])
    print(f"0x{0x100+i:x}: 0x{w:08x}")
