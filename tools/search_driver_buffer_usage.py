import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p2e'
TMP_DIR = GH / 'tmp'
SETTINGS_DIR = GH / 'settings'

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

def disassemble_range(p, start_ea, end_ea):
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)
    addr = s.getAddress(start_ea)
    end = s.getAddress(end_ea)
    lines = []
    while addr.compareTo(end) < 0:
        ins = pd.disassemble(addr)
        if ins is None:
            addr = addr.add(4)
            continue
        txt = ins.toString()
        lines.append((addr.getOffset(), txt))
        addr = addr.add(ins.getLength())
    return lines

stock_elf = ROOT / 'local_only' / 'stock.elf'
with pyghidra.open_program(str(stock_elf), project_location=str(GH / 'projects'),
                           project_name='stock_p2e_analysis', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()

    # 1. Search for references to 0x1448 and 0x1458 in CDVD driver (0x133000..0x137000)
    print("=== CDVD driver references to 0x1448, 0x1450, 0x1458 ===")
    cdvd_ins = disassemble_range(p, 0x133000, 0x138000)
    for off, txt in cdvd_ins:
        if any(k in txt for k in ['0x1448', '0x1450', '0x1458']):
            print(f"  0x{off:06x}: {txt}")

    # 2. Search for storage hypercalls in stock.elf:
    # 248 = 0xf8 (storage_send_device_command)
    # 245 = 0xf5 (storage_read)
    # 254 = 0xfe (storage_check_async_status)
    print("\n=== Hypercall 248 (0xf8), 245 (0xf5), 254 (0xfe) in stock.elf ===")
    all_text = disassemble_range(p, 0x100000, 0x140000)
    for i, (off, txt) in enumerate(all_text):
        if 'li r11,0xf8' in txt or 'li r11,0xf5' in txt or 'li r11,0xfe' in txt:
            print(f"Hypercall found around 0x{off:06x}: {txt}")
            # print surrounding 15 instructions
            start = max(0, i - 10)
            end = min(len(all_text), i + 10)
            for j in range(start, end):
                print(f"    0x{all_text[j][0]:06x}: {all_text[j][1]}")
