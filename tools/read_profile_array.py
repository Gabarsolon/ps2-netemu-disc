from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
toc = 0xc0012f40
disp = -29208 # 0x8de8

va = toc + disp
off = va - 0xc0000000 + 0x50000
array_ptr = struct.unpack_from('>Q', elf, off)[0]
print(f"Profile array pointer at TOC - 29208: {hex(array_ptr)}")

# array_ptr is in sysmgr_ss address space
def ptr_to_off(p):
    if 0x80000000 <= p < 0x80040000:
        return p - 0x80000000 + 0x10000
    if 0xc0000000 <= p < 0xc0010000:
        return p - 0xc0000000 + 0x50000
    return None

a_off = ptr_to_off(array_ptr)
print(f"Profile array file offset: {hex(a_off) if a_off else 'None'}")

if a_off:
    for i in range(5):
        elem = struct.unpack_from('>Q', elf, a_off + i * 8)[0]
        e_off = ptr_to_off(elem)
        print(f"  profile_array[{i}]: {hex(elem)} (off: {hex(e_off) if e_off else 'None'})")
        # inspect object at elem
        if e_off:
            # vtable is first 8 bytes
            vtable = struct.unpack_from('>Q', elf, e_off)[0]
            print(f"    vtable: {hex(vtable)}")
