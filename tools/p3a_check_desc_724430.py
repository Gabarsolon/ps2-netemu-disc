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

def find_pointers_to(target):
    target_bytes = struct.pack('>Q', target)
    ptrs = []
    for vaddr, off, sz in segs:
        seg_bytes = data[off:off+sz]
        idx = 0
        while True:
            idx = seg_bytes.find(target_bytes, idx)
            if idx == -1: break
            ptrs.append(vaddr + idx)
            idx += 8
    return ptrs

print("=== Pointers to 0x724430 (descriptor of 0x12cc98) ===")
for ptr in find_pointers_to(0x724430):
    print(f"Pointer at 0x{ptr:x}")

# Also check surrounding descriptors around 0x724400..0x724460
def read_u64(va):
    for vaddr, off, sz in segs:
        if vaddr <= va <= vaddr + sz - 8:
            return struct.unpack_from('>Q', data, off + (va - vaddr))[0]
    return None

print("\n=== Descriptors around 0x724400..0x724460 ===")
for va in range(0x724400, 0x724460, 16):
    func = read_u64(va)
    toc = read_u64(va + 8)
    print(f"0x{va:06x}: func=0x{func:06x}, toc=0x{toc:06x}")

