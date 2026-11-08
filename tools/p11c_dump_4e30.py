from pathlib import Path
import struct
from elftools.elf.elffile import ELFFile

ROOT = Path('.').resolve()
ss1_elf = ROOT / 'local_only' / 'analysis' / 'p0i' / 'modules' / 'ss_server1.elf'
data = ss1_elf.read_bytes()

with open(ss1_elf, 'rb') as f:
    e = ELFFile(f)
    for seg in e.iter_segments():
        if seg['p_type'] == 'PT_LOAD':
            s_va = seg['p_vaddr']
            s_sz = seg['p_memsz']
            if s_va <= 0x80024e30 < s_va + s_sz:
                off = seg['p_offset'] + (0x80024e30 - s_va)
                code = data[off : off + 0xc0]
                break

# Let's inspect 32-bit instructions
import subprocess
# We can use llvm-objdump or pyghidra or a simple PPC disasm
print("Bytes of _opd_FUN_80024e30:")
for i in range(0, len(code), 4):
    w, = struct.unpack('>I', code[i:i+4])
    print(f"0x{0x80024e30 + i:x}: 0x{w:08x}")
