from pathlib import Path
import struct
import re

data = Path('local_only/fw355/out/vsh.elf').read_bytes()

# Find string "avset_setvideomode\0"
s_off = data.find(b'avset_setvideomode\x00')
print(f"String 'avset_setvideomode' at file off {hex(s_off)}")

# Parse ELF segments for vsh.elf
e_phoff = struct.unpack_from('>I', data, 0x1c)[0] if data[4] == 1 else struct.unpack_from('>Q', data, 0x20)[0]
is_64 = (data[4] == 2)
print(f"ELF is {'64-bit' if is_64 else '32-bit'}")

# In 32-bit or 64-bit:
# Let's search references to s_off or its VA
# Let's inspect ELF program headers
if is_64:
    e_phentsize = struct.unpack_from('>H', data, 0x36)[0]
    e_phnum = struct.unpack_from('>H', data, 0x38)[0]
    segments = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, off)
        if p_type == 1:
            segments.append((p_offset, p_filesz, p_vaddr, p_memsz))
            print(f"Load seg: {hex(p_offset)}..{hex(p_offset+p_filesz)} -> VA {hex(p_vaddr)}")
else:
    e_phentsize = struct.unpack_from('>H', data, 0x2a)[0]
    e_phnum = struct.unpack_from('>H', data, 0x2c)[0]
    segments = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack_from('>IIIIIIII', data, off)
        if p_type == 1:
            segments.append((p_offset, p_filesz, p_vaddr, p_memsz))
            print(f"Load seg: {hex(p_offset)}..{hex(p_offset+p_filesz)} -> VA {hex(p_vaddr)}")

def off2va(off):
    for p_offset, p_filesz, p_vaddr, p_memsz in segments:
        if p_offset <= off < p_offset + p_filesz:
            return p_vaddr + (off - p_offset)
    return None

def va2off(va):
    for p_offset, p_filesz, p_vaddr, p_memsz in segments:
        if p_vaddr <= va < p_vaddr + p_filesz:
            return p_offset + (va - p_vaddr)
    return None

s_va = off2va(s_off)
print(f"String VA: {hex(s_va) if s_va else 'None'}")
# Find references to s_va
if s_va:
    ptr_bytes = struct.pack('>I' if not is_64 else '>Q', s_va)
    pos = 0
    while True:
        pos = data.find(ptr_bytes, pos)
        if pos == -1: break
        rva = off2va(pos)
        print(f"  Referenced by pointer at file {hex(pos)} (VA {hex(rva) if rva else 'None'})")
        pos += 1
