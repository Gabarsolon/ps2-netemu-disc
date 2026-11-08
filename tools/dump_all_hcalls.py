import struct
from pathlib import Path

def dump_hcalls(elf_path, name):
    data = Path(elf_path).read_bytes()
    def va2off(va):
        return va - 0x200000 + 0x20000
    def off2va(off):
        return off - 0x20000 + 0x200000

    p170 = struct.pack('>QQQQ', 170, 0, 171, 0)
    idx = data.find(p170)
    if idx == -1:
        p170 = struct.pack('>Q', 170)
        p171 = struct.pack('>Q', 171)
        pos = 0
        while True:
            pos = data.find(p170, pos)
            if pos == -1: break
            if pos + 16 < len(data) and data[pos+16:pos+24] == p171:
                idx = pos
                break
            pos += 1

    rec_va = off2va(idx)
    print(f"\n=================== {name} ===================")
    print(f"HV 170 record at VA {hex(rec_va)}")

    p_rec = struct.pack('>Q', rec_va)
    ref_pos = data.find(p_rec)
    ref_va = off2va(ref_pos)
    print(f"Referenced at VA: {hex(ref_va)}")

    # ref_va is the second element of the pair: (desc_ptr, rec_ptr)
    pair_va = ref_va - 8
    pair_off = va2off(pair_va)

    cur_off = pair_off
    while cur_off >= 16:
        d_ptr, r_ptr = struct.unpack_from('>QQ', data, cur_off - 16)
        if 0x200000 <= r_ptr < 0x400000 and 0x200000 <= d_ptr < 0x400000:
            r_off = va2off(r_ptr)
            hv_num = struct.unpack_from('>Q', data, r_off)[0]
            if 0 <= hv_num < 256:
                cur_off -= 16
                continue
        break
    start_pair_off = cur_off
    start_pair_va = off2va(start_pair_off)

    cur_off = pair_off
    while cur_off + 16 <= len(data):
        d_ptr, r_ptr = struct.unpack_from('>QQ', data, cur_off)
        if 0x200000 <= r_ptr < 0x400000 and 0x200000 <= d_ptr < 0x400000:
            r_off = va2off(r_ptr)
            hv_num = struct.unpack_from('>Q', data, r_off)[0]
            if 0 <= hv_num < 256:
                cur_off += 16
                continue
        break
    end_pair_off = cur_off
    count = (end_pair_off - start_pair_off) // 16
    print(f"Pair table: {hex(start_pair_va)}..{hex(off2va(end_pair_off))}, total {count} entries")

    hcalls = {}
    for i in range(count):
        d_ptr, r_ptr = struct.unpack_from('>QQ', data, start_pair_off + i*16)
        r_off = va2off(r_ptr)
        hv_num = struct.unpack_from('>Q', data, r_off)[0]
        d_off = va2off(d_ptr)
        func_addr, toc = struct.unpack_from('>QQ', data, d_off)
        hcalls[hv_num] = (func_addr, toc, d_ptr, r_ptr)

    print("Target Hypercalls:")
    target_nums = [91, 162, 163, 164, 165, 166, 170, 171, 197, 210, 211, 212, 213, 214, 216, 217, 218, 221, 225, 227, 228, 245, 246, 248, 249]
    for num in target_nums:
        if num in hcalls:
            func_addr, toc, d_ptr, r_ptr = hcalls[num]
            print(f"  HV {num:3d} (0x{num:02x}): func={hex(func_addr)} opd={hex(d_ptr)} rec={hex(r_ptr)}")
        else:
            print(f"  HV {num:3d} (0x{num:02x}): NOT FOUND")

    return hcalls

if __name__ == '__main__':
    dump_hcalls('local_only/fw355/out/lv1.elf', 'FW 3.55 LV1')
    dump_hcalls('local_only/fw493/lv1.elf', 'FW 4.93 LV1')
