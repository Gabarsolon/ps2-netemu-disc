from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()

# 0x140b38 in file -> vaddr 0x320b38
meddling_va = 0x320b38
print(f"meddling at vaddr {hex(meddling_va)}")

# inspect surrounding bytes
p = 0x140b38
print("Surrounding strings:")
for i in range(p - 64, p + 128):
    if elf[i:i+8] == b'meddling':
        print(f"  {hex(i)}: {elf[i:i+20]}")

# search for references to meddling_va:
# 1. 64-bit pointer
p64 = struct.pack('>Q', meddling_va)
p32 = struct.pack('>I', meddling_va)
# 2. 8-byte ASCII packed into a register / constant:
# "meddling" in hex BE is 0x6d6564646c696e67!
packed_meddling = struct.pack('>Q', 0x6d6564646c696e67)

print(f"\nSearching for pointer to {hex(meddling_va)}:")
idx = 0
while True:
    pos = elf.find(p64, idx)
    if pos == -1: break
    va = pos - 0x20000 + 0x200000 if 0x20000 <= pos < 0x20000 + 0x1c2c00 else pos
    print(f"  p64 at file off {hex(pos)} (va {hex(va)})")
    idx = pos + 1

idx = 0
while True:
    pos = elf.find(p32, idx)
    if pos == -1: break
    va = pos - 0x20000 + 0x200000 if 0x20000 <= pos < 0x20000 + 0x1c2c00 else pos
    print(f"  p32 at file off {hex(pos)} (va {hex(va)})")
    idx = pos + 1

print(f"\nSearching for packed 8-byte constant 'meddling' (0x6d6564646c696e67):")
idx = 0
while True:
    pos = elf.find(packed_meddling, idx)
    if pos == -1: break
    va = pos - 0x20000 + 0x200000 if 0x20000 <= pos < 0x20000 + 0x1c2c00 else pos
    print(f"  packed 'meddling' at file off {hex(pos)} (va {hex(va)})")
    idx = pos + 1
