import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
base = 0x210000

for o in range(0, len(data) - 4, 4):
    w, = struct.unpack_from('>I', data, o)
    op = w >> 26
    rd = (w >> 21) & 0x1f
    if rd == 2 and op in [14, 15]: # addi/addis into r2
        ra = (w >> 16) & 0x1f
        imm = w & 0xffff
        print(f"VA 0x{o+base:x}: op={op} ra=r{ra} imm=0x{imm:x}")
