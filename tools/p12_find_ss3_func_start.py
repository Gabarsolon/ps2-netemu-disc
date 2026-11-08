import struct
from pathlib import Path

ss3 = Path('local_only/analysis/p0i/modules/ss_server3.elf')
data = ss3.read_bytes()

off = 0x10b44
for o in range(off - 256, off, 4):
    w, = struct.unpack_from('>I', data, o)
    if (w >> 16) == 0xf821: # stdu r1, ...
        print(f"Function start at file off 0x{o:x} (VA 0x{0x80000000 + o - 0x10000:x}): 0x{w:08x}")
