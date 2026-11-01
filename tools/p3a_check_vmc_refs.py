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

for name, target in [("0x300bc1 /savedata/vmc/", 0x300bc1), ("0x300c5c %s%s.VM2", 0x300c5c)]:
    print(f"=== Pointers to {name} ===")
    for ptr in find_pointers_to(target):
        print(f"Pointer at 0x{ptr:x}")
        # If in TOC, print TOC offset
        toc = 0x751280
        if 0x740000 <= ptr <= 0x760000:
            print(f"  TOC offset: {ptr - toc:#x}")
