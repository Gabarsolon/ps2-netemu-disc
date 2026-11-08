import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

sysmgr = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
data = sysmgr.read_bytes()

with open(sysmgr, 'rb') as f:
    e = ELFFile(f)
    print("Entry:", hex(e.header['e_entry']))
    entry = e.header['e_entry']
    for seg in e.iter_segments():
        if seg['p_type'] == 'PT_LOAD':
            va = seg['p_vaddr']
            sz = seg['p_memsz']
            off = seg['p_offset']
            if va <= entry < va + sz:
                off_entry = off + (entry - va)
                func_va, toc_va = struct.unpack_from('>2Q', data, off_entry)
                print(f"Entry OPD at 0x{entry:x}: func = 0x{func_va:x}, TOC (r2) = 0x{toc_va:x}")
