import capstone
import struct
from elftools.elf.elffile import ELFFile
import re

cs = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN)
toc = 0xc0014728

with open(r'C:\Users\remus\ps2-netemu-disc\local_only\analysis\p0h\modules\ss_server1.elf', 'rb') as f:
    elf = ELFFile(f)
    segments = list(elf.iter_segments())
    def va_to_file(va):
        for s in segments:
            v = s['p_vaddr']
            sz = s['p_memsz']
            if v <= va < v + sz:
                return s['p_offset'] + (va - v)
        return None

    def read_str(va):
        fo = va_to_file(va)
        if fo is None: return "NOT_MAPPED"
        f.seek(fo)
        chars = []
        for _ in range(64):
            b = f.read(1)
            if not b or b == b'\x00': break
            chars.append(b.decode('latin1', errors='replace'))
        return "".join(chars)

    f.seek(65536)
    code = f.read(0x59d10)

    base_va = 0x80000000
    start = 0x1f344
    end = 0x1f600

    for ins in cs.disasm(code[start:end], base_va + start):
        if 'r2' in ins.op_str:
            m = re.search(r'(-?0x[0-9a-fA-F]+)\(r2\)', ins.op_str)
            if m:
                off = int(m.group(1), 16)
                va = toc + off
                fo = va_to_file(va)
                if fo:
                    f.seek(fo)
                    ptr = struct.unpack('>Q', f.read(8))[0]
                    s = read_str(ptr)
                    print(f"0x{ins.address:x}: {ins.mnemonic:8s} {ins.op_str:20s} -> [0x{va:x}] = 0x{ptr:x} string: '{s}'")
                continue
        if ins.mnemonic in ['bl', 'bne', 'beq', 'cmpwi', 'cmpdi', 'li', 'b']:
            print(f"0x{ins.address:x}: {ins.mnemonic:8s} {ins.op_str}")
