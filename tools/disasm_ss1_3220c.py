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

from disasm_ss1_20638 import decode_ppc

print(f"Disassembling ss_server1 0x8003220c to 0x80032280:")
for va in range(0x8003220c, 0x80032280, 4):
    fo = va_to_off(va)
    w, = struct.unpack_from(">I", data, fo)
    d = decode_ppc(w, va)
    print(f"  0x{va:08x}: {w:08x}  {d}")
