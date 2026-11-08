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

p1 = 0x409E00702FBE0001
p2 = 0x38800002409C0014

print("Searching lv1.elf for patterns...")
for o in range(0, len(data) - 8, 4):
    v64, = struct.unpack_from('>Q', data, o)
    if v64 == p1:
        print(f"Pattern 1 (auth) found at file off 0x{o:x}, VA 0x{off_to_va(o):x}")
    if v64 == p2:
        print(f"Pattern 2 (unauth) found at file off 0x{o:x}, VA 0x{off_to_va(o):x}")
