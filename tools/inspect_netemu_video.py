import struct
from pathlib import Path
import re

data = Path('local_only/stock.elf').read_bytes()
print(f"stock.elf length: {len(data)} bytes")

# Check hypercalls (sc 1 is opcode 0x44000022 in PowerPC!)
# In PowerPC:
# sc 1: 0x44000022 (hypercall)
# sc 2: 0x44000002 (syscall in lv2)
p_sc1 = b'\x44\x00\x00\x22'
p_sc2 = b'\x44\x00\x00\x02'

sc1_matches = [m.start() for m in re.finditer(re.escape(p_sc1), data)]
sc2_matches = [m.start() for m in re.finditer(re.escape(p_sc2), data)]

print(f"Hypercalls (sc 1): {len(sc1_matches)}")
print(f"Syscalls (sc 2): {len(sc2_matches)}")

# For each hypercall, look at previous instruction (typically li r11, HV_NUM)
for off in sc1_matches:
    prev_w = struct.unpack_from('>I', data, off - 4)[0]
    hv_num = prev_w & 0xffff
    print(f"  HV call at off {hex(off)}: prev_word=0x{prev_w:08x} (r11 = {hv_num})")

# Check video strings
patterns = [b'video', b'mode', b'480', b'576', b'720', b'1080', b'cellVideoOut', b'avset']
for pat in patterns:
    matches = [m.start() for m in re.finditer(pat, data, re.IGNORECASE)]
    print(f"Pattern '{pat.decode()}': {len(matches)} matches")
    for m in matches[:5]:
        s = max(0, m - 10)
        e = min(len(data), m + 30)
        chunk = data[s:e]
        pr = ''.join(chr(b) if 0x20 <= b <= 0x7e else '.' for b in chunk)
        print(f"    off {hex(m)}: {pr}")
