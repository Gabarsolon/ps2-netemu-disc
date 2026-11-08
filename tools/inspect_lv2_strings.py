from pathlib import Path
import re

data = Path('local_only/fw355/out/lv2_kernel.elf').read_bytes()
patterns = [b'cxm', b'CXM', b'dve', b'DVE', b'avset', b'ps3av', b'video_out']

print("=================== lv2_kernel.elf strings ===================")
for pat in patterns:
    matches = [m.start() for m in re.finditer(pat, data, re.IGNORECASE)]
    print(f"Pattern '{pat.decode()}': {len(matches)} matches")
    for m in matches[:10]:
        s = m
        while s > 0 and data[s-1] >= 0x20 and data[s-1] <= 0x7e: s -= 1
        e = m
        while e < len(data) and data[e] >= 0x20 and data[e] <= 0x7e: e += 1
        print(f"  off={hex(m)}: \"{data[s:e].decode('ascii', errors='ignore')}\"")
