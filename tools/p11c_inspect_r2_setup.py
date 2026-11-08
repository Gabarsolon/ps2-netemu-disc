import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

lv1 = Path('local_only/fw493/lv1.elf')
data = lv1.read_bytes()

with open(lv1, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def va_to_off(va):
    for s_va, s_sz, s_off in segs:
        if s_va <= va < s_va + s_sz:
            return s_off + (va - s_va)
    return None

def print_disasm(va, n):
    off = va_to_off(va)
    print(f"=== VA 0x{va:x} ===")
    for i in range(0, n*4, 4):
        w, = struct.unpack_from('>I', data, off + i)
        print(f"  0x{va+i:x}: 0x{w:08x}")

print_disasm(0xfa0, 8)
print_disasm(0x3af070, 8)
