import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

ss3 = Path('local_only/analysis/p0i/modules/ss_server3.elf')
data = ss3.read_bytes()

with open(ss3, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def off_to_va(off):
    for s_va, s_sz, s_off in segs:
        if s_off <= off < s_off + s_sz:
            return s_va + (off - s_off)
    return None

off = 0x10b44
va = off_to_va(off)
print(f"ss_server3.elf: off 0x{off:x}, VA 0x{va:x}")

for o in range(off - 32, off + 48, 4):
    w, = struct.unpack_from('>I', data, o)
    print(f"  off 0x{o:x} (VA 0x{off_to_va(o):x}): 0x{w:08x}")
