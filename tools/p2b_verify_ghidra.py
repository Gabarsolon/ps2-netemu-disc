import os, sys, hashlib, warnings
from pathlib import Path

warnings.filterwarnings('ignore', category=DeprecationWarning)
ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
GH_DIR = ROOT / 'local_only' / 'ghidra_p2b'
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

def disassemble_range(p, start_ea, count=40):
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)
    addr = s.getAddress(start_ea)
    lines = []
    for _ in range(count):
        ins = pd.disassemble(addr)
        if ins is None:
            lines.append(f"0x{addr.getOffset():08x}: <unable to disassemble>")
            addr = addr.add(4)
            continue
        lines.append(f"0x{addr.getOffset():08x}: {ins.toString()}")
        addr = addr.add(ins.getLength())
    return "\n".join(lines)

def analyze_stock():
    stock_path = ROOT / 'local_only' / 'stock.elf'
    with pyghidra.open_program(
        str(stock_path),
        project_location=str(GH_DIR / 'projects'),
        project_name='stock_netemu_p2b_disas',
        analyze=False,
        language='PowerPC:BE:64:default'
    ) as flat:
        p = flat.getCurrentProgram()
        print("--- 0x17700 disassembly ---")
        dis = disassemble_range(p, 0x17700, 40)
        print(dis)
        (ROOT / 'local_only' / 'ghidra_p2b' / '0x17700_disas.txt').write_text(dis, encoding='utf-8')

if __name__ == '__main__':
    analyze_stock()
