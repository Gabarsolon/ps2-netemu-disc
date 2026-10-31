import os, sys, hashlib, warnings
from pathlib import Path

warnings.filterwarnings('ignore', category=DeprecationWarning)
ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
GH_DIR = ROOT / 'local_only' / 'ghidra_p2'
GH_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = GH_DIR / 'tmp'
TMP_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_DIR = GH_DIR / 'settings'
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

for k in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[k] = str(TMP_DIR if k in ['TEMP', 'TMP', 'TMPDIR'] else SETTINGS_DIR)

os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

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

def disassemble_range(p, start_ea, count=30):
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)
    addr = s.getAddress(start_ea)
    lines = []
    for _ in range(count):
        ins = pd.disassemble(addr)
        if ins is None:
            lines.append(f"0x{addr.getOffset():08x}: <unable to disassemble>")
            addr = addr.add(4)
            continue
        lines.append(f"0x{addr.getOffset():08x}: {ins.toString()}")
        addr = addr.add(ins.getLength())
    return "\n".join(lines)

def inspect_lv1():
    print("=== Inspecting LV1 (local_only/fw493/lv1.elf) ===")
    lv1_path = ROOT / 'local_only' / 'fw493' / 'lv1.elf'
    with pyghidra.open_program(
        str(lv1_path),
        project_location=str(GH_DIR / 'projects'),
        project_name='lv1_493',
        analyze=False,
        language='PowerPC:BE:64:default'
    ) as flat:
        p = flat.getCurrentProgram()
        handlers = [
            ("HV 174 (allocate_device_dma_region)", 0x306a6c, 25),
            ("HV 175 (free_device_dma_region)", 0x306918, 20),
            ("HV 176 (map_device_dma_region)", 0x306770, 25),
            ("HV 177 (unmap_device_dma_region)", 0x30660c, 20),
            ("HV 245 (storage_read)", 0x308b88, 30),
            ("HV 248 (storage_send_device_command)", 0x3094e4, 30),
            ("HV 249 (storage_get_async_status)", 0x3093ac, 25),
            ("HV 254 (storage_check_async_status)", 0x30926c, 25),
        ]
        out_lines = []
        for name, addr, cnt in handlers:
            header = f"\n--- {name} at 0x{addr:08x} ---"
            print(header)
            out_lines.append(header)
            dis = disassemble_range(p, addr, cnt)
            print(dis)
            out_lines.append(dis)
        (ROOT / 'local_only' / 'analysis' / 'p2_lv1_handlers.txt').write_text("\n".join(out_lines), encoding='utf-8')

def inspect_stock():
    print("=== Inspecting Stock Netemu (local_only/stock.elf) ===")
    stock_path = ROOT / 'local_only' / 'stock.elf'
    with pyghidra.open_program(
        str(stock_path),
        project_location=str(GH_DIR / 'projects'),
        project_name='stock_netemu',
        analyze=False,
        language='PowerPC:BE:64:default'
    ) as flat:
        p = flat.getCurrentProgram()
        sections = [
            ("HDD init DMA setup", 0x12c010, 25),
            ("DMA map helper 0x160fc", 0x160fc, 25),
            ("HDD read submission (245)", 0x12b650, 30),
            ("HDD interrupt handler (249)", 0x12b320, 25),
            ("Allocator shim 0x19a5c", 0x19a5c, 25),
            ("Allocator 0x19900", 0x19900, 35),
            ("Memory allocator 0x1622c", 0x1622c, 30),
            ("Page-table mapping helper 0x16790", 0x16790, 30),
            ("Native clock 0xb9cd0", 0xb9cd0, 20),
        ]
        out_lines = []
        for name, addr, cnt in sections:
            header = f"\n--- {name} at 0x{addr:08x} ---"
            print(header)
            out_lines.append(header)
            dis = disassemble_range(p, addr, cnt)
            print(dis)
            out_lines.append(dis)
        (ROOT / 'local_only' / 'analysis' / 'p2_stock_callsites.txt').write_text("\n".join(out_lines), encoding='utf-8')

if __name__ == '__main__':
    inspect_lv1()
    inspect_stock()
