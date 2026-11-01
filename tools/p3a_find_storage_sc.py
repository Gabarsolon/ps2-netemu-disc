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

def va_to_off(va):
    for vaddr, off, sz in segs:
        if vaddr <= va < vaddr + sz:
            return off + (va - vaddr)
    return None

print("=== Searching for LV1 storage write (246 / 0xf6) ===")
# li r11, 246 is 0x396000f6 or 0x396b00f6 or similar
# also search for 0x44000002 (sc 0) and check r11
for vaddr, off, sz in segs:
    seg_bytes = data[off:off+sz]
    for pos in range(0, sz - 3, 4):
        w = struct.unpack_from('>I', seg_bytes, pos)[0]
        if w == 0x396000f6: # li r11, 246
            cur_va = vaddr + pos
            print(f"li r11, 246 at 0x{cur_va:x}")

print("\n=== Searching for LV1 storage read (245 / 0xf5) ===")
for vaddr, off, sz in segs:
    seg_bytes = data[off:off+sz]
    for pos in range(0, sz - 3, 4):
        w = struct.unpack_from('>I', seg_bytes, pos)[0]
        if w == 0x396000f5: # li r11, 245
            cur_va = vaddr + pos
            print(f"li r11, 245 at 0x{cur_va:x}")

