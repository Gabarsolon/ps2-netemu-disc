import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

def check_ss_ports(p):
    data = p.read_bytes()
    print(f"\n=== {p.name} ===")
    with open(p, 'rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

    def off_to_va(off):
        for s_va, s_sz, s_off in segs:
            if s_off <= off < s_off + s_sz:
                return s_va + (off - s_off)
        return None

    for sid in [0x1000, 0x2000, 0x3000, 0x4000, 0x5000, 0x6000, 0x7000, 0x8000]:
        matches = []
        for o in range(0, len(data) - 4, 4):
            w, = struct.unpack_from('>I', data, o)
            if w == sid or (w >> 16) == sid:
                va = off_to_va(o)
                if va is not None:
                    matches.append((o, va))
        if matches:
            print(f"  Service ID 0x{sid:x}: {len(matches)} occurrences (first at VA 0x{matches[0][1]:x})")

for name in ['ss_server1.elf', 'ss_server2.elf', 'ss_server3.elf']:
    check_ss_ports(Path('local_only/analysis/p0i/modules') / name)
