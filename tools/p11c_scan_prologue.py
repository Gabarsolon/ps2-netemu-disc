import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
off = 0x2ff734
# VA 0x50f734 = file offset 0x2ff734 (base delta: 0x50f734 - 0x2ff734 = 0x210000)
base = 0x210000

for o in range(off - 256, off + 128, 4):
    va = o + base
    w, = struct.unpack_from('>I', data, o)
    # Check for mflr r0 (0x7c0802a6) or stdu r1, -N(r1) (0xf821...)
    mark = ""
    if w == 0x7c0802a6:
        mark = " <-- mflr r0"
    elif (w >> 16) == 0xf821:
        mark = " <-- stdu r1"
    elif w == 0x4e800020:
        mark = " <-- blr"
    print(f"0x{va:x} (off 0x{o:x}): 0x{w:08x}{mark}")
