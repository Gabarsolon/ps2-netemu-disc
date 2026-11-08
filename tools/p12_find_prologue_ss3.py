import struct
from pathlib import Path

data = Path('local_only/analysis/p0i/modules/ss_server3.elf').read_bytes()
off = 0x10b44

for o in range(off - 512, off, 4):
    w, = struct.unpack_from('>I', data, o)
    if w == 0x7c0802a6 or (w >> 16) == 0xf821:
        va = 0x80000000 + (o - 0x10000)
        print(f"Prologue at off 0x{o:x}, VA 0x{va:x}: 0x{w:08x}")
