from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()
code = elf[0x20000:0x20000 + 0x1c2c00]

# Search for references to 0x3544d0 .. 0x354550
# By lis/addi or TOC displacement if in TOC
# Check TOC displacements:
toc = 0x36bc90
for target in [0x3544e8, 0x354508, 0x354510, 0x3544d0]:
    disp = target - toc
    print(f"Target {hex(target)}: TOC disp {disp}")
    hi = (target >> 16) & 0xffff
    lo = target & 0xffff
    if lo >= 0x8000: hi += 1
    for i in range(0, len(code) - 8, 4):
        w1 = struct.unpack_from('>I', code, i)[0]
        # lis rD, hi
        if (w1 >> 26) == 15 and ((w1 >> 16) & 0x1f) == 0 and (w1 & 0xffff) == (hi & 0xffff):
            rD = (w1 >> 21) & 0x1f
            w2 = struct.unpack_from('>I', code, i + 4)[0]
            if (w2 >> 26) == 14 and ((w2 >> 16) & 0x1f) == rD and (w2 & 0xffff) == lo:
                va = 0x200000 + i
                print(f"  lis/addi at va {hex(va)} -> r{rD}")
        # ld rD, disp(r2)
        op = w1 >> 26
        rA = (w1 >> 16) & 0x1f
        if rA == 2 and op == 58:
            ds = w1 & 0xfffc
            if ds >= 0x8000: ds -= 0x10000
            if ds == disp:
                va = 0x200000 + i
                print(f"  ld r{(w1 >> 21) & 0x1f}, {disp}(r2) at va {hex(va)}")

# Also search for table base 0x3544e8 in pointer tables or xrefs
for off in range(0x3544d0, 0x354560, 8):
    p64 = struct.pack('>Q', off)
    pos = 0
    while True:
        idx = elf.find(p64, pos)
        if idx == -1: break
        va = idx - 0x20000 + 0x200000
        if va != off:
            print(f"  Pointer to {hex(off)} at va {hex(va)}")
        pos = idx + 1
