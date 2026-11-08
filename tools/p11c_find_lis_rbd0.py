import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
base = 0x210000

# String addresses in lv1:
# 0x325810 (off 0x115810)
# 0x46dd7d (off 0x25dd7d)
# 0x53d6a5 (off 0x32d6a5)

targets = [0x325810, 0x46dd7d, 0x53d6a5]

for o in range(0, len(data) - 4, 4):
    va = o + base
    w, = struct.unpack_from('>I', data, o)
    op = w >> 26
    # lis rA, imm1
    # addi rB, rA, imm2
    if op == 15: # addis / lis
        ra = (w >> 16) & 0x1f
        rd = (w >> 21) & 0x1f
        imm1 = w & 0xffff
        hi = imm1 if imm1 < 0x8000 else imm1 - 0x10000
        # check next few instructions for addi with rd
        for next_o in range(o + 4, min(len(data) - 4, o + 32), 4):
            w2, = struct.unpack_from('>I', data, next_o)
            op2 = w2 >> 26
            if op2 == 14: # addi
                ra2 = (w2 >> 16) & 0x1f
                rd2 = (w2 >> 21) & 0x1f
                imm2 = w2 & 0xffff
                lo = imm2 if imm2 < 0x8000 else imm2 - 0x10000
                if ra2 == rd:
                    target_va = (hi << 16) + lo
                    if target_va in targets or (target_va & ~0xff) in [t & ~0xff for t in targets]:
                        print(f"Target 0x{target_va:x} referenced at 0x{va:x} / 0x{next_o+base:x}")
