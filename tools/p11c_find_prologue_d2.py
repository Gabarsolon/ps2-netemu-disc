import struct
from pathlib import Path

sysmgr = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
data = sysmgr.read_bytes()

off_base = 0x10000 - 0x80000000
for va in range(0x8001d234, 0x8001d000, -4):
    o = va + off_base
    w, = struct.unpack_from('>I', data, o)
    if (w >> 16) == 0xf821: # stdu r1, ...
        print(f"Function prologue at VA 0x{va:x}: 0x{w:08x}")
        break
