from pathlib import Path
import struct

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
elf_path = ROOT / "local_only" / "analysis" / "p0i" / "modules" / "ss_server3.elf"
ss3 = elf_path.read_bytes()

from disasm_ss1_20638 import decode_ppc

off, = struct.unpack_from(">Q", ss3, 0x20)
n, = struct.unpack_from(">H", ss3, 0x38)
phdrs = [struct.unpack_from(">IIQQQQQQ", ss3, off + i*0x38) for i in range(n)]

def va_to_off(va):
    for p in phdrs:
        if p[0] == 1 and p[3] <= va < p[3] + p[5]:
            return p[2] + va - p[3]
    return None

def off_to_va(fo):
    for p in phdrs:
        if p[0] == 1 and p[2] <= fo < p[2] + p[5]:
            return p[3] + fo - p[2]
    return None

# Find opd for 0x80000a60
target_va = 0x80000a60
opd_va = None
for i in range(0, len(ss3)-16, 8):
    va, = struct.unpack_from(">Q", ss3, i)
    if va == target_va:
        opd_va = off_to_va(i)
        print(f"OPD for 0x{target_va:x} at VA 0x{opd_va:x} (fo 0x{i:x})")
        break

# Find callers of 0x80000a60 or opd_va
for fo in range(0, len(ss3)-4, 4):
    w, = struct.unpack_from(">I", ss3, fo)
    op = w >> 26
    if op == 18:
        lk = w & 1
        li = (w & 0x03fffffc)
        if li >= 0x02000000: li -= 0x04000000
        pc = off_to_va(fo)
        if pc:
            dest = pc + li
            if dest == target_va:
                print(f"Direct BL to 0x{target_va:x} from VA 0x{pc:x} (fo 0x{fo:x})")
