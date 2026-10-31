import os, sys, warnings
from pathlib import Path
ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
GH = ROOT / 'local_only' / 'ghidra_p1e'
STOCK = ROOT / 'local_only' / 'stock.elf'
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'
warnings.filterwarnings('ignore', category=DeprecationWarning)
import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G',
                    '-Duser.home=' + str(GH / 'settings'),
                    '-Dapplication.settingsdir=' + str(GH / 'settings'),
                    '-Djava.io.tmpdir=' + str(GH / 'tmp'))
launcher.start()
from ghidra.app.util import PseudoDisassembler
with pyghidra.open_program(str(STOCK), project_location=str(GH / 'projects'),
                           project_name='stock_p1e', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    space = p.getAddressFactory().getDefaultAddressSpace()
    pdis = PseudoDisassembler(p)
    addr = space.getAddress(0x0c00)
    for _ in range(25):
        inst = pdis.disassemble(addr)
        if inst:
            print(f"0x{addr.getOffset():08x}: {inst.toString()}")
            addr = addr.add(inst.getLength())
