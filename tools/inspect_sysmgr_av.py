from pathlib import Path
import re

data = Path('local_only/analysis/p0h/modules/sysmgr_ss.elf').read_bytes()
patterns = [b'video', b'audio', b'mode', b'hdmi', b'i2c', b'smbus', b'cxm', b'dve', b'display', b'crtc', b'resolution']

print("=================== sysmgr_ss.elf video/audio strings ===================")
for pat in patterns:
    matches = [m.start() for m in re.finditer(pat, data, re.IGNORECASE)]
    print(f"Pattern '{pat.decode()}': {len(matches)} matches")
    for m in matches[:6]:
        s = max(0, m - 15)
        e = min(len(data), m + 35)
        # extract printable ascii
        chunk = data[s:e]
        pr = ''.join(chr(b) if 0x20 <= b <= 0x7e else '.' for b in chunk)
        print(f"  off {hex(m)}: {pr}")
