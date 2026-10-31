from pathlib import Path
import re
import struct

elf_path = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf')
d = elf_path.read_bytes()
print(f"sysmgr_ss.elf size: {len(d)}")

strings = []
for m in re.finditer(rb'[ -~]{4,}', d):
    s = m.group(0).decode('ascii', errors='ignore')
    strings.append((hex(m.start()), s))

print(f"Total ASCII strings (len>=4): {len(strings)}")

interesting = [
    'lpar', 'ps2', 'emu', 'net', 'rbd', 'drive', 'meddling', 'optical', 'storage',
    'reset', 'profile', 'laid', 'paid', '0x82', 'shut', 'reboot', 'capability'
]

matches = []
for off, s in strings:
    low = s.lower()
    if any(k in low for k in interesting):
        matches.append((off, s))

print(f"Interesting matches: {len(matches)}")
for off, s in matches[:80]:
    print(f"  {off}: {s}")

# Specifically check exact profile names
profile_keywords = ['ps2', 'lpar', 'softemu', 'netemu', 'gxemu']
for off, s in strings:
    low = s.lower()
    if any(k in low for k in profile_keywords):
        print(f"  PROFILE-RELATED: {off}: {s}")
