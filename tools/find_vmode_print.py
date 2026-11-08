from pathlib import Path
import struct
import sys
sys.path.insert(0, str(Path(__file__).parent))
from disasm_ppc import decode_ppc

data = Path('local_only/stock.elf').read_bytes()

# Search for ld rD, -208(r2) (simm16 = -208 = 0xff30)
# opcode 58: (58 << 26) | (rD << 21) | (2 << 16) | 0xff30
for rD in range(32):
    ins_word = (58 << 26) | (rD << 21) | (2 << 16) | 0xff30
    p = struct.pack('>I', ins_word)
    pos = 0
    while True:
        pos = data.find(p, pos)
        if pos == -1: break
        va = pos - 0x10000
        print(f"Found ld r{rD}, -208(r2) at off {hex(pos)} (VA {hex(va)})")
        pos += 1
