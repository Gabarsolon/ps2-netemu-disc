import struct
from pathlib import Path

def search_ff6x(path):
    if not path.is_file():
        return
    data = path.read_bytes()
    matches = []
    # search for 16-bit 0xff60, 0xff61
    for o in range(0, len(data) - 2, 2):
        w16, = struct.unpack_from('>H', data, o)
        if w16 in [0xff60, 0xff61]:
            # check if 32-bit immediate or data
            matches.append((o, hex(w16)))
    if matches:
        print(f"=== {path.name}: {len(matches)} matches for 0xFF60/0xFF61 ===")
        for o, m in matches[:10]:
            print(f"  off 0x{o:x}: {m}")

for p in Path('local_only').rglob('*.elf'):
    search_ff6x(p)
