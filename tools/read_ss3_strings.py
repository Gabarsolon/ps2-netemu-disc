from pathlib import Path
import struct

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
elf_path = ROOT / "local_only" / "analysis" / "p0i" / "modules" / "ss_server3.elf"
ss3 = elf_path.read_bytes()

off, = struct.unpack_from(">Q", ss3, 0x20)
n, = struct.unpack_from(">H", ss3, 0x38)
phdrs = [struct.unpack_from(">IIQQQQQQ", ss3, off + i*0x38) for i in range(n)]

def va_to_off(va):
    for p in phdrs:
        if p[0] == 1 and p[3] <= va < p[3] + p[5]:
            return p[2] + va - p[3]
    return None

def read_str_at_va(va):
    fo = va_to_off(va)
    if fo is None: return f"<invalid VA 0x{va:x}>"
    end = ss3.find(b"\0", fo)
    if end == -1: end = fo + 100
    return repr(ss3[fo:end])

toc_va = 0xC000E7E8

disps = [-0x7fc8, -0x7fb8, -0x7fb0, -0x7fa8, -0x7fa0, -0x7f98, -0x7f90, -0x7f88, -0x7f80, -0x7f78]
for d in disps:
    addr = toc_va + d
    fo = va_to_off(addr)
    if fo:
        s_va, = struct.unpack_from(">Q", ss3, fo)
        s = read_str_at_va(s_va)
        print(f"TOC[{d:#x}] -> 0x{s_va:x}: {s}")
