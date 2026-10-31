"""P0E: fresh Ghidra decoding of local ELFs, one JVM and one program at a time."""
from pathlib import Path
import hashlib, json, os, struct, sys, warnings

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT/'local_only'/'ghidra'
OUT = ROOT/'local_only'/'analysis'/'p0e'
OUT.mkdir(parents=True, exist_ok=True)
for key in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[key] = str(GH/('tmp' if key in ['TEMP', 'TMP', 'TMPDIR'] else 'settings'))
os.environ['JAVA_HOME'] = 'C:/Program Files/Microsoft/jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = 'C:/ghidra_12.1.3_PUBLIC'
warnings.filterwarnings('ignore', category=DeprecationWarning)
import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G', '-Duser.home='+str(GH/'settings'), '-Dapplication.settingsdir='+str(GH/'settings'), '-Djava.io.tmpdir='+str(GH/'tmp'))
launcher.start()
from ghidra.app.util import PseudoDisassembler

jobs = {
 'ps2_emu': [(0x1d400,0x1e200),(0x22138,0x22990),(0x26988,0x26ae0),(0x28da8,0x28ec0),(0x42e58,0x43030),(0xfbc28,0xfbd40),(0x477c,0x4b00),(0x3a24,0x3b00)],
 'ps2_gxemu': [(0x400c0,0x40360),(0x413a8,0x423c0),(0x56a6c,0x56e00),(0x8b2a0,0x8b400),(0x8d510,0x8da80),(0x92a50,0x92b20),(0x95f3c,0x96070),(0x98244,0x98640),(0x4f810,0x4f8d0),(0x501d8,0x50d00)],
 'netemu': [(0xc00,0xd20),(0xf40,0xf90),(0x111000,0x1120ac),(0x114dc8,0x1157cc),(0x12be04,0x12c110),(0x12b320,0x12b390),(0x12b5fc,0x12b73c),(0x1e9ba0,0x1ea2a0),(0x16000,0x20b80),(0x12d5b0,0x12d630)]
}
manifest = {}
for variant, ranges in jobs.items():
    if len(sys.argv) > 1 and variant not in sys.argv[1:]: continue
    if len(sys.argv) == 4: ranges = [(int(sys.argv[2],16),int(sys.argv[3],16))]
    elf = ROOT/'local_only'/('stock.elf' if variant == 'netemu' else 'variants/'+variant+'.elf')
    binary = elf.read_bytes()
    digest = hashlib.sha256(binary).hexdigest()
    project = 'stock_63f12b7e' if variant == 'netemu' else variant+'_'+digest[:12]
    location = GH/'projects' if variant == 'netemu' else GH/'p0d'/'projects'
    with pyghidra.open_program(str(elf), project_location=str(location), project_name=project, analyze=False, language='PowerPC:BE:64:default') as flat:
        p = flat.getCurrentProgram()
        pd = PseudoDisassembler(p)
        space = p.getAddressFactory().getDefaultAddressSpace()
        lines, count = [], 0
        for lo, hi in ranges:
            for n in range(lo,hi,4):
                ad = space.getAddress(n)
                try: ins = pd.disassemble(ad)
                except Exception: ins = None
                if ins:
                    raw = p.getMemory().getInt(ad) & 0xffffffff
                    lines.append(f'{n:08x}: {raw:08x} {ins}')
                    count += 1
        suffix = '_'+sys.argv[2] if len(sys.argv) == 4 else ''
        (OUT/(variant+suffix+'.asm')).write_text(chr(10).join(lines)+chr(10))
        manifest[variant+suffix] = {'sha256':digest,'ranges':ranges,'instructions':count}
        print(variant,count,digest,flush=True)
existing = json.loads((OUT/'manifest.json').read_text()) if (OUT/'manifest.json').exists() else {}
existing.update(manifest)
(OUT/'manifest.json').write_text(json.dumps(existing,indent=2))
print('DONE',flush=True)
