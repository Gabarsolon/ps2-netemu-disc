import struct
from pathlib import Path

b = open('C:/Users/remus/ps2-netemu-disc/local_only/analysis/p0i/modules/ss_server1.elf', 'rb').read()

target_va = 0x8001c418
for off in range(0, len(b) - 8, 8):
    w = struct.unpack('>Q', b[off:off+8])[0]
    if w == target_va:
        print(f"64-bit pointer ref at file offset {hex(off)}")

for off in range(0x10000, 0x56ea0 - 4, 4):
    va = 0x80000000 + off - 0x10000
    instr = struct.unpack('>I', b[off:off+4])[0]
    # check bl / b
    if (instr >> 26) in (18,): # B / BL
        li = (instr & 0x03fffffc)
        if li & 0x02000000:
            li -= 0x04000000
        if va + li == target_va:
            print(f"Branch ref at VA {hex(va)} (file off {hex(off)})")
