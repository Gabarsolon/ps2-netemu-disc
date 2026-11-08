import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p11'
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

def disasm(p, ea, count):
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)
    addr = s.getAddress(ea)
    for _ in range(count):
        ins = pd.disassemble(addr)
        if not ins: break
        print(f"0x{addr.getOffset():08x}: {ins}")
        addr = addr.add(ins.getLength())

softemu_elf = ROOT / 'local_only' / 'fw355' / 'out' / 'ps2_softemu.elf'
with pyghidra.open_program(str(softemu_elf), project_location=str(GH / 'projects'),
                           project_name='p11_softemu', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    for target in [0x84ec0, 0x86630, 0x87940]:
        print(f"\n--- Disassembly around {hex(target)} ---")
        disasm(p, target, 35)
