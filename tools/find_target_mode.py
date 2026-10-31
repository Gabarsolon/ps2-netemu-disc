from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
code = elf[0x10000:0x10000 + 0x3f6c8]
toc = 0xc0012f40
disp = -29264 # 0x8db0

print(f"Target mode variable at TOC offset {disp} ({hex(disp & 0xffff)})")

# Let's find all ld/std from r2 at disp
for i in range(0, len(code), 4):
    w = struct.unpack_from('>I', code, i)[0]
    op = w >> 26
    rD = (w >> 21) & 0x1f
    rA = (w >> 16) & 0x1f
    if rA == 2 and (op in (58, 62)):
        ds = w & 0xfffc
        if ds >= 0x8000: ds -= 0x10000
        if ds == disp:
            va = 0x80000000 + i
            mnemonic = "ld" if op == 58 else "std"
            print(f"  va {hex(va)}: {mnemonic} r{rD}, {ds}(r2)")
