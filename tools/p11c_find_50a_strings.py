import struct
from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()
base = 0x210000

for off in range(0x50a000 - base, 0x50b000 - base, 4):
    va = off + base
    w, = struct.unpack_from('>I', data, off)
    # look for string pointers or calls
    if off + 8 <= len(data):
        w64, = struct.unpack_from('>Q', data, off)
        if 0x400000 <= w64 < 0x600000:
            # check if it points to a string
            str_off = w64 - base
            if 0 <= str_off < len(data):
                end = data.find(b'\x00', str_off)
                if end != -1 and 3 <= end - str_off < 64:
                    s = data[str_off:end]
                    if all(32 <= c < 127 for c in s):
                        print(f"0x{va:x}: ptr to '{s.decode()}' at 0x{w64:x}")
