"""P0 reproducible local-only Ghidra inventory and targeted decompilation.

Run python tools/p0_ghidra.py [--no-analyze] [hex-address ...]. One JVM/job only.
All imported binary data and Ghidra state stay inside local_only.
"""
from pathlib import Path
import bisect, hashlib, json, os, re, struct, sys, warnings

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT / 'local_only' / 'ghidra'
OUT = ROOT / 'local_only' / 'analysis'
for d in (GH, OUT, GH/'projects', GH/'tmp', GH/'settings'):
    d.mkdir(parents=True, exist_ok=True)
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
from ghidra.app.decompiler import DecompInterface
from ghidra.app.util import PseudoDisassembler
from ghidra.util.task import ConsoleTaskMonitor

elf = ROOT/'local_only'/'stock.elf'
assert hashlib.sha256(elf.read_bytes()).hexdigest() == '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
with pyghidra.open_program(str(elf), project_location=str(GH/'projects'),
                          project_name='stock_63f12b7e', analyze='--no-analyze' not in sys.argv,
                          language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    fm, listing, refs = p.getFunctionManager(), p.getListing(), p.getReferenceManager()
    space = p.getAddressFactory().getDefaultAddressSpace()
    addr = lambda n: space.getAddress(n)
    pseudo = PseudoDisassembler(p)
    def instruction(n):
        x=listing.getInstructionAt(addr(n))
        if x is None:
            try: x=pseudo.disassemble(addr(n))
            except Exception: pass
        return x
    # ELFv1 function descriptors recover code entries missed by default analysis.
    binary=elf.read_bytes(); phoff=struct.unpack_from('>Q',binary,32)[0]
    descriptors={}
    for j in range(struct.unpack_from('>H',binary,56)[0]):
        typ,flags,offset,va,pa,size,memsize,align=struct.unpack_from('>IIQQQQQQ',binary,phoff+j*56)
        if typ != 1: continue
        for pos in range(offset,offset+size-16,8):
            entry,toc=struct.unpack_from('>QQ',binary,pos)
            if toc == 0x751280 and 0x20 <= entry < 0x2ff940 and entry%4 == 0:
                descriptors.setdefault(entry,[]).append(va+pos-offset)
    entries=sorted(descriptors)
    def descriptor_start(n):
        index=bisect.bisect_right(entries,n)-1
        return entries[index] if index >= 0 else n
    sc_lines=(ROOT/'local_only'/'sc_sites.txt').read_text().splitlines()
    for line in sc_lines:
        n=int(line.split()[0],16)
        if n < 0x10000: continue
        start=descriptor_start(n)
        if fm.getFunctionAt(addr(start)) is None:
            flat.disassemble(addr(start))
            try: flat.createFunction(addr(start),None)
            except Exception: pass
    (OUT/'function_descriptors.json').write_text(json.dumps({hex(k):[hex(v) for v in vs] for k,vs in descriptors.items()},indent=2),encoding='utf-8')
    def callers(f):
        if f is None: return []
        return [{'from':str(r.getFromAddress()), 'type':str(r.getReferenceType()),
                 'function':str(fm.getFunctionContaining(r.getFromAddress()).getEntryPoint())
                 if fm.getFunctionContaining(r.getFromAddress()) else None}
                for r in refs.getReferencesTo(f.getEntryPoint())]
    print('Imported; functions', fm.getFunctionCount(), flush=True)
    sites = []
    # Decode the sites from the independent word scan with Ghidra; do not assume
    # scanner r11 guesses are data flow analysis.
    for line in sc_lines:
        n = int(line.split()[0],16)
        ins = instruction(n)
        f = fm.getFunctionContaining(addr(n))
        context=[]
        for off in range(max(0,n-96),n+20,4):
            x=instruction(off)
            if x: context.append(f'{off:08x}: {x}')
        val=None
        for off in range(max(0,n-96),n,4):
            x=instruction(off)
            st=str(x)
            match=re.fullmatch(r'li r11,(-?0x[0-9a-f]+)',st)
            if match: val=int(match.group(1),16)
            elif st == 'oris r11,r11,0x8000' and val is not None: val|=0x80000000
            elif re.match(r'\w+ r11,',st): val=None
            elif st.startswith('sc '): val=None
        forwarded='lev=0' in line and val is not None and 0x80000000 <= val < 0x80000100
        sites.append({'site':hex(n),'scan':line,'instruction':str(ins),'r11_local':val,
                      'hypercall': val & 0xff if forwarded else val if 'lev=1' in line else None,
                      'forwarded':forwarded,'descriptor_start':hex(descriptor_start(n)) if n>=0x10000 else None,
                      'function':str(f.getEntryPoint()) if f else None,
                      'name':str(f.getName()) if f else None,
                      'references':callers(f), 'context':context})
    (OUT/'sc_inventory.json').write_text(json.dumps(sites,indent=2),encoding='utf-8')
    with (OUT/'functions.tsv').open('w',encoding='utf-8') as out:
        for f in fm.getFunctions(True):
            out.write(f'{f.getEntryPoint()}\t{f.getName()}\t{f.getBody().getNumAddresses()}\n')
    strings=[]
    for d in listing.getDefinedData(True):
        if d.hasStringValue():
            val=str(d.getValue())
            if re.search(r'ufs|storage|bdvd|cdvd|disc|atapi|media|iso|scsi|sector|repository|hdd',val,re.I):
                strings.append({'address':str(d.getAddress()),'value':val,
                                'references':[str(r.getFromAddress()) for r in refs.getReferencesTo(d.getAddress())]})
    (OUT/'strings.json').write_text(json.dumps(strings,indent=2),encoding='utf-8')
    for lo,hi in ((0,0x18000),(0x19800,0x1a300),(0x12b000,0x12d800),(0x135000,0x137a00),(0x1eb000,0x1ebb80)):
        with (OUT/f'range_{lo:08x}_{hi:08x}.asm').open('w',encoding='utf-8') as out:
            for n in range(lo,hi,4):
                x=instruction(n)
                if x: out.write(f'{n:08x}: {x}\n')
    with (OUT/'toc.tsv').open('w',encoding='utf-8') as out:
        for off in range(-0x8000,0x8000,8):
            try: val=p.getMemory().getLong(addr(0x751280+off)) & ((1<<64)-1)
            except Exception: continue
            out.write(f'{off:+#x}\t{val:#x}\n')
    targets={0x1ed5cc,0x1ecc5c,0x1ec760,0x3cfc,0x3960,0x39b0,0x135f70,0x135fac,0x136ff4}
    if '--focus' in sys.argv: targets.clear()
    targets.update(int(x,16) for x in sys.argv[1:] if not x.startswith('--'))
    for n in list(targets):
        if fm.getFunctionContaining(addr(n)) is None:
            flat.disassemble(addr(n))
            try: flat.createFunction(addr(n),None)
            except Exception: pass
    for row in ([] if '--focus' in sys.argv else sites):
        if ('lev=1' in row['scan'] or row['forwarded']) and row['function']:
            targets.add(int(row['function'],16))
    # Include direct callers of targets as the initial trace frontier.
    for n in list(targets):
        f=fm.getFunctionContaining(addr(n))
        for r in callers(f):
            if r['function']: targets.add(int(r['function'],16))
    decomp=DecompInterface(); decomp.openProgram(p)
    done=set()
    with (OUT/'target_references.json').open('w',encoding='utf-8') as out:
        json.dump({hex(n):[{'from':str(r.getFromAddress()),'type':str(r.getReferenceType())}
                          for r in refs.getReferencesTo(addr(n))] for n in targets},out,indent=2)
    for n in sorted(targets):
        f=fm.getFunctionContaining(addr(n))
        if not f or str(f.getEntryPoint()) in done: continue
        key=str(f.getEntryPoint()); done.add(key)
        result=decomp.decompileFunction(f,60,ConsoleTaskMonitor())
        body=result.getDecompiledFunction()
        (OUT/f'fn_{key}.c').write_text((body.getC() if body else result.getErrorMessage()).replace('\r\n','\n'),encoding='utf-8')
        with (OUT/f'fn_{key}.asm').open('w',encoding='utf-8') as out:
            out.write(json.dumps(callers(f),indent=2)+'\n')
            for ins in listing.getInstructions(f.getBody(),True):
                out.write(f'{ins.getAddress()}: {ins}\n')
        print('Decompiled', key, flush=True)
    decomp.dispose()
    print('Saved under',OUT,flush=True)
