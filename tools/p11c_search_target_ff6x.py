import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

def search_target(p):
    data = p.read_bytes()
    print(f"\n=================== {p.name} ===================")
    with open(p, 'rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

    def off_to_va(off):
        for s_va, s_sz, s_off in segs:
            if s_off <= off < s_off + s_sz:
                return s_va + (off - s_off)
        return None

    # Search for instructions with immediate 0xff60 or 0xff61
    # or cmplwi/cmpwi with 0xff60/0xff61
    # or 32-bit constant 0x0000ff60 / 0x0000ff61
    for o in range(0, len(data) - 4, 4):
        w32, = struct.unpack_from('>I', data, o)
        if w32 in [0x0000ff60, 0x0000ff61, 0xff60, 0xff61]:
            va = off_to_va(o)
            va_str = f"0x{va:x}" if va else "None"
            print(f"  32-bit constant 0x{w32:08x} at off 0x{o:x}, VA {va_str}")
        imm = w32 & 0xffff
        op = w32 >> 26
        if imm in [0xff60, 0xff61] and op in [10, 11, 12, 13, 14, 15, 24, 25, 28]:
            va = off_to_va(o)
            va_str = f"0x{va:x}" if va else "None"
            print(f"  Instruction 0x{w32:08x} (imm=0x{imm:x}, op={op}) at off 0x{o:x}, VA {va_str}")

targets = [
    Path('local_only/fw493/lv1.elf'),
    Path('local_only/fw355/lv1.elf'),
    Path('local_only/analysis/p0i/modules/ss_server1.elf'),
    Path('local_only/analysis/p0i/modules/sysmgr_ss.elf'),
    Path('local_only/analysis/p0i/modules/ps2_softemu.elf'),
    Path('local_only/analysis/p0i/modules/vsh.elf'),
]

for t in targets:
    if t.exists():
        search_target(t)
    else:
        print(f"Not found: {t}")
