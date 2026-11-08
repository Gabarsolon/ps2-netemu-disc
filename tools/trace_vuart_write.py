import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import struct
from disasm_ppc import decode_ppc

# HV 163 in 3.55 LV1: func = 0x2eb298
# Let's find HV 163 in 4.93 LV1:
# Let's search registration record 163 in 4.93
data493 = Path('local_only/fw493/lv1.elf').read_bytes()
p163 = struct.pack('>QQ', 163, 0)
off = data493.find(p163)
print(f"4.93 HV 163 record at off {hex(off)} (VA {hex(off - 0x20000 + 0x200000)})")
# Find references to this VA
p_rec = struct.pack('>Q', off - 0x20000 + 0x200000)
ref = data493.find(p_rec)
print(f"  Referenced at off {hex(ref)} (VA {hex(ref - 0x20000 + 0x200000)})")
# Pair is (opd, rec) or (rec, opd)
# Look around ref
ref_va = ref - 0x20000 + 0x200000
for delta in [-16, -8, 8, 16]:
    val = struct.unpack_from('>Q', data493, ref + delta)[0]
    if 0x200000 <= val < 0x400000:
        val_off = val - 0x200000 + 0x20000
        f_addr, toc = struct.unpack_from('>QQ', data493, val_off)
        if 0x200000 <= f_addr < 0x400000:
            print(f"  delta={delta}: OPD at {hex(val)} -> func={hex(f_addr)}, toc={hex(toc)}")

def disasm_func(elf_path, va, count=80):
    data = Path(elf_path).read_bytes()
    off = va - 0x200000 + 0x20000
    print(f"\nDisassembly of {hex(va)} ({elf_path}):")
    for i in range(count):
        pc = va + i * 4
        w = struct.unpack_from('>I', data, off + i * 4)[0]
        ins = decode_ppc(w, pc)
        mark = " ***" if "bl " in ins or "cmpi" in ins or "r4" in ins else ""
        print(f"  {hex(pc)}:  {w:08x}  {ins}{mark}")

disasm_func('local_only/fw355/out/lv1.elf', 0x2eb298, 60)
