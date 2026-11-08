import struct
from pathlib import Path

data355 = Path('local_only/fw355/out/lv1.elf').read_bytes()
# Segment 1: file 0x20000 -> VA 0x200000
def va2off(va):
    return va - 0x200000 + 0x20000

# Look at 0x3ac2b8 (HV 170)
off = va2off(0x3ac2b8)
print(f"Bytes at 0x3ac2b8 (off {hex(off)}):")
for i in range(4):
    q = struct.unpack_from('>Q', data355, off + i*8)[0]
    print(f"  +0x{i*8:02x}: 0x{q:016x}")

# Let's search where 0x3ac2b8 is referenced
p64 = struct.pack('>Q', 0x3ac2b8)
p = 0
while True:
    idx = data355.find(p64, p)
    if idx == -1: break
    va = idx - 0x20000 + 0x200000
    print(f"Referenced at VA {hex(va)}")
    p = idx + 1
