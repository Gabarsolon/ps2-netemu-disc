import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

data = Path('local_only/fw493/lv1.elf').read_bytes()
def va2off(va): return va - 0x200000 + 0x20000

for va in range(0x20d220, 0x20d360, 4):
    off = va2off(va)
    w = struct.unpack_from('>I', data, off)[0]
    ins = decode_ppc(w, va)
    mark = " ***" if any(k in ins for k in ["cmpi", "cmpli", "bl ", "b ", "blr", "0x100"]) else ""
    print(f"  {hex(va)}:  {w:08x}  {ins}{mark}")
