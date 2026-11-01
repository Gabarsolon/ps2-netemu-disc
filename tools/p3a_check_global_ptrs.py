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

def read_u64(va):
    for vaddr, off, sz in segs:
        if vaddr <= va <= vaddr + sz - 8:
            return struct.unpack_from('>Q', data, off + (va - vaddr))[0]
    return None

toc = 0x751280
print(f"-0x42f8(r2) at 0x{toc - 0x42f8:x}: 0x{read_u64(toc - 0x42f8):x}")
print(f"-0x42f0(r2) at 0x{toc - 0x42f0:x}: 0x{read_u64(toc - 0x42f0):x}")
print(f"-0x6f58(r2) at 0x{toc - 0x6f58:x}: 0x{read_u64(toc - 0x6f58):x}")
