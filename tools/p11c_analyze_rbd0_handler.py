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

def va_to_off(va):
    for s_va, s_sz, s_off in segs:
        if s_va <= va < s_va + s_sz:
            return s_off + (va - s_va)
    return None

# Search for the string "/dev/rbd0" at 0x8003c038
# Where is 0x8003c038 referenced in .data / tables?
for i in range(0, len(data) - 8, 4):
    v64, = struct.unpack_from('>Q', data, i)
    if v64 == 0x8003c038:
        print(f"64-bit reference to '/dev/rbd0' at file offset 0x{i:x}, VA 0x{off_to_va(i):x}")
        # print surrounding structure
        start = max(0, i - 32)
        end = min(len(data), i + 64)
        for j in range(start, end, 8):
            val, = struct.unpack_from('>Q', data, j)
            print(f"  0x{off_to_va(j):x}: 0x{val:016x}")
