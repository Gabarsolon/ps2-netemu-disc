import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

def analyze_module(path, name):
    data = path.read_bytes()
    with open(path, 'rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

    def off_to_va(off):
        for s_va, s_sz, s_off in segs:
            if s_off <= off < s_off + s_sz:
                return s_va + (off - s_off)
        return None

    print(f"=== Analyzing {name} for 0x30000 / cmd 0x11 ===")
    # Look for 0x30000 in .text or .data
    # In PPC64: lis rX, 3 (0x3c...0003) or 0x00030000 in data
    # And check references near cmd 0x11 (17)
    for i in range(0, len(data) - 4, 4):
        w, = struct.unpack_from('>I', data, i)
        # lis rX, 3: (w >> 26) == 15 and (w & 0xffff) == 3
        if (w >> 26) == 15 and (w & 0xffff) == 3:
            va = off_to_va(i)
            # check if nearby there is 0x11 or 17
            nearby = data[max(0, i-64) : min(len(data), i+64)]
            has_17 = any((struct.unpack_from('>I', data, j)[0] & 0xffff) == 17 for j in range(max(0, i-64), min(len(data)-4, i+64), 4))
            if has_17:
                print(f"  lis rX, 3 near 17 at file off 0x{i:x}, VA 0x{va:x}")

analyze_module(Path('local_only/analysis/p0i/modules/sysmgr_ss.elf'), 'sysmgr_ss.elf')
analyze_module(Path('local_only/fw493/lv1.elf'), 'lv1.elf')
analyze_module(Path('local_only/analysis/p0i/modules/ss_server1.elf'), 'ss_server1.elf')
