import struct
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
stock_elf = ROOT / 'local_only' / 'stock.elf'
data = stock_elf.read_bytes()

# Load segments
phoff = struct.unpack_from('>Q', data, 32)[0]
phnum = struct.unpack_from('>H', data, 56)[0]
segs = []
for i in range(phnum):
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, phoff + i * 56)
    if p_type == 1:
        segs.append((p_vaddr, p_offset, p_filesz))

def va_to_off(va):
    for vaddr, off, sz in segs:
        if vaddr <= va < vaddr + sz:
            return off + (va - vaddr)
    return None

def find_branches_to(target):
    branches = []
    for vaddr, off, sz in segs:
        seg_bytes = data[off:off+sz]
        for pos in range(0, sz - 3, 4):
            w = struct.unpack_from('>I', seg_bytes, pos)[0]
            opcode = w >> 26
            if opcode == 18:
                lk = w & 1
                aa = w & 2
                li = (w & 0x03fffffc)
                if li & 0x02000000:
                    li -= 0x04000000
                cur_va = vaddr + pos
                dest = cur_va + li if aa == 0 else li
                if dest == target:
                    branches.append((cur_va, lk))
    return branches

callers = find_branches_to(0x1ecc5c)

# Let's use pyghidra or disassembler to check the 8 instructions before each call
import os, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
GH_DIR = ROOT / 'local_only' / 'ghidra_p3a'
TMP_DIR = GH_DIR / 'tmp'
SETTINGS_DIR = GH_DIR / 'settings'
PROJECTS_DIR = GH_DIR / 'projects'
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher

launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G', '-Duser.home='+str(SETTINGS_DIR), '-Dapplication.settingsdir='+str(SETTINGS_DIR), '-Djava.io.tmpdir='+str(TMP_DIR))
launcher.start()
from ghidra.app.util import PseudoDisassembler

with pyghidra.open_program(str(stock_elf), project_location=str(PROJECTS_DIR), project_name='stock_p3a', analyze=False, language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    space = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)
    
    for c_va, lk in callers[:10]:
        print(f"=== Caller at 0x{c_va:x} ===")
        # disassemble 8 instructions before call
        addr = space.getAddress(c_va - 32)
        for _ in range(9):
            ins = pd.disassemble(addr)
            txt = ins.toString() if ins else "???"
            print(f"  0x{addr.getOffset():08x}: {txt}")
            addr = addr.add(4)
