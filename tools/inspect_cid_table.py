from pathlib import Path
import struct

d355 = Path('local_only/fw355/out/lv1.elf').read_bytes()
for k in range(0x3a2900, 0x3a2a80, 16):
    words = [f'0x{struct.unpack_from(">I", d355, k + i*4)[0]:08x}' for i in range(4)]
    print(f'  {hex(k)}: {" ".join(words)}')
