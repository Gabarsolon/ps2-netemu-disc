import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
base = 0x210000

targets = [0x50f634, 0x50f670, 0x50f6b0]
for t in targets:
    print(f"=== References to 0x{t:x} ===")
    for o in range(0, len(data) - 4, 4):
        va = o + base
        w, = struct.unpack_from('>I', data, o)
        op = w >> 26
        if op == 18 and (w & 1): # bl
            li = w & 0x03fffffc
            if li >= 0x02000000:
                li -= 0x04000000
            dest = va + li
            if dest == t:
                print(f"  bl 0x{t:x} from 0x{va:x}")
        # also check 64-bit pointers
        if o + 8 <= len(data):
            w64, = struct.unpack_from('>Q', data, o)
            if w64 == t:
                print(f"  64-bit ptr to 0x{t:x} at 0x{va:x}")
