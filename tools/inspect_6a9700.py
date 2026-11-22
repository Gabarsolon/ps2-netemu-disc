#!/usr/bin/env python3
import re
from pathlib import Path

dump_path = Path(r"C:\Users\remus\ps2-netemu-disc\local_only\lv1_mem_300000_700000.bin")
dump = dump_path.read_bytes()

off = 0x6A9700 - 0x300000
chunk = dump[off:off+2048]

print("Strings in 0x6A9700..0x6A9F00:")
for m in re.finditer(b"[\x20-\x7E]{4,}", chunk):
    print(f"  0x{0x6A9700+m.start():06X}: {m.group().decode('latin1')}")
