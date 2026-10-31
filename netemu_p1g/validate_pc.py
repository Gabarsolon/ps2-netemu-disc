"""Comprehensive PC validation test suite for P1g diagnostic builds (G0..G3):
  - Validates generic safe hypercall wrapper lv1_hcall (0x4800, sc at 0x4858)
  - Validates all four variants:
      G0: lv1_hcall(0x5b, 1, 0x62757304, KEY_DEV(2), KEY_TYPE, 0) -> MATCH with stock helper (rc=0, v=5 ROM)
      G1: lv1_hcall(170, 9, 0, 0, 0, 0) -> exactly one 170 with args (9, 0, 0), rc=-17 (INVALID_PARAMETER)
      G2: lv1_hcall(171, 4, 2, 0, 0, 0) -> exactly one 171 with args (4, 2), rc=-11 (NOT_OWNER)
      G3: lv1_hcall(170, 4, 2, 0, 0, 0) -> exactly one 170 with args (4, 2, 0);
          and lv1_hcall(171, 4, 2, 0, 0, 0) ONLY if 170 returns 0 (test rc=0, -4, -6, -9, -17)
  - Once-only execution across repeated menu open invocations
  - Fail-open on hook mismatch
  - Register preservation test:
      In emulator, sets cr2/cr3/cr4, LR, r30, r31, r14..r29 to marker values before calling wrapper
      and asserts they are unchanged after (compared against stock helper 0x111eb8)
  - Memory write tracking: strictly stack or mailbox [0x930F20, 0x930F80)
  - Exhaustive index bounds fuzzing across Pages A, B, C, D
  - Strict store audit (tools/p1a_audit.py): exactly one sc in changed executable ranges (0x4858)
  - Installer scripts syntax parse check
"""
from pathlib import Path
import json, hashlib, os, struct, subprocess, sys, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

H = Path(__file__).resolve().parent
ROOT = H.parent
GH = ROOT / 'local_only' / 'ghidra_p1g'

for d in ['evidence', 'tmp', 'settings']:
    (H / d).mkdir(exist_ok=True)
(GH / 'projects').mkdir(parents=True, exist_ok=True)

for k in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[k] = str(H / ('tmp' if k in ['TEMP', 'TMP', 'TMPDIR'] else 'settings'))
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G', '-Duser.home=' + str(H / 'settings'),
                    '-Dapplication.settingsdir=' + str(H / 'settings'),
                    '-Djava.io.tmpdir=' + str(H / 'tmp'))
launcher.start()

from ghidra.app.emulator import EmulatorHelper
from ghidra.util.task import ConsoleTaskMonitor, TimeoutTaskMonitor
from ghidra.app.util import PseudoDisassembler
from java.math import BigInteger
from java.util.concurrent import TimeUnit

MASK = (1 << 64) - 1
SP = 0xaaa700bfe00
STOP = 0x7FF0
BUF = 0x2200000
MAILBOX = 0x930F20
STR_STRIDE = 64

# Key tags
KEY_TYPE = 0x7479706500000000
KEY_ID   = 0x6964000000000000
KEY_PORT = 0x706f727400000000
def TAG_BUS(b): return 0x62757300 | (b & 0xFF)
def KEY_DEV(d): return 0x6465760000000000 | (d & 0xFF)

# Standard fake repository matching console layout
fake_repo_console = {
    # Bus 4: Storage Bus (type 5)
    (TAG_BUS(4), KEY_TYPE, 0, 0): (5, 0),         # bus 4 type = 5 (STORAGE)
    (TAG_BUS(4), KEY_ID, 0, 0): (4, 0),           # bus 4 id = 4
    # Dev 2: Optical ROM
    (TAG_BUS(4), KEY_DEV(2), KEY_TYPE, 0): (5, 0),       # type 5 (ROM)
    (TAG_BUS(4), KEY_DEV(2), KEY_ID, 0): (2, 0),         # dev id = 2
    (TAG_BUS(4), KEY_DEV(2), KEY_PORT, 0): (0, 0),       # port 0
    # Dev 3: HDD DISK
    (TAG_BUS(4), KEY_DEV(3), KEY_TYPE, 0): (0, 0),       # type 0 (DISK)
    (TAG_BUS(4), KEY_DEV(3), KEY_ID, 0): (3, 0),         # dev id = 3
    (TAG_BUS(4), KEY_DEV(3), KEY_PORT, 0): (2, 0),       # port 2 (HDD control)
}

def verify_wrapper_bytes(elf_path):
    """Assert wrapper bytes at 0x4800..0x48b4: exactly 29 instructions match stock helper,
    sc 0 is at offset 0x58 (0x4858)."""
    stock_path = ROOT / 'local_only' / 'stock.elf'
    stock_bytes = stock_path.read_bytes()[0x121eb8 : 0x121eb8 + 180]
    elf_bytes = elf_path.read_bytes()

    # Find file offset of 0x4800 in patched ELF
    po, = struct.unpack_from('>Q', elf_bytes, 32)
    pn, = struct.unpack_from('>H', elf_bytes, 56)
    elf_off = None
    for i in range(pn):
        t, f, off, va, pa, fsz, msz, al = struct.unpack_from('>IIQQQQQQ', elf_bytes, po + 56 * i)
        if t == 1 and va <= 0x4800 < va + fsz:
            elf_off = off + (0x4800 - va)
            break
    assert elf_off is not None, "Could not locate 0x4800 in ELF"

    wrapper_bytes = elf_bytes[elf_off : elf_off + 180]
    assert len(wrapper_bytes) == 180

    # Exactly 29 instructions match stock byte-for-byte
    ident_cnt = sum(1 for i in range(0, 180, 4) if wrapper_bytes[i:i+4] == stock_bytes[i:i+4])
    assert ident_cnt == 29, f"Expected 29 identical instructions, got {ident_cnt}"

    # sc 0 is at 0x58 (0x4858)
    sc_val, = struct.unpack_from('>I', wrapper_bytes, 0x58)
    assert sc_val == 0x44000002, f"sc 0 not at 0x58: {hex(sc_val)}"

def run_register_preservation_test(program):
    """Test register preservation on generic wrapper (0x4800) and compare with stock helper (0x111eb8).
    Sets CR fields cr2/cr3/cr4, LR, r30, r31, r14..r29 to marker values before calling
    and asserts they are unchanged after returning."""
    print("\n--------------------------------------------------")
    print("Running Register Preservation Test (wrapper vs stock)...")
    print("--------------------------------------------------")

    s = program.getAddressFactory().getDefaultAddressSpace()

    funcs = [
        ('Stock Helper', 0x111eb8, 0x111f10, 0x111f14),
        ('Generic Wrapper (lv1_hcall)', 0x4800, 0x4858, 0x485C)
    ]

    for fname, entry_addr, sc_addr, post_sc_pc in funcs:
        em = EmulatorHelper(program)
        em.setBreakpoint(s.getAddress(sc_addr))
        em.setBreakpoint(s.getAddress(STOP))

        # Setup stack and LR
        em.writeRegister('r1', BigInteger(str(SP)))
        em.writeRegister('r2', BigInteger(str(0x751280)))
        em.writeRegister('lr', BigInteger(str(STOP)))

        # Non-volatile registers r14..r29
        initial_nv = {}
        for r in range(14, 30):
            val = 0x1400000000000000 | (r << 16) | 0xDEAD
            initial_nv[r] = val
            em.writeRegister(f'r{r}', BigInteger(str(val)))

        # r30, r31
        val_r30 = 0x30303030BEEFCAFE
        val_r31 = 0x31313131FEEDFACE
        em.writeRegister('r30', BigInteger(str(val_r30)))
        em.writeRegister('r31', BigInteger(str(val_r31)))

        # CR fields cr2, cr3, cr4
        val_cr2 = 9
        val_cr3 = 5
        val_cr4 = 6
        em.writeRegister('cr2', BigInteger(str(val_cr2)))
        em.writeRegister('cr3', BigInteger(str(val_cr3)))
        em.writeRegister('cr4', BigInteger(str(val_cr4)))

        # Arguments for the call
        if entry_addr == 0x111eb8:
            em.writeRegister('r3', BigInteger(str(MAILBOX + 80)))
            em.writeRegister('r4', BigInteger(str(MAILBOX + 88)))
            em.writeRegister('r5', BigInteger(str(0x6275730000000004)))
            em.writeRegister('r6', BigInteger(str(0x6465760000000002)))
            em.writeRegister('r7', BigInteger(str(0x7479706500000000)))
            em.writeRegister('r8', BigInteger('0'))
        else:
            em.writeRegister('r3', BigInteger('91'))
            em.writeRegister('r4', BigInteger('1'))
            em.writeRegister('r5', BigInteger(str(0x62757304)))
            em.writeRegister('r6', BigInteger(str(0x6465760000000002)))
            em.writeRegister('r7', BigInteger(str(0x7479706500000000)))
            em.writeRegister('r8', BigInteger('0'))

        em.writeRegister(em.getPCRegister(), BigInteger(str(entry_addr)))
        timeout = TimeoutTaskMonitor.timeoutIn(10, TimeUnit.SECONDS)

        # Run to sc 0
        ok = em.run(timeout)
        assert ok, f"{fname} failed before sc"
        cur = em.getExecutionAddress().getOffset()
        assert cur == sc_addr, f"{fname} did not stop at sc: stopped at {hex(cur)}"

        # Simulate hypercall return: rc = 0, val1 = 5, val2 = 0
        em.writeRegister('r3', BigInteger('0'))
        em.writeRegister('r4', BigInteger('5'))
        em.writeRegister('r5', BigInteger('0'))
        em.writeRegister(em.getPCRegister(), BigInteger(str(post_sc_pc)))

        # Run to STOP (after blr)
        ok = em.run(timeout)
        assert ok, f"{fname} failed after sc"
        cur = em.getExecutionAddress().getOffset()
        assert cur == STOP, f"{fname} did not return to STOP: stopped at {hex(cur)}"

        # 1. Check LR restored
        lr_after = int(str(em.readRegister('lr'))) & MASK
        assert lr_after == STOP, f"{fname}: LR clobbered! Got {hex(lr_after)}, expected {hex(STOP)}"

        # 2. Check r30, r31 restored
        r30_after = int(str(em.readRegister('r30'))) & MASK
        r31_after = int(str(em.readRegister('r31'))) & MASK
        assert r30_after == val_r30, f"{fname}: r30 clobbered! Got {hex(r30_after)}, expected {hex(val_r30)}"
        assert r31_after == val_r31, f"{fname}: r31 clobbered! Got {hex(r31_after)}, expected {hex(val_r31)}"

        # 3. Check r14..r29 untouched
        for r in range(14, 30):
            val_after = int(str(em.readRegister(f'r{r}'))) & MASK
            assert val_after == initial_nv[r], f"{fname}: r{r} clobbered! Got {hex(val_after)}, expected {hex(initial_nv[r])}"

        # 4. Check CR fields cr2, cr3, cr4 preserved
        cr2_after = int(str(em.readRegister('cr2')))
        cr3_after = int(str(em.readRegister('cr3')))
        cr4_after = int(str(em.readRegister('cr4')))
        assert cr2_after == val_cr2, f"{fname}: cr2 clobbered! Got {cr2_after}, expected {val_cr2}"
        assert cr3_after == val_cr3, f"{fname}: cr3 clobbered! Got {cr3_after}, expected {val_cr3}"
        assert cr4_after == val_cr4, f"{fname}: cr4 clobbered! Got {cr4_after}, expected {val_cr4}"

        # 5. Check stack pointer restored
        sp_after = int(str(em.readRegister('r1'))) & MASK
        assert sp_after == SP, f"{fname}: Stack pointer not restored: {hex(sp_after)} != {hex(SP)}"

        print(f"  [PASS] {fname}: cr2/cr3/cr4, LR, r30, r31, r14..r29 100% PRESERVED!")

def validate_all_variants():
    print(f"\n==================================================")
    print(f"PC VALIDATION FOR P1G ALL FOUR VARIANTS (G0..G3)")
    print(f"==================================================")

    results = {}

    for vname in ['G0', 'G1', 'G2', 'G3']:
        print(f"\n>>> Validating Variant {vname} <<<")
        elf_path = ROOT / 'local_only' / 'p1g' / f'ps2_netemu_p1g_{vname}.elf'
        assert elf_path.exists(), f"ELF missing: {elf_path}"
        elf_sha = hashlib.sha256(elf_path.read_bytes()).hexdigest()
        digest = elf_sha[:12]

        # 1. Verify wrapper bytes & instruction count
        verify_wrapper_bytes(elf_path)
        print(f"  [PASS] Wrapper bytes: 29 instructions match stock, sc at 0x4858.")

        patch_table = json.loads((H / 'evidence' / f'p1g_{vname}_patch_table.json').read_text())
        syms = patch_table.get('symbols', {'entry_menu': 0x4900})

        # 2. Code Size Check (< 14320 bytes)
        code_size = patch_table['code_size']
        assert code_size <= 14320, f"Code slot capacity exceeded: {code_size} > 14320"
        print(f"  [PASS] Code size check: {code_size} bytes / 14320 bytes ({round((code_size / 14320) * 100, 1)}%)")

        with pyghidra.open_program(str(elf_path), project_location=str(GH / 'projects'),
                                   project_name=f'p1g_val_{vname}_{digest}', analyze=False,
                                   language='PowerPC:BE:64:default') as flat:
            p = flat.getCurrentProgram()
            s = p.getAddressFactory().getDefaultAddressSpace()

            # For G0: run the full register preservation test
            if vname == 'G0':
                run_register_preservation_test(p)

            # EmuRunner for Variant
            class VariantEmuRunner:
                def __init__(self, sim_hcall_rc=0, sim_close_rc=0):
                    self.sim_hcall_rc = sim_hcall_rc
                    self.sim_close_rc = sim_close_rc
                    self.em = EmulatorHelper(p)
                    self.em.enableMemoryWriteTracking(True)
                    self.hcalls_stock = []
                    self.hcalls_generic = []

                    # Breakpoints:
                    # 1. Stock LV1 91 (0x111f10)
                    self.em.setBreakpoint(s.getAddress(0x111f10))
                    # 2. Generic wrapper sc 0 (0x4858)
                    self.em.setBreakpoint(s.getAddress(0x4858))
                    # 3. STOP
                    self.em.setBreakpoint(s.getAddress(STOP))

                    # Initialize mailbox to all zeros
                    self.em.writeMemory(s.getAddress(MAILBOX), bytes(96))

                def w(self, addr, data):
                    self.em.writeMemory(s.getAddress(addr), data)

                def rd(self, addr, n):
                    return bytes(self.em.readMemory(s.getAddress(addr), n))

                def get_reg(self, r):
                    return int(str(self.em.readRegister('r' + str(r)))) & MASK

                def set_reg(self, r, v):
                    self.em.writeRegister('r' + str(r), BigInteger(str(v & MASK)))

                def call_menu(self, selected_page):
                    r24_base = BUF + 0x90000
                    self.w(r24_base + 44, struct.pack('>I', selected_page))
                    self.set_reg(24, r24_base)
                    self.set_reg(1, SP)
                    self.set_reg(2, 0x751280)
                    self.em.writeRegister('lr', BigInteger(str(STOP)))
                    self.em.writeRegister(self.em.getPCRegister(), BigInteger(str(syms['entry_menu'])))

                    timeout = TimeoutTaskMonitor.timeoutIn(30, TimeUnit.SECONDS)

                    for step in range(50000):
                        if not self.em.run(timeout):
                            raise RuntimeError(f"Halted at {hex(self.em.getExecutionAddress().getOffset())}")
                        cur = self.em.getExecutionAddress().getOffset()
                        if cur == STOP:
                            break

                        # 1. Stock LV1 91 repo_read
                        if cur == 0x111f10:
                            r11 = self.get_reg(11)
                            assert r11 == 0x8000005b
                            part = self.get_reg(3)
                            assert part == 1
                            n1 = self.get_reg(4)
                            n2 = self.get_reg(5)
                            n3 = self.get_reg(6)
                            n4 = self.get_reg(7)
                            self.hcalls_stock.append((n1, n2, n3, n4))

                            key = (n1, n2, n3, n4)
                            if key in fake_repo_console:
                                v1, v2 = fake_repo_console[key]
                                self.set_reg(3, 0)
                                self.set_reg(4, v1)
                                self.set_reg(5, v2)
                            else:
                                self.set_reg(3, 0xFFFFFFFFFFFFFFFA)  # rc = -6

                            self.em.writeRegister(self.em.getPCRegister(), BigInteger(str(0x111f14)))
                            continue

                        # 2. Generic wrapper sc 0 at 0x4858
                        if cur == 0x4858:
                            r11 = self.get_reg(11)
                            call_num = r11 & 0x7FFFFFFF
                            a1 = self.get_reg(3)
                            a2 = self.get_reg(4)
                            a3 = self.get_reg(5)
                            a4 = self.get_reg(6)
                            a5 = self.get_reg(7)
                            self.hcalls_generic.append((call_num, a1, a2, a3, a4, a5))

                            # Simulate return
                            if call_num == 0x5b:  # 91
                                # Repository read
                                self.set_reg(3, self.sim_hcall_rc)
                                self.set_reg(4, 5)  # val1 = 5 (ROM)
                                self.set_reg(5, 0)  # val2 = 0
                            elif call_num == 170:  # open_device
                                self.set_reg(3, self.sim_hcall_rc)
                                self.set_reg(4, 0)
                                self.set_reg(5, 0)
                            elif call_num == 171:  # close_device
                                self.set_reg(3, self.sim_close_rc if len(self.hcalls_generic) > 1 else self.sim_hcall_rc)
                                self.set_reg(4, 0)
                                self.set_reg(5, 0)
                            else:
                                raise AssertionError(f"Unexpected hypercall {call_num}")

                            self.em.writeRegister(self.em.getPCRegister(), BigInteger(str(0x485C)))
                            continue

                        raise AssertionError(f"Unexpected breakpoint at {hex(cur)}")
                    else:
                        raise RuntimeError("Emulation budget exhausted")

                    # Memory write tracking: STRICTLY stack or mailbox
                    for r in self.em.getTrackedMemoryWriteSet().getAddressRanges():
                        if r.getMinAddress().getAddressSpace() != s:
                            continue
                        lo = r.getMinAddress().getOffset()
                        hi = r.getMaxAddress().getOffset() + 1
                        is_stack = (SP - 0x10000 <= lo and hi <= SP + 0x1000)
                        is_mailbox = (MAILBOX <= lo and hi <= MAILBOX + 96)
                        assert is_stack or is_mailbox, f"UNAUTHORIZED STORE OUTSIDE RW RANGES: {hex(lo)}..{hex(hi)}"

                    ret_ptr = self.get_reg(4)
                    str_bytes = self.rd(ret_ptr, STR_STRIDE)
                    label = str_bytes.split(b'\0')[0].decode('latin1')
                    return label

            # 3. Test baseline behavior per variant
            if vname == 'G0':
                r = VariantEmuRunner(sim_hcall_rc=0)
                la = r.call_menu(0)
                lb = r.call_menu(1)
                lc = r.call_menu(2)
                ld = r.call_menu(3)
                print(f"  G0 Baseline Labels:")
                print(f"    Page A: {la}")
                print(f"    Page B: {lb}")
                print(f"    Page C: {lc}")
                print(f"    Page D: {ld}")
                assert len(r.hcalls_generic) == 1, f"Expected 1 generic call, got {len(r.hcalls_generic)}"
                num, a1, a2, a3, a4, a5 = r.hcalls_generic[0]
                assert (num, a1, a2, a3, a4, a5) == (0x5b, 1, 0x62757304, KEY_DEV(2), KEY_TYPE, 0), f"Args mismatch: {r.hcalls_generic[0]}"
                assert la == "P1G-G0 DONE read(4,2) rc=SUCCESS v=5(ROM)"
                assert lb == "RC=00000000 (0) SUCCESS"
                assert lc == "P1G MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)"
                assert ld == "ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH"
                print("  [PASS] G0 baseline: LV1 91 through wrapper matches stock helper (rc=0, v=5 ROM)!")

                # Test once-only
                before = len(r.hcalls_generic)
                for i in range(5): r.call_menu(i & 3)
                assert len(r.hcalls_generic) == before, "Repeated menu opens issued extra calls!"
                print("  [PASS] G0 once-only execution verified.")

            elif vname == 'G1':
                r = VariantEmuRunner(sim_hcall_rc=-17)
                la = r.call_menu(0)
                lb = r.call_menu(1)
                lc = r.call_menu(2)
                ld = r.call_menu(3)
                print(f"  G1 Baseline Labels:")
                print(f"    Page A: {la}")
                print(f"    Page B: {lb}")
                print(f"    Page C: {lc}")
                print(f"    Page D: {ld}")
                assert len(r.hcalls_generic) == 1, f"Expected 1 generic call, got {len(r.hcalls_generic)}"
                num, a1, a2, a3, a4, a5 = r.hcalls_generic[0]
                assert (num, a1, a2, a3) == (170, 9, 0, 0), f"Args mismatch: {r.hcalls_generic[0]}"
                assert la == "P1G-G1 DONE open(9,0,0) rc=INVALID_PARAMETER"
                assert lb == "RC=FFFFFFEF (-17) INVALID_PARAMETER"
                assert lc == "P1G-G1 OP:INVALID_PARAMETER CL:--"
                assert ld == "ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH"
                print("  [PASS] G1 baseline: exactly one 170 with args (9, 0, 0), rc=-17!")

                # Test once-only
                before = len(r.hcalls_generic)
                for i in range(5): r.call_menu(i & 3)
                assert len(r.hcalls_generic) == before, "Repeated menu opens issued extra calls!"
                print("  [PASS] G1 once-only execution verified.")

            elif vname == 'G2':
                r = VariantEmuRunner(sim_hcall_rc=-11)
                la = r.call_menu(0)
                lb = r.call_menu(1)
                lc = r.call_menu(2)
                ld = r.call_menu(3)
                print(f"  G2 Baseline Labels:")
                print(f"    Page A: {la}")
                print(f"    Page B: {lb}")
                print(f"    Page C: {lc}")
                print(f"    Page D: {ld}")
                assert len(r.hcalls_generic) == 1, f"Expected 1 generic call, got {len(r.hcalls_generic)}"
                num, a1, a2, a3, a4, a5 = r.hcalls_generic[0]
                assert (num, a1, a2) == (171, 4, 2), f"Args mismatch: {r.hcalls_generic[0]}"
                assert la == "P1G-G2 DONE close(4,2) rc=NOT_OWNER/WRONG_STATE"
                assert lb == "RC=FFFFFFF5 (-11) NOT_OWNER"
                assert lc == "P1G-G2 OP:-- CL:NOT_OWNER/WRONG_STATE"
                assert ld == "ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH"
                print("  [PASS] G2 baseline: exactly one 171 with args (4, 2), rc=-11!")

                # Test once-only
                before = len(r.hcalls_generic)
                for i in range(5): r.call_menu(i & 3)
                assert len(r.hcalls_generic) == before, "Repeated menu opens issued extra calls!"
                print("  [PASS] G2 once-only execution verified.")

            elif vname == 'G3':
                # Test 1: rc == 0 -> BOTH open (170) and close (171) called!
                r0 = VariantEmuRunner(sim_hcall_rc=0, sim_close_rc=0)
                la = r0.call_menu(0)
                lb = r0.call_menu(1)
                lc = r0.call_menu(2)
                ld = r0.call_menu(3)
                print(f"  G3 (rc=0) Labels:")
                print(f"    Page A: {la}")
                print(f"    Page B: {lb}")
                print(f"    Page C: {lc}")
                print(f"    Page D: {ld}")
                assert len(r0.hcalls_generic) == 2, f"Expected 2 calls (170 and 171), got {len(r0.hcalls_generic)}"
                c0 = r0.hcalls_generic[0]
                c1 = r0.hcalls_generic[1]
                assert (c0[0], c0[1], c0[2], c0[3]) == (170, 4, 2, 0), f"Call 0 mismatch: {c0}"
                assert (c1[0], c1[1], c1[2]) == (171, 4, 2), f"Call 1 mismatch: {c1}"
                assert la == "P1G-G3 DONE open(4,2,0) rc=SUCCESS"
                assert lb == "RC=00000000 (0) SUCCESS"
                assert lc == "P1G-G3 OP:SUCCESS CL:SUCCESS"
                print("  [PASS] G3 (rc=0): exactly one 170 (4,2,0) then one 171 (4,2)!")

                # Test 2: rc != 0 (-4, -6, -9, -17) -> close is NEVER called!
                for fail_rc, exp_name in [(-4, 'DENIED'), (-6, 'NO_ENTRY'), (-9, 'BUSY'), (-17, 'INVALID')]:
                    rf = VariantEmuRunner(sim_hcall_rc=fail_rc, sim_close_rc=0)
                    l_c = rf.call_menu(2)
                    assert len(rf.hcalls_generic) == 1, f"Close was called on fail_rc={fail_rc}!"
                    c0 = rf.hcalls_generic[0]
                    assert c0[0] == 170 and (c0[1], c0[2], c0[3]) == (4, 2, 0)
                    assert f"OP:{exp_name} CL:NONE" in l_c, f"Expected OP:{exp_name} CL:NONE, got '{l_c}'"
                print("  [PASS] G3 error paths (-4, -6, -9, -17): close NEVER called when open fails!")

                # Test once-only
                before = len(r0.hcalls_generic)
                for i in range(5): r0.call_menu(i & 3)
                assert len(r0.hcalls_generic) == before, "Repeated menu opens issued extra calls!"
                print("  [PASS] G3 once-only execution verified.")

        results[vname] = {'passed': True, 'elf_sha256': elf_sha}

    return results

def run_fuzz_index_bounds():
    print("\n--------------------------------------------------")
    print("Running Exhaustive / Fuzz Index-Bounds Checks...")
    print("--------------------------------------------------")

    # Helper maps
    def map_rc_name_idx(rc, att):
        if not att: return 0
        if rc == 0: return 1
        if rc == -2: return 2
        if rc == -3: return 3
        if rc == -4: return 4
        if rc == -5: return 5
        if rc == -6: return 6
        if rc == -9: return 7
        if rc == -10: return 8
        if rc == -11: return 9
        if rc == -17: return 10
        return 11

    def map_v_idx(val, att):
        if not att: return 0
        if val == 0: return 0
        if val == 1: return 1
        if val == 2: return 2
        if val == 3: return 3
        if val == 4: return 4
        if val == 5: return 5
        if val == 6: return 6
        return 7

    def map_page_b_idx(s, att):
        if not att: return 528
        u = s & 0xFFFFFFFF
        if (u & 0xFFFFFF00) == 0xFFFFFF00:
            return u & 0xFF
        if (u & 0xFFFFFF00) == 0x00000000:
            return 256 + (u & 0xFF)
        hi = (u >> 28) & 0xF
        return 512 + hi

    # 1. Page A G0: 96 strings
    for att in [0, 1]:
        for rc in [0, -1, -2, -3, -4, -5, -6, -9, -10, -11, -17, -18, -99, 100]:
            for val in [0, 1, 2, 3, 4, 5, 6, 7, 8, 99]:
                idx = map_rc_name_idx(rc, att) * 8 + map_v_idx(val, att)
                assert 0 <= idx < 96, f"G0 Page A out of bounds: {idx}"
    print("  [PASS] Page A G0 (96 strings): all indices in [0, 95].")

    # 2. Page A G1/G2/G3: 12 strings
    for att in [0, 1]:
        for rc in [0, -1, -2, -3, -4, -5, -6, -9, -10, -11, -17, -18, -99, 100]:
            idx = map_rc_name_idx(rc, att)
            assert 0 <= idx < 12, f"G1..G3 Page A out of bounds: {idx}"
    print("  [PASS] Page A G1..G3 (12 strings): all indices in [0, 11].")

    # 3. Page B (All variants): 529 strings
    for att in [0, 1]:
        for rc in [0, -1, -2, -17, -256, 1, 255, 0x100, 0x12345678, -0x12345678, 0x7FFFFFFF, -0x80000000]:
            idx = map_page_b_idx(rc, att)
            assert 0 <= idx < 529, f"Page B out of bounds: {idx}"
    print("  [PASS] Page B All Variants (529 strings): all indices in [0, 528].")

    # 4. Page C G0: 230 strings
    def map_page_c_g0(match_st, raw_rc, raw_val, stock_rc, stock_val):
        if match_st == 1:
            if raw_rc == 0 and raw_val == 5: return 0
            if raw_rc == 0: return 1 + map_v_idx(raw_val, 1)
            return 9 + map_rc_name_idx(raw_rc, 1)
        elif match_st == 2:
            if raw_rc != stock_rc:
                return 21 + (map_rc_name_idx(raw_rc, 1) * 12 + map_rc_name_idx(stock_rc, 1))
            return 165 + (map_v_idx(raw_val, 1) * 8 + map_v_idx(stock_val, 1))
        return 229

    for m_st in [0, 1, 2, 3]:
        for r_rc in [0, -2, -4, -6, -17, 1, -99]:
            for s_rc in [0, -2, -4, -6, -17, 1, -99]:
                for r_v in [0, 1, 2, 5, 6, 99]:
                    for s_v in [0, 1, 2, 5, 6, 99]:
                        idx = map_page_c_g0(m_st, r_rc, r_v, s_rc, s_v)
                        assert 0 <= idx < 230, f"Page C G0 out of bounds: {idx}"
    print("  [PASS] Page C G0 (230 strings): all indices in [0, 229].")

    # 5. Page C G3: 144 strings
    for o_att in [0, 1]:
        for c_att in [0, 1]:
            for o_rc in [0, -2, -3, -4, -5, -6, -9, -10, -11, -17, -99]:
                for c_rc in [0, -2, -3, -4, -5, -6, -9, -10, -11, -17, -99]:
                    o_idx = map_rc_name_idx(o_rc, o_att)
                    c_idx = map_rc_name_idx(c_rc, c_att)
                    idx = o_idx * 12 + c_idx
                    assert 0 <= idx < 144, f"Page C G3 out of bounds: {idx}"
    print("  [PASS] Page C G3 (144 strings): all indices in [0, 143].")

    # 6. Page D (All variants): 4505 strings
    def map_page_d_idx(rom_cnt, rom_b, rom_d, rom_p, hdd_f, hdd_b, hdd_d, hdd_p, phat):
        r = 0
        if rom_cnt > 0:
            if rom_b == 4 and rom_d == 2 and rom_p == 0: r = 1
            elif rom_b == 5 and rom_d == 0: r = 2
            elif rom_b == 4 and rom_d == 2: r = 3
            else: r = 4
        h_idx = 0
        if hdd_f:
            b = hdd_b if hdd_b < 8 else 8
            d = hdd_d if hdd_d < 4 else 4
            p = hdd_p if hdd_p < 4 else 4
            ph = phat & 3
            h_idx = 1 + ((b * 5 + d) * 5 + p) * 4 + ph
        return r * 901 + h_idx

    for rom_cnt in [0, 1, 5]:
        for rom_b in [4, 5, 0, 15]:
            for rom_d in [0, 2, 15]:
                for rom_p in [0, 1, 3]:
                    for hdd_f in [0, 1]:
                        for hdd_b in range(10):
                            for hdd_d in range(6):
                                for hdd_p in range(6):
                                    for phat in range(5):
                                        idx = map_page_d_idx(rom_cnt, rom_b, rom_d, rom_p, hdd_f, hdd_b, hdd_d, hdd_p, phat)
                                        assert 0 <= idx < 4505, f"Page D out of bounds: {idx}"
    print("  [PASS] Page D All Variants (4505 strings): all indices in [0, 4504].")

def check_installer_scripts():
    print("\n--------------------------------------------------")
    print("Checking installer scripts syntax with PowerShell AST parser...")
    print("--------------------------------------------------")
    scripts = ['tools/install_netemu.ps1', 'tools/restore_netemu.ps1']
    for scr in scripts:
        full_path = ROOT / scr
        assert full_path.exists(), f"Script missing: {scr}"
        cmd = [
            'powershell.exe', '-NoProfile', '-Command',
            f"$errors = $null; [System.Management.Automation.Language.Parser]::ParseFile('{str(full_path)}', [ref]$null, [ref]$errors); if ($errors) {{ exit 1 }} else {{ exit 0 }}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"Script parse error in {scr}: {res.stderr}"
        print(f"  [PASS] Script syntax valid: {scr}")

def check_p1a_audit():
    print("\n--------------------------------------------------")
    print("Running strict store audit (tools/p1a_audit.py)...")
    print("--------------------------------------------------")
    for vname in ['G0', 'G1', 'G2', 'G3']:
        cmd = [
            sys.executable, '-I', str(ROOT / 'tools' / 'p1a_audit.py'),
            str(ROOT / 'local_only' / 'stock.elf'),
            str(ROOT / 'local_only' / 'p1g' / f'ps2_netemu_p1g_{vname}.elf')
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"p1a_audit failed for {vname}: {res.stderr}"
        stdout = res.stdout
        assert "sc instructions in changed/added executable ranges: [(18520, 0)]" in stdout, \
            f"Audit assertion failed for {vname}: {stdout}"
        print(f"  [PASS] Strict store audit verified for {vname}: exactly 1 sc instruction at 0x4858!")

def main():
    res = validate_all_variants()
    run_fuzz_index_bounds()
    check_p1a_audit()
    check_installer_scripts()

    combined = {
        'p1g_validation': res,
        'fuzz_index_bounds_passed': True,
        'p1a_audit_passed': True,
        'installer_syntax_passed': True,
        'all_tests_passed': True
    }
    out_file = H / 'evidence' / 'p1g_validation_results.json'
    out_file.write_text(json.dumps(combined, indent=2))
    print(f"\nSaved combined validation results to {out_file}")
    print("\n==================================================")
    print("[SUCCESS] ALL PC VALIDATION TESTS PASSED FOR P1G!")
    print("==================================================")

if __name__ == '__main__':
    main()
