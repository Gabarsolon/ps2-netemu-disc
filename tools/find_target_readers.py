from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
code = elf[0x10000:0x10000 + 0x3f6c8]
targets = {-30120: 'TOC disp -30120 (0xc000b998)', -29712: 'TOC disp -29712 (0xc000bb30)'}

for i in range(0, len(code), 4):
    w = struct.unpack_from('>I', code, i)[0]
    op = w >> 26
    rD = (w >> 21) & 0x1f
    rA = (w >> 16) & 0x1f
    if rA == 2 and op in (58, 62):
        ds = w & 0xfffc
        if ds >= 0x8000: ds -= 0x10000
        if ds in targets:
            va = 0x80000000 + i
            mnemonic = "ld" if op == 58 else "std"
            print(f"  va {hex(va)}: {mnemonic} r{rD}, {ds}(r2) -> {targets[ds]}")
