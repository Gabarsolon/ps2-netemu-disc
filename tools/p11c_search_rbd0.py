from pathlib import Path
import struct
from elftools.elf.elffile import ELFFile

def search_elf_strings(elf_path, needle):
    data = elf_path.read_bytes()
    idx = 0
    matches = []
    while True:
        idx = data.find(needle, idx)
        if idx == -1:
            break
        matches.append(idx)
        idx += len(needle)
    print(f"=== {elf_path.name}: {len(matches)} matches for {needle} ===")
    with open(elf_path, 'rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
    for m in matches:
        va = None
        for s_va, s_sz, off in segs:
            if off <= m < off + s_sz:
                va = s_va + (m - off)
                break
        ctx = data[max(0, m - 16) : min(len(data), m + 48)]
        va_str = f"0x{va:x}" if va is not None else "None"
        print(f"Offset 0x{m:x}, VA {va_str}: {repr(ctx)}")

search_elf_strings(Path('local_only/fw493/lv1.elf'), b'rbd0')
search_elf_strings(Path('local_only/analysis/p0i/modules/sysmgr_ss.elf'), b'rbd0')
