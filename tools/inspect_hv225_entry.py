import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

def disasm_func(elf_path, va_start, count, name):
    data = Path(elf_path).read_bytes()
    def va2off(va): return va - 0x200000 + 0x20000
    off = va2off(va_start)
    print(f"\n=================== {name} HV 225 Entry: {hex(va_start)} ===================")
    for i in range(count):
        pc = va_start + i * 4
        w = struct.unpack_from('>I', data, off + i * 4)[0]
        ins = decode_ppc(w, pc)
        mark = " ***" if any(k in ins for k in ["cmpi", "cmpli", "bl ", "b ", "blr", "0x100"]) else ""
        print(f"  {hex(pc)}:  {w:08x}  {ins}{mark}")

disasm_func('local_only/fw355/out/lv1.elf', 0x20d010, 45, 'FW 3.55 LV1')
disasm_func('local_only/fw493/lv1.elf', 0x20d060, 45, 'FW 4.93 LV1')
