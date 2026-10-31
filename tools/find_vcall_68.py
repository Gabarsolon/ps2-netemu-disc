from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
code = elf[0x10000:0x10000 + 0x3f6c8]

print("=== Searching for calls to virtual method +0x68 ===")
for i in range(0, len(code), 4):
    w = struct.unpack_from('>I', code, i)[0]
    op = w >> 26
    rD = (w >> 21) & 0x1f
    rA = (w >> 16) & 0x1f
    if op == 58: # ld
        ds = w & 0xfffc
        if ds == 0x68:
            va = 0x80000000 + i
            print(f"  va {hex(va)}: ld r{rD}, 0x68(r{rA})")
