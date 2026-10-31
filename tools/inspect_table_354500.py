from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()
base_va = 0x3544d0
off = base_va - 0x200000 + 0x20000

for i in range(0, 0xa0, 8):
    va = base_va + i
    val = struct.unpack_from('>Q', elf, off + i)[0]
    s = ""
    if 0x200000 <= val < 0x3c0000:
        poff = val - 0x200000 + 0x20000
        nul = elf.find(b'\0', poff)
        if nul != -1 and nul - poff < 64:
            try: s = elf[poff:nul].decode('ascii', errors='ignore')
            except: pass
    print(f"  {hex(va)}: {hex(val)} \"{s}\"")
