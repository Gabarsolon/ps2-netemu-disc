import struct
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from disasm_ppc import decode_ppc

data = Path('local_only/stock.elf').read_bytes()

# Find which instructions in stock.elf reference the pointer at 0x759298
# In stock.elf, r2 is the TOC pointer.
# Let's find what value r2 has in the function that calls this, or search for ld rX, simm16(r2)
# Let's find r2 value first:
# Look around entry points or search for 'addis r2, r12, ...' or 'ld r2, ...'
for i in range(0x10000, 0x40000, 4):
    w = struct.unpack_from('>I', data, i)[0]
    if (w >> 26) == 15 and ((w >> 21) & 0x1f) == 2: # addis r2, ...
        simm = w & 0xffff
        if simm >= 0x8000: simm -= 0x10000
        w2 = struct.unpack_from('>I', data, i + 4)[0]
        simm2 = w2 & 0xffff
        if simm2 >= 0x8000: simm2 -= 0x10000
        print(f"r2 setup at off {hex(i)}: addis r2 = {simm}, addi = {simm2} -> TOC ~ {hex((simm<<16) + simm2)}")
        break

# Or we can search for the offset of 0x749298 relative to common TOCs
# In 64-bit ELF, TOC is typically around 0x750000..0x760000
# If TOC is T, then offset = 0x749298 - T
# If -0x8000 <= offset < 0x8000:
# ld rX, offset(r2) has opcode 58, rA=2, simm16 = offset & 0xfffc
for T in range(0x740000, 0x760000, 0x1000):
    diff = 0x749298 - T
    if -0x8000 <= diff < 0x8000:
        simm = diff & 0xfffc
        # search for ld rX, simm(r2)
        # opcode 58, rA=2: w = (58 << 26) | (rD << 21) | (2 << 16) | (simm & 0xffff)
        for rD in range(32):
            target_ins = (58 << 26) | (rD << 21) | (2 << 16) | (simm & 0xffff)
            p = struct.pack('>I', target_ins)
            pos = 0
            while True:
                pos = data.find(p, pos)
                if pos == -1: break
                va = pos - 0x10000
                print(f"Found ld r{rD}, {diff}(r2) [TOC={hex(T)}] at off {hex(pos)} (VA {hex(va)})")
                pos += 1
