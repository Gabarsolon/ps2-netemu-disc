from disasm_ss1_20638 import data
import struct

toc = 0xC000B000  # wait, what was ss_server1's TOC?
# Let's find r2 from ss_server1 headers or functions
# In ppc64 elf, opd entries have [func_va, toc_va, env]
# Let's inspect OPD section of ss_server1.elf

off, = struct.unpack_from(">Q", data, 0x20)
n, = struct.unpack_from(">H", data, 0x38)
phdrs = [struct.unpack_from(">IIQQQQQQ", data, off + i*0x38) for i in range(n)]

def va_to_off(va):
    for p in phdrs:
        if p[0] == 1 and p[3] <= va < p[3] + p[5]:
            return p[2] + va - p[3]
    return None

# Find TOC from opd
# Look for 0x80020638 in file
for i in range(0, len(data)-16, 8):
    va, = struct.unpack_from(">Q", data, i)
    if va == 0x80020638:
        toc_va, = struct.unpack_from(">Q", data, i+8)
        print(f"Found OPD at file offset 0x{i:x}: func=0x{va:x}, TOC=0x{toc_va:x}")
        break
