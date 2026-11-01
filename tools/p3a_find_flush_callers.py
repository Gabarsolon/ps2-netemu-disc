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

def find_branches_to(target):
    branches = []
    for vaddr, off, sz in segs:
        seg_bytes = data[off:off+sz]
        for pos in range(0, sz - 3, 4):
            w = struct.unpack_from('>I', seg_bytes, pos)[0]
            opcode = w >> 26
            if opcode == 18:
                lk = w & 1
                aa = w & 2
                li = (w & 0x03fffffc)
                if li & 0x02000000:
                    li -= 0x04000000
                cur_va = vaddr + pos
                dest = cur_va + li if aa == 0 else li
                if dest == target:
                    branches.append((cur_va, lk))
    return branches

print("=== Callers of 0x12cc98 (hdd_cache_flush) ===")
for va, lk in find_branches_to(0x12cc98):
    print(f"Branch at 0x{va:x} (lk={lk})")

# Also search for pointers to 0x12cc98
target_bytes = struct.pack('>Q', 0x12cc98)
for vaddr, off, sz in segs:
    seg_bytes = data[off:off+sz]
    idx = 0
    while True:
        idx = seg_bytes.find(target_bytes, idx)
        if idx == -1: break
        print(f"Pointer at 0x{vaddr + idx:x}")
        idx += 8

