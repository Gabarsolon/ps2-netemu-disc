from pathlib import Path
import struct

lv1_data = Path('local_only/fw493/lv1.elf').read_bytes()

# Find PT_LOAD segments of lv1.elf
e_phoff = struct.unpack_from('>Q', lv1_data, 0x20)[0]
e_phnum = struct.unpack_from('>H', lv1_data, 0x38)[0]

phdrs = []
for i in range(e_phnum):
    off = e_phoff + i * 56
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', lv1_data, off)
    if p_type == 1:
        phdrs.append((p_vaddr, p_filesz, p_offset))

def va2off(va):
    for vaddr, filesz, offset in phdrs:
        if vaddr <= va < vaddr + filesz:
            return offset + (va - vaddr)
    return None

# Hypercall table in LV1:
# In LV1, the table of function pointers for hypercalls is indexed by hypercall number (0..255 or 0..384)
# Let's search for HV 170 (storage_open), HV 174, etc.
# In earlier tasks, HV 248 was at 0x3094E4.
# Let's check table entry at 0x309000 + num * 8:
# 248 * 8 = 1984 = 0x7C0. 0x3094E4 - 0x7C0 = 0x308D24?
# Let's search for 0x00000000003094E4 in lv1:
pat = struct.pack('>Q', 0x3094E4)
pos = lv1_data.find(pat)
print(f'0x3094E4 found at offset {hex(pos)}')
if pos != -1:
    # Table base:
    # HV 248 is at pos.
    table_base_file = pos - 248 * 8
    print(f'Hypercall table base at file offset {hex(table_base_file)}')
    for hcall in [162, 163, 164, 165]:
        entry_off = table_base_file + hcall * 8
        func_va = struct.unpack_from('>Q', lv1_data, entry_off)[0]
        print(f'HV {hcall}: VA {hex(func_va)}')
