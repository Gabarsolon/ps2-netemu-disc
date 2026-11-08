from pathlib import Path
from elftools.elf.elffile import ELFFile

modules_dir = Path('local_only/analysis/p0i/modules')
for f in modules_dir.glob('*.elf'):
    try:
        e = ELFFile(open(f, 'rb'))
        print(f"{f.name:20s}: entry 0x{e.header['e_entry']:x}, size {f.stat().st_size}")
    except Exception as ex:
        print(f"{f.name:20s}: error {ex}")
