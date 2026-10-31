from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()
code = elf[0x20000:0x20000 + 0x1c2c00]

target_va = 0x354510
p64 = struct.pack('>Q', target_va)

print(f"=== Searching for references to {hex(target_va)} ===")
p = 0
while True:
    idx = elf.find(p64, p)
    if idx == -1: break
    va = idx - 0x20000 + 0x200000
    print(f"  Pointer64 at va {hex(va)}")
    p = idx + 1

# Also check lis/addi or lis/ori to meddling_va (0x320b38)
hi = (0x320b38 >> 16) & 0xffff
lo = 0x320b38 & 0xffff
if lo >= 0x8000: hi += 1

print(f"\nSearching for lis/addi to 0x320b38 (hi={hex(hi)}, lo={hex(lo)}):")
for i in range(0, len(code) - 8, 4):
    w1 = struct.unpack_from('>I', code, i)[0]
    if (w1 >> 26) == 15 and ((w1 >> 16) & 0x1f) == 0 and (w1 & 0xffff) == (hi & 0xffff):
        rD = (w1 >> 21) & 0x1f
        w2 = struct.unpack_from('>I', code, i + 4)[0]
        if (w2 >> 26) == 14 and ((w2 >> 16) & 0x1f) == rD and (w2 & 0xffff) == lo:
            va = 0x200000 + i
            print(f"  lis/addi at va {hex(va)}")

# Also search for lis/addi or lis/ori to 0x354510
hi2 = (0x354510 >> 16) & 0xffff
lo2 = 0x354510 & 0xffff
if lo2 >= 0x8000: hi2 += 1
print(f"\nSearching for lis/addi to 0x354510 (hi={hex(hi2)}, lo={hex(lo2)}):")
for i in range(0, len(code) - 8, 4):
    w1 = struct.unpack_from('>I', code, i)[0]
    if (w1 >> 26) == 15 and ((w1 >> 16) & 0x1f) == 0 and (w1 & 0xffff) == (hi2 & 0xffff):
        rD = (w1 >> 21) & 0x1f
        w2 = struct.unpack_from('>I', code, i + 4)[0]
        if (w2 >> 26) == 14 and ((w2 >> 16) & 0x1f) == rD and (w2 & 0xffff) == lo2:
            va = 0x200000 + i
            print(f"  lis/addi at va {hex(va)}")
