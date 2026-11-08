from pathlib import Path
from elftools.elf.elffile import ELFFile

for m in ['ss_server1.elf', 'ss_server3.elf']:
    p = Path('local_only/analysis/p0i/modules/' + m)
    e = ELFFile(open(p, 'rb'))
    print(f"=== {m} ===")
    for i, s in enumerate(e.iter_segments()):
        if s['p_type'] == 'PT_LOAD':
            print(f"  Seg {i}: p_offset=0x{s['p_offset']:x} vaddr=0x{s['p_vaddr']:x} filesz=0x{s['p_filesz']:x} memsz=0x{s['p_memsz']:x}")
    for sec in e.iter_sections():
        if sec['sh_type'] in ('SHT_PROGBITS', 'SHT_NOBITS'):
            print(f"  Sec {sec.name:15s}: addr=0x{sec['sh_addr']:x} off=0x{sec['sh_offset']:x} size=0x{sec['sh_size']:x}")
