from pathlib import Path
import struct

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
p1 = bytes.fromhex("409E00702FBE0001")
p2 = bytes.fromhex("38800002409C0014")

for f in ROOT.glob("local_only/**/*.elf"):
    data = f.read_bytes()
    idx1 = data.find(p1)
    if idx1 != -1:
        print(f"[FOUND P1] in {f.name} at offset 0x{idx1:x}")
    idx2 = data.find(p2)
    if idx2 != -1:
        print(f"[FOUND P2] in {f.name} at offset 0x{idx2:x}")

for f in ROOT.glob("local_only/**/*.bin"):
    if f.stat().st_size > 50_000_000: continue
    data = f.read_bytes()
    idx1 = data.find(p1)
    if idx1 != -1:
        print(f"[FOUND P1] in {f.name} at offset 0x{idx1:x}")
    idx2 = data.find(p2)
    if idx2 != -1:
        print(f"[FOUND P2] in {f.name} at offset 0x{idx2:x}")
