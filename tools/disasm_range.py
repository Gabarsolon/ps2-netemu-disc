import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

def disasm_range(elf_path, start_va, end_va):
    data = Path(elf_path).read_bytes()
    def va2off(va): return va - 0x200000 + 0x20000
    off = va2off(start_va)
    count = (end_va - start_va) // 4
    for i in range(count):
        pc = start_va + i * 4
        w = struct.unpack_from('>I', data, off + i * 4)[0]
        ins_str = decode_ppc(w, pc)
        mark = " ***" if "r20" in ins_str or "bl " in ins_str or "cmpi" in ins_str or "cmpli" in ins_str else ""
        print(f"  {hex(pc)}:  {w:08x}  {ins_str}{mark}")

if __name__ == '__main__':
    disasm_range('local_only/fw355/out/lv1.elf', 0x20d380, 0x20d580)
