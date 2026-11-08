from pathlib import Path
import re

patterns = [b'ps3av', b'CXM', b'cxm', b'DVE', b'dve', b'avset', b'cellVideoOut', b'sys_rsx_context_attribute', b'PS3AV']

search_dirs = [
    Path('local_only/analysis/p0h/modules'),
    Path('local_only/fw493'),
    Path('local_only/fw355/out'),
]

for sdir in search_dirs:
    if not sdir.exists(): continue
    for f in sdir.glob('*.elf'):
        data = f.read_bytes()
        found = []
        for pat in patterns:
            if pat in data:
                found.append(pat.decode())
        if found:
            print(f"{f.name}: {found}")

for f in Path('local_only/fw355/out').glob('*.elf'):
    data = f.read_bytes()
    found = []
    for pat in patterns:
        if pat.lower() in data.lower():
            found.append(pat.decode())
    if found:
        print(f"out/{f.name}: {found}")
