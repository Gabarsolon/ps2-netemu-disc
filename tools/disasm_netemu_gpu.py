import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

data = Path('local_only/stock.elf').read_bytes()

def disasm_netemu(file_off_start, count=80):
    print(f"\nDisassembly of netemu at file off {hex(file_off_start)} (VA {hex(file_off_start - 0x10000)}):")
    for i in range(count):
        off = file_off_start + i * 4
        pc = off - 0x10000
        w = struct.unpack_from('>I', data, off)[0]
        ins = decode_ppc(w, pc)
        mark = " ***" if "bl " in ins or "r11" in ins or "sc " in ins or "cmpi" in ins else ""
        print(f"  {hex(pc)}:  {w:08x}  {ins}{mark}")

if __name__ == '__main__':
    disasm_netemu(0x236a0, 80)
