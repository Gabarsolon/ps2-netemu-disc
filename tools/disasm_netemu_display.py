import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

data = Path('local_only/stock.elf').read_bytes()

def disasm_netemu(va_start, count=50):
    file_off = va_start + 0x10000
    print(f"\nDisassembly of netemu at VA {hex(va_start)}:")
    for i in range(count):
        off = file_off + i * 4
        pc = va_start + i * 4
        w = struct.unpack_from('>I', data, off)[0]
        ins = decode_ppc(w, pc)
        mark = " ***" if "bl " in ins or "r11" in ins or "sc " in ins or "cmpi" in ins else ""
        print(f"  {hex(pc)}:  {w:08x}  {ins}{mark}")

if __name__ == '__main__':
    disasm_netemu(0x14b830, 40)
    disasm_netemu(0x1525d0, 40)
