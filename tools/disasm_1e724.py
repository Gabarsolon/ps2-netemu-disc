from disasm_ss1_20638 import data, va_to_off, decode_ppc
import struct

print(f"Disassembling ss_server1 0x8001e710 to 0x8001e760:")
for va in range(0x8001e710, 0x8001e760, 4):
    fo = va_to_off(va)
    w, = struct.unpack_from(">I", data, fo)
    d = decode_ppc(w, va)
    print(f"  0x{va:08x}: {w:08x}  {d}")
