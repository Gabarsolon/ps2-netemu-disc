import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

data = Path('local_only/fw493/lv1.elf').read_bytes()
def va2off(va): return va - 0x200000 + 0x20000

for va in range(0x213998, 0x213ad8, 4):
    off = va2off(va)
    w = struct.unpack_from('>I', data, off)[0]
    ins = decode_ppc(w, va)
    print(f"  {hex(va)}:  {w:08x}  {ins}")
