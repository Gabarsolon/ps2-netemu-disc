from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()
code = elf[0x20000:0x20000 + 0x1c2c00]

target_va = 0x3c2910 # HV 170 registration
p64 = struct.pack('>Q', target_va)
p32 = struct.pack('>I', target_va)

print(f"=== Searching for references to HV 170 record {hex(target_va)} ===")
p = 0
while True:
    idx = elf.find(p64, p)
    if idx == -1: break
    va = idx - 0x20000 + 0x200000
    print(f"  p64 at va {hex(va)}")
    p = idx + 1

# Check lis/addi to 0x3c2910 or 0x3c2918
for target in [0x3c2910, 0x3c2918, 0x3c2920, 0x3c2928]:
    hi = (target >> 16) & 0xffff
    lo = target & 0xffff
    if lo >= 0x8000: hi += 1
    for i in range(0, len(code) - 8, 4):
        w1 = struct.unpack_from('>I', code, i)[0]
        if (w1 >> 26) == 15 and ((w1 >> 16) & 0x1f) == 0 and (w1 & 0xffff) == (hi & 0xffff):
            rD = (w1 >> 21) & 0x1f
            w2 = struct.unpack_from('>I', code, i + 4)[0]
            if (w2 >> 26) == 14 and ((w2 >> 16) & 0x1f) == rD and (w2 & 0xffff) == lo:
                va = 0x200000 + i
                print(f"  lis/addi to {hex(target)} at va {hex(va)}")
