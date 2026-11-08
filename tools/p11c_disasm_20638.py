import struct
from pathlib import Path

data = Path('local_only/analysis/p0i/modules/ss_server1.elf').read_bytes()
# 0x80020700 to 0x80020750
off_base = 0x10000 - 0x80000000
for va in range(0x80020700, 0x80020750, 4):
    o = va + off_base
    w, = struct.unpack_from('>I', data, o)
    print(f"0x{va:x}: 0x{w:08x}")
