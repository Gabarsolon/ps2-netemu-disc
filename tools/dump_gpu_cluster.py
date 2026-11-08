import struct
from pathlib import Path

def dump_gpu_table(elf_path, name, start_ref):
    data = Path(elf_path).read_bytes()
    def va2off(va):
        return va - 0x200000 + 0x20000
    def off2va(off):
        return off - 0x20000 + 0x200000

    print(f"\n=================== GPU Hypercall Cluster: {name} ===================")
    # The table around start_ref consists of pairs: (rec_ptr, desc_ptr) or (desc_ptr, rec_ptr)
    # Let's inspect 0x349500:
    # 0x3494f0: rec 0x3abd68
    # 0x3494f8: opd 0x322fc0
    # 0x349500: rec 0x3abd78 (HV 225)
    # 0x349508: opd 0x322e88
    # 0x349510: rec 0x3abd88
    # So the layout is 16-byte pairs: (rec_ptr, opd_ptr)!
    cur_va = start_ref
    while True:
        prev_va = cur_va - 16
        r_ptr, d_ptr = struct.unpack_from('>QQ', data, va2off(prev_va))
        if 0x200000 <= r_ptr < 0x400000 and 0x200000 <= d_ptr < 0x400000:
            cur_va = prev_va
        else:
            break
    cluster_start = cur_va

    cur_va = start_ref
    while True:
        r_ptr, d_ptr = struct.unpack_from('>QQ', data, va2off(cur_va))
        if 0x200000 <= r_ptr < 0x400000 and 0x200000 <= d_ptr < 0x400000:
            cur_va += 16
        else:
            break
    cluster_end = cur_va

    count = (cluster_end - cluster_start) // 16
    print(f"Cluster at {hex(cluster_start)}..{hex(cluster_end)} ({count} hypercalls):")
    for i in range(count):
        va = cluster_start + i * 16
        r_ptr, d_ptr = struct.unpack_from('>QQ', data, va2off(va))
        r_off = va2off(r_ptr)
        num = struct.unpack_from('>Q', data, r_off)[0]
        d_off = va2off(d_ptr)
        func_addr, toc = struct.unpack_from('>QQ', data, d_off)
        print(f"  HV {num:3d} (0x{num:02x}): func={hex(func_addr)} opd={hex(d_ptr)} rec={hex(r_ptr)} table_slot={hex(va)}")

if __name__ == '__main__':
    dump_gpu_table('local_only/fw355/out/lv1.elf', 'FW 3.55 LV1', 0x349500)
    dump_gpu_table('local_only/fw493/lv1.elf', 'FW 4.93 LV1', 0x3523a8)
