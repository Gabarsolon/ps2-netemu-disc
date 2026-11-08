import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
base = 0x210000

# Search for OPD pointing to 0x50f538
target = 0x50f538
for o in range(0, len(data) - 16, 8):
    func, toc = struct.unpack_from('>2Q', data, o)
    if func == target:
        print(f"OPD at VA 0x{o+base:x}: func = 0x{func:x}, TOC = 0x{toc:x}")
        # print what is at TOC - 0x6640 and TOC - 0x6638
        toc_off = toc - base
        v1, = struct.unpack_from('>Q', data, toc_off - 0x6640)
        v2, = struct.unpack_from('>Q', data, toc_off - 0x6638)
        print(f"  TOC - 0x6640: 0x{v1:x}")
        print(f"  TOC - 0x6638: 0x{v2:x}")
        # let's read vtable at v1
        v1_off = v1 - base
        for i in range(0, 8 * 8, 8):
            m, = struct.unpack_from('>Q', data, v1_off + i)
            print(f"    vtable +0x{i:02x}: 0x{m:x}")
