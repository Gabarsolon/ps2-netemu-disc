from pathlib import Path
import re
import struct

def inspect_self(path):
    d = Path(path).read_bytes()
    magic, ver, rev, typ = struct.unpack_from('>4sIHH', d)
    print(f"File: {path.name}, size: {len(d)}, magic: {magic}, ver: {hex(ver)}, rev: {hex(rev)}, type: {typ}")
    # printable strings length >= 5
    strings = [m.group(0).decode('ascii', errors='ignore') for m in re.finditer(rb'[ -~]{5,}', d)]
    print(f"  Total strings: {len(strings)}")
    print(f"  First 20 strings:")
    for s in strings[:20]:
        print(f"    {s}")
    # search for ps2, emu, netemu, iso, me, sv
    keywords = ['ps2', 'emu', 'netemu', 'me', 'sv', 'iso', 'auth', 'spu', 'spe']
    matching = [s for s in strings if any(k in s.lower() for k in keywords)]
    print(f"  Matching keywords (up to 30):")
    for s in matching[:30]:
        print(f"    {s}")

p1 = Path('local_only/fw493/me_iso_for_ps2emu.self')
p2 = Path('local_only/fw493/sv_iso_for_ps2emu.self')
inspect_self(p1)
print("="*60)
inspect_self(p2)
