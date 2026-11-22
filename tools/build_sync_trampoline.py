#!/usr/bin/env python3
import struct
import capstone

cs = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN)

TRAMPOLINE_BASE = 0x0053BD00
DATA_TABLE_BASE = 0x0053BD80

# Data table entries (8 bytes each):
# +0x00: 0x0000000000713210 (phys 1)
# +0x08: 0x48000164e92296c0 (patch 1)
# +0x10: 0x0000000000714710 (phys 2)
# +0x18: 0x4800001c7fc3f378 (patch 2)
# +0x20: 0x8000000014713210 (kernel EA 1)
# +0x28: 0x8000000014714710 (kernel EA 2)

data_table = struct.pack(
    ">QQQQQQ",
    0x0000000000713210,
    0x48000164e92296c0,
    0x0000000000714710,
    0x4800001c7fc3f378,
    0x8000000014713210,
    0x8000000014714710,
)

# We can simplify the trampoline:
# anchor r12 ONCE at the start!
# r12 = DATA_TABLE_BASE (0x0053BD80) in 64-bit kernel EA!
# How?
# bl +4
# mflr r12   (r12 = 0x0053BD04)
# addi r12, r12, (0x0053BD80 - 0x0053BD04) = 0x7C!
# Now r12 points directly to DATA_TABLE_BASE!
# Then:
# ld r3, 0x00(r12)  (phys 1)
# ld r4, 0x08(r12)  (patch 1)
# li r11, 183
# sc 1
# ld r3, 0x10(r12)  (phys 2)
# ld r4, 0x18(r12)  (patch 2)
# li r11, 183
# sc 1
# ld r3, 0x20(r12)  (EA 1)
# dcbf 0, r3
# sync
# icbi 0, r3
# isync
# ld r3, 0x28(r12)  (EA 2)
# dcbf 0, r3
# sync
# icbi 0, r3
# isync
# std r2, 0x28(r1)  (displaced stock instruction)
# b 0x005308D8      (resume Cobra)

insns = []
def emit(op_hex):
    insns.append(bytes.fromhex(op_hex))

def branch_opcode(pc, target):
    delta = target - pc
    val = (18 << 26) | (delta & 0x03FFFFFC)
    return struct.pack(">I", val).hex()

# 0x0053bd00:
emit("48000005")  # bl +4
# 0x0053bd04:
emit("7d8802a6")  # mflr r12
# 0x0053bd08:
emit("398c007c")  # addi r12, r12, 0x7c (r12 = 0x0053BD80)

# Patch 1:
emit("e86c0000")  # ld r3, 0(r12)
emit("e88c0008")  # ld r4, 8(r12)
emit("396000b7")  # li r11, 183
emit("44000022")  # sc 1

# Patch 2:
emit("e86c0010")  # ld r3, 0x10(r12)
emit("e88c0018")  # ld r4, 0x18(r12)
emit("396000b7")  # li r11, 183
emit("44000022")  # sc 1

# Cache sync 1:
emit("e86c0020")  # ld r3, 0x20(r12)
emit("7c0018ac")  # dcbf 0, r3
emit("7c0004ac")  # sync
emit("7c001fac")  # icbi 0, r3
emit("4c00012c")  # isync

# Cache sync 2:
emit("e86c0028")  # ld r3, 0x28(r12)
emit("7c0018ac")  # dcbf 0, r3
emit("7c0004ac")  # sync
emit("7c001fac")  # icbi 0, r3
emit("4c00012c")  # isync

# Displaced instruction from 0x005308D4:
emit("f8410028")  # std r2, 0x28(r1)

# Branch back to 0x005308D8:
cur_pc = TRAMPOLINE_BASE + len(insns) * 4
b_hex = branch_opcode(cur_pc, 0x005308D8)
emit(b_hex)

code = b"".join(insns)
print(f"Trampoline size: {len(code)} bytes ({len(insns)} instructions)")
print("Disassembly:")
for ins in cs.disasm(code, TRAMPOLINE_BASE):
    print(f"  0x{ins.address:08X}: {ins.bytes.hex()}  {ins.mnemonic:8s} {ins.op_str}")

assert len(code) <= 0x80, f"Trampoline too large: {len(code)} > 128 bytes"
print("\nValidation passed! Clean, compact, single-anchor PIC trampoline.")
