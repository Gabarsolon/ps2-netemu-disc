from pathlib import Path
import struct

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
elf_path = ROOT / "local_only" / "analysis" / "p0i" / "modules" / "ss_server3.elf"
data = elf_path.read_bytes()

from disasm_ss1_20638 import decode_ppc

# In ss_server3.elf, find VA of 0x10b44
# phdrs
off, = struct.unpack_from(">Q", data, 0x20)
n, = struct.unpack_from(">H", data, 0x38)
phdrs = [struct.unpack_from(">IIQQQQQQ", data, off + i*0x38) for i in range(n)]

def off_to_va(fo):
    for p in phdrs:
        if p[0] == 1 and p[2] <= fo < p[2] + p[5]:
            return p[3] + fo - p[2]
    return None

print("Disassembling ss_server3 around P1 (0x10b44):")
for fo in range(0x10b40, 0x10b70, 4):
    va = off_to_va(fo) or fo
    w, = struct.unpack_from(">I", data, fo)
    d = decode_ppc(w, va)
    phys = 0x100000 + fo
    print(f"  FO 0x{fo:05x} (phys 0x{phys:06x}, VA 0x{va:08x}): {w:08x}  {d}")

print("\nDisassembling ss_server3 around P2 (0x10cc0):")
for fo in range(0x10cb0, 0x10cf0, 4):
    va = off_to_va(fo) or fo
    w, = struct.unpack_from(">I", data, fo)
    d = decode_ppc(w, va)
    phys = 0x100000 + fo
    print(f"  FO 0x{fo:05x} (phys 0x{phys:06x}, VA 0x{va:08x}): {w:08x}  {d}")
