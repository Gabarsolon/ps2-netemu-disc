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

def find_pointers_to(target):
    target_bytes = struct.pack('>Q', target)
    ptrs = []
    for vaddr, off, sz in segs:
        seg_bytes = data[off:off+sz]
        idx = 0
        while True:
            idx = seg_bytes.find(target_bytes, idx)
            if idx == -1: break
            ptrs.append(vaddr + idx)
            idx += 8
    return ptrs

print("=== Pointers to 0x948a68 (vtable) ===")
for p in find_pointers_to(0x948a68):
    print(f"Pointer at 0x{p:x}")

# Let's inspect instructions in 0x270c24
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
    addr = space.getAddress(0x270c24)
    print("=== Disassembly of 0x270C24 first 40 ins ===")
    for _ in range(40):
        ins = pd.disassemble(addr)
        print(f"  0x{addr.getOffset():08x}: {ins.toString() if ins else '???'}")
        addr = addr.add(ins.getLength())
