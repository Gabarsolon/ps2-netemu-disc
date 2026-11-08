import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

def disasm_vsh(va, count=60):
    data = Path('local_only/fw355/out/vsh.elf').read_bytes()
    off = va - 0x10000
    print(f"\nDisassembly of {hex(va)} (file off {hex(off)}):")
    for i in range(count):
        pc = va + i * 4
        w = struct.unpack_from('>I', data, off + i * 4)[0]
        ins = decode_ppc(w, pc)
        mark = " ***" if "bl " in ins or "sc" in ins or "cmpi" in ins else ""
        print(f"  {hex(pc)}:  {w:08x}  {ins}{mark}")

if __name__ == '__main__':
    disasm_vsh(0x5f1cd4, 40)
    disasm_vsh(0x5ee3e4, 40)
