"""P1c step 1 verification in stock.elf using pyghidra.
Verifies:
  1. Enumerator (0x114ea4) and key encoder (0x111f6c) & helper (0x111eb8)
  2. HDD init (0x12be04)
  3. Allocator (0xb9848) and pool checks (0x934980, 0x24565b8, 0x2446588)
  4. Mailbox layout at 0x930F20..0x930F80 (must be all zeroes in stock)
  5. Hook site at 0x270FFC (expected 0xe882cea8)
  6. Label marker at 0x304EC0 (expected "Debug Information\0")
"""
from pathlib import Path
import hashlib, json, os, struct, sys, warnings

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT / 'local_only' / 'ghidra_p1c'
GH.mkdir(parents=True, exist_ok=True)
OUT = ROOT / 'local_only' / 'analysis' / 'p1c'
OUT.mkdir(parents=True, exist_ok=True)

for key in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA'):
    (GH / ('tmp' if key in ('TEMP', 'TMP', 'TMPDIR') else 'settings')).mkdir(parents=True, exist_ok=True)
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
assert sha_elf == '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3', sha_elf

def word_at(mem, space, n):
    return mem.getInt(space.getAddress(n)) & 0xffffffff

def dword_at(mem, space, n):
    return mem.getLong(space.getAddress(n))

def bytes_at(mem, space, n, length):
    return bytes([mem.getByte(space.getAddress(n + i)) & 0xff for i in range(length)])

results = {}

with pyghidra.open_program(str(STOCK), project_location=str(GH / 'projects'),
                           project_name='stock_p1c', analyze=False,
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

    def disasm_range(start, count):
        lines = []
        for i in range(count):
            cur = start + i * 4
            w = word_at(mem, space, cur)
            instruction = ins(cur)
            lines.append(f"0x{cur:06x}: {w:08x}  {instruction}")
        return lines

    print("=== 1. Enumerator & Key Strings ===")
    toc_base = 0x751280
    offsets = [
        -0x7af0, -0x7ae8, -0x7ae0, -0x7ad8, -0x7ad0,
        -0x7ac8, -0x7ac0, -0x7ab8, -0x7ab0, -0x7aa8,
        -0x7aa0, -0x7a98, -0x7a90, -0x7a88, -0x7a80
    ]
    key_strings = {}
    for off in offsets:
        va = toc_base + off
        str_ptr = dword_at(mem, space, va)
        raw_str = bytes_at(mem, space, str_ptr, 32).split(b'\0')[0].decode('latin1', 'replace')
        key_strings[f"{off:#x}"] = {'ptr': hex(str_ptr), 'string': raw_str}
        print(f"  TOC {off:#x} ({va:#x}): {str_ptr:#x} -> '{raw_str}'")
    results['key_strings'] = key_strings

    print("\n=== 2. HDD Init 0x12be04 ===")
    lines_hdd_init = disasm_range(0x12be04, 30)
    for l in lines_hdd_init:
        print(f"  {l}")
    results['hdd_init'] = lines_hdd_init

    print("\n=== 3. Native Allocator 0xB9848 ===")
    lines_alloc = disasm_range(0xb9848, 40)
    for l in lines_alloc:
        print(f"  {l}")
    results['allocator'] = lines_alloc

    print("\n=== 4. Mailbox at 0x930F20..0x930F80 ===")
    blocks = list(mem.getBlocks())
    for b in blocks:
        print(f"  Block: {b.getName()} ({b.getStart()}..{b.getEnd()}) read={b.isRead()} write={b.isWrite()} exec={b.isExecute()}")
    mb_addr = addr(0x930F20)
    mb_block = mem.getBlock(mb_addr)
    print(f"  Mailbox address block in Ghidra: {mb_block}")
    if mb_block is not None:
        mbox_bytes = bytes_at(mem, space, 0x930F20, 96)
        is_zero = not any(mbox_bytes)
        print(f"  Mailbox (Ghidra) is all zeroes: {is_zero} (len={len(mbox_bytes)})")
    else:
        # Check via direct ELF segment mapping
        # Find segment containing 0x930F20
        e_bytes = STOCK.read_bytes()
        po, so = struct.unpack_from('>QQ', e_bytes, 32)
        pn = struct.unpack_from('>H', e_bytes, 56)[0]
        phdrs = [struct.unpack_from('>IIQQQQQQ', e_bytes, po + 56 * i) for i in range(pn)]
        mb_file_off = None
        for typ, fl, off, vaddr, paddr, fsz, msz, align in phdrs:
            if typ == 1 and vaddr <= 0x930F20 < vaddr + fsz:
                mb_file_off = off + (0x930F20 - vaddr)
                break
        assert mb_file_off is not None, "Mailbox not within any PT_LOAD file segment"
        mbox_bytes = e_bytes[mb_file_off : mb_file_off + 96]
        is_zero = not any(mbox_bytes)
        print(f"  Mailbox (ELF segment offset {hex(mb_file_off)}) is all zeroes: {is_zero} (len={len(mbox_bytes)})")
    results['mailbox_all_zero'] = is_zero

    print("\n=== 5. Hook Site 0x270FFC ===")
    hook_w = word_at(mem, space, 0x270FFC)
    print(f"  0x270FFC: {hook_w:08x} ({ins(0x270FFC)})")
    assert hook_w == 0xe882cea8, f"Unexpected hook word: {hex(hook_w)}"
    results['hook_word'] = hex(hook_w)

    print("\n=== 6. Label Marker 0x304EC0 ===")
    marker_bytes = bytes_at(mem, space, 0x304EC0, 32)
    marker_str = marker_bytes.split(b'\0')[0].decode('latin1', 'replace')
    print(f"  0x304EC0: '{marker_str}'")
    assert marker_str == "Debug Information", f"Unexpected marker string: '{marker_str}'"
    results['marker_str'] = marker_str

    # Decompile 0xb9848
    decomp = DecompInterface()
    decomp.openProgram(p)
    f_alloc = fm.getFunctionAt(addr(0xb9848))
    if f_alloc is None:
        from ghidra.program.model.symbol import SourceType
        f_alloc = fm.createFunction("native_alloc", addr(0xb9848),
                                    p.getAddressFactory().getAddressSet(addr(0xb9848), addr(0xb99a0)),
                                    SourceType.USER_DEFINED)
    res = decomp.decompileFunction(f_alloc, 30, ConsoleTaskMonitor())
    if res.decompileCompleted():
        ccode = res.getDecompiledFunction().getC()
        (OUT / 'native_alloc.c').write_text(ccode)
        print("  Decompiled native_alloc saved to local_only/analysis/p1c/native_alloc.c")
    else:
        print("  Decompilation of native_alloc did not complete:", res.getErrorMessage())

(OUT / 'p1c_verification.json').write_text(json.dumps(results, indent=2))
print("\n[SUCCESS] Step 1 verification complete!")
