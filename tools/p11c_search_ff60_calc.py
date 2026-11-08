import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

def search_ff60_calc(p):
    data = p.read_bytes()
    with open(p, 'rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

    def off_to_va(off):
        for s_va, s_sz, s_off in segs:
            if s_off <= off < s_off + s_sz:
                return s_va + (off - s_off)
        return None

    matches = []
    for o in range(0, len(data) - 8, 4):
        w1, = struct.unpack_from('>I', data, o)
        w2, = struct.unpack_from('>I', data, o + 4)
        # w1: addis rD, rA, -1 -> (w1 >> 26) == 15 and (w1 & 0xffff) == 0xffff
        # w2: addi rD, rA, 0x00a0 -> (w2 >> 26) == 14 and (w2 & 0xffff) == 0x00a0
        if (w1 >> 26) == 15 and (w1 & 0xffff) == 0xffff and (w2 >> 26) == 14 and (w2 & 0xffff) == 0x00a0:
            va = off_to_va(o)
            va_str = f"0x{va:x}" if va else "None"
            matches.append((o, va_str))
    if matches:
        print(f"=== {p.name}: {len(matches)} matches for -0xff60 ===")
        for o, va_str in matches:
            print(f"  off 0x{o:x}, VA {va_str}")

targets = [
    Path('local_only/fw493/lv1.elf'),
    Path('local_only/analysis/p0i/modules/ss_server1.elf'),
    Path('local_only/analysis/p0i/modules/sysmgr_ss.elf'),
]

for t in targets:
    if t.exists():
        search_ff60_calc(t)
