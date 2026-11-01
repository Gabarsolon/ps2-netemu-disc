import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p2e'
TMP_DIR = GH / 'tmp'
SETTINGS_DIR = GH / 'settings'

for k in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[k] = str(TMP_DIR if k in ['TEMP', 'TMP', 'TMPDIR'] else SETTINGS_DIR)

os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'
sys.path = [p for p in sys.path if not Path(p).resolve().name.lower() == 'local_only']

import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher

launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs(
    '-Xmx3G',
    '-Duser.home=' + str(SETTINGS_DIR),
    '-Dapplication.settingsdir=' + str(SETTINGS_DIR),
    '-Djava.io.tmpdir=' + str(TMP_DIR)
)
launcher.start()

from ghidra.app.util import PseudoDisassembler

def disassemble_range(p, start_ea, end_ea):
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)
    addr = s.getAddress(start_ea)
    end = s.getAddress(end_ea)
    lines = []
    while addr.compareTo(end) < 0:
        ins = pd.disassemble(addr)
        if ins is None:
            addr = addr.add(4)
            continue
        txt = ins.toString()
        lines.append((addr.getOffset(), txt))
        addr = addr.add(ins.getLength())
    return lines

stock_elf = ROOT / 'local_only' / 'stock.elf'
with pyghidra.open_program(str(stock_elf), project_location=str(GH / 'projects'),
                           project_name='stock_p2e_analysis', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()

    print("=== HDD driver references to 0x20(r30/r31/r28) and 0x28(r30/r31/r28) ===")
    hdd_ins = disassemble_range(p, 0x12b000, 0x12d000)
    for off, txt in hdd_ins:
        if any(f",0x20(" in txt or f",0x28(" in txt for _ in [1]):
            print(f"  0x{off:06x}: {txt}")
