import struct
from pathlib import Path

# Simple PPC64 disassembler helper for control flow and instructions
def decode_ppc(w, pc):
    op = w >> 26
    rD = (w >> 21) & 0x1f
    rA = (w >> 16) & 0x1f
    rB = (w >> 11) & 0x1f
    imm16 = w & 0xffff
    simm16 = imm16 if imm16 < 0x8000 else imm16 - 0x10000

    if op == 18: # B, BL, BA, BLA
        aa = (w >> 1) & 1
        lk = w & 1
        li = (w & 0x03fffffc)
        if li >= 0x02000000: li -= 0x04000000
        target = (pc + li) if not aa else li
        m = "bl" if lk else "b"
        return f"{m:<8} {hex(target)}"
    elif op == 16: # BC
        bo = (w >> 21) & 0x1f
        bi = (w >> 16) & 0x1f
        bd = (w & 0xfffc)
        if bd >= 0x8000: bd -= 0x10000
        target = pc + bd
        lk = w & 1
        return f"bc{'l' if lk else ''}     bo={bo}, bi={bi}, {hex(target)}"
    elif op == 14: # ADDI
        return f"addi     r{rD}, r{rA}, {simm16}"
    elif op == 15: # ADDIS
        return f"addis    r{rD}, r{rA}, {simm16}"
    elif op == 10: # CMPLI
        return f"cmpli    cr{(rD>>2)&7}, {rD&1}, r{rA}, {imm16}"
    elif op == 11: # CMPI
        return f"cmpi     cr{(rD>>2)&7}, {rD&1}, r{rA}, {simm16}"
    elif op == 32: return f"lwz      r{rD}, {simm16}(r{rA})"
    elif op == 34: return f"lbz      r{rD}, {simm16}(r{rA})"
    elif op == 36: return f"stw      r{rD}, {simm16}(r{rA})"
    elif op == 38: return f"stb      r{rD}, {simm16}(r{rA})"
    elif op == 40: return f"lhz      r{rD}, {simm16}(r{rA})"
    elif op == 44: return f"sth      r{rD}, {simm16}(r{rA})"
    elif op == 58: # LD, LDU, LWA
        xo = w & 3
        if xo == 0: return f"ld       r{rD}, {simm16 & ~3}(r{rA})"
        elif xo == 1: return f"ldu      r{rD}, {simm16 & ~3}(r{rA})"
        elif xo == 2: return f"lwa      r{rD}, {simm16 & ~3}(r{rA})"
    elif op == 62: # STD, STDU
        xo = w & 3
        if xo == 0: return f"std      r{rD}, {simm16 & ~3}(r{rA})"
        elif xo == 1: return f"stdu     r{rD}, {simm16 & ~3}(r{rA})"
    elif op == 19: # BCLR, BCCTR, etc.
        xo = (w >> 1) & 0x3ff
        if xo == 16:
            return "blr" if (rD == 20 and rA == 0) else f"bclr     {rD}, {rA}"
        elif xo == 528:
            return "bctr" if (rD == 20 and rA == 0) else f"bcctr    {rD}, {rA}"
    elif op == 31: # Extended
        xo = (w >> 1) & 0x3ff
        if xo == 266: return f"add      r{rD}, r{rA}, r{rB}"
        elif xo == 40: return f"subf     r{rD}, r{rA}, r{rB}"
        elif xo == 444: return f"mr       r{rA}, r{rD}"
        elif xo == 28: return f"and      r{rA}, r{rD}, r{rB}"
        elif xo == 442: return f"or       r{rA}, r{rD}, r{rB}"
        elif xo == 0: return f"cmp      cr{(rD>>2)&7}, {rD&1}, r{rA}, r{rB}"
        elif xo == 32: return f"cmpl     cr{(rD>>2)&7}, {rD&1}, r{rA}, r{rB}"
        elif xo == 83: return f"mfmsr    r{rD}"
        elif xo == 146: return f"mtmsrd   r{rD}"
        elif xo == 339: return f"mfspr    r{rD}, {((rB<<5)|rA)}"
        elif xo == 467: return f"mtspr    {((rB<<5)|rA)}, r{rD}"
        elif xo == 21: return f"ldx      r{rD}, r{rA}, r{rB}"
        elif xo == 149: return f"stdx     r{rD}, r{rA}, r{rB}"
        return f"op31_{xo}  r{rD}, r{rA}, r{rB}"
    return f"word_{op} (0x{w:08x})"

def disasm_func(elf_path, start_va, num_ins=120):
    data = Path(elf_path).read_bytes()
    def va2off(va): return va - 0x200000 + 0x20000
    off = va2off(start_va)
    print(f"\nDisassembly of {hex(start_va)} ({elf_path}):")
    for i in range(num_ins):
        pc = start_va + i * 4
        w = struct.unpack_from('>I', data, off + i * 4)[0]
        ins_str = decode_ppc(w, pc)
        print(f"  {hex(pc)}:  {w:08x}  {ins_str}")

if __name__ == '__main__':
    print("3.55 LV1 lv1_gpu_context_attribute (0x20d010):")
    disasm_func('local_only/fw355/out/lv1.elf', 0x20d010, 80)
