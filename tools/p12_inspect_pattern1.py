import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

lv1 = Path('local_only/fw493/lv1.elf')
data = lv1.read_bytes()

# Pattern 1 is at file offset 0x3a7b54
# Let's inspect instructions from 0x3a7b54 - 0x20 to 0x3a7b54 + 0x40
off = 0x3a7b54
for o in range(off - 32, off + 48, 4):
    w, = struct.unpack_from('>I', data, o)
    print(f"off 0x{o:x} (VA 0x{o+0x210000:x}): 0x{w:08x}")
