import os, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
stock_elf = ROOT / 'local_only' / 'stock.elf'
data = stock_elf.read_bytes()

# Find all bl to 0x111eb8
# bl instruction: 0x48000001 | (disp & 0x03fffffc)
# disp = target - pc => target = pc + sign_ext(disp)
target = 0x111eb8
print(f"Scanning stock.elf for calls to {hex(target)}...")

po, = struct.unpack_from('>Q', data, 32)
pn, = struct.unpack_from('>H', data, 56)

exec_segs = []
for i in range(pn):
    t, f, off, va, pa, fsz, msz, al = struct.unpack_from('>IIQQQQQQ', data, po + 56 * i)
    if t == 1 and (f & 1):  # executable
        exec_segs.append((off, va, fsz))

calls = []
for off, va, fsz in exec_segs:
    for pc in range(va, va + fsz, 4):
        file_off = off + (pc - va)
        w, = struct.unpack_from('>I', data, file_off)
        if (w & 0xFC000003) == 0x48000001:
            disp = w & 0x03FFFFFC
            if disp & 0x02000000:
                disp -= 0x04000000
            dest = pc + disp
            if dest == target:
                calls.append(pc)

print(f"Found {len(calls)} calls to 0x111eb8:")
for c in calls[:10]:
    print(f"  Call at {hex(c)}")

# Check caller at 0x12beb0 (HDD init)
# Let's inspect instructions preceding 0x12beb0
print("\nInstructions before HDD call at 0x12beb0:")
va = 0x12beb0
off_va = 0x10000 + va
for pc in range(va - 32, va + 8, 4):
    w, = struct.unpack_from('>I', data, 0x10000 + pc)
    print(f"  {hex(pc)}: {hex(w)}")
