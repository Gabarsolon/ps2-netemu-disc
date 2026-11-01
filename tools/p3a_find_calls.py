import struct
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
stock_elf = ROOT / 'local_only' / 'stock.elf'
data = stock_elf.read_bytes()

# Find loadable segments
phoff = struct.unpack_from('>Q', data, 32)[0]
phnum = struct.unpack_from('>H', data, 56)[0]
segs = []
for i in range(phnum):
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, phoff + i * 56)
    if p_type == 1: # PT_LOAD
        segs.append((p_vaddr, p_offset, p_filesz))

def va_to_off(va):
    for vaddr, off, sz in segs:
        if vaddr <= va < vaddr + sz:
            return off + (va - vaddr)
    return None

def off_to_va(offset):
    for vaddr, off, sz in segs:
        if off <= offset < off + sz:
            return vaddr + (offset - off)
    return None

target = 0x1ec084
print(f"Searching for bl to 0x{target:x}...")
# In PowerPC: bl is opcode 18: [010010][LI (24 bits)][AA(1)][LK(1)]
# LI is signed 24-bit shifted right by 2 (bits 6..29), LK=1 (bit 31), AA=0 (bit 30)
# So diff = target - current_va
# LI = (diff >> 2) & 0x00ffffff
# instruction word = (18 << 26) | (diff & 0x03fffffc) | 1

for vaddr, off, sz in segs:
    seg_bytes = data[off:off+sz]
    for pos in range(0, sz - 3, 4):
        w = struct.unpack_from('>I', seg_bytes, pos)[0]
        opcode = w >> 26
        if opcode == 18: # 'b' or 'bl'
            lk = w & 1
            aa = w & 2
            li = (w & 0x03fffffc)
            if li & 0x02000000:
                li -= 0x04000000 # sign extend
            cur_va = vaddr + pos
            dest = cur_va + li if aa == 0 else li
            if dest == target:
                print(f"Found branch to 0x{target:x} at 0x{cur_va:x} (lk={lk}): word=0x{w:08x}")

