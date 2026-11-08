from disasm_ss1_20638 import decode_ppc
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

print("Disassembling ss_server3 0x8000a890:")
for va in range(0x8000a890, 0x8000a8e0, 4):
    fo = va_to_off(va)
    w, = struct.unpack_from(">I", ss3, fo)
    d = decode_ppc(w, va)
    print(f"  VA 0x{va:08x}: {w:08x}  {d}")
