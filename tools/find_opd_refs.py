from disasm_ss1_20638 import data, phdrs, va_to_off
import struct

target = 0xc0007740
for i in range(0, len(data)-8, 4):
    v, = struct.unpack_from(">Q", data, i)
    if v == target:
        for p in phdrs:
            if p[0] == 1 and p[2] <= i < p[2] + p[5]:
                ptr_va = p[3] + i - p[2]
                print(f"64-bit Pointer to OPD at VA 0x{ptr_va:08x} (file offset 0x{i:x})")
                break
    v32, = struct.unpack_from(">I", data, i)
    if v32 == target:
        for p in phdrs:
            if p[0] == 1 and p[2] <= i < p[2] + p[5]:
                ptr_va = p[3] + i - p[2]
                print(f"32-bit Pointer to OPD at VA 0x{ptr_va:08x} (file offset 0x{i:x})")
                break
