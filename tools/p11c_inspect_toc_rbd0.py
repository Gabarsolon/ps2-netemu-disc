import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

lv1 = Path('local_only/fw493/lv1.elf')
data = lv1.read_bytes()

with open(lv1, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def va_to_off(va):
    for s_va, s_sz, s_off in segs:
        if s_va <= va < s_va + s_sz:
            return s_off + (va - s_va)
    return None

off = va_to_off(0x3539f8)
v1, v2 = struct.unpack_from('>2Q', data, off)
print(f"At VA 0x3539f8 (TOC - 0x6640): 0x{v1:x}")
print(f"At VA 0x353a00 (TOC - 0x6638): 0x{v2:x}")

# Let's inspect string or data at v2:
off_v2 = va_to_off(v2)
print("Data at v2:", repr(data[off_v2:off_v2+32]))

# Let's inspect vtable at v1:
off_v1 = va_to_off(v1)
print(f"Vtable at 0x{v1:x}:")
for i in range(0, 8 * 8, 8):
    m, = struct.unpack_from('>Q', data, off_v1 + i)
    print(f"  +0x{i:02x}: 0x{m:x}")
