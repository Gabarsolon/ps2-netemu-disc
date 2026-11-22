#!/usr/bin/env python3
from pathlib import Path
import struct

dump = Path(r"C:\Users\remus\ps2-netemu-disc\local_only\lv1_mem_300000_700000.bin").read_bytes()
BASE = 0x300000

off = 0x540200 - BASE
print("Table entries around 0x540200:")
for i in range(-10, 20):
    entry_off = off + i * 16
    entry_phys = BASE + entry_off
    w0, w1, w2, w3 = struct.unpack_from(">IIII", dump, entry_off)
    print(f"  [0x{entry_phys:06X}] ID=0x{w0:08X}  W1=0x{w1:08X}  W2=0x{w2:08X}  W3=0x{w3:08X}")
