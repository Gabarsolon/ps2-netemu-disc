import struct
from pathlib import Path

sysmgr = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
data = sysmgr.read_bytes()

# Search for 64-bit or 32-bit references to 0xc000bf60, or lis/addi to 0xc000bf60
targets = [0xc000bf60, 0xc000bf80, 0xc000bf88, 0xc000b078]

for o in range(0, len(data) - 8, 4):
    w64, = struct.unpack_from('>Q', data, o)
    if w64 in targets:
        print(f"64-bit ref to 0x{w64:x} at off 0x{o:x}")
    w32, = struct.unpack_from('>I', data, o)
    if w32 in targets:
        print(f"32-bit ref to 0x{w32:x} at off 0x{o:x}")
