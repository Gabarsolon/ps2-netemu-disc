from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()

# File offset to vaddr and vaddr to file offset
def vaddr_to_off(va):
    if 0x80000000 <= va < 0x8003f6c8:
        return va - 0x80000000 + 0x10000
    if 0xc0000000 <= va < 0xc000ce88:
        return va - 0xc0000000 + 0x50000
    return None

def off_to_va(off):
    if 0x10000 <= off < 0x10000 + 0x3f6c8:
        return off - 0x10000 + 0x80000000
    if 0x50000 <= off < 0x50000 + 0xce88:
        return off - 0x50000 + 0xc0000000
    return None

targets = {
    'PS2_NE_LPAR': 0x8003b2b8,
    'SCE_CELLOS_SYSTEM_MGR_PS2_NE': 0x8003b268,
    'sysmgr.boot.ps2netemu.1st': 0x8003b830,
    'PS2_SW_LPAR': 0x80039610,
    'PS2_GX_LPAR': 0x80039600,
    'PS2_LPAR': 0x800395f0,
    'PS3_LPAR': 0x800395e0,
}

for name, va in targets.items():
    print(f"=== Searching for references to {name} ({hex(va)}) ===")
    # 1. Exact 32-bit or 64-bit pointer
    p32 = struct.pack('>I', va)
    p64 = struct.pack('>Q', va)
    idx = 0
    while True:
        pos = elf.find(p32, idx)
        if pos == -1:
            break
        print(f"  Pointer32 at file off {hex(pos)} (va {hex(off_to_va(pos)) if off_to_va(pos) else 'none'})")
        idx = pos + 1
    idx = 0
    while True:
        pos = elf.find(p64, idx)
        if pos == -1:
            break
        print(f"  Pointer64 at file off {hex(pos)} (va {hex(off_to_va(pos)) if off_to_va(pos) else 'none'})")
        idx = pos + 1

    # 2. PPC lis/addi pair
    # lis rD, va >> 16 (or +1 if low >= 0x8000)
    # addi rD, rD, va & 0xffff (as signed)
    hi = (va >> 16) & 0xffff
    lo = va & 0xffff
    if lo >= 0x8000:
        hi += 1
    # Check all instructions in PH0
    code = elf[0x10000:0x10000 + 0x3f6c8]
    for i in range(0, len(code) - 8, 4):
        w1 = struct.unpack_from('>I', code, i)[0]
        # lis is addis rD, 0, hi: op=15, rA=0
        if (w1 >> 26) == 15 and ((w1 >> 16) & 0x1f) == 0 and (w1 & 0xffff) == (hi & 0xffff):
            rD = (w1 >> 21) & 0x1f
            w2 = struct.unpack_from('>I', code, i + 4)[0]
            # addi rD2, rD, lo: op=14
            if (w2 >> 26) == 14 and ((w2 >> 16) & 0x1f) == rD and (w2 & 0xffff) == lo:
                cur_va = 0x80000000 + i
                print(f"  lis/addi pair at va {hex(cur_va)} -> reg r{(w2 >> 21) & 0x1f}")
            # or ori rD2, rD, lo: op=24
            elif (w2 >> 26) == 24 and ((w2 >> 16) & 0x1f) == rD and (w2 & 0xffff) == (va & 0xffff):
                cur_va = 0x80000000 + i
                print(f"  lis/ori pair at va {hex(cur_va)} -> reg r{(w2 >> 21) & 0x1f}")
