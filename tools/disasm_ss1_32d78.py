from disasm_ss1_20638 import decode_ppc, va_to_off, data
import struct

print(f"Disassembling ss_server1 0x80032d78 to 0x80032df0:")
for va in range(0x80032d78, 0x80032df0, 4):
    fo = va_to_off(va)
    w, = struct.unpack_from(">I", data, fo)
    d = decode_ppc(w, va)
    print(f"  0x{va:08x}: {w:08x}  {d}")
