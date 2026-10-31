import os, sys, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p1f'
GH.mkdir(parents=True, exist_ok=True)
(GH / 'projects').mkdir(parents=True, exist_ok=True)
(GH / 'tmp').mkdir(parents=True, exist_ok=True)
(GH / 'settings').mkdir(parents=True, exist_ok=True)

os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

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

stock_elf = ROOT / 'local_only' / 'stock.elf'
with pyghidra.open_program(str(stock_elf), project_location=str(GH / 'projects'),
                           project_name='p1f_stock_inspect', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)

    start_addr = 0x111eb8
    end_addr = 0x111f6c

    print(f"Disassembling stock helper: {hex(start_addr)} .. {hex(end_addr)} ({end_addr - start_addr} bytes)")
    cur = start_addr
    while cur < end_addr:
        addr = s.getAddress(cur)
        ins = pd.disassemble(addr)
        w = p.getMemory().getInt(addr) & 0xFFFFFFFF
        if ins:
            print(f"0x{cur:06x}: {w:08x}  {ins}")
            cur += ins.getLength()
        else:
            print(f"0x{cur:06x}: {w:08x}  <cannot disassemble>")
            cur += 4
