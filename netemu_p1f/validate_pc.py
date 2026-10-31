"""Comprehensive PC validation test suite for P1f diagnostic build:
  - ps2_netemu_p1f.elf / self: issues ONE LV1 91 read through relocated clone of stock helper (0x4800, sc at 0x4858)
  - Target node: bus/4/dev/2/type (optical ROM device type, expected value 5)

Strict assertions verified on PC:
  1. Issues exactly ONE clone repository read through code slot clone at 0x4858 with expected args:
     (partition_id=1, node1=0x62757304, node2=KEY_DEV(2), node3=KEY_TYPE, node4=0).
  2. Issues ZERO calls to LV1 170 (open_device) or LV1 171 (close_device).
  3. Hypercalls are strictly LV1 91 only (both stock helper and clone).
  4. Both stock helper result and clone result are recorded in mailbox.
  5. Correct labels on Pages A, B, C, D:
     - Page A: P1F-CLONE DONE rc=SUCCESS v=5(ROM)
     - Page B: P1F-STOCK DONE rc=SUCCESS v=5(ROM)
     - Page C: P1F MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)
     - Page D: ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH
  6. Return code / value edge cases tested (MATCH, DIFF in RC, DIFF in VAL, errors).
  7. Once-only execution: repeated menu opens issue zero additional hypercalls.
  8. Memory write tracking: all stores strictly inside stack frame or 96-byte mailbox [0x930F20, 0x930F80).
  9. Exhaustive / fuzz index bounds checking across all label tables (Pages A, B, C, D).
 10. Code slot size check (< 14,320 bytes).
 11. Strict store audit (tools/p1a_audit.py): exactly one sc instruction in changed ranges (0x4858).
 12. Relocated clone byte equality assert: exactly equals stock helper modulo branch fixup at 0xAC.
 13. Installer scripts syntax parse check.
"""
from pathlib import Path
import json, hashlib, os, struct, subprocess, sys, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

H = Path(__file__).resolve().parent
ROOT = H.parent
GH = ROOT / 'local_only' / 'ghidra_p1f'

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

def verify_clone_bytes(elf_path):
    """Assert clone bytes at 0x4800..0x48b4 equal stock 0x111eb8..0x111f6c modulo branch fixup."""
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

    clone_bytes = elf_bytes[elf_off : elf_off + 180]
    assert len(clone_bytes) == 180

    # 176 out of 180 bytes must be identical
    mismatches = []
    for i in range(180):
        if i in (0xAC, 0xAD, 0xAE, 0xAF):
            continue
        if clone_bytes[i] != stock_bytes[i]:
            mismatches.append((hex(i), hex(clone_bytes[i]), hex(stock_bytes[i])))
    assert not mismatches, f"Byte mismatches between stock and clone: {mismatches}"

    # Check branch word at 0xAC
    w_branch, = struct.unpack_from('>I', clone_bytes, 0xAC)
    disp = w_branch & 0x03FFFFFC
    if disp & 0x02000000:
        disp -= 0x04000000
    target = (0x4800 + 0xAC) + disp
    assert target == 0x111A7C, f"Branch at 0xac does not resolve to 0x111a7c: got {hex(target)}"
    print("[PASS] Clone byte equality verified: 176/180 bytes equal stock, branch at 0xac resolves to 0x111a7c.")

def validate_p1f():
    print(f"\n==================================================")
    print(f"PC VALIDATION FOR P1F DIAGNOSTIC BUILD")
    print(f"==================================================")

    elf_path = ROOT / 'local_only' / 'p1f' / 'ps2_netemu_p1f.elf'
    assert elf_path.exists(), f"ELF not found: {elf_path}"
    elf_sha = hashlib.sha256(elf_path.read_bytes()).hexdigest()
    digest = elf_sha[:12]

    # Verify clone byte equality
    verify_clone_bytes(elf_path)

    results = {
        'variant': 'P1F',
        'elf_sha256': elf_sha,
        'tests': {}
    }

    patch_table = json.loads((H / 'evidence' / 'p1f_patch_table.json').read_text())
    syms = patch_table.get('symbols', {'entry_menu': 0x4900})

    # 1. Code Size Check
    code_size = patch_table['code_size']
    assert code_size <= 14320, f"Code slot capacity exceeded: {code_size} > 14320"
    results['tests']['code_size'] = {
        'passed': True,
        'code_size_bytes': code_size,
        'slot_capacity_bytes': 14320,
        'slot_usage_pct': round((code_size / 14320) * 100, 1)
    }
    print(f"[PASS] Code size check: {code_size} bytes / 14320 bytes ({round((code_size / 14320) * 100, 1)}%)")

    # 2. Store Audit Check (IR audit file)
    ir_audit = json.loads((H / 'evidence' / 'p1f_ir_store_audit.json').read_text())
    assert ir_audit['passed'], "IR store audit failed for P1f"

    with pyghidra.open_program(str(elf_path), project_location=str(GH / 'projects'),
                              project_name=f'p1f_val_{digest}', analyze=False,
                              language='PowerPC:BE:64:default') as flat:
        p = flat.getCurrentProgram()
        s = p.getAddressFactory().getDefaultAddressSpace()
        pd = PseudoDisassembler(p)

        # 3. Assembly Store & SC Scan
        asm_stores = []
        sc_sites = []
        for pc in range(0x4800, 0x4800 + code_size, 4):
            ins = pd.disassemble(s.getAddress(pc))
            if ins is None:
                continue
            pcode = ins.getPcode()
            is_store = any(op.getOpcode() == op.STORE for op in pcode)
            if is_store:
                ins_str = str(ins)
                asm_stores.append({'pc': hex(pc), 'ins': ins_str})
                mnem = ins.getMnemonicString()
                assert mnem in ('stb', 'sth', 'stw', 'std', 'stdu', 'stwu', 'stwx', 'stdx'), f"Unexpected store: {ins_str}"

            w = p.getMemory().getInt(s.getAddress(pc)) & 0xFFFFFFFF
            if (w & 0xFC000003) == 0x44000002:
                sc_sites.append((hex(pc), hex(w)))

        # Exactly ONE SC site in code slot: 0x4858 (inside lv1_repo_clone)
        assert sc_sites == [('0x4858', '0x44000002')], f"Unexpected SC instructions: {sc_sites}"
        print(f"[PASS] SC instruction scan: exactly 1 hypercall site in code slot (0x4858=lv1_repo_clone)")

        results['tests']['store_audit'] = {
            'passed': True,
            'ir_stores_verified': len(ir_audit['stores']),
            'asm_stores_scanned': len(asm_stores),
            'sc_sites': sc_sites
        }
        print(f"[PASS] Store audit: {len(ir_audit['stores'])} IR stores and {len(asm_stores)} assembly stores verified safe.")

        # 4. Emulator Class
        class EmuRunner:
            def __init__(self, fake_repo, sim_clone_rc=0, sim_clone_v1=5, sim_clone_v2=0, sim_stock_repo=None):
                self.fake_repo = dict(fake_repo) if sim_stock_repo is None else dict(sim_stock_repo)
                self.sim_clone_rc = sim_clone_rc
                self.sim_clone_v1 = sim_clone_v1
                self.sim_clone_v2 = sim_clone_v2
                self.em = EmulatorHelper(p)
                self.em.enableMemoryWriteTracking(True)
                self.hypercall_count = 0
                self.call_log_91_stock = []
                self.call_log_91_clone = []
                self.illegal_calls = []

                # Breakpoints:
                # 1. LV1 91 `sc 0` inside stock repo_read (0x111eb8 -> 0x111f10)
                self.em.setBreakpoint(s.getAddress(0x111f10))
                # 2. LV1 91 `sc 0` inside our relocated clone lv1_repo_clone (0x4858)
                self.em.setBreakpoint(s.getAddress(0x4858))
                # 3. Return breakpoint at STOP
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
                        raise RuntimeError(f"Emulation halted at {hex(self.em.getExecutionAddress().getOffset())}: {self.em.getLastError()}")
                    cur = self.em.getExecutionAddress().getOffset()
                    if cur == STOP:
                        break

                    # 1. Stock LV1 91 repo_read
                    if cur == 0x111f10:
                        r11 = self.get_reg(11)
                        assert r11 == 0x8000005b, f"Expected r11=0x8000005b for LV1 91, got {hex(r11)}"
                        part_id = self.get_reg(3)
                        assert part_id == 1, f"Expected partition_id=1, got {part_id}"
                        n1 = self.get_reg(4)
                        n2 = self.get_reg(5)
                        n3 = self.get_reg(6)
                        n4 = self.get_reg(7)
                        self.hypercall_count += 1
                        self.call_log_91_stock.append((n1, n2, n3, n4))

                        key = (n1, n2, n3, n4)
                        if key in self.fake_repo:
                            v1, v2 = self.fake_repo[key]
                            self.set_reg(3, 0)
                            self.set_reg(4, v1)
                            self.set_reg(5, v2)
                        else:
                            self.set_reg(3, 0xFFFFFFFFFFFFFFFA)  # rc = -6

                        self.em.writeRegister(self.em.getPCRegister(), BigInteger(str(0x111f14)))
                        continue

                    # 2. Relocated clone lv1_repo_clone at 0x4858
                    if cur == 0x4858:
                        r11 = self.get_reg(11)
                        assert r11 == 0x8000005b, f"Expected r11=0x8000005b for clone LV1 91, got {hex(r11)}"
                        part_id = self.get_reg(3)
                        assert part_id == 1, f"Expected partition_id=1, got {part_id}"
                        n1 = self.get_reg(4)
                        n2 = self.get_reg(5)
                        n3 = self.get_reg(6)
                        n4 = self.get_reg(7)
                        self.hypercall_count += 1
                        self.call_log_91_clone.append((n1, n2, n3, n4))

                        # Strict assertion: target node must match bus/4/dev/2/type
                        # Note: 0x62757304 is folded from KEY_BUS(4) by the clone's instructions!
                        assert (n1, n2, n3, n4) == (0x62757304, KEY_DEV(2), KEY_TYPE, 0), \
                            f"Unexpected arguments to lv1_repo_clone: ({hex(n1)}, {hex(n2)}, {hex(n3)}, {hex(n4)})"

                        rc = self.sim_clone_rc
                        v1 = self.sim_clone_v1
                        v2 = self.sim_clone_v2
                        self.set_reg(3, rc & MASK)
                        self.set_reg(4, v1 & MASK)
                        self.set_reg(5, v2 & MASK)

                        self.em.writeRegister(self.em.getPCRegister(), BigInteger(str(0x485C)))
                        continue

                    raise AssertionError(f"Unexpected breakpoint at {hex(cur)}")
                else:
                    raise RuntimeError("Emulation budget exhausted")

                # Validate memory writes: STRICTLY stack or mailbox [0x930F20, 0x930F80)
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
                return label, ret_ptr

        # 5. Test Baseline Scenario (Harmless good call: match)
        runner = EmuRunner(fake_repo_console, sim_clone_rc=0, sim_clone_v1=5, sim_clone_v2=0)

        # Call menu row 0 (Page A)
        lbl_a, _ = runner.call_menu(0)
        # Call menu row 1 (Page B)
        lbl_b, _ = runner.call_menu(1)
        # Call menu row 2 (Page C)
        lbl_c, _ = runner.call_menu(2)
        # Call menu row 3 (Page D)
        lbl_d, _ = runner.call_menu(3)

        print(f"Emulated menu rows (baseline: clone=5 stock=5 rc=0):")
        print(f"  Page A (row 0): {lbl_a}")
        print(f"  Page B (row 1): {lbl_b}")
        print(f"  Page C (row 2): {lbl_c}")
        print(f"  Page D (row 3): {lbl_d}")

        # Baseline assertions
        assert len(runner.call_log_91_clone) == 1, f"Expected exactly 1 clone read, got {len(runner.call_log_91_clone)}"
        assert runner.call_log_91_clone[0] == (0x62757304, KEY_DEV(2), KEY_TYPE, 0), f"Clone args mismatch: {runner.call_log_91_clone[0]}"
        assert lbl_a == "P1F-CLONE DONE rc=SUCCESS v=5(ROM)", f"Page A unexpected label: '{lbl_a}'"
        assert lbl_b == "P1F-STOCK DONE rc=SUCCESS v=5(ROM)", f"Page B unexpected label: '{lbl_b}'"
        assert lbl_c == "P1F MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)", f"Page C unexpected label: '{lbl_c}'"
        assert lbl_d == "ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH", f"Page D unexpected label: '{lbl_d}'"
        print("[PASS] Baseline scenario: exactly 1 clone LV1 91 read issued, MATCH reported on Page C, all labels exact.")

        # 6. Once-only test across multiple repeated menu openings
        calls_before_clone = len(runner.call_log_91_clone)
        calls_before_stock = len(runner.call_log_91_stock)
        for i in range(5):
            runner.call_menu(i & 3)
        assert len(runner.call_log_91_clone) == calls_before_clone, "Repeated menu opens issued extra clone calls!"
        assert len(runner.call_log_91_stock) == calls_before_stock, "Repeated menu opens issued extra stock calls!"
        print("[PASS] Once-only execution verified across repeated menu opens (zero extra hypercalls).")

        # 7. Test Edge Cases (MATCH & DIFF scenarios)
        test_scenarios = [
            # (clone_rc, clone_v1, clone_v2, stock_repo_mod, exp_a, exp_b, exp_c_substr)
            (0, 5, 0, None, "P1F-CLONE DONE rc=SUCCESS v=5(ROM)", "P1F-STOCK DONE rc=SUCCESS v=5(ROM)", "P1F MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)"),
            (-4, 0, 0, None, "P1F-CLONE DONE rc=DENIED_BY_POLICY v=0", "P1F-STOCK DONE rc=SUCCESS v=5(ROM)", "P1F DIFF: RC clone=DENIED stock=SUCCESS"),
            (-6, 0, 0, None, "P1F-CLONE DONE rc=NO_ENTRY v=0", "P1F-STOCK DONE rc=SUCCESS v=5(ROM)", "P1F DIFF: RC clone=NO_ENTRY stock=SUCCESS"),
            (-17, 0, 0, None, "P1F-CLONE DONE rc=INVALID_PARAMETER v=0", "P1F-STOCK DONE rc=SUCCESS v=5(ROM)", "P1F DIFF: RC clone=INVALID stock=SUCCESS"),
            (0, 2, 0, None, "P1F-CLONE DONE rc=SUCCESS v=2", "P1F-STOCK DONE rc=SUCCESS v=5(ROM)", "P1F DIFF: VAL clone=2 stock=5(ROM)"),
        ]

        print(f"Testing {len(test_scenarios)} edge case scenarios...")
        for c_rc, c_v1, c_v2, s_mod, exp_a, exp_b, exp_c in test_scenarios:
            r = EmuRunner(fake_repo_console, sim_clone_rc=c_rc, sim_clone_v1=c_v1, sim_clone_v2=c_v2, sim_stock_repo=s_mod)
            la, _ = r.call_menu(0)
            lb, _ = r.call_menu(1)
            lc, _ = r.call_menu(2)
            assert la == exp_a, f"Page A mismatch: got '{la}', expected '{exp_a}'"
            assert lb == exp_b, f"Page B mismatch: got '{lb}', expected '{exp_b}'"
            assert exp_c in lc, f"Page C mismatch: got '{lc}', expected '{exp_c}'"

        print(f"[PASS] All {len(test_scenarios)} edge case scenarios verified on Pages A, B, C!")
        results['tests']['scenarios_passed'] = True

    return results

def run_fuzz_index_bounds():
    print("\n--------------------------------------------------")
    print("Running Exhaustive / Fuzz Index-Bounds Checks...")
    print("--------------------------------------------------")

    # Page A / B: 96 strings (rc_idx * 8 + v_idx)
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

    max_idx_ab = 0
    for att in [0, 1]:
        for rc in [0, -1, -2, -3, -4, -5, -6, -9, -10, -11, -17, -18, -100, 1, 100, 0x7FFFFFFFFFFFFFFF, -0x8000000000000000]:
            for val in [0, 1, 2, 3, 4, 5, 6, 7, 10, 0xFFFFFFFFFFFFFFFF]:
                r_i = map_rc_name_idx(rc, att)
                v_i = map_v_idx(val, att)
                idx = r_i * 8 + v_i
                if idx > max_idx_ab: max_idx_ab = idx
                assert 0 <= idx < 96, f"Page A/B out of bounds: {idx}"
    print(f"  Page A/B: max reachable index = {max_idx_ab} (table size = 96 strings) [BOUNDED]")

    # Page C: 230 strings (indices 0..229)
    def map_page_c_idx(match_status, raw_rc, raw_val1, stock_rc, stock_val1):
        if match_status == 1:
            if raw_rc == 0 and raw_val1 == 5:
                return 0
            if raw_rc == 0:
                v = map_v_idx(raw_val1, 1)
                return 1 + v
            r = map_rc_name_idx(raw_rc, 1)
            return 9 + r
        elif match_status == 2:
            if raw_rc != stock_rc:
                r_rc = map_rc_name_idx(raw_rc, 1)
                s_rc = map_rc_name_idx(stock_rc, 1)
                return 21 + (r_rc * 12 + s_rc)
            r_v = map_v_idx(raw_val1, 1)
            s_v = map_v_idx(stock_val1, 1)
            return 165 + (r_v * 8 + s_v)
        return 229

    max_idx_c = 0
    for m_st in [0, 1, 2, 3]:
        for r_rc in [0, -2, -4, -6, -17, 1, -99]:
            for s_rc in [0, -2, -4, -6, -17, 1, -99]:
                for r_v in [0, 1, 2, 5, 6, 99]:
                    for s_v in [0, 1, 2, 5, 6, 99]:
                        idx = map_page_c_idx(m_st, r_rc, r_v, s_rc, s_v)
                        if idx > max_idx_c: max_idx_c = idx
                        assert 0 <= idx < 230, f"Page C out of bounds: {idx}"
    print(f"  Page C: max reachable index = {max_idx_c} (table size = 230 strings) [BOUNDED]")

    # Page D: 4505 strings (indices 0..4504)
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

    max_idx_d = 0
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
                                        if idx > max_idx_d: max_idx_d = idx
                                        assert 0 <= idx < 4505, f"Page D out of bounds: {idx}"
    print(f"  Page D: max reachable index = {max_idx_d} (table size = 4505 strings) [BOUNDED]")
    print("[PASS] Exhaustive index bounds fuzzing PASSED for all pages!")

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
    cmd = [
        sys.executable, '-I', str(ROOT / 'tools' / 'p1a_audit.py'),
        str(ROOT / 'local_only' / 'stock.elf'),
        str(ROOT / 'local_only' / 'p1f' / 'ps2_netemu_p1f.elf')
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"p1a_audit failed: {res.stderr}"
    stdout = res.stdout
    print(stdout)
    assert "sc instructions in changed/added executable ranges: [(18520, 0)]" in stdout, \
        f"Audit assertion failed: expected exactly 1 sc at 0x4858 (18520), got output: {stdout}"
    print("[PASS] Strict store audit verified: exactly 1 sc instruction in changed ranges (0x4858=lv1_repo_clone)!")

def main():
    res = validate_p1f()
    run_fuzz_index_bounds()
    check_p1a_audit()
    check_installer_scripts()

    combined = {
        'p1f_validation': res,
        'fuzz_index_bounds_passed': True,
        'p1a_audit_passed': True,
        'installer_syntax_passed': True,
        'all_tests_passed': True
    }
    out_file = H / 'evidence' / 'p1f_validation_results.json'
    out_file.write_text(json.dumps(combined, indent=2))
    print(f"\nSaved combined validation results to {out_file}")
    print("\n==================================================")
    print("[SUCCESS] ALL PC VALIDATION TESTS PASSED FOR P1F!")
    print("==================================================")

if __name__ == '__main__':
    main()
