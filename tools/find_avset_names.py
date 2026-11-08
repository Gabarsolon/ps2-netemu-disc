from pathlib import Path
import re

data = Path('local_only/fw355/out/vsh.elf').read_bytes()
matches = [m.start() for m in re.finditer(b'avset', data, re.IGNORECASE)]
print(f"Matches for 'avset' in vsh.elf: {len(matches)}")
for m in matches[:15]:
    s = max(0, m - 10)
    e = min(len(data), m + 35)
    print(f"  off {hex(m)}: {data[s:e]}")
