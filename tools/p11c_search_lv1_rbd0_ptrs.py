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
    for s_va, s_sz, off in segs:
        if s_va <= va < s_va + s_sz:
            return off + (va - s_va)
    return None

# Find pointers to 0x46dd7d (or 0x46dd75..0x46dd85)
target1 = 0x46dd7d # "/dev/rbd0"
target2 = 0x53d6a5 # "/dev/rbd0"

print("Searching for pointers to targets in lv1.elf...")
for i in range(0, len(data) - 8, 4):
    v64, = struct.unpack_from('>Q', data, i)
    if v64 in [target1, target1 - 1, target1 + 1, target2]:
        print(f"Found 64-bit ptr to 0x{v64:x} at file off 0x{i:x}, VA 0x{off_to_va(i):x}")
