import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

lv1 = Path('local_only/fw493/lv1.elf')
data = lv1.read_bytes()

with open(lv1, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def off_to_va(off):
    for s_va, s_sz, s_off in segs:
        if s_off <= off < s_off + s_sz:
            return s_va + (off - s_off)
    return None

def va_to_off(va):
    for s_va, s_sz, s_off in segs:
        if s_va <= va < s_va + s_sz:
            return s_off + (va - s_va)
    return None

print("Scanning for lis r2, ... / addis r2, ...")
for off in range(0, len(data) - 4, 4):
    w, = struct.unpack_from('>I', data, off)
    op = w >> 26
    rd = (w >> 21) & 0x1f
    if rd == 2 and op == 15: # lis / addis r2, imm
        ra = (w >> 16) & 0x1f
        imm = w & 0xffff
        va = off_to_va(off)
        if va:
            # check next instruction
            w2, = struct.unpack_from('>I', data, off + 4)
            print(f"VA 0x{va:x}: lis r2, 0x{imm:x} (next: 0x{w2:08x})")
