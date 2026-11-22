#!/usr/bin/env python3
import struct
import capstone
from pathlib import Path

dump1 = Path(r"C:\Users\remus\ps2-netemu-disc\local_only\lv1_mem_100000_300000.bin").read_bytes()
BASE1 = 0x100000

cs = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN)

print("Searching for hypercall table and lv1_poked in lv1_mem_100000_300000.bin...")

# In Cobra / Evilnat CFW, HVSC 182 and 183 are custom hypercalls added by CFW (or peek/poke syscalls)!
# Wait! Are 182 and 183 standard Sony hypercalls, or are they added by Cobra / Evilnat?
# In PS3 CFW:
# Hypercall 182 (0xB6) = lv1_peekd
# Hypercall 183 (0xB7) = lv1_poked
# Let's search for lv1_poked implementation:
# typically:
#   std r4, 0(r3)
#   li r3, 0
#   blr
# In machine code:
#   f8 83 00 00  (std r4, 0(r3))
#   38 60 00 00  (li r3, 0)
#   4e 80 00 20  (blr)

target = bytes.fromhex("f8830000386000004e800020")
idx = dump1.find(target)
if idx >= 0:
    phys = BASE1 + idx
    print(f"FOUND lv1_poked pattern at phys 0x{phys:06X}!")
else:
    print("Exact 3-insn pattern not found, searching for std r4, 0(r3)...")
    for i in range(0, len(dump1) - 16, 4):
        if dump1[i:i+4] == bytes.fromhex("f8830000"):
            phys = BASE1 + i
            chunk = dump1[i:i+16]
            dis = list(cs.disasm(chunk, phys))
            mnems = " ; ".join(f"{ins.mnemonic} {ins.op_str}" for ins in dis)
            print(f"  [0x{phys:06X}] {mnems}")
