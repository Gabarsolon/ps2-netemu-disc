import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
base = 0x210000
off = 0x2faf4c
for o in range(off - 256, off, 4):
    w, = struct.unpack('>I', data[o:o+4])
    if (w >> 16) == 0xf821: # stdu r1, ...
        print(f"Function start at VA 0x{o+base:x} (off 0x{o:x}): 0x{w:08x}")
