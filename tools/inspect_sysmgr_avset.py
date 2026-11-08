from pathlib import Path
import struct
import re

data = Path('local_only/analysis/p0h/modules/sysmgr_ss.elf').read_bytes()
matches = [m.start() for m in re.finditer(b'avset', data)]
print(f"sysmgr_ss.elf: 'avset' matches: {len(matches)}")
for m in matches:
    # find string boundaries
    s = m
    while s > 0 and data[s-1] >= 0x20 and data[s-1] <= 0x7e: s -= 1
    e = m
    while e < len(data) and data[e] >= 0x20 and data[e] <= 0x7e: e += 1
    print(f"  off={hex(m)}: \"{data[s:e].decode()}\"")
    # find references to m or the string pointer
    # in 32-bit or 64-bit
    # Let's search references to this offset
    p4 = struct.pack('>I', 0x80000000 + m) # sysmgr is often loaded at 0x80000000
    p8 = struct.pack('>Q', 0x80000000 + m)
    r4 = [r.start() for r in re.finditer(re.escape(p4), data)]
    r8 = [r.start() for r in re.finditer(re.escape(p8), data)]
    print(f"    refs p4={len(r4)}, p8={len(r8)}")
