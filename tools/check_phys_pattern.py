from pathlib import Path
import struct

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
mem_path = ROOT / "local_only" / "lv1_mem_700000_800000.bin"
mem = mem_path.read_bytes()

# Pattern from 0x80020700:
# lwz r9, 112(r1)  => 81 21 00 70
# addis r9, r9, -1 => 3d 29 ff ff
# addi r9, r9, 160 => 39 29 00 a0
# cmpli cr7, 0, r9, 1 => 2b 89 00 01
pattern = bytes.fromhex("812100703d29ffff392900a02b890001")

pos = 0
found = []
while True:
    pos = mem.find(pattern, pos)
    if pos == -1: break
    phys = 0x700000 + pos
    found.append(phys)
    print(f"Found pattern at dump offset 0x{pos:x} -> physical address 0x{phys:08x}")
    # Print next 8 bytes
    w1, w2 = struct.unpack_from(">II", mem, pos + 16)
    print(f"  Word at phys 0x{phys+16:08x}: 0x{w1:08x} (0x{w2:08x})")
    pos += 1

print(f"Total occurrences: {len(found)}")
