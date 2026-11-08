from pathlib import Path
import re

data = Path('local_only/fw355/out/vsh.elf').read_bytes()
matches = [m.start() for m in re.finditer(b'avset_', data)]
print(f"Total avset_ occurrences: {len(matches)}")
strings = set()
for m in matches:
    s = m
    while s > 0 and data[s-1] >= 0x20 and data[s-1] <= 0x7e: s -= 1
    e = m
    while e < len(data) and data[e] >= 0x20 and data[e] <= 0x7e: e += 1
    strings.add(data[s:e].decode('ascii', errors='ignore'))

for s in sorted(strings):
    print(f"  {s}")
