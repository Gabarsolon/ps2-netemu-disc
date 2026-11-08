from pathlib import Path
import struct

data = Path('local_only/stock.elf').read_bytes()
# Search for 0x13734 or 0x136ac
for target_va in [0x13734, 0x136ac, 0x13670, 0x137c0]:
    p64 = struct.pack('>Q', target_va)
    p32 = struct.pack('>I', target_va)
    print(f"Target {hex(target_va)}:")
    for p, s in [(p64, 8), (p32, 4)]:
        pos = 0
        while True:
            pos = data.find(p, pos)
            if pos == -1: break
            print(f"  {s*8}-bit ptr at file off {hex(pos)} (VA {hex(pos - 0x10000)})")
            pos += 1
