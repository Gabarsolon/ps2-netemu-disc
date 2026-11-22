#!/usr/bin/env python3
import os
import struct
import hashlib

path = r'C:\Users\remus\ps2-netemu-disc\local_only\lv1_mem_300000_700000.bin'
print(f"File size: {os.path.getsize(path)} bytes")

with open(path, 'rb') as f:
    data = f.read()

sha = hashlib.sha256(data).hexdigest()
print(f"SHA256: {sha}")

total_len = len(data)
block_size = 64 * 1024
print(f"\nAnalyzing density across {total_len // block_size} blocks of 64KB:")
active_blocks = []
for i in range(0, total_len, block_size):
    chunk = data[i:i+block_size]
    phys_addr = 0x300000 + i
    nz = sum(1 for b in chunk if b != 0)
    if nz > 0:
        active_blocks.append((phys_addr, nz))
        print(f"  [0x{phys_addr:06X} - 0x{phys_addr+block_size:06X}]: {nz:5d}/{block_size} non-zero bytes ({nz*100/block_size:.1f}%)")

print(f"\nTotal active 64KB blocks: {len(active_blocks)} / {total_len // block_size}")
