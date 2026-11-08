import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p11'
TMP_DIR = GH / 'tmp'
SETTINGS_DIR = GH / 'settings'

for d in [TMP_DIR, SETTINGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

for k in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[k] = str(TMP_DIR.resolve() if k in ['TEMP', 'TMP', 'TMPDIR'] else SETTINGS_DIR.resolve())

os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'
sys.path = [p for p in sys.path if not Path(p).resolve().name.lower() == 'local_only']

import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher

launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs(
    '-Xmx3G',
    '-Duser.home=' + str(SETTINGS_DIR.resolve()),
    '-Dapplication.settingsdir=' + str(SETTINGS_DIR.resolve()),
    '-Djava.io.tmpdir=' + str(TMP_DIR.resolve())
)
launcher.start()

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.cmd.disassemble import DisassembleCommand
from ghidra.program.model.symbol import SourceType
from ghidra.app.cmd.function import CreateFunctionCmd

ss3_elf = ROOT / 'local_only' / 'analysis' / 'p0i' / 'modules' / 'ss_server3.elf'
with pyghidra.open_program(str(ss3_elf), project_location=str(GH / 'projects'),
                           project_name='p12_ss3_auth', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    s = p.getAddressFactory().getDefaultAddressSpace()
    monitor = ConsoleTaskMonitor()
    decomp = DecompInterface()
    decomp.openProgram(p)

    targets = [0x80000A14]
    for target in targets:
        cmd = DisassembleCommand(s.getAddress(target), None, True)
        cmd.applyTo(p)
        cmd = CreateFunctionCmd(f'func_{hex(target)}', s.getAddress(target), None, SourceType.USER_DEFINED)
        cmd.applyTo(p)
        f = p.getFunctionManager().getFunctionAt(s.getAddress(target))
        if f:
            res = decomp.decompileFunction(f, 60, monitor)
            print(f"\n=================== DECOMPILED {hex(target)} ===================")
            print(res.getDecompiledFunction().getC())
