import struct
from pathlib import Path

elf = Path('local_only/analysis/p0i/modules/ss_server1.elf').read_bytes()

def get_rodata_str(ea):
    off = ea - 0x80000000 + 0x10000
    if 0 <= off < len(elf):
        s = elf[off:off+80].split(b'\0')[0]
        return s.decode('ascii', errors='replace')
    return ''

def get_toc_ptr(ea):
    off = ea - 0xC0000000 + 0x70000
    if 0 <= off <= len(elf) - 8:
        return struct.unpack('>Q', elf[off:off+8])[0]
    return 0

for toc_ea in [0xc000e368, 0xc000e370, 0xc000e378, 0xc000e380, 0xc000e388, 0xc000e390, 0xc000e398, 0xc000e3a0, 0xc000e3a8, 0xc000e4b0, 0xc000e2e0, 0xc000e428, 0xc000e2f8]:
    ptr = get_toc_ptr(toc_ea)
    s = get_rodata_str(ptr)
    print(f"TOC 0x{toc_ea:08X} -> 0x{ptr:08X}: '{s}'")
