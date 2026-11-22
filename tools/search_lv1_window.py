#!/usr/bin/env python3
import re
from pathlib import Path

dump_path = Path(r"C:\Users\remus\ps2-netemu-disc\local_only\lv1_mem_300000_700000.bin")
data = dump_path.read_bytes()
BASE = 0x300000

print(f"Searching strings and signatures in {dump_path.name} (phys 0x300000..0x700000)...")

# 1. Search for SCE or ss_ or sysmgr strings
strings = set()
for match in re.finditer(b"[\x20-\x7E]{6,}", data):
    s = match.group().decode('ascii')
    off = match.start()
    phys = BASE + off
    if any(k in s.lower() for k in ["ss_", "sysmgr", "cell", "vuart", "port", "auth", "disc", "rbd", "scsi", "storage", "device"]):
        print(f"  [phys 0x{phys:06X}] string: \"{s[:80]}\"")

# 2. Check for ELF magic (\x7fELF)
for match in re.finditer(b"\x7fELF", data):
    off = match.start()
    phys = BASE + off
    print(f"  *** ELF HEADER found at phys 0x{phys:06X} (off 0x{off:06X}) ***")

# 3. Check for specific opcodes (0x5000, 0x5005, 0x5004)
print("\nSearching for 0x5005 / 0x5004 / 0x5000 32-bit / 64-bit constants:")
for val in [0x5005, 0x5004, 0x5000]:
    b32 = val.to_bytes(4, 'big')
    b64 = val.to_bytes(8, 'big')
    c32 = len(list(re.finditer(re.escape(b32), data)))
    c64 = len(list(re.finditer(re.escape(b64), data)))
    print(f"  Constant 0x{val:04X}: {c32} 32-bit occurrences, {c64} 64-bit occurrences")
