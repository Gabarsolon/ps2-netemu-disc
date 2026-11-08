import struct
from pathlib import Path

sysmgr = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
data = sysmgr.read_bytes()

# TOC = 0xc0012f40
# 0xc000bf60 - 0xc0012f40 = -0x6fe0
# 0xc000bf80 - 0xc0012f40 = -0x6fc0
# 0xc000bf88 - 0xc0012f40 = -0x6fb8

print("Scanning for instructions referencing TOC near -0x6fc0...")
for o in range(0x10000, len(data) - 4, 4):
    va = 0x80000000 + (o - 0x10000)
    w, = struct.unpack_from('>I', data, o)
    op = w >> 26
    ra = (w >> 16) & 0x1f
    rd = (w >> 21) & 0x1f
    imm = w & 0xffff
    simm = imm if imm < 0x8000 else imm - 0x10000
    if ra == 2: # using r2
        calc_addr = 0xc0012f40 + simm
        if 0xc000bf00 <= calc_addr <= 0xc000c000 or 0xc000b000 <= calc_addr <= 0xc000b100:
            print(f"VA 0x{va:x}: op={op} rd=r{rd} simm={simm} (0x{calc_addr:x})")
