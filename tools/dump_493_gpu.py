import struct
from pathlib import Path

def dump_493_gpu():
    data = Path('local_only/fw493/lv1.elf').read_bytes()
    def va2off(va):
        return va - 0x200000 + 0x20000
    def off2va(off):
        return off - 0x20000 + 0x200000

    print("=================== FW 4.93 LV1 GPU HYPERCALLS ===================")
    # Start around 0x3523a8 (which is HV 225)
    # The pairs are at 0x352318..
    for va in range(0x352318, 0x352450, 16):
        r_ptr, d_ptr = struct.unpack_from('>QQ', data, va2off(va))
        if 0x200000 <= r_ptr < 0x400000 and 0x200000 <= d_ptr < 0x400000:
            r_off = va2off(r_ptr)
            num = struct.unpack_from('>Q', data, r_off)[0]
            d_off = va2off(d_ptr)
            func_addr, toc = struct.unpack_from('>QQ', data, d_off)
            print(f"  HV {num:3d} (0x{num:02x}): func={hex(func_addr)} opd={hex(d_ptr)} rec={hex(r_ptr)} table_slot={hex(va)}")

dump_493_gpu()
