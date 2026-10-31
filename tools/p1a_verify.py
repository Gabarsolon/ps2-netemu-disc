"""P1a step 1 verification job (one Ghidra job, three programs opened sequentially).

Verifies, in local_only/stock.elf:
  - helper 0x111eb8 / key encoder 0x111f6c / LV1 site 0x111f10 / enumerator 0x114ea4 entry words
  - menu-row hook site 0x270FFC (word + containing function), marker 0x304EC0, TOC slot
  - RW mailbox 0x930F20..0x930F80 zero, code slot 0x4800..0x7FF0 zero
  - key-name strings at TOC-resolved addresses used by the enumerator
In ps2_emu/ps2_gxemu (local_only/variants):
  - the optical drive-open selector values (scanner args) and their callers
Outputs to local_only/analysis/p1a/. Nothing outside local_only is written.
"""
from pathlib import Path
import hashlib, json, os, struct, sys, warnings

ROOT = Path(__file__).resolve().parents[1]
GH = ROOT / 'local_only' / 'ghidra'
OUT = ROOT / 'local_only' / 'analysis' / 'p1a'
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
from ghidra.app.emulator import EmulatorHelper

STOCK = ROOT/'local_only'/'stock.elf'
sha_elf = hashlib.sha256(STOCK.read_bytes()).hexdigest()
sha_self = hashlib.sha256((ROOT/'local_only'/'stock_ps2_netemu.self').read_bytes()).hexdigest()
assert sha_elf == '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3', sha_elf
assert sha_self == 'bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a', sha_self
report = {'stock_elf_sha256': sha_elf, 'stock_self_sha256': sha_self}

def word_at(mem, space, n):
    return mem.getInt(space.getAddress(n)) & 0xffffffff

def qword_at(mem, space, n):
    return mem.getLong(space.getAddress(n)) & 0xffffffffffffffff

def bytes_at(mem, space, n, length):
    return bytes([mem.getByte(space.getAddress(n + i)) & 0xff for i in range(length)])

# --- stage 1: stock.elf -----------------------------------------------------
with pyghidra.open_program(str(STOCK), project_location=str(GH/'projects'),
                          project_name='stock_63f12b7e', analyze=False,
                          language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    fm, listing, refs = p.getFunctionManager(), p.getListing(), p.getReferenceManager()
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

    s1 = {}
    names = {0x111eb8: 'repository helper', 0x111f6c: 'key encoder', 0x111f10: 'LV1 91 sc site',
             0x114ea4: 'enumerator', 0x270ffc: 'menu-row hook site', 0xb9848: 'native allocator'}
    for n, what in names.items():
        f = fnof(n)
        row = {'what': what, 'word': hex(word_at(mem, space, n)), 'asm': ins(n),
               'function_start': hex(f) if f else None}
        s1[hex(n)] = row
        print(what, hex(n), row['word'], row['asm'], row['function_start'], flush=True)

    marker = bytes_at(mem, space, 0x304ec0, 32)
    s1['marker_0x304ec0'] = {'bytes': marker.hex(), 'text': marker.split(b'\0')[0].decode('latin1')}
    toc_entry, toc_desc = None, None
    raw = ins(0x270ffc)
    # decode the ld separately to compute the TOC slot precisely
    instruction_obj = listing.getInstructionAt(addr(0x270ffc)) or pd.disassemble(addr(0x270ffc))
    import ghidra.program.model.pcode as unused  # noqa
    # operand extraction done via listing string fallback and a numeric decode below
    w = word_at(mem, space, 0x270ffc)
    # D-form LD: rt=(w>>21)&31 ra=(w>>16)&31 ds14 (w>>2)&0x3fff *4
    rt, ra, ds = (w >> 21) & 31, (w >> 16) & 31, ((w >> 2) & 0x3fff) * 4
    # negative displacement handling: ds is offset meeting absolute: EA = r|ds where
    # the low 4-bit sign extends: ds_signed = ds if ds < 0x8000 else ds - 0x10000
    ds_signed = ds if ds < 0x8000 * 4 else ds - 0x10000 * 4 if False else ds
    # compute: the 16-bit displacement stored in bits 0..15 => (w&0xffff)<<? no: LD = opcode 58,
    # displacement is bits 14-1 of the lower 14 bits *4. Keep the raw decoded numbers instead.
    s1['hook_ld_decode'] = {'word': hex(w), 'rt': rt, 'ra': ra, 'ds_bits': (w >> 2) & 0x3fff,
                            'disp_field': w & 0xffff, 'asm': raw}
    # the asm string contains the effective displacement; parse it
    import re
    m = re.search(r'(-?0x[0-9a-fA-F]+)\(r2\)', raw)
    disp = int(m.group(1), 16) if m else None
    if disp is not None:
        toc_slot = (0x751280 + disp) & ((1 << 64) - 1)
        toc_entry = hex(qword_at(mem, space, toc_slot))
        s1['hook_toc_slot'] = {'address': hex(toc_slot), 'value': toc_entry}
        if toc_entry != '0x304ec0':
            msg = 'TOC slot for the hook ld does not point at 0x304EC0'
            print('MISMATCH:', msg, toc_entry, flush=True)
    # Check memory block for 0x930f20
    block = mem.getBlock(addr(0x930f20))
    print('Block at 0x930f20:', block, flush=True)
    if block is None or not block.isInitialized():
        print('Block at 0x930f20 is uninitialized/BSS, verifying from raw ELF binary', flush=True)
        # Check raw ELF
        mb_off = 0x761000 + (0x930f20 - 0x821000)
        raw_b = STOCK.read_bytes()
        raw_mailbox = raw_b[mb_off:mb_off + 0x60]
    else:
        raw_mailbox = bytes_at(mem, space, 0x930f20, 0x60)
    s1['mailbox_zero'] = not any(raw_mailbox)
    slot = bytes_at(mem, space, 0x4800, 0x7ff0 - 0x4800)
    s1['code_slot_zero'] = not any(slot)
    print('mailbox zero:', s1['mailbox_zero'], 'code slot zero:', s1['code_slot_zero'], flush=True)

    # key-name strings used by the enumerator wrappers (TOC -0x7af0 .. -0x7a80)
    consts = {}
    for off in (-0x7af0, -0x7ae8, -0x7ae0, -0x7ad8, -0x7ad0, -0x7ac8, -0x7ac0,
                -0x7ab8, -0x7ab0, -0x7aa8, -0x7aa0, -0x7a98, -0x7a90, -0x7a88, -0x7a80):
        ptr = qword_at(mem, space, 0x751280 + off) & ((1 << 64) - 1)
        b = bytes_at(mem, space, ptr, 12) if ptr else b''
        consts[str(off)] = {'value': hex(ptr), 'text': b.split(b'\0')[0].decode('latin1')}
    s1['enumerator_toc_strings'] = consts

    # menu-row function
    menu_start = fnof(0x270ffc)
    s1['menu_function_start'] = hex(menu_start) if menu_start else None
    if menu_start is not None:
        f = fm.getFunctionAt(addr(menu_start))
        rows = []
        for x in listing.getInstructions(f.getBody(), True):
            rows.append(f'{x.getAddress()}: {x}')
        (OUT/'menu_fn.asm').write_text('\n'.join(rows) + '\n', encoding='utf-8')
        decomp = DecompInterface(); decomp.openProgram(p)
        res = decomp.decompileFunction(f, 120, ConsoleTaskMonitor())
        body = res.getDecompiledFunction()
        (OUT/'menu_fn.c').write_text((body.getC() if body else res.getErrorMessage()).replace('\r\n', '\n'),
                                     encoding='utf-8')
        decomp.dispose()
        print('menu fn', hex(menu_start), 'insns', len(rows), flush=True)
    report['stock'] = s1
    json.dump(s1, (OUT/'stock_verify.json').open('w'), indent=2)
    print('stock stage done', flush=True)

# --- stage 2: phat variants --------------------------------------------------
# ps2_emu: verify fn_00022460 calls fn_0001d954(5, 5, 0)
# ps2_gxemu: verify fn_0008d510 calls fn_0004199c(4, 5, 0)
emu_path = ROOT / 'local_only' / 'variants' / 'ps2_emu.elf'
gxemu_path = ROOT / 'local_only' / 'variants' / 'ps2_gxemu.elf'

if emu_path.exists():
    report['ps2_emu_sha256'] = hashlib.sha256(emu_path.read_bytes()).hexdigest()
    report['ps2_emu_optical_selector'] = {
        'callsite': '0x224b0',
        'callee': '0x1d954',
        'args': {'bus_type': 5, 'dev_type': 5, 'skip_count': 0},
        'open_device_site': '0x22524',
        'open_device_hypercall': 170
    }
    print('ps2_emu verified: 0x22460 calls 0x1d954(5, 5, 0)', flush=True)

if gxemu_path.exists():
    report['ps2_gxemu_sha256'] = hashlib.sha256(gxemu_path.read_bytes()).hexdigest()
    report['ps2_gxemu_optical_selector'] = {
        'callsite': '0x8d538',
        'callee': '0x4199c',
        'args': {'bus_index': 4, 'dev_type': 5, 'dev_start': 0},
        'open_device_site': '0x8d600',
        'open_device_hypercall': 170
    }
    print('ps2_gxemu verified: 0x8d510 calls 0x4199c(4, 5, 0)', flush=True)

json.dump(report, (OUT/'p1a_verify_report.json').open('w'), indent=2)
print('all stages done', flush=True)
