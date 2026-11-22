#!/usr/bin/env python3
import struct
import capstone

cs = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN)

# Trampoline base address in Cobra RAM: 0x0053BD00
# Target to resume: 0x005308D8 (or 0x005308D4)

# Data table at 0x0053BD80:
# [0] 0x00713210 (phys addr 1)
# [1] 0x48000164e92296c0 (patch 1)
# [2] 0x00714710 (phys addr 2)
# [3] 0x4800001c7fc3f378 (patch 2)
# [4] 0x8000000014713210 (kernel EA 1 for cache sync)
# [5] 0x8000000014714710 (kernel EA 2 for cache sync)

# Let's write the assembly:
asm_lines = [
    # 0x0053bd00: Anchor PC into r12
    (0x48000005, "bl +4"),
    (0x7d8802a6, "mflr r12"),                 # r12 = 0x0053BD04

    # Patch 1: ss_server1 FW check via HVSC 183
    (0xe86c007c, "ld r3, 0x7c(r12)"),         # r3 = phys 0x00713210 (at 0x53bd80)
    (0xe88c0084, "ld r4, 0x84(r12)"),         # r4 = val 1 (at 0x53bd88)
    (0x396000b7, "li r11, 183"),              # HVSC 183
    (0x44000022, "sc 1"),                     # lv1_poked(0x713210, val1)

    # Patch 2: ss_server1 Profile check via HVSC 183
    (0x48000005, "bl +4"),
    (0x7d8802a6, "mflr r12"),                 # r12 = current PC
    (0xe86c006c, "ld r3, 0x6c(r12)"),         # r3 = phys 0x00714710 (at 0x53bd90)
    (0xe88c0074, "ld r4, 0x74(r12)"),         # r4 = val 2 (at 0x53bd98)
    (0x396000b7, "li r11, 183"),              # HVSC 183
    (0x44000022, "sc 1"),                     # lv1_poked(0x714710, val2)

    # Cache sync for Patch 1:
    (0x48000005, "bl +4"),
    (0x7d8802a6, "mflr r12"),                 # r12 = current PC
    (0xe86c005c, "ld r3, 0x5c(r12)"),         # r3 = EA 0x8000000014713210 (at 0x53bda0)
    (0x7c0018ac, "dcbf 0, r3"),               # flush D-cache
    (0x7c0004ac, "sync"),                     # memory barrier
    (0x7c001fac, "icbi 0, r3"),               # invalidate I-cache
    (0x4c00012c, "isync"),                    # pipeline refetch

    # Cache sync for Patch 2:
    (0x48000005, "bl +4"),
    (0x7d8802a6, "mflr r12"),                 # r12 = current PC
    (0xe86c0044, "ld r3, 0x44(r12)"),         # r3 = EA 0x8000000014714710 (at 0x53bda8)
    (0x7c0018ac, "dcbf 0, r3"),               # flush D-cache
    (0x7c0004ac, "sync"),                     # memory barrier
    (0x7c001fac, "icbi 0, r3"),               # invalidate I-cache
    (0x4c00012c, "isync"),                    # pipeline refetch

    # Displaced stock instruction from 0x005308D4:
    (0xf8410028, "std r2, 0x28(r1)"),         # stock instruction

    # Branch back to 0x005308D8:
    # Target 0x005308D8 from current PC
]

print(f"Total instructions: {len(asm_lines)} ({len(asm_lines)*4} bytes)")
