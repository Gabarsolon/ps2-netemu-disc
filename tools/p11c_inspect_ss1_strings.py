import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

ss1_elf = Path('local_only/analysis/p0i/modules/ss_server1.elf')
data = ss1_elf.read_bytes()

with open(ss1_elf, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def va_to_off(va):
    for s_va, s_sz, s_off in segs:
        if s_va <= va < s_va + s_sz:
            return s_off + (va - s_va)
    return None

def read_str_at_ptr(va):
    off = va_to_off(va)
    if off is None:
        return None
    ptr, = struct.unpack_from('>Q', data, off)
    ptr_off = va_to_off(ptr)
    if ptr_off is None:
        return f"ptr=0x{ptr:x} (bad off)"
    end = data.find(b'\x00', ptr_off)
    return data[ptr_off:end].decode('latin1', errors='replace')

print("String at c000e378:", read_str_at_ptr(0xc000e378))
print("String at c000e380:", read_str_at_ptr(0xc000e380))
print("String at c000e388:", read_str_at_ptr(0xc000e388))
print("String at c000e4b8:", read_str_at_ptr(0xc000e4b8))
print("String at c000e2e0:", read_str_at_ptr(0xc000e2e0))
print("String at c000e428:", read_str_at_ptr(0xc000e428))
print("String at c000e4b0:", read_str_at_ptr(0xc000e4b0))
