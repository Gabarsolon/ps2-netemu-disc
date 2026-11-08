from pathlib import Path
import re

mod_dir = Path('local_only/analysis/p0h/modules')
for f in mod_dir.glob('*.elf'):
    data = f.read_bytes()
    for kw in [b'avset', b'cxm', b'dve', b'ps3av', b'video_mode', b'hdmi', b'SYSCON']:
        matches = [m.start() for m in re.finditer(kw, data, re.IGNORECASE)]
        if matches:
            print(f"{f.name}: found {len(matches)} matches for {kw}")
            for m in matches[:5]:
                s = max(0, m - 20)
                e = min(len(data), m + 40)
                print(f"    off {hex(m)}: {data[s:e]}")
