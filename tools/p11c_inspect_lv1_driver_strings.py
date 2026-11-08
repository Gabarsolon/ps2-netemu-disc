import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

lv1 = Path('local_only/fw493/lv1.elf')
data = lv1.read_bytes()

# Let's inspect strings around 0x327000..0x32e000
idx = 0x320000
while idx < 0x330000:
    end = data.find(b'\0', idx)
    if end != -1:
        s = data[idx:end]
        if len(s) >= 4 and all(32 <= b <= 126 for b in s):
            print(f"0x{idx:x}: {s.decode('ascii')}")
        idx = end + 1
    else:
        break
