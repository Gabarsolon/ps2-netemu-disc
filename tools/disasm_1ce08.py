from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
toc = 0xc0012f40

def disasm_func(start_va, count):
    start_off = start_va - 0x80000000 + 0x10000
    for i in range(count):
        va = start_va + i * 4
        w = struct.unpack_from('>I', elf, start_off + i * 4)[0]
        op = w >> 26
        s = f"{hex(va)}: {hex(w):10s} "
        if op == 11: # cmpwi
            cr = (w >> 23) & 7; rA = (w >> 16) & 0x1f; imm = w & 0xffff
            if imm >= 0x8000: imm -= 0x10000
            s += f"cmpwi cr{cr}, r{rA}, {imm}"
        elif op == 14: # addi / li
            rD = (w >> 21) & 0x1f; rA = (w >> 16) & 0x1f; imm = w & 0xffff
            if imm >= 0x8000: imm -= 0x10000
            s += f"li r{rD}, {imm}" if rA == 0 else f"addi r{rD}, r{rA}, {imm}"
        elif op == 16: # bc
            bo = (w >> 21) & 0x1f; bi = (w >> 16) & 0x1f; bd = w & 0xfffc
            if bd >= 0x8000: bd -= 0x10000
            s += f"bc bo={bo}, bi={bi}, {hex(va + bd)}"
        elif op == 18: # b / bl
            li = w & 0x03fffffc
            if li >= 0x02000000: li -= 0x04000000
            s += f"{'bl' if (w & 1) else 'b'} {hex(va + li)}"
        elif op == 19:
            s += "blr" if (w & 0x7fe) == 0x44 else f"op19 {hex(w)}"
        elif op == 58: # ld
            rD = (w >> 21) & 0x1f; rA = (w >> 16) & 0x1f; ds = w & 0xfffc
            if ds >= 0x8000: ds -= 0x10000
            extra = ""
            if rA == 2:
                t_va = toc + ds
                t_off = t_va - 0xc0000000 + 0x50000 if t_va >= 0xc0000000 else t_va - 0x80000000 + 0x10000
                if 0 <= t_off < len(elf) - 8:
                    ptr = struct.unpack_from('>Q', elf, t_off)[0]
                    p_off = ptr - 0xc0000000 + 0x50000 if ptr >= 0xc0000000 else (ptr - 0x80000000 + 0x10000 if ptr >= 0x80000000 else -1)
                    if 0 <= p_off < len(elf):
                        nul = elf.find(b'\0', p_off)
                        if nul != -1 and nul - p_off < 64:
                            try: extra = f" -> \"{elf[p_off:nul].decode('ascii')}\""
                            except: pass
            s += f"ld r{rD}, {ds}(r{rA}){extra}"
        elif op == 62: # std
            rS = (w >> 21) & 0x1f; rA = (w >> 16) & 0x1f; ds = w & 0xfffc
            if ds >= 0x8000: ds -= 0x10000
            s += f"std r{rS}, {ds}(r{rA})"
        else:
            s += f"op={op}"
        print(s)

print("=== 0x8001cdd0 to 0x8001ce60 ===")
disasm_func(0x8001cdd0, 36)
