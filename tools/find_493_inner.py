import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

def find_inner_dispatch(elf_path, start_va, end_va):
    data = Path(elf_path).read_bytes()
    def va2off(va): return va - 0x200000 + 0x20000
    off = va2off(start_va)
    count = (end_va - start_va) // 4
    for i in range(count):
        pc = start_va + i * 4
        w = struct.unpack_from('>I', data, off + i * 4)[0]
        ins_str = decode_ppc(w, pc)
        if "bl " in ins_str or "r20" in ins_str:
            print(f"  {hex(pc)}:  {w:08x}  {ins_str}")

if __name__ == '__main__':
    print("4.93 LV1 inner dispatch search:")
    find_inner_dispatch('local_only/fw493/lv1.elf', 0x20d060, 0x20d480)
