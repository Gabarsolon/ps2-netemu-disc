import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

def analyze_attr_dispatcher(elf_path, func_va, name, count=180):
    data = Path(elf_path).read_bytes()
    def va2off(va): return va - 0x200000 + 0x20000
    off = va2off(func_va)
    print(f"\n=================== {name}: Attr Dispatcher {hex(func_va)} ===================")
    for i in range(count):
        pc = func_va + i * 4
        w = struct.unpack_from('>I', data, off + i * 4)[0]
        ins = decode_ppc(w, pc)
        # Highlight cmpi, cmpli, branches, calls
        mark = ""
        for tag in ["0x100", "0x101", "0x102", "0x200", "0x301", "0x600", "0x601", " 256", " 257", " 258", " 512", " 769", " 1536"]:
            if tag in ins:
                mark = f" <--- {tag}"
        if "cmpi" in ins or "cmpli" in ins or "bl " in ins:
            mark += " *"
        print(f"  {hex(pc)}:  {w:08x}  {ins}{mark}")

if __name__ == '__main__':
    analyze_attr_dispatcher('local_only/fw355/out/lv1.elf', 0x21340c, 'FW 3.55 LV1')
    analyze_attr_dispatcher('local_only/fw493/lv1.elf', 0x213998, 'FW 4.93 LV1')
