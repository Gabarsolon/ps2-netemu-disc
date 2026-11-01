import os, sys, warnings
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
GH_DIR = ROOT / 'local_only' / 'ghidra_p3a'
TMP_DIR = GH_DIR / 'tmp'
SETTINGS_DIR = GH_DIR / 'settings'
PROJECTS_DIR = GH_DIR / 'projects'

for k in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[k] = str(TMP_DIR if k in ['TEMP', 'TMP', 'TMPDIR'] else SETTINGS_DIR)

os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

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

def main():
    stock_path = ROOT / 'local_only' / 'stock.elf'
    with pyghidra.open_program(
        str(stock_path),
        project_location=str(PROJECTS_DIR),
        project_name='stock_p3a',
        analyze=False,
        language='PowerPC:BE:64:default'
    ) as flat:
        p = flat.getCurrentProgram()
        space = p.getAddressFactory().getDefaultAddressSpace()
        pd = PseudoDisassembler(p)
        
        print("=== Checking 0x1ED744 onwards ===")
        addr = space.getAddress(0x1ed744)
        for i in range(120):
            ins = pd.disassemble(addr)
            if ins is None:
                print(f"0x{addr.getOffset():08x}: <none>")
                addr = addr.add(4)
                continue
            txt = ins.toString()
            print(f"0x{addr.getOffset():08x}: {txt}")
            addr = addr.add(ins.getLength())
            if "blr" in txt and i > 40:
                print(f"--- blr at 0x{addr.getOffset()-4:08x} ---")
                break

if __name__ == '__main__':
    main()
