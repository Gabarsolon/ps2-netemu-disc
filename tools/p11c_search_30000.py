import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

lv1 = Path('local_only/fw493/lv1.elf')
data = lv1.read_bytes()

with open(lv1, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def off_to_va(off):
    for s_va, s_sz, off_s in segs:
        if off_s <= off < off_s + s_sz:
            return s_va + (off - off_s)
    return None

print("Searching for 0x30000 in lv1.elf...")
# Look for lis rX, 3 (0x3c...0003) or 64-bit 0x30000
for i in range(0, len(data) - 8, 4):
    v64, = struct.unpack_from('>Q', data, i)
    if v64 == 0x30000:
        print(f"64-bit 0x30000 at file off 0x{i:x}, VA 0x{off_to_va(i):x}")
    v32, = struct.unpack_from('>I', data, i)
    if v32 == 0x30000:
        print(f"32-bit 0x30000 at file off 0x{i:x}, VA 0x{off_to_va(i):x}")
