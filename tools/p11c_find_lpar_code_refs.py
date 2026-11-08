import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

sysmgr = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
data = sysmgr.read_bytes()

targets = [0x8003b2b8, 0x80039610, 0x80039600]

print(f"Data size: {len(data)}")
# Search entire file for lis/addi combinations
for o in range(0x10000, len(data) - 36, 4):
    w, = struct.unpack_from('>I', data, o)
    op = w >> 26
    if op == 15:
        rd = (w >> 21) & 0x1f
        imm = w & 0xffff
        hi = imm if imm < 0x8000 else imm - 0x10000
        for next_o in range(o + 4, min(len(data) - 4, o + 32), 4):
            w2, = struct.unpack_from('>I', data, next_o)
            if (w2 >> 26) == 14: # addi
                ra2 = (w2 >> 16) & 0x1f
                imm2 = w2 & 0xffff
                lo = imm2 if imm2 < 0x8000 else imm2 - 0x10000
                if ra2 == rd:
                    target_va = (hi << 16) + lo
                    if target_va in targets:
                        print(f"Ref to 0x{target_va:x} at off 0x{o:x} / 0x{next_o:x}")
