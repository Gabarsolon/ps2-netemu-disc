import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
stock_elf = ROOT / 'local_only' / 'stock.elf'

with open(stock_elf, 'rb') as f:
    elf_data = f.read()

e_phoff = struct.unpack_from('>Q', elf_data, 0x20)[0]
e_phnum = struct.unpack_from('>H', elf_data, 0x38)[0]
e_phentsize = struct.unpack_from('>H', elf_data, 0x36)[0]

segments = []
for i in range(e_phnum):
    ph = elf_data[e_phoff + i*e_phentsize : e_phoff + (i+1)*e_phentsize]
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack('>IIQQQQQQ', ph)
    if p_type == 1:
        segments.append((p_vaddr, p_offset, p_filesz))

def read_u64(va):
    for vaddr, offset, filesz in segments:
        if vaddr <= va < vaddr + filesz - 8:
            return struct.unpack_from('>Q', elf_data, offset + (va - vaddr))[0]
    return None

ptr = read_u64(0x749430)
print(f"0x749430 (-0x7e50): 0x{ptr:016x}")
