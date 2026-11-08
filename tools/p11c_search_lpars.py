import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

sysmgr = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
data = sysmgr.read_bytes()

with open(sysmgr, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def off_to_va(off):
    for s_va, s_sz, s_off in segs:
        if s_off <= off < s_off + s_sz:
            return s_va + (off - s_off)
    return None

def find_str_ptrs(s):
    needle = s.encode() if isinstance(s, str) else s
    idx = 0
    while True:
        idx = data.find(needle, idx)
        if idx == -1:
            break
        va = off_to_va(idx)
        print(f"Found '{s}' at off 0x{idx:x}, VA 0x{va:x}")
        # Search for 64-bit pointers to va
        for o in range(0, len(data) - 8, 4):
            w64, = struct.unpack_from('>Q', data, o)
            if w64 == va:
                print(f"  64-bit ptr to '{s}' at off 0x{o:x}, VA 0x{off_to_va(o):x}")
        idx += len(needle)

find_str_ptrs('PS2_SW_LPAR')
find_str_ptrs('PS2_NE_LPAR')
find_str_ptrs('PS2_HW_LPAR')
find_str_ptrs('PS2_GX_LPAR')
