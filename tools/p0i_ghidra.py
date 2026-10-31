"""P0I Ghidra import / focused decoding for 4.93 LV1 and modules."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import warnings

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0i'
ap = argparse.ArgumentParser()
ap.add_argument('--module', default='lv1')
ap.add_argument('--analyze', action='store_true')
ap.add_argument('--range', nargs=2, action='append', default=[])
ap.add_argument('--function', action='append', default=[])
ap.add_argument('--xref', action='append', default=[])
ap.add_argument('--remove-function', action='append', default=[])
ap.add_argument('--depth', type=int, default=0)
args = ap.parse_args()

GH = BASE / 'ghidra'
OUT = BASE / args.module
for p in [GH / 'projects', GH / 'tmp', GH / 'settings', OUT]:
    p.mkdir(parents=True, exist_ok=True)

for key in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[key] = str(GH / ('tmp' if key in ['TEMP', 'TMP', 'TMPDIR'] else 'settings'))
os.environ['JAVA_HOME'] = 'C:/Program Files/Microsoft/jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = 'C:/ghidra_12.1.3_PUBLIC'
warnings.filterwarnings('ignore', category=DeprecationWarning)

from pyghidra.launcher import HeadlessPyGhidraLauncher
import pyghidra

launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G', '-Duser.home=' + str(GH / 'settings'),
                   '-Dapplication.settingsdir=' + str(GH / 'settings'),
                   '-Djava.io.tmpdir=' + str(GH / 'tmp'))
launcher.start()

from ghidra.app.decompiler import DecompInterface
from ghidra.app.util import PseudoDisassembler
from ghidra.app.cmd.function import CreateFunctionCmd
from ghidra.util.task import ConsoleTaskMonitor
from java.math import BigInteger

if args.module == 'lv1':
    elf = ROOT / 'local_only/fw493/lv1.elf'
else:
    elf = BASE / 'modules' / (args.module + '.elf')

digest = hashlib.sha256(elf.read_bytes()).hexdigest()
print('Opening', args.module, digest, flush=True)

with pyghidra.open_program(str(elf), project_location=str(GH / 'projects'),
                          project_name=args.module + '_targeted_' + digest[:12],
                          analyze=False, language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    fm, listing, refs = p.getFunctionManager(), p.getListing(), p.getReferenceManager()
    addr = p.getAddressFactory().getDefaultAddressSpace().getAddress

    for item in args.remove_function:
        fm.removeFunction(addr(int(item, 16)))

    if args.analyze:
        options = p.getOptions('Analyzers')
        options.setBoolean('Address Tables', False)
        options.setBoolean('Aggressive Instruction Finder', False)
        print('Analyzing with speculative address tables disabled', flush=True)
        flat.analyzeAll(p)

    if args.module == 'lv1':
        toc = 0x35a038
        p.getProgramContext().setValue(p.getRegister('r2'), addr(0), addr(0x3c2c10), BigInteger(str(toc)))
    else:
        import struct
        binary = elf.read_bytes()
        entry = struct.unpack_from('>Q', binary, 24)[0]
        toc = p.getMemory().getLong(addr(entry + 8))
        for block in p.getMemory().getBlocks():
            p.getProgramContext().setValue(p.getRegister('r2'), block.getStart(), block.getEnd(), BigInteger(str(toc)))

    pd = PseudoDisassembler(p)
    def ins(n):
        try:
            return listing.getInstructionAt(addr(n)) or pd.disassemble(addr(n))
        except Exception:
            return None

    targets = {int(x, 16) for x in args.function}
    xrefs = {}
    for item in args.xref:
        n = int(item, 16)
        rows = []
        for r in refs.getReferencesTo(addr(n)):
            fn = fm.getFunctionContaining(r.getFromAddress())
            rows.append({'from': str(r.getFromAddress()), 'type': str(r.getReferenceType()),
                         'function': str(fn.getEntryPoint()) if fn else None})
            if fn:
                targets.add(int(fn.getEntryPoint().getOffset()))
        xrefs[item] = rows
    if args.xref:
        (OUT / ('xrefs_' + args.xref[0] + '.json')).write_text(json.dumps(xrefs, indent=2))
        print('XREFS', json.dumps(xrefs), flush=True)

    for low, high in args.range:
        lo, hi = int(low, 16), int(high, 16)
        with (OUT / f'range_{lo:x}_{hi:x}.asm').open('w') as f:
            for n in range(lo, hi, 4):
                instruction = ins(n)
                if instruction:
                    raw = p.getMemory().getInt(addr(n)) & 0xffffffff
                    f.write(f'{n:08x}: {raw:08x} {instruction}' + chr(10))

    for _ in range(args.depth):
        for n in list(targets):
            fn = fm.getFunctionAt(addr(n))
            if fn:
                flat.disassemble(addr(n))
                flat.disassemble(addr(n + 4))
                CreateFunctionCmd.fixupFunctionBody(p, fn, ConsoleTaskMonitor())
                for instruction in listing.getInstructions(fn.getBody(), True):
                    if instruction.getFlowType().isCall():
                        targets.update(int(a.getOffset()) for a in instruction.getFlows())

    di = DecompInterface()
    di.openProgram(p)
    for n in sorted(targets):
        fn = fm.getFunctionAt(addr(n))
        flat.disassemble(addr(n))
        flat.disassemble(addr(n + 4))
        if fn is None:
            try:
                fn = flat.createFunction(addr(n), None)
            except Exception:
                fn = fm.getFunctionContaining(addr(n))
        if fn is None:
            continue
        CreateFunctionCmd.fixupFunctionBody(p, fn, ConsoleTaskMonitor())
        result = di.decompileFunction(fn, 60, ConsoleTaskMonitor())
        c = result.getDecompiledFunction()
        (OUT / f'fn_{n:08x}.c').write_text(c.getC() if c else result.getErrorMessage(), encoding='utf-8')
        with (OUT / f'fn_{n:08x}.asm').open('w') as f:
            for instruction in listing.getInstructions(fn.getBody(), True):
                f.write(f'{instruction.getAddress()}: {instruction}' + chr(10))
        print('Decompiled', hex(n), flush=True)
    di.dispose()
    print('DONE', args.module, fm.getFunctionCount(), flush=True)
