#!/usr/bin/env python3
"""Offline: confirm stock bytes at sysmgr_ss firmware-route patch sites (Components A/B).

Reads local sysmgr_ss.elf, maps target VAs -> file offsets via program headers,
prints the 4-byte big-endian word(s) and a tiny PPC decode for the ones we care about.
No console access. Pass the elf path as argv[1].
"""
import sys, struct

PATH = sys.argv[1] if len(sys.argv) > 1 else r"local_only/analysis/p0h/modules/sysmgr_ss.elf"

def ppc_decode(w):
    # minimal decode for the few forms we expect
    if w == 0x38600001: return "li r3,1"
    if w == 0x38600002: return "li r3,2"
    if w == 0x4e800020: return "blr"
    if w == 0x60000000: return "nop"
    if w == 0x7c004838: return "and r0,r0,r9"
    op = w >> 26
    if op == 31 and (w & 0x7fe) == (444<<1): return "or/and-form (ext)"
    return f"op={op}"

def main():
    data = open(PATH, "rb").read()
    print(f"file {PATH} size {len(data)}")
    assert data[:4] == b"\x7fELF", "not ELF"
    is64 = data[4] == 2
    be = data[5] == 2
    endp = ">" if be else "<"
    print(f"ELF{'64' if is64 else '32'} {'BE' if be else 'LE'}")
    if is64:
        e_phoff = struct.unpack(endp+"Q", data[0x20:0x28])[0]
        e_phentsize = struct.unpack(endp+"H", data[0x36:0x38])[0]
        e_phnum = struct.unpack(endp+"H", data[0x38:0x3a])[0]
    else:
        e_phoff = struct.unpack(endp+"I", data[0x1c:0x20])[0]
        e_phentsize = struct.unpack(endp+"H", data[0x2a:0x2c])[0]
        e_phnum = struct.unpack(endp+"H", data[0x2c:0x2e])[0]
    segs = []
    for i in range(e_phnum):
        off = e_phoff + i*e_phentsize
        if is64:
            p_type = struct.unpack(endp+"I", data[off:off+4])[0]
            p_offset = struct.unpack(endp+"Q", data[off+8:off+16])[0]
            p_vaddr = struct.unpack(endp+"Q", data[off+16:off+24])[0]
            p_filesz = struct.unpack(endp+"Q", data[off+32:off+40])[0]
            p_memsz = struct.unpack(endp+"Q", data[off+40:off+48])[0]
        else:
            p_type = struct.unpack(endp+"I", data[off:off+4])[0]
            p_offset = struct.unpack(endp+"I", data[off+4:off+8])[0]
            p_vaddr = struct.unpack(endp+"I", data[off+8:off+12])[0]
            p_filesz = struct.unpack(endp+"I", data[off+16:off+20])[0]
            p_memsz = struct.unpack(endp+"I", data[off+20:off+24])[0]
        if p_type == 1:
            segs.append((p_vaddr, p_offset, p_filesz, p_memsz))
            print(f"  PT_LOAD vaddr={p_vaddr:#x} off={p_offset:#x} filesz={p_filesz:#x} memsz={p_memsz:#x}")

    def va2off(va):
        for vaddr, offset, filesz, memsz in segs:
            if vaddr <= va < vaddr + filesz:
                return offset + (va - vaddr)
        return None

    def word(va):
        o = va2off(va)
        if o is None: return None
        return struct.unpack(endp+"I", data[o:o+4])[0]

    print("\n== Component A: ability-bit strip at 0x8001e334 (expect and r0,r0,r9 = 0x7c004838) ==")
    for va in (0x8001e328,0x8001e32c,0x8001e330,0x8001e334,0x8001e338,0x8001e33c):
        w = word(va); print(f"  {va:#x}: {w:08x} {ppc_decode(w)}" if w is not None else f"  {va:#x}: <unmapped>")

    print("\n== Component B: PS2_NE_LPAR +0xc0 stub 0x8001dad8 (expect li r3,1; blr) ==")
    for va in (0x8001dad8,0x8001dadc):
        w = word(va); print(f"  {va:#x}: {w:08x} {ppc_decode(w)}" if w is not None else f"  {va:#x}: <unmapped>")
    print("   power-on routine 0x8001decc (PS2_SW_LPAR +0xc0 target):")
    for va in (0x8001decc,0x8001ded0,0x8001ded4):
        w = word(va); print(f"  {va:#x}: {w:08x} {ppc_decode(w)}" if w is not None else f"  {va:#x}: <unmapped>")

    print("\n== vtable PS2_NE_LPAR 0x8003e220, +0xc0 entry at 0x8003e2e0 (pointer; OPD of 0x8001dad8) ==")
    for va in (0x8003e220+0xc0,):
        o = va2off(va)
        if o is None:
            print(f"  {va:#x}: <unmapped>"); continue
        q = struct.unpack(endp+"Q", data[o:o+8])[0]
        print(f"  {va:#x}: {q:#018x}  (vtable slot +0xc0)")
    # print 16-byte context windows for signature building
    print("\n== signature windows (8-byte BE doublewords) ==")
    for name,va in (("A@0x8001e330",0x8001e330),("Bstub@0x8001dad8",0x8001dad8)):
        o = va2off(va)
        if o is None: print(f"  {name}: <unmapped>"); continue
        dw = struct.unpack(endp+"Q", data[o:o+8])[0]
        print(f"  {name}: peekd={dw:#018x}")

if __name__ == "__main__":
    main()
