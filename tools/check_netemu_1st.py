from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
toc = 0xc0012f40
target_va = 0xc000c188
disp = target_va - toc
print(f"sysmgr.boot.ps2netemu.1st pointer at {hex(target_va)} (TOC disp: {disp})")

# Let's inspect around 0xc000c170 to 0xc000c1a0
off = target_va - 0xc0000000 + 0x50000
for i in range(-16, 24, 8):
    p = off + i
    val = struct.unpack_from('>Q', elf, p)[0]
    # check string
    s = ""
    if 0x80000000 <= val < 0x80040000:
        poff = val - 0x80000000 + 0x10000
        nul = elf.find(b'\0', poff)
        if nul != -1 and nul - poff < 64:
            s = elf[poff:nul].decode('ascii', errors='ignore')
    print(f"  {hex(target_va + i)}: {hex(val)} \"{s}\"")

# Search code for ld rD, disp(r2)
code = elf[0x10000:0x10000 + 0x3f6c8]
for i in range(0, len(code), 4):
    w = struct.unpack_from('>I', code, i)[0]
    op = w >> 26
    rD = (w >> 21) & 0x1f
    rA = (w >> 16) & 0x1f
    if rA == 2 and op in (58, 62):
        ds = w & 0xfffc
        if ds >= 0x8000: ds -= 0x10000
        if ds == disp:
            va = 0x80000000 + i
            print(f"  Code hit at {hex(va)}: op={op} r{rD}, {ds}(r2)")
