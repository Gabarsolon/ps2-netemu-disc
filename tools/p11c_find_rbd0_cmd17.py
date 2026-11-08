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

def va_to_off(va):
    for s_va, s_sz, off_s in segs:
        if s_va <= va < s_va + s_sz:
            return off_s + (va - s_va)
    return None

# Search for cmpwi rX, 17 or cmpdi rX, 17 or cmplwi rX, 17
# cmpwi: opcode 11, L=0, ra=X, imm=17 -> 0x2c0X0011
# cmpdi: opcode 11, L=1, ra=X, imm=17 -> 0x2c2X0011
# cmplwi: opcode 10, L=0, ra=X, imm=17 -> 0x280X0011
# cmplwi with 0x11:
print("Scanning for comparison with 0x11 (17) in lv1.elf...")
matches = []
for i in range(0, len(data) - 4, 4):
    w, = struct.unpack_from('>I', data, i)
    op = w >> 26
    imm = w & 0xffff
    if op in [10, 11] and imm == 17:
        va = off_to_va(i)
        if va:
            matches.append((va, i, hex(w)))

print(f"Found {len(matches)} comparisons with 17 in lv1.elf")
for va, off, w_hex in matches:
    # check if near storage/rbd0 code (e.g. va between 0x200000 and 0x500000)
    # let's print context
    print(f"VA 0x{va:x} (off 0x{off:x}): {w_hex}")
