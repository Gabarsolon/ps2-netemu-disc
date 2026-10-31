from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()

def disasm_func(start_va, count):
    start_off = start_va - 0x80000000 + 0x10000
    for i in range(count):
        va = start_va + i * 4
        w = struct.unpack_from('>I', elf, start_off + i * 4)[0]
        op = w >> 26
        s = f"{hex(va)}: {hex(w):10s} "
        if op == 11: # cmpwi
            cr = (w >> 23) & 7
            rA = (w >> 16) & 0x1f
            imm = w & 0xffff
            if imm >= 0x8000: imm -= 0x10000
            s += f"cmpwi cr{cr}, r{rA}, {imm}"
        elif op == 10: # cmplwi
            cr = (w >> 23) & 7
            rA = (w >> 16) & 0x1f
            imm = w & 0xffff
            s += f"cmplwi cr{cr}, r{rA}, {imm}"
        elif op == 14: # addi / li
            rD = (w >> 21) & 0x1f
            rA = (w >> 16) & 0x1f
            imm = w & 0xffff
            if imm >= 0x8000: imm -= 0x10000
            if rA == 0: s += f"li r{rD}, {imm}"
            else: s += f"addi r{rD}, r{rA}, {imm}"
        elif op == 15: # addis / lis
            rD = (w >> 21) & 0x1f
            rA = (w >> 16) & 0x1f
            imm = w & 0xffff
            if imm >= 0x8000: imm -= 0x10000
            if rA == 0: s += f"lis r{rD}, {imm}"
            else: s += f"addis r{rD}, r{rA}, {imm}"
        elif op == 16: # bc
            bo = (w >> 21) & 0x1f
            bi = (w >> 16) & 0x1f
            bd = w & 0xfffc
            if bd >= 0x8000: bd -= 0x10000
            target = va + bd
            cond = "bt " if bo == 12 else ("bf " if bo == 4 else "")
            s += f"bc {cond}{bi}, {hex(target)}"
        elif op == 18: # b / bl
            li = w & 0x03fffffc
            if li >= 0x02000000: li -= 0x04000000
            target = va + li
            s += f"{'bl' if (w & 1) else 'b'} {hex(target)}"
        elif op == 32: # lwz
            rD = (w >> 21) & 0x1f
            rA = (w >> 16) & 0x1f
            d = w & 0xffff
            if d >= 0x8000: d -= 0x10000
            s += f"lwz r{rD}, {d}(r{rA})"
        elif op == 34: # lbz
            rD = (w >> 21) & 0x1f
            rA = (w >> 16) & 0x1f
            d = w & 0xffff
            if d >= 0x8000: d -= 0x10000
            s += f"lbz r{rD}, {d}(r{rA})"
        elif op == 36: # stw
            rS = (w >> 21) & 0x1f
            rA = (w >> 16) & 0x1f
            d = w & 0xffff
            if d >= 0x8000: d -= 0x10000
            s += f"stw r{rS}, {d}(r{rA})"
        elif op == 58: # ld
            rD = (w >> 21) & 0x1f
            rA = (w >> 16) & 0x1f
            ds = w & 0xfffc
            if ds >= 0x8000: ds -= 0x10000
            s += f"ld r{rD}, {ds}(r{rA})"
        elif op == 62: # std
            rS = (w >> 21) & 0x1f
            rA = (w >> 16) & 0x1f
            ds = w & 0xfffc
            if ds >= 0x8000: ds -= 0x10000
            s += f"std r{rS}, {ds}(r{rA})"
        else:
            s += f"op={op}"
        print(s)

print("=== 0x8001d070 to 0x8001d300 ===")
disasm_func(0x8001d070, 100)
