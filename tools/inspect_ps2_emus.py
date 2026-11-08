from pathlib import Path
import struct
import re

for name in ['ps2_emu.elf', 'ps2_gxemu.elf', 'ps2_softemu.elf']:
    path = Path('local_only/fw355/out') / name
    if not path.exists(): continue
    data = path.read_bytes()
    print(f"\n==================== {name} ====================")
    # Search for video strings
    for m in re.finditer(b'Video Mode', data, re.IGNORECASE):
        print(f"  String at {hex(m.start())}: {data[m.start():m.start()+32]}")
    # Search for PS3AV_CID_VIDEO_MODE
    pat = struct.pack('>I', 0x01000002)
    pos = 0
    c = 0
    while True:
        pos = data.find(pat, pos)
        if pos == -1: break
        print(f"  CID 0x01000002 at {hex(pos)}")
        c += 1
        pos += 1
    if c == 0:
        print("  CID 0x01000002 not found")
