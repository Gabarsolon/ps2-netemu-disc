import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()

def va2off(va): return va - 0x200000 + 0x20000
def off2va(off): return off - 0x20000 + 0x200000

for num in [162, 163, 164, 165]:
    pat = struct.pack('>Q', num)
    pos = 0
    while True:
        pos = data.find(pat, pos)
        if pos == -1: break
        # Check if next 8 bytes look like permission mask or 0
        w2 = struct.unpack_from('>Q', data, pos + 8)[0]
        # In LV1, hypercall records have (num, allowed_lpar_mask, ...)
        if pos % 8 == 0:
            va = off2va(pos)
            # Find if this record VA is referenced as a pointer
            ref_pat = struct.pack('>Q', va)
            ref_pos = data.find(ref_pat)
            if ref_pos != -1:
                ref_va = off2va(ref_pos)
                desc_va = struct.unpack_from('>Q', data, ref_pos - 8)[0]
                if 0x200000 <= desc_va < 0x500000:
                    func_va = struct.unpack_from('>Q', data, va2off(desc_va))[0]
                    print(f"HV {num} record at VA {hex(va)}, ref at {hex(ref_va)}, desc={hex(desc_va)}, func={hex(func_va)}, mask={hex(w2)}")
        pos += 1
