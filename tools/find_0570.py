from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
toc = 0xc0012f40

target = 0xc0000570
target_bytes = struct.pack('>Q', target)

# Search for 64-bit pointer in data
p = 0
while True:
    idx = elf.find(target_bytes, p)
    if idx == -1: break
    va = idx - 0x50000 + 0xc0000000 if idx >= 0x50000 else idx - 0x10000 + 0x80000000
    disp = va - toc
    print(f"Found pointer to 0xc0000570 at va {hex(va)} (TOC disp: {disp})")
    p = idx + 1
