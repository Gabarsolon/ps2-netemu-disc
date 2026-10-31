"""Local-only PHAT inventory. Run one variant/job at a time; never contacts a console."""
from pathlib import Path
import argparse, bisect, collections, hashlib, json, os, re, struct, warnings

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('variant', choices=['ps2_emu', 'ps2_gxemu'])
ap.add_argument('--no-analyze', action='store_true')
ap.add_argument('--focus', action='store_true')
ap.add_argument('--depth', type=int, default=1)
ap.add_argument('--range', nargs=2, metavar=('LOW', 'HIGH'))
ap.add_argument('addresses', nargs='*')
args = ap.parse_args()
GH = ROOT/'local_only'/'ghidra'/'p0d'
OUT = ROOT/'local_only'/'analysis'/'p0d'/args.variant
for d in [GH, OUT, GH/'projects', GH/'tmp', GH/'settings']:
    d.mkdir(parents=True, exist_ok=True)
for key in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[key] = str(GH/('tmp' if key in ['TEMP', 'TMP', 'TMPDIR'] else 'settings'))
os.environ['JAVA_HOME'] = 'C:/Program Files/Microsoft/jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = 'C:/ghidra_12.1.3_PUBLIC'
warnings.filterwarnings('ignore', category=DeprecationWarning)
import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G', '-Duser.home='+str(GH/'settings'),
                   '-Dapplication.settingsdir='+str(GH/'settings'), '-Djava.io.tmpdir='+str(GH/'tmp'))
launcher.start()
from ghidra.app.decompiler import DecompInterface
from ghidra.app.util import PseudoDisassembler
from ghidra.util.task import ConsoleTaskMonitor
from java.math import BigInteger

elf = ROOT/'local_only'/'variants'/(args.variant+'.elf')
binary = elf.read_bytes()
digest = hashlib.sha256(binary).hexdigest()
segments = []
for i in range(struct.unpack_from('>H', binary, 56)[0]):
    row = struct.unpack_from('>IIQQQQQQ', binary, struct.unpack_from('>Q', binary, 32)[0]+56*i)
    if row[0] == 1:
        segments.append(row)
toc_counts = collections.Counter()
for typ, flags, off, va, pa, size, memsize, align in segments:
    for pos in range(off, off+size-16, 8):
        entry, toc = struct.unpack_from('>QQ', binary, pos)
        if entry % 4 == 0 and any(s[1]&1 and s[3] <= entry < s[3]+s[5] for s in segments):
            toc_counts[toc] += 1
toc = next(value for value, count in toc_counts.most_common()
           if value >= 0x10000 and any(s[3] <= value < s[3]+s[6] for s in segments))
descriptors = {}
sites_raw = []
for typ, flags, off, va, pa, size, memsize, align in segments:
    for pos in range(off, off+size-16, 8):
        entry, candidate = struct.unpack_from('>QQ', binary, pos)
        if candidate == toc and entry % 4 == 0 and any(s[1]&1 and s[3] <= entry < s[3]+s[5] for s in segments):
            descriptors.setdefault(entry, []).append(va+pos-off)
    if flags & 1:
        for pos in range(off, off+size-4, 4):
            word = struct.unpack_from('>I', binary, pos)[0]
            if word in [0x44000002, 0x44000022]:
                sites_raw.append((va+pos-off, (word >> 5)&1))
entries = sorted(descriptors)
(OUT/'manifest.json').write_text(json.dumps({'sha256':digest,'toc':hex(toc),'segments':segments,
    'toc_candidates':toc_counts.most_common(6),'descriptor_count':len(entries)}, indent=2))
with pyghidra.open_program(str(elf), project_location=str(GH/'projects'),
        project_name=args.variant+'_'+digest[:12], analyze=not args.no_analyze,
        language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    fm, listing, refs = p.getFunctionManager(), p.getListing(), p.getReferenceManager()
    space = p.getAddressFactory().getDefaultAddressSpace()
    addr = lambda n: space.getAddress(n)
    p.getProgramContext().setValue(p.getRegister('r2'), addr(0),
        addr(max(s[3]+s[5] for s in segments)-1), BigInteger(str(toc)))
    pseudo = PseudoDisassembler(p)
    def instruction(n):
        x = listing.getInstructionAt(addr(n))
        if x is None:
            try: x = pseudo.disassemble(addr(n))
            except Exception: pass
        return x
    for start in entries:
        if fm.getFunctionAt(addr(start)) is None:
            flat.disassemble(addr(start))
            try: flat.createFunction(addr(start), None)
            except Exception: pass
    def callers(f):
        if f is None: return []
        return [{'from':str(r.getFromAddress()),'type':str(r.getReferenceType()),
                 'function':str(g.getEntryPoint()) if (g := fm.getFunctionContaining(r.getFromAddress())) else None}
                for r in refs.getReferencesTo(f.getEntryPoint())]
    sites = []
    for n, lev in sites_raw:
        val = None
        context = []
        for off in range(max(0,n-96), n+20, 4):
            x = instruction(off)
            st = str(x)
            if x: context.append(f'{off:08x}: {st}')
            if off >= n: continue
            m = re.fullmatch(r'li r11,(-?0x[0-9a-f]+)', st)
            if m: val = int(m[1],16)
            elif st == 'oris r11,r11,0x8000' and val is not None: val |= 0x80000000
            elif re.match(r'\w+ r11,',st) or st.startswith('sc '): val = None
        f = fm.getFunctionContaining(addr(n))
        forwarded = lev == 0 and val is not None and 0x80000000 <= val < 0x80000100
        sites.append({'site':hex(n),'lev':lev,'instruction':str(instruction(n)), 'r11_local':val,
            'hypercall':val&255 if forwarded else val if lev == 1 else None,
            'forwarded':forwarded,'function':str(f.getEntryPoint()) if f else None,
            'references':callers(f),'context':context})
    (OUT/'sc_inventory.json').write_text(json.dumps(sites,indent=2))
    (OUT/'function_descriptors.json').write_text(json.dumps({hex(k):[hex(v) for v in vs] for k,vs in descriptors.items()},indent=2))
    strings = []
    for d in listing.getDefinedData(True):
        if d.hasStringValue():
            value = str(d.getValue())
            if re.search('ufs|storage|bdvd|cdvd|disc|atapi|media|iso|scsi|sector|repository|hdd|dvd|toc|auth',value,re.I):
                strings.append({'address':str(d.getAddress()),'value':value,
                    'references':[str(r.getFromAddress()) for r in refs.getReferencesTo(d.getAddress())]})
    (OUT/'strings.json').write_text(json.dumps(strings,indent=2))
    with (OUT/'functions.tsv').open('w') as out:
        for f in fm.getFunctions(True):
            out.write(f'{f.getEntryPoint()}\t{f.getName()}\t{f.getBody().getNumAddresses()}\n')
    if not args.focus:
        with (OUT/'text.asm').open('w') as out:
            for ins in listing.getInstructions(True):
                out.write(f'{ins.getAddress()}: {ins}\n')
        with (OUT/'toc.tsv').open('w') as out:
            for off in range(-0x8000,0x8000,8):
                try: value = p.getMemory().getLong(addr(toc+off)) & ((1<<64)-1)
                except Exception: continue
                out.write(f'{off:+#x}\t{value:#x}\n')
    targets = {int(x,16) for x in args.addresses}
    if args.range:
        low, high = [int(x,16) for x in args.range]
        targets.update(n for n in entries if low <= n < high)
        with (OUT/f'range_{low:08x}_{high:08x}.asm').open('w') as out:
            for n in range(low,high,4):
                ins = instruction(n)
                if ins: out.write(f'{n:08x}: {ins}\n')
    if not args.focus:
        targets.update(int(row['function'],16) for row in sites
                       if row['function'] and (row['lev']==1 or row['forwarded']))
    for _ in range(args.depth):
        for n in list(targets):
            f = fm.getFunctionContaining(addr(n))
            targets.update(int(r['function'],16) for r in callers(f) if r['function'])
    decomp = DecompInterface()
    decomp.openProgram(p)
    done = set()
    for n in sorted(targets):
        f = fm.getFunctionContaining(addr(n))
        if not f:
            flat.disassemble(addr(n))
            try: f = flat.createFunction(addr(n),None)
            except Exception: continue
        if not f: continue
        key = str(f.getEntryPoint())
        if key in done: continue
        done.add(key)
        result = decomp.decompileFunction(f,45,ConsoleTaskMonitor())
        body = result.getDecompiledFunction()
        (OUT/f'fn_{key}.c').write_text(body.getC() if body else result.getErrorMessage(),encoding='utf-8')
        with (OUT/f'fn_{key}.asm').open('w') as out:
            out.write(json.dumps(callers(f),indent=2)+'\n')
            for ins in listing.getInstructions(f.getBody(),True):
                out.write(f'{ins.getAddress()}: {ins}\n')
        print('Decompiled',key,flush=True)
    decomp.dispose()
    print('DONE',args.variant,digest,'TOC',hex(toc),'sites',len(sites),'functions',fm.getFunctionCount(),flush=True)
