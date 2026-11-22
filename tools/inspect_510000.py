#!/usr/bin/env python3
import re
from pathlib import Path

dump = Path(r"C:\Users\remus\ps2-netemu-disc\local_only\lv1_mem_300000_700000.bin").read_bytes()
BASE = 0x300000

off = 0x510000 - BASE
chunk = dump[off:off + 0x40000]

print("Strings in 0x510000..0x550000:")
found = 0
for m in re.finditer(b"[\x20-\x7E]{5,}", chunk):
    found += 1
    if found <= 30:
        print(f"  0x{0x510000+m.start():06X}: {m.group().decode('latin1')}")
print(f"Total ASCII strings in range: {found}")
