import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

sysmgr = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
data = sysmgr.read_bytes()

with open(sysmgr, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def va_to_off(va):
    for s_va, s_sz, s_off in segs:
        if s_va <= va < s_va + s_sz:
            return s_off + (va - s_va)
    return None

def off_to_va(off):
    for s_va, s_sz, s_off in segs:
        if s_off <= off < s_off + s_sz:
            return s_va + (off - s_off)
    return None

def dump_struct(va, num_words):
    off = va_to_off(va)
    print(f"=== Dump at VA 0x{va:x} (file off 0x{off:x}) ===")
    for i in range(0, num_words * 8, 8):
        w64, = struct.unpack_from('>Q', data, off + i)
        print(f"  0x{va+i:x}: 0x{w64:016x}")

dump_struct(0xc000b050, 16)
dump_struct(0xc000bf60, 16)
