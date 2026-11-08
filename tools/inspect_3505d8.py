import struct
from pathlib import Path

data355 = Path('local_only/fw355/out/lv1.elf').read_bytes()
def va2off(va):
    return va - 0x200000 + 0x20000

off = va2off(0x3505d8)
print(f"Around 0x3505d8 (off {hex(off)}):")
for i in range(-4, 16):
    q = struct.unpack_from('>Q', data355, off + i*8)[0]
    print(f"  {hex(0x3505d8 + i*8)}: 0x{q:016x}")
