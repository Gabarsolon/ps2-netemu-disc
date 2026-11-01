import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p2e'

for k in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[k] = str(GH / 'tmp')
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

sys.path = [p for p in sys.path if not Path(p).resolve().name.lower() == 'local_only']

import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G')
launcher.start()

from ghidra.app.emulator import EmulatorHelper

elf_path = ROOT / 'local_only' / 'p2e' / 'ps2_netemu_p2e_K0.elf'
with pyghidra.open_program(str(elf_path), project_location=str(GH / 'projects'),
                           project_name='test_track', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    em = EmulatorHelper(p)
    em.enableMemoryWriteTracking(True)
    # Print methods on em related to write tracking
    methods = [m for m in dir(em) if 'Track' in m or 'Write' in m or 'write' in m]
    print("Methods:", methods)
