from pathlib import Path
from elftools.elf.elffile import ELFFile

modules = ['pme_init.elf', 'sysmgr_ss.elf', 'ss_init.elf', 'updater_frontend.elf', 'ss_server1.elf', 'ss_server2.elf', 'ss_server3.elf']
for m in modules:
    p = Path('local_only/analysis/p0i/modules/' + m)
    if not p.exists(): continue
    e = ELFFile(open(p, 'rb'))
    entry = e.header['e_entry']
    print(f"=== {m} === (entry: 0x{entry:x})")
    for i, s in enumerate(e.iter_segments()):
        if s['p_type'] == 'PT_LOAD':
            print(f"  Seg {i}: vaddr=0x{s['p_vaddr']:x} filesz=0x{s['p_filesz']:x} memsz=0x{s['p_memsz']:x} align=0x{s['p_align']:x} flags={s['p_flags']}")
