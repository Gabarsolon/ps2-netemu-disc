import os, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
stock_elf = ROOT / 'local_only' / 'stock.elf'

with open(stock_elf, 'rb') as f:
    elf_data = f.read()

# In 64-bit ELF, find PT_LOAD containing 0x12b5fc
# Or look at ELF header
e_phoff = struct.unpack_from('>Q', elf_data, 0x20)[0]
e_phnum = struct.unpack_from('>H', elf_data, 0x38)[0]
e_phentsize = struct.unpack_from('>H', elf_data, 0x36)[0]

segments = []
for i in range(e_phnum):
    ph = elf_data[e_phoff + i*e_phentsize : e_phoff + (i+1)*e_phentsize]
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack('>IIQQQQQQ', ph)
    if p_type == 1: # PT_LOAD
        segments.append((p_vaddr, p_offset, p_filesz))

def va_to_offset(va):
    for vaddr, offset, filesz in segments:
        if vaddr <= va < vaddr + filesz:
            return offset + (va - vaddr)
    return None

def offset_to_va(off):
    for vaddr, offset, filesz in segments:
        if offset <= off < offset + filesz:
            return vaddr + (off - offset)
    return None

target_va = 0x12b5fc

# Search all text for 'bl target_va'
# In PPC: 'bl offset': opcode 18 (0x48000001)
# bits 6..29 are (LI << 2), signed 24-bit immediate
for vaddr, offset, filesz in segments:
    seg_bytes = elf_data[offset : offset + filesz]
    for i in range(0, filesz - 4, 4):
        w = struct.unpack_from('>I', seg_bytes, i)[0]
        if (w & 0xFC000003) == 0x48000001: # bl
            li = w & 0x03FFFFFC
            if li & 0x02000000: # sign extend
                li -= 0x04000000
            curr_va = vaddr + i
            if curr_va + li == target_va:
                print(f"bl to 0x{target_va:x} at VA 0x{curr_va:06x}")
