import struct, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p1g'
stock_elf = ROOT / 'local_only' / 'stock.elf'

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

def build_wrapper_bytes(stock_bytes):
    assert len(stock_bytes) == 180
    w = bytearray(stock_bytes)

    # Dictionary of changed offsets -> new 32-bit hex words
    changes = {
        0x04: 0x60000000,  # nop
        0x08: 0x60000000,  # nop
        0x18: 0x3FC00093,  # lis r30, 0x93
        0x1C: 0x3BDE0F70,  # addi r30, r30, 0x0f70 (r30 = 0x930F70 = &raw_val1)
        0x20: 0x3BFE0008,  # addi r31, r30, 8      (r31 = 0x930F78 = &raw_val2)
        0x24: 0x7C6B1B78,  # mr r11, r3           (r11 = num)
        0x28: 0x7C832378,  # mr r3, r4            (r3 = a1)
        0x38: 0x7CA42B78,  # mr r4, r5            (r4 = a2)
        0x3C: 0x7CC53378,  # mr r5, r6            (r5 = a3)
        0x40: 0x7CE63B78,  # mr r6, r7            (r6 = a4)
        0x44: 0x7D074378,  # mr r7, r8            (r7 = a5)
        0x48: 0x60000000,  # nop
        0x4C: 0x60000000,  # nop
        0x50: 0x60000000,  # nop
        0xA8: 0x60000000,  # nop
        0xAC: 0x60000000,  # nop
        0xB0: 0x60000000,  # nop
    }

    for off, val in changes.items():
        struct.pack_into('>I', w, off, val)

    return bytes(w)

stock_bytes = stock_elf.read_bytes()[0x121eb8 : 0x121eb8 + 180]
wrapper_bytes = build_wrapper_bytes(stock_bytes)
assert len(wrapper_bytes) == 180

with pyghidra.open_program(str(stock_elf), project_location=str(GH / 'projects'),
                           project_name='p1g_asm_verify', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    s = p.getAddressFactory().getDefaultAddressSpace()
    pd = PseudoDisassembler(p)

    target_va = 0x4800
    print(f"\n--- Disassembly of Generic Wrapper (0x4800..0x48B4) ---")
    ident_cnt = 0
    for i in range(0, 180, 4):
        w = struct.unpack_from('>I', wrapper_bytes, i)[0]
        sw = struct.unpack_from('>I', stock_bytes, i)[0]
        is_ident = (w == sw)
        if is_ident: ident_cnt += 1
        ident_str = "MATCH" if is_ident else "DIFF "
        print(f"+0x{i:02x} (0x{target_va+i:04x}): {w:08x} [{ident_str}] (stock: {sw:08x})")

    print(f"\nTotal identical instructions: {ident_cnt} / 45")
    assert ident_cnt == 28, f"Expected 28 identical instructions, got {ident_cnt}"
    print("[PASS] Exactly 28 instructions match stock byte-for-byte!")
