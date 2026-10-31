import os, sys, warnings, hashlib, json
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
GH = ROOT / 'local_only' / 'ghidra_p1e'
OUT = ROOT / 'local_only' / 'analysis' / 'p1e'
OUT.mkdir(parents=True, exist_ok=True)
GH.mkdir(parents=True, exist_ok=True)

for key in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA'):
    os.environ[key] = str(GH / ('tmp' if key in ('TEMP', 'TMP', 'TMPDIR') else 'settings'))
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

warnings.filterwarnings('ignore', category=DeprecationWarning)
import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G',
                    '-Duser.home=' + str(GH / 'settings'),
                    '-Dapplication.settingsdir=' + str(GH / 'settings'),
                    '-Djava.io.tmpdir=' + str(GH / 'tmp'))
launcher.start()

from ghidra.app.decompiler import DecompInterface
from ghidra.app.util import PseudoDisassembler
from ghidra.util.task import ConsoleTaskMonitor

STOCK = ROOT / 'local_only' / 'stock.elf'
sha_elf = hashlib.sha256(STOCK.read_bytes()).hexdigest()
assert sha_elf == '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'

print("Opening stock.elf in pyghidra...")
with pyghidra.open_program(str(STOCK), project_location=str(GH / 'projects'),
                           project_name='stock_p1e', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    space = p.getAddressFactory().getDefaultAddressSpace()
    mem = p.getMemory()
    listing = p.getListing()
    pdis = PseudoDisassembler(p)

    def disasm_range(start_addr, count):
        addr = space.getAddress(start_addr)
        lines = []
        for _ in range(count):
            inst = pdis.disassemble(addr)
            if inst is None:
                lines.append(f"0x{addr.getOffset():08x}: <unable to disassemble>")
                addr = addr.add(4)
                continue
            lines.append(f"0x{addr.getOffset():08x}: {inst.toString()}")
            addr = addr.add(inst.getLength())
        return lines

    print("Disassembling 0x111eb8..0x111f30 (repo helper)...")
    repo_lines = disasm_range(0x111eb8, 30)
    for l in repo_lines:
        print(l)

    print("\nDisassembling 0x0c50..0x0cb0 (bridge)...")
    bridge_lines = disasm_range(0x0c50, 25)
    for l in bridge_lines:
        print(l)

    print("\nDisassembling bridge panic / check code around 0x0f50..0x0f70...")
    panic_lines = disasm_range(0x0f50, 10)
    for l in panic_lines:
        print(l)

    print("\nDisassembling 0x10550..0x105a0 (privilege table init)...")
    init_lines = disasm_range(0x10550, 20)
    for l in init_lines:
        print(l)

    print("\nDisassembling 0x10834..0x10870 (second init loop)...")
    init2_lines = disasm_range(0x10834, 16)
    for l in init2_lines:
        print(l)

    results = {
        'repo_helper': repo_lines,
        'bridge': bridge_lines,
        'panic': panic_lines,
        'init1': init_lines,
        'init2': init2_lines,
    }
    (OUT / 'step1_disasm.json').write_text(json.dumps(results, indent=2))
    print(f"Disassembly saved to {OUT / 'step1_disasm.json'}")
