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

# find callers of 0x270ffc
print("=== Callers of 0x270FFC ===")
for va, lk in find_branches_to(0x270ffc):
    print(f"Branch at 0x{va:x} (lk={lk})")

# find callers of 0x270c24
print("\n=== Callers of 0x270C24 ===")
for va, lk in find_branches_to(0x270c24):
    print(f"Branch at 0x{va:x} (lk={lk})")

# Also let's see what function 0x270c24 is in
def find_prologue(va):
    for vaddr, off, sz in segs:
        if vaddr <= va < vaddr + sz:
            cur = va
            while cur > va - 0x2000:
                w = struct.unpack_from('>I', data, off + (cur - vaddr))[0]
                if (w & 0xffff0000) == 0xf8210000 or (w & 0xffff0003) == 0xf8210001:
                    return cur
                cur -= 4
    return None

p_c24 = find_prologue(0x270c24)
p_ffc = find_prologue(0x270ffc)
print(f"Prologue of 0x270c24: 0x{p_c24:x}")
print(f"Prologue of 0x270ffc: 0x{p_ffc:x}")
