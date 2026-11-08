import struct
from pathlib import Path

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
elf_path = ROOT / "local_only" / "analysis" / "p0i" / "modules" / "ss_server1.elf"
data = elf_path.read_bytes()

off, = struct.unpack_from(">Q", data, 0x20)
n, = struct.unpack_from(">H", data, 0x38)
phdrs = [struct.unpack_from(">IIQQQQQQ", data, off + i*0x38) for i in range(n)]

def va_to_off(va):
    for p in phdrs:
        if p[0] == 1 and p[3] <= va < p[3] + p[5]:
            return p[2] + va - p[3]
    return None

def decode_ppc(w, pc):
    op = w >> 26
    rD = (w >> 21) & 0x1f
    rA = (w >> 16) & 0x1f
    rB = (w >> 11) & 0x1f
    imm16 = w & 0xffff
    simm16 = imm16 if imm16 < 0x8000 else imm16 - 0x10000

    if op == 18:
        aa = (w >> 1) & 1
        lk = w & 1
        li = (w & 0x03fffffc)
        if li >= 0x02000000: li -= 0x04000000
        target = (pc + li) if not aa else li
        m = "bl" if lk else "b"
        return f"{m:<8} 0x{target:08x}"
    elif op == 16:
        bo = (w >> 21) & 0x1f
        bi = (w >> 16) & 0x1f
        bd = (w & 0xfffc)
        if bd >= 0x8000: bd -= 0x10000
        target = pc + bd
        lk = w & 1
        return f"bc{'l' if lk else ''}     bo={bo}, bi={bi}, 0x{target:08x}"
    elif op == 14: return f"addi     r{rD}, r{rA}, {simm16}"
    elif op == 15: return f"addis    r{rD}, r{rA}, {simm16}"
    elif op == 10: return f"cmpli    cr{(rD>>2)&7}, {rD&1}, r{rA}, {imm16}"
    elif op == 11: return f"cmpi     cr{(rD>>2)&7}, {rD&1}, r{rA}, {simm16}"
    elif op == 32: return f"lwz      r{rD}, {simm16}(r{rA})"
    elif op == 34: return f"lbz      r{rD}, {simm16}(r{rA})"
    elif op == 36: return f"stw      r{rD}, {simm16}(r{rA})"
    elif op == 38: return f"stb      r{rD}, {simm16}(r{rA})"
    elif op == 40: return f"lhz      r{rD}, {simm16}(r{rA})"
    elif op == 44: return f"sth      r{rD}, {simm16}(r{rA})"
    elif op == 58:
        xo = w & 3
        if xo == 0: return f"ld       r{rD}, {simm16 & ~3}(r{rA})"
        elif xo == 1: return f"ldu      r{rD}, {simm16 & ~3}(r{rA})"
        elif xo == 2: return f"lwa      r{rD}, {simm16 & ~3}(r{rA})"
    elif op == 62:
        xo = w & 3
        if xo == 0: return f"std      r{rD}, {simm16 & ~3}(r{rA})"
        elif xo == 1: return f"stdu     r{rD}, {simm16 & ~3}(r{rA})"
    elif op == 19:
        xo = (w >> 1) & 0x3ff
        if xo == 16: return "blr" if (rD == 20 and rA == 0) else f"bclr     {rD}, {rA}"
        elif xo == 528: return "bctr" if (rD == 20 and rA == 0) else f"bcctr    {rD}, {rA}"
    elif op == 31:
        xo = (w >> 1) & 0x3ff
        if xo == 266: return f"add      r{rD}, r{rA}, r{rB}"
        elif xo == 40: return f"subf     r{rD}, r{rA}, r{rB}"
        elif xo == 444: return f"mr       r{rA}, r{rD}"
        elif xo == 28: return f"and      r{rA}, r{rD}, r{rB}"
        elif xo == 442: return f"or       r{rA}, r{rD}, r{rB}"
        elif xo == 0: return f"cmp      cr{(rD>>2)&7}, {rD&1}, r{rA}, r{rB}"
        elif xo == 32: return f"cmpl     cr{(rD>>2)&7}, {rD&1}, r{rA}, r{rB}"
        return f"op31_{xo}  r{rD}, r{rA}, r{rB}"
    return f"word_0x{op:02x} (0x{w:08x})"

print(f"Disassembling ss_server1 0x80020638 to 0x80020780:")
for va in range(0x80020638, 0x80020780, 4):
    fo = va_to_off(va)
    w, = struct.unpack_from(">I", data, fo)
    d = decode_ppc(w, va)
    print(f"  0x{va:08x} (phys 0x{va - 0x80020000 + 0x714000:08x}): {w:08x}  {d}")
