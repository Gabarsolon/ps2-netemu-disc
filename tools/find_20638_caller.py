from disasm_ss1_20638 import data, phdrs, va_to_off
import struct

# Look for opd referencing 0x80020638
opd_va = None
for i in range(0, len(data)-16, 8):
    va, = struct.unpack_from(">Q", data, i)
    if va == 0x80020638:
        # find VA of this opd entry
        for p in phdrs:
            if p[0] == 1 and p[2] <= i < p[2] + p[5]:
                opd_va = p[3] + i - p[2]
                print(f"OPD for 0x80020638 at VA 0x{opd_va:08x}")
                break

if opd_va:
    # Find pointers to this opd in data or code
    for i in range(0, len(data)-8, 8):
        val, = struct.unpack_from(">Q", data, i)
        if val == opd_va:
            for p in phdrs:
                if p[0] == 1 and p[2] <= i < p[2] + p[5]:
                    ptr_va = p[3] + i - p[2]
                    print(f"Pointer to OPD at VA 0x{ptr_va:08x}")
