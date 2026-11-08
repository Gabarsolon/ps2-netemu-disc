from disasm_ss1_20638 import data, va_to_off, phdrs
import struct

def read_str_at_va(va):
    fo = va_to_off(va)
    if fo is None: return f"<invalid VA 0x{va:x}>"
    end = data.find(b"\0", fo)
    if end == -1: end = fo + 100
    return repr(data[fo:end])

toc = 0xc0014cc0

offsets = [
    ("0x80020718 (-26640)", -26640),
    ("0x80020740 (-27080)", -27080),
    ("0x80020758 (-26784)", -26784),
    ("0x80032d58 (-24408)", -24408),
    ("0x80032d84 (-24400)", -24400),
    ("0x80032dac (-24392)", -24392),
]

for label, disp in offsets:
    addr = toc + disp
    fo = va_to_off(addr)
    if fo is not None:
        str_va, = struct.unpack_from(">Q", data, fo)
        s = read_str_at_va(str_va)
        print(f"{label}: TOC[0x{addr:x}] -> VA 0x{str_va:x}: {s}")
    else:
        print(f"{label}: TOC addr 0x{addr:x} not in file!")
