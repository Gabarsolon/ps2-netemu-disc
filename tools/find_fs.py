from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()

# Search for "sysmgr_ss" in elf
pos = 0
while True:
    idx = elf.find(b'sysmgr_ss', pos)
    if idx == -1:
        break
    print(f"Found 'sysmgr_ss' at 0x{idx:x}")
    pos = idx + 1
