import os, sys, warnings, struct
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
GH = ROOT / 'local_only' / 'ghidra_p1e'
STOCK = ROOT / 'local_only' / 'stock.elf'

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

from ghidra.app.util import PseudoDisassembler

with pyghidra.open_program(str(STOCK), project_location=str(GH / 'projects'),
                           project_name='stock_p1e', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    space = p.getAddressFactory().getDefaultAddressSpace()
    mem = p.getMemory()
    pdis = PseudoDisassembler(p)

    # Let's check TOC of stock.elf. What is r2?
    # In stock netemu, r2 is commonly 0x751280 or similar.
    # Let's check references to 0x10550 and 0x10834.
    refs = p.getReferenceManager()
    ref_10550 = list(refs.getReferencesTo(space.getAddress(0x10550)))
    print("References to 0x10550:")
    for r in ref_10550:
        print(f"  from {r.getFromAddress()}")

    ref_10834 = list(refs.getReferencesTo(space.getAddress(0x10834)))
    print("References to 0x10834:")
    for r in ref_10834:
        print(f"  from {r.getFromAddress()}")

    # Let's inspect the caller of 0x10550 at 0x16f38 and 0x175e0
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

    print("\nDisassembling caller at 0x16f30..0x16f50:")
    for l in disasm_range(0x16f30, 8):
        print(l)

    # Let's check the base address calculation in 0x10550:
    # 0x00010564: ld r6,-0x7ff8(r2)
    # What is at r2 - 0x7ff8 when r2 = 0x751280?
    toc = 0x751280
    val_addr = toc - 0x7ff8
    val = mem.getLong(space.getAddress(val_addr))
    print(f"TOC at {hex(val_addr)}: value = {hex(val)}")
    # r0 = r0 (bank offset) + r6 (val)
    # r9 = r0 + r11 (index 0..255)
    # r9 = r9 + 0x750
    # stb r10, 0xc(r9)
    # So address is: val + bank + index + 0x750 + 0xc = val + 0x75c + bank + index
    print(f"Effective store address for bank 0, index 0: {hex(val + 0x75c)}")
    print(f"Bridge read address at 0xc74: 0x238c + bank + call_num")
    print(f"Difference: {hex((val + 0x75c) - 0x238c)}")
