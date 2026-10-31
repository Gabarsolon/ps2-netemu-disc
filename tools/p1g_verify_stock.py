import os, sys, struct, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p1g'
GH.mkdir(parents=True, exist_ok=True)
(GH / 'projects').mkdir(parents=True, exist_ok=True)
(GH / 'tmp').mkdir(parents=True, exist_ok=True)
(GH / 'settings').mkdir(parents=True, exist_ok=True)

os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

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

stock_elf = ROOT / 'local_only' / 'stock.elf'
stock_self = ROOT / 'local_only' / 'stock_ps2_netemu.self'

stock_bytes = stock_elf.read_bytes()
elf_sha = hashlib.sha256(stock_bytes).hexdigest()
self_sha = hashlib.sha256(stock_self.read_bytes()).hexdigest()

print(f"stock.elf SHA256: {elf_sha}")
print(f"stock.self SHA256: {self_sha}")
assert elf_sha == '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
assert self_sha == 'bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'

with pyghidra.open_program(str(stock_elf), project_location=str(GH / 'projects'),
                           project_name='p1g_stock_inspect', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)

    def disasm_range(title, start_addr, end_addr):
        print(f"\n--- {title}: {hex(start_addr)} .. {hex(end_addr)} ---")
        cur = start_addr
        lines = []
        while cur < end_addr:
            addr = s.getAddress(cur)
            ins = pd.disassemble(addr)
            w = p.getMemory().getInt(addr) & 0xFFFFFFFF
            if ins:
                line = f"0x{cur:06x}: {w:08x}  {ins}"
                print(line)
                lines.append((cur, w, str(ins)))
                cur += ins.getLength()
            else:
                line = f"0x{cur:06x}: {w:08x}  <cannot disassemble>"
                print(line)
                lines.append((cur, w, "<cannot disassemble>"))
                cur += 4
        return lines

    disasm_range("Stock Helper 0x111eb8", 0x111eb8, 0x111f6c)
    disasm_range("HV 170 Stock Call Site (HDD Init)", 0x12bf70, 0x12bfa0)
    disasm_range("HV 171 Stock Call Site (Close Site)", 0x12d600, 0x12d620)
    disasm_range("Hook Site 0x270FFC", 0x270FF8, 0x271008)

    # Check hook word
    hook_addr = s.getAddress(0x270FFC)
    hook_val = p.getMemory().getInt(hook_addr) & 0xFFFFFFFF
    print(f"\nHook word at 0x270FFC: {hook_val:08x} (expected e882cea8)")
    assert hook_val == 0xe882cea8, f"Hook word mismatch: {hook_val:08x}"
    print("[PASS] Hook word matches 0xe882cea8 exactly.")
