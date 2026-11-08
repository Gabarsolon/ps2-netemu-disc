from pathlib import Path
import struct
import re

data = Path('local_only/stock.elf').read_bytes()

# Find ELF program headers for stock.elf
e_phoff = struct.unpack_from('>Q', data, 0x20)[0]
e_phentsize = struct.unpack_from('>H', data, 0x36)[0]
e_phnum = struct.unpack_from('>H', data, 0x38)[0]
segments = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, off)
    if p_type == 1:
        segments.append((p_offset, p_filesz, p_vaddr, p_memsz))
        print(f"Seg: off {hex(p_offset)}..{hex(p_offset+p_filesz)} -> VA {hex(p_vaddr)}")

def off2va(off):
    for p_offset, p_filesz, p_vaddr, p_memsz in segments:
        if p_offset <= off < p_offset + p_filesz:
            return p_vaddr + (off - p_offset)
    return None

str_va = off2va(0x314b10)
print(f"String 'Video Mode  : %08x' is at VA {hex(str_va)}")

# Search for references to str_va (or lis/addi, or 64-bit ptr)
p64 = struct.pack('>Q', str_va)
p32 = struct.pack('>I', str_va & 0xffffffff)

for p, size in [(p64, 8), (p32, 4)]:
    pos = 0
    while True:
        pos = data.find(p, pos)
        if pos == -1: break
        print(f"  found {size*8}-bit ptr at off {hex(pos)} (VA {hex(off2va(pos))})")
        pos += 1

# Check lis/addi in code segments
hi = (str_va >> 16) & 0xffff
lo = str_va & 0xffff
if lo >= 0x8000: hi += 1
for i in range(0, len(data) - 8, 4):
    w1 = struct.unpack_from('>I', data, i)[0]
    if (w1 >> 26) == 15 and (w1 & 0xffff) == (hi & 0xffff):
        rD = (w1 >> 21) & 0x1f
        w2 = struct.unpack_from('>I', data, i + 4)[0]
        if (w2 >> 26) == 14 and ((w2 >> 16) & 0x1f) == rD and (w2 & 0xffff) == lo:
            print(f"  lis/addi at off {hex(i)} (VA {hex(off2va(i))})")
