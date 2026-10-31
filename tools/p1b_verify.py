"""P1b step 1 verification: examine LV1 170 (open_device) and 171 (close_device)
and HDD init 0x12be04 in local_only/stock.elf using pyghidra.
"""
from pathlib import Path
import hashlib, json, os, struct, sys, warnings

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT / 'local_only' / 'ghidra'
OUT = ROOT / 'local_only' / 'analysis' / 'p1b'
OUT.mkdir(parents=True, exist_ok=True)
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

STOCK = ROOT / 'local_only' / 'stock.elf'
sha_elf = hashlib.sha256(STOCK.read_bytes()).hexdigest()
assert sha_elf == '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3', sha_elf

def word_at(mem, space, n):
    return mem.getInt(space.getAddress(n)) & 0xffffffff

def bytes_at(mem, space, n, length):
    return bytes([mem.getByte(space.getAddress(n + i)) & 0xff for i in range(length)])

with pyghidra.open_program(str(STOCK), project_location=str(GH/'projects'),
                          project_name='stock_63f12b7e', analyze=False,
                          language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    fm, listing = p.getFunctionManager(), p.getListing()
    space = p.getAddressFactory().getDefaultAddressSpace()
    mem = p.getMemory()
    addr = lambda n: space.getAddress(n)
    pd = PseudoDisassembler(p)

    def ins(n):
        x = listing.getInstructionAt(addr(n))
        if x is None:
            try: x = pd.disassemble(addr(n))
            except Exception: pass
        return str(x) if x else None

    def fnof(n):
        f = fm.getFunctionContaining(addr(n))
        return int(str(f.getEntryPoint()), 16) if f else None

    def disasm_range(start, count):
        lines = []
        for i in range(count):
            cur = start + i * 4
            w = word_at(mem, space, cur)
            instruction = ins(cur)
            lines.append(f"0x{cur:06x}: {w:08x}  {instruction}")
        return lines

    results = {}

    print("=== Disassembly around 0x12bf8c (HDD init open_device) ===")
    lines_open = disasm_range(0x12bf50, 25)
    for l in lines_open:
        print(l)
    results['hdd_init_open'] = lines_open

    print("\n=== Disassembly around 0x12d610 (HDD cleanup close_device) ===")
    lines_close = disasm_range(0x12d5d0, 25)
    for l in lines_close:
        print(l)
    results['hdd_close'] = lines_close

    print("\n=== Disassembly of other 170 (open) sites ===")
    for site in (0x137b68, 0x19d48, 0x1e79a4):
        print(f"\n--- Site 0x{site:x} ---")
        lines = disasm_range(site - 16, 12)
        for l in lines:
            print(l)
        results[f'open_site_0x{site:x}'] = lines

    print("\n=== Disassembly of other 171 (close) sites ===")
    for site in (0x137440, 0x1e77b4):
        print(f"\n--- Site 0x{site:x} ---")
        lines = disasm_range(site - 16, 12)
        for l in lines:
            print(l)
        results[f'close_site_0x{site:x}'] = lines

    print("\n=== Exception bridge around 0xca0 ===")
    lines_bridge = disasm_range(0xc40, 30)
    for l in lines_bridge:
        print(l)
    results['bridge_0xca0'] = lines_bridge

    # Save to analysis output
    (OUT / 'p1b_verify_results.json').write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {OUT / 'p1b_verify_results.json'}")
