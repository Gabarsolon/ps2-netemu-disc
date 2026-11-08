from pathlib import Path
import struct

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
elf_path = ROOT / "local_only" / "fw493" / "lv1.elf"
data = elf_path.read_bytes()

for num in [182, 183]:
    p = struct.pack(">Q", num)
    pos = 0
    while True:
        pos = data.find(p, pos)
        if pos == -1: break
        print(f"Found {num} at offset 0x{pos:x}")
        w = struct.unpack_from(">QQQQ", data, max(0, pos-8))
        print(f"  Context: {[hex(x) for x in w]}")
        pos += 1
