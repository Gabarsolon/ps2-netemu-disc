import struct
from pathlib import Path

def find_hv225(elf_path, name):
    data = Path(elf_path).read_bytes()
    def va2off(va):
        return va - 0x200000 + 0x20000
    def off2va(off):
        return off - 0x20000 + 0x200000

    print(f"\n=================== {name} ===================")
    p225 = struct.pack('>QQ', 225, 0)
    pos = 0
    while True:
        pos = data.find(p225, pos)
        if pos == -1: break
        va = off2va(pos)
        print(f"Record 225 found at VA {hex(va)} (file off {hex(pos)})")
        # Check references to this VA
        p_va = struct.pack('>Q', va)
        rpos = 0
        while True:
            rpos = data.find(p_va, rpos)
            if rpos == -1: break
            rva = off2va(rpos)
            print(f"  Referenced at VA {hex(rva)}")
            roff = va2off(rva)
            for delta in [-16, -8, 0, 8, 16]:
                val = struct.unpack_from('>Q', data, roff + delta)[0]
                print(f"    {hex(rva + delta)}: {hex(val)}")
                if 0x200000 <= val < 0x400000:
                    cand_off = va2off(val)
                    if cand_off + 16 <= len(data):
                        f_addr, toc = struct.unpack_from('>QQ', data, cand_off)
                        if 0x200000 <= f_addr < 0x400000 and 0x200000 <= toc < 0x400000:
                            print(f"      -> OPD at {hex(val)}: func={hex(f_addr)}, toc={hex(toc)}")
            rpos += 1
        pos += 1

if __name__ == '__main__':
    find_hv225('local_only/fw355/out/lv1.elf', 'FW 3.55 LV1')
    find_hv225('local_only/fw493/lv1.elf', 'FW 4.93 LV1')
