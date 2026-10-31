"""Check HDD init error path at 0x12c050 and repository lookup in 0x12be04."""
from pathlib import Path
import json, os, warnings

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT / 'local_only' / 'ghidra'
for key in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA'):
    os.environ[key] = str(GH / ('tmp' if key in ('TEMP','TMP','TMPDIR') else 'settings'))
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'
warnings.filterwarnings('ignore', category=DeprecationWarning)
import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G', '-Duser.home='+str(GH/'settings'),
                   '-Dapplication.settingsdir='+str(GH/'settings'),
                   '-Djava.io.tmpdir='+str(GH/'tmp'))
launcher.start()
from ghidra.app.util import PseudoDisassembler

STOCK = ROOT / 'local_only' / 'stock.elf'

with pyghidra.open_program(str(STOCK), project_location=str(GH/'projects'),
                          project_name='stock_63f12b7e', analyze=False,
                          language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    listing = p.getListing()
    space = p.getAddressFactory().getDefaultAddressSpace()
    mem = p.getMemory()
    addr = lambda n: space.getAddress(n)
    pd = PseudoDisassembler(p)

    def ins(n):
        x = listing.getInstructionAt(addr(n))
        if x is None:
            try: x = pd.disassemble(addr(n))
            except Exception: pass
        return str(x) if x else None

    def word_at(n):
        return mem.getInt(addr(n)) & 0xffffffff

    print("=== Disassembly at 0x12c050 (error branch of open_device in HDD init) ===")
    for i in range(20):
        c = 0x12c050 + i * 4
        print(f"0x{c:06x}: {word_at(c):08x}  {ins(c)}")

    print("\n=== Disassembly of HDD init repository reads (0x12be70..0x12bf40) ===")
    for i in range(35):
        c = 0x12be70 + i * 4
        print(f"0x{c:06x}: {word_at(c):08x}  {ins(c)}")
