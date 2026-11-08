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

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

softemu_elf = ROOT / 'local_only' / 'fw355' / 'out' / 'ps2_softemu.elf'
with pyghidra.open_program(str(softemu_elf), project_location=str(GH / 'projects'),
                           project_name='p11_softemu', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    s = p.getAddressFactory().getDefaultAddressSpace()
    monitor = ConsoleTaskMonitor()
    decomp = DecompInterface()
    decomp.openProgram(p)

    # Disassemble functions first so decompiler knows them
    from ghidra.app.cmd.disassemble import DisassembleCommand
    for target in [0x8B2BC, 0x22130C, 0x87980, 0x87600, 0x870D0, 0x221598]:
        cmd = DisassembleCommand(s.getAddress(target), None, True)
        cmd.applyTo(p)

    from ghidra.program.model.symbol import SourceType
    from ghidra.app.cmd.function import CreateFunctionCmd
    for target, name in [(0x8B2BC, 'ps2_disc_auth'), (0x22130C, 'auth_caller')]:
        cmd = CreateFunctionCmd(name, s.getAddress(target), None, SourceType.USER_DEFINED)
        cmd.applyTo(p)

    for target in [0x8B2BC, 0x22130C]:
        f = p.getFunctionManager().getFunctionAt(s.getAddress(target))
        if f:
            res = decomp.decompileFunction(f, 30, monitor)
            print(f"\n=================== DECOMPILED {hex(target)} ===================")
            print(res.getDecompiledFunction().getC())
