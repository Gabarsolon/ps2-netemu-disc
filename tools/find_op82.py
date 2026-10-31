from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
code = elf[0x10000:0x10000 + 0x3f6c8]

print("=== Searching for cmpi/cmpwi with 0x82 ===")
for i in range(0, len(code), 4):
    w = struct.unpack_from('>I', code, i)[0]
    # cmplwi is op 10 (0x0a), cmpwi is op 11 (0x0b)
    op = w >> 26
    if op in (10, 11):
        imm = w & 0xffff
        if imm == 0x82:
            va = 0x80000000 + i
            print(f"  va {hex(va)}: cmpwi/cmplwi with 0x82 (word: {hex(w)})")
