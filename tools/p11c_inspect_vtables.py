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

def read_vtable(name, va_ptr):
    off = va_to_off(va_ptr)
    vt_va, = struct.unpack_from('>Q', data, off)
    print(f"=== {name}: Vtable at 0x{vt_va:x} ===")
    vt_off = va_to_off(vt_va)
    for i in range(0, 20 * 8, 8):
        m_va, = struct.unpack_from('>Q', data, vt_off + i)
        print(f"  +0x{i:02x}: 0x{m_va:016x}")

read_vtable('PS2_SW_LPAR (0xc000c048)', 0xc000c048)
read_vtable('PS2_NE_LPAR (0xc000c058)', 0xc000c058)
