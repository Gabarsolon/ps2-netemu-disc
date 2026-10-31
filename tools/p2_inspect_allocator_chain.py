import os, sys, warnings
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
GH_DIR = ROOT / 'local_only' / 'ghidra_p2'
TMP_DIR = GH_DIR / 'tmp'
SETTINGS_DIR = GH_DIR / 'settings'

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

def disassemble_func(p, start_ea, count=50):
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)
    addr = s.getAddress(start_ea)
    lines = []
    for _ in range(count):
        ins = pd.disassemble(addr)
        if ins is None:
            break
        lines.append(f"0x{addr.getOffset():08x}: {ins.toString()}")
        if ins.getMnemonicString() == 'blr':
            break
        addr = addr.add(ins.getLength())
    return "\n".join(lines)

def run():
    stock_path = ROOT / 'local_only' / 'stock.elf'
    with pyghidra.open_program(
        str(stock_path),
        project_location=str(GH_DIR / 'projects'),
        project_name='stock_netemu',
        analyze=False,
        language='PowerPC:BE:64:default'
    ) as flat:
        p = flat.getCurrentProgram()
        print("=== 0x19900..0x199f0 ===")
        print(disassemble_func(p, 0x19900, 60))
        print("=== 0x1622c..0x16320 ===")
        print(disassemble_func(p, 0x1622c, 60))

if __name__ == '__main__':
    run()
