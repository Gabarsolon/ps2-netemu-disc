import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
# 0x3df07c is in segment 1 (base delta 0x1e0000)!
off = 0x3df07c - 0x1e0000

for i in range(0, 32, 4):
    w, = struct.unpack_from('>I', data, off + i)
    print(f"0x{0x3df07c+i:x}: 0x{w:08x}")
