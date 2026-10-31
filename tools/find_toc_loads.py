from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
code = elf[0x10000:0x10000 + 0x3f6c8]
toc = 0xc0012f40

targets = {
    -0x7018: 'PS3_LPAR (0xc000bf28)',
    -0x7008: 'PS2_LPAR (0xc000bf38)',
    -0x7000: 'SCE_CELLOS_SYSTEM_MGR_PS2 (0xc000bf40)',
    -0x6ff8: 'SCE_CELLOS_SYSTEM_MGR_PS2_GX (0xc000bf48)',
    -0x6ff0: 'SCE_CELLOS_SYSTEM_MGR_PS2_SW (0xc000bf50)',
    -0x6fe8: 'SCE_CELLOS_SYSTEM_MGR_PS2_NE (0xc000bf58)',
    -0x6fc8: 'PS2_GX_LPAR (0xc000bf78)',
    -0x6fc0: 'PS2_SW_LPAR (0xc000bf80)',
    -0x6fb8: 'PS2_NE_LPAR (0xc000bf88)',
}

print("=== Scanning code for TOC loads ===")
for i in range(0, len(code), 4):
    w = struct.unpack_from('>I', code, i)[0]
    op = w >> 26
    rD = (w >> 21) & 0x1f
    rA = (w >> 16) & 0x1f
    d = w & 0xffff
    if d >= 0x8000:
        d_signed = d - 0x10000
    else:
        d_signed = d

    # ld is op 58, ds = d & ~3, xo = d & 3 (xo=0 for ld)
    if op == 58 and (w & 3) == 0 and rA == 2:
        ds = (w & 0xfffc)
        if ds >= 0x8000:
            ds_signed = ds - 0x10000
        else:
            ds_signed = ds
        if ds_signed in targets:
            va = 0x80000000 + i
            print(f"  va {hex(va)}: ld r{rD}, {ds_signed}(r2) -> {targets[ds_signed]}")
    # addi is op 14, addi rD, r2, d
    elif op == 14 and rA == 2:
        if d_signed in targets:
            va = 0x80000000 + i
            print(f"  va {hex(va)}: addi r{rD}, r2, {d_signed} -> {targets[d_signed]}")
