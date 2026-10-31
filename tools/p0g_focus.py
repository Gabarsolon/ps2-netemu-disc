"""Small targeted extraction from existing P0G projects; no whole-ELF scan.

usage: python -I tools/p0g_focus.py VARIANT LOW HIGH [function entries ...]
VSH uses 32-bit OPDs and a different TOC; other inputs use the P0G manifest.
"""
from pathlib import Path
import json
import os
import sys
import warnings

root = Path(__file__).resolve().parents[1]
base = root/'local_only/analysis/p0g'
variant = sys.argv[1]
out = base/variant
gh = base/'ghidra'
manifest = json.loads((out/'manifest.json').read_text())
toc = 0x6f7370 if variant == 'vsh' else int(manifest['toc'],16)
for key in ['TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA']:
    os.environ[key] = str(gh/('tmp' if key in ['TEMP','TMP','TMPDIR'] else 'settings'))
os.environ['JAVA_HOME'] = 'C:/Program Files/Microsoft/jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = 'C:/ghidra_12.1.3_PUBLIC'
warnings.filterwarnings('ignore',category=DeprecationWarning)
from pyghidra.launcher import HeadlessPyGhidraLauncher
import pyghidra
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G','-Duser.home='+str(gh/'settings'),'-Dapplication.settingsdir='+str(gh/'settings'),'-Djava.io.tmpdir='+str(gh/'tmp'))
launcher.start()
from ghidra.app.util import PseudoDisassembler
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from java.math import BigInteger

elf = root/'local_only'/('stock.elf' if variant=='netemu' else 'fw355/out/'+variant+'.elf')
with pyghidra.open_program(str(elf),project_location=str(gh/'projects'),project_name=variant+'_'+manifest['sha256'][:12],analyze=False,language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    addr = p.getAddressFactory().getDefaultAddressSpace().getAddress
    lo,hi = [int(x,16) for x in sys.argv[2:4]]
    p.getProgramContext().setValue(p.getRegister('r2'),addr(lo),addr(hi-1),BigInteger(str(toc)))
    pd = PseudoDisassembler(p)
    with (out/f'range_{lo:08x}_{hi:08x}.asm').open('w') as f:
        for n in range(lo,hi,4):
            try: ins = pd.disassemble(addr(n))
            except Exception: ins = None
            if ins: f.write(f'{n:08x}: {ins}'+chr(10))
    print('Range saved',variant,hex(lo),hex(hi),flush=True)
    di = DecompInterface()
    di.openProgram(p)
    for item in sys.argv[4:]:
        n = int(item,16)
        fn = p.getFunctionManager().getFunctionAt(addr(n))
        if fn is None:
            flat.disassemble(addr(n))
            fn = flat.createFunction(addr(n),None)
        if fn is None: continue
        p.getProgramContext().setValue(p.getRegister('r2'),fn.getEntryPoint(),fn.getBody().getMaxAddress(),BigInteger(str(toc)))
        result = di.decompileFunction(fn,60,ConsoleTaskMonitor())
        c = result.getDecompiledFunction()
        (out/f'fn_{n:08x}.c').write_text(c.getC() if c else result.getErrorMessage(),encoding='utf-8')
        print('Decompiled',hex(n),flush=True)
    di.dispose()
print('DONE',variant,flush=True)
