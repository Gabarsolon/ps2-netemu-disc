import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p1g'
stock_elf = ROOT / 'local_only' / 'stock.elf'

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

with pyghidra.open_program(str(stock_elf), project_location=str(GH / 'projects'),
                           project_name='p1g_regs_test2', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    regs = [r.getName() for r in p.getLanguage().getRegisters()]
    lr_regs = [r for r in regs if 'lr' in r.lower() or 'link' in r.lower()]
    print("LR related registers in Ghidra PPC64:")
    print(lr_regs)

    from ghidra.app.emulator import EmulatorHelper
    from java.math import BigInteger

    em = EmulatorHelper(p)
    print("Testing read/write:")
    for reg_name in ['LR', 'lr', 'crall', 'cr0', 'cr2', 'cr3', 'cr4', 'r1', 'r30']:
        try:
            val = em.readRegister(reg_name)
            em.writeRegister(reg_name, BigInteger('12345'))
            val2 = em.readRegister(reg_name)
            print(f"  {reg_name}: read={val}, wrote 12345, read={val2}")
        except Exception as e:
            print(f"  {reg_name}: FAILED ({e})")
