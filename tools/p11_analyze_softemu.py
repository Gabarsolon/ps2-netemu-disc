import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p11'
TMP_DIR = GH / 'tmp'
SETTINGS_DIR = GH / 'settings'

for d in [GH, TMP_DIR, SETTINGS_DIR, GH / 'projects']:
    d.mkdir(parents=True, exist_ok=True)

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

from ghidra.app.util import PseudoDisassembler
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

out_file = ROOT / 'local_only' / 'p11_softemu_analysis.txt'

def disasm_range(pd, space, start_ea, count=50):
    lines = []
    addr = space.getAddress(start_ea)
    for _ in range(count):
        ins = pd.disassemble(addr)
        if ins is None:
            break
        lines.append(f"0x{addr.getOffset():08x}: {ins.toString()}")
        addr = addr.add(ins.getLength())
    return lines

with open(out_file, 'w', encoding='utf-8') as out:
    softemu_elf = ROOT / 'local_only' / 'fw355' / 'out' / 'ps2_softemu.elf'
    out.write(f"Analyzing {softemu_elf}...\n")
    with pyghidra.open_program(str(softemu_elf), project_location=str(GH / 'projects'),
                               project_name='p11_softemu', analyze=False,
                               language='PowerPC:BE:64:default') as flat:
        p = flat.getCurrentProgram()
        s = p.getAddressFactory().getDefaultAddressSpace()
        pd = PseudoDisassembler(p)

        out.write("\n=== ps2_softemu.elf 0x8B2BC (ps2_disc_auth) ===\n")
        for line in disasm_range(pd, s, 0x8B2BC, 120):
            out.write(line + "\n")

        out.write("\n=== ps2_softemu.elf 0x22130C caller region (0x221200..0x221450) ===\n")
        for line in disasm_range(pd, s, 0x221200, 150):
            out.write(line + "\n")

        out.write("\n=== ps2_softemu.elf 0x42C74 (write_all_vuart) ===\n")
        for line in disasm_range(pd, s, 0x42C74, 50):
            out.write(line + "\n")

        out.write("\n=== ps2_softemu.elf 0x8AE28 (reply reader) ===\n")
        for line in disasm_range(pd, s, 0x8AE28, 80):
            out.write(line + "\n")

    gxemu_elf = ROOT / 'local_only' / 'fw355' / 'out' / 'ps2_gxemu.elf'
    out.write(f"\nAnalyzing {gxemu_elf}...\n")
    with pyghidra.open_program(str(gxemu_elf), project_location=str(GH / 'projects'),
                               project_name='p11_gxemu', analyze=False,
                               language='PowerPC:BE:64:default') as flat_gx:
        p_gx = flat_gx.getCurrentProgram()
        s_gx = p_gx.getAddressFactory().getDefaultAddressSpace()
        pd_gx = PseudoDisassembler(p_gx)

        out.write("\n=== ps2_gxemu.elf 0x8FF8C ===\n")
        for line in disasm_range(pd_gx, s_gx, 0x8FF8C, 100):
            out.write(line + "\n")

    emu_elf = ROOT / 'local_only' / 'fw355' / 'out' / 'ps2_emu.elf'
    out.write(f"\nAnalyzing {emu_elf}...\n")
    with pyghidra.open_program(str(emu_elf), project_location=str(GH / 'projects'),
                               project_name='p11_emu', analyze=False,
                               language='PowerPC:BE:64:default') as flat_emu:
        p_emu = flat_emu.getCurrentProgram()
        s_emu = p_emu.getAddressFactory().getDefaultAddressSpace()
        pd_emu = PseudoDisassembler(p_emu)

        out.write("\n=== ps2_emu.elf 0x2053C ===\n")
        for line in disasm_range(pd_emu, s_emu, 0x2053C, 100):
            out.write(line + "\n")

print("Analysis written to", out_file)
