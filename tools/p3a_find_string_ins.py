import struct
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
stock_elf = ROOT / 'local_only' / 'stock.elf'
data = stock_elf.read_bytes()

# Load segments
phoff = struct.unpack_from('>Q', data, 32)[0]
phnum = struct.unpack_from('>H', data, 56)[0]
segs = []
for i in range(phnum):
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, phoff + i * 56)
    if p_type == 1:
        segs.append((p_vaddr, p_offset, p_filesz))

# 0x300bc1: hi16 is 0x30, lo16 is 0x0bc1 (or with sign: hi 0x30, lo 0x0bc1)
# lis rX, 0x30 -> 0x3c..0030
# addi rY, rX, 0x0bc1 -> 0x38..0bc1
for vaddr, off, sz in segs:
    seg_bytes = data[off:off+sz]
    for pos in range(0, sz - 3, 4):
        w = struct.unpack_from('>I', seg_bytes, pos)[0]
        # check if lo16 is 0x0bc1 or 0x0c5c
        lo = w & 0xffff
        if lo in (0x0bc1, 0x0c5c):
            cur_va = vaddr + pos
            print(f"Match for lo=0x{lo:04x} at 0x{cur_va:x}: 0x{w:08x}")
