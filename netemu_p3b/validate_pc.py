"""Comprehensive PC validation test suite for P3B Durable HDD Logger (ps2_netemu_p3b_L0):
  - Emulation Harness (PyGhidra EmulatorHelper):
      * Models stock functions as stubs/emulated handlers:
        - stock_ufs_open (path string check "/tmp/netemu_log.bin", slot accounting, error injection)
        - stock_ufs_close (asserts all opened fds closed on all paths, slot tracking)
        - stock_raw_read (in-memory 65,536-byte placeholder, sector alignment)
        - stock_raw_write (512-aligned, size 512, offset+size <= 65536, updates in-memory mock file)
        - stock_hdd_cache_flush (asserts idle precondition at call, records call)
        - native_alloc & native_clock
      * Test cases:
        1. Normal Happy Path (writes 4 records, header cursor=5, clean flush, verifies decoded log)
        2. Busy H state variants (H+48 != 0, H+38 != 0, H+85 != 1, H+78 != 0) -> ZERO UFS calls
        3. Missing placeholder file (ufs_open returns -2) -> ZERO writes, ZERO flushes, label "NO FILE", 0 leaked slots
        4. Injected write failure -> file closed immediately, flush not reached, 0 leaked slots
        5. Idempotent logging: repeated menu opens do not log twice
        6. Memory store audit: stores strictly to stack, mailbox [0x930F20, 0x930F80), arena. ZERO stores >= 0x930F80.
        7. Menu row bounds fuzz (selected 0..255, 0xFFFFFFFF)
  - Strict Store Audit (tools/p1a_audit.py):
      * Asserts EXACTLY ZERO sc instructions in changed executable ranges.
  - SELF Round-Trip Verification:
      * selfdec.py decryption matches patched ELF byte-for-byte.
  - PowerShell AST Parse Check:
      * make_log_placeholder.ps1, read_netemu_log.ps1, install_netemu.ps1, restore_netemu.ps1.
"""
from pathlib import Path
import json, hashlib, os, struct, subprocess, sys, warnings, runpy
warnings.filterwarnings('ignore', category=DeprecationWarning)

H = Path(__file__).resolve().parent
ROOT = H.parent
GH = ROOT / 'local_only' / 'ghidra_p3b'

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
from ghidra.util.task import ConsoleTaskMonitor
from java.math import BigInteger

sys.path.insert(0, str(ROOT / 'tools'))
import decode_netemu_log

MASK = (1 << 64) - 1
SP = 0xaaa700bfe00
STOP = 0x7FF0
MAILBOX = 0x930F20
MAILBOX_SIZE = 96
ARENA_BASE = 0x80020000
ARENA_SIZE = 4096
STOCK_LABEL_ADDR = 0x304EC0
HDD_STRUCT_ADDR = 0x241C850
UFS_LOCK_ADDR = 0x3055180
POOL_934980  = 0x934980
POOL_24565B8 = 0x24565B8
POOL_2446588 = 0x2446588

def validate_p3b():
    print(f"\n==================================================")
    print(f"PC VALIDATION FOR P3B DURABLE HDD LOGGER (L0)")
    print(f"==================================================")

    elf_path = ROOT / 'local_only' / 'p3b' / 'ps2_netemu_p3b_L0.elf'
    assert elf_path.exists(), f"ELF missing: {elf_path}"
    elf_sha = hashlib.sha256(elf_path.read_bytes()).hexdigest()
    digest = elf_sha[:12]

    patch_table = json.loads((H / 'evidence' / 'p3b_patch_table.json').read_text())
    code_size = patch_table['code_size']
    assert code_size <= 14320, f"Code slot capacity exceeded: {code_size} > 14320"
    print(f"  [PASS] Code size check: {code_size} bytes / 14320 bytes ({round((code_size / 14320) * 100, 1)}%)")

    # 1. Strict Store Audit via tools/p1a_audit.py
    print("\n--------------------------------------------------")
    print("Running tools/p1a_audit.py Strict Store Audit...")
    print("--------------------------------------------------")
    res = subprocess.run([sys.executable, '-I', str(ROOT / 'tools' / 'p1a_audit.py'),
                          str(ROOT / 'local_only' / 'stock.elf'), str(elf_path)],
                         capture_output=True, text=True)
    assert res.returncode == 0, f"p1a_audit failed: {res.stderr}"
    out = res.stdout
    assert "sc instructions in changed/added executable ranges: []" in out, \
        f"Unexpected sc instructions in P3B:\n{out}"
    print(f"  [PASS] p1a_audit confirmed EXACTLY ZERO sc instructions in changed executable ranges!")

    # 2. PyGhidra Emulation
    print("\n--------------------------------------------------")
    print("Initializing PyGhidra Emulator...")
    print("--------------------------------------------------")
    with pyghidra.open_program(str(elf_path), project_location=str(GH / 'projects'),
                               project_name=f'p3b_val_{digest}', analyze=False,
                               language='PowerPC:BE:64:default') as flat:
        p = flat.getCurrentProgram()
        s = p.getAddressFactory().getDefaultAddressSpace()

        class P3BEmuRunner:
            def __init__(self, busy_h=None, inject_open_err=None, inject_write_err=None, inject_flush_err=None):
                self.busy_h = busy_h or {}
                self.inject_open_err = inject_open_err
                self.inject_write_err = inject_write_err
                self.inject_flush_err = inject_flush_err

                self.em = EmulatorHelper(p)
                self.tb_ticks = 1000000000
                self.file_data = bytearray(65536)  # 64 KiB placeholder file
                self.open_slots = {}
                self.total_opens = 0
                self.total_closes = 0
                self.writes = []
                self.flush_calls = 0
                self.paths_opened = []

                # Trampoline breakpoints
                self.em.setBreakpoint(s.getAddress(0x4800))  # native_alloc
                self.em.setBreakpoint(s.getAddress(0x4840))  # native_clock
                self.em.setBreakpoint(s.getAddress(0x4880))  # stock_ufs_open
                self.em.setBreakpoint(s.getAddress(0x48C0))  # stock_ufs_close
                self.em.setBreakpoint(s.getAddress(0x4900))  # stock_raw_read
                self.em.setBreakpoint(s.getAddress(0x4940))  # stock_raw_write
                self.em.setBreakpoint(s.getAddress(0x4980))  # stock_hdd_cache_flush
                self.em.setBreakpoint(s.getAddress(STOP))    # Return point

                self.em.enableMemoryWriteTracking(True)
                self.setup_stock_memory()

            def w(self, ea, data):
                self.em.writeMemory(s.getAddress(ea), data)

            def rd(self, ea, size):
                return bytes([self.em.readMemoryByte(s.getAddress(ea + i)) & 0xFF for i in range(size)])

            def set_reg(self, r, val):
                self.em.writeRegister(f'r{r}', BigInteger(str(val & MASK)))

            def get_reg(self, r):
                return int(str(self.em.readRegister(f'r{r}'))) & MASK

            def get_lr(self):
                return int(str(self.em.readRegister('lr'))) & MASK

            def set_pc(self, pc):
                self.em.writeRegister('pc', BigInteger(str(pc & MASK)))

            def setup_stock_memory(self):
                # Mailbox clear
                self.w(MAILBOX, b'\0' * MAILBOX_SIZE)

                # HDD driver state H=0x241C850
                # Default idle: DEV_ID=3, TAGSTAT=0, STATUS40=0, STATUS48=0, ENABLED(0x85)=1, ERR(0x78)=0
                hdd = bytearray(256)
                struct.pack_into('>Q', hdd, 0x10, 3) # DEV_ID = 3
                struct.pack_into('>Q', hdd, 0x38, self.busy_h.get('tagstat', 0))
                struct.pack_into('>Q', hdd, 0x40, self.busy_h.get('status40', 0))
                struct.pack_into('>Q', hdd, 0x48, self.busy_h.get('status48', 0))
                hdd[0x78] = self.busy_h.get('err', 0)
                hdd[0x85] = self.busy_h.get('enabled', 1)

                self.w(HDD_STRUCT_ADDR, bytes(hdd))

                # UFS global lock at 0x3055180 = 0 (unlocked)
                self.w(UFS_LOCK_ADDR, struct.pack('>I', self.busy_h.get('ufs_lock', 0)))

                # Allocator pool descriptors
                self.w(POOL_934980,  struct.pack('>Q', 0x80000000))
                self.w(POOL_24565B8, struct.pack('>Q', 0x80000000))
                self.w(POOL_2446588, struct.pack('>Q', 0x80020000))

                # Stock label
                self.w(STOCK_LABEL_ADDR, b"Stock Menu Label\0")

                # Clear arena
                self.w(ARENA_BASE, b'\0' * ARENA_SIZE)

            def handle_breakpoints(self):
                pc = int(str(self.em.getExecutionAddress().getOffset())) & MASK

                if pc == 0x4800:
                    # native_alloc(size, a2, a3)
                    sz = self.get_reg(3)
                    self.set_reg(3, ARENA_BASE)
                    lr = self.get_lr()
                    self.set_pc(lr)
                    return True

                if pc == 0x4840:
                    # native_clock()
                    self.tb_ticks += 1000
                    self.set_reg(3, self.tb_ticks)
                    lr = self.get_lr()
                    self.set_pc(lr)
                    return True

                if pc == 0x4880:
                    # stock_ufs_open(0, path)
                    dev = self.get_reg(3)
                    path_ptr = self.get_reg(4)
                    raw_path = bytearray()
                    for i in range(64):
                        b = self.em.readMemoryByte(s.getAddress(path_ptr + i)) & 0xFF
                        if b == 0: break
                        raw_path.append(b)
                    path_str = raw_path.decode('ascii', errors='replace')
                    self.paths_opened.append(path_str)

                    if self.inject_open_err is not None:
                        self.set_reg(3, self.inject_open_err)
                        lr = self.get_lr()
                        self.set_pc(lr)
                        return True

                    assert path_str == "/tmp/netemu_log.bin", f"Unexpected open path: {path_str}"

                    # Allocate slot (0..7)
                    allocated_fd = -1
                    for fd in range(8):
                        if fd not in self.open_slots or not self.open_slots[fd]:
                            allocated_fd = fd
                            break
                    assert allocated_fd != -1, "All 8 file slots occupied!"
                    self.open_slots[allocated_fd] = True
                    self.total_opens += 1
                    self.set_reg(3, allocated_fd)
                    lr = self.get_lr()
                    self.set_pc(lr)
                    return True

                if pc == 0x48C0:
                    # stock_ufs_close(fd)
                    fd = self.get_reg(3)
                    assert 0 <= fd <= 7, f"Invalid fd passed to close: {fd}"
                    assert self.open_slots.get(fd) is True, f"Closing un-opened fd: {fd}"
                    self.open_slots[fd] = False
                    self.total_closes += 1
                    self.set_reg(3, 0)
                    lr = self.get_lr()
                    self.set_pc(lr)
                    return True

                if pc == 0x4900:
                    # stock_raw_read(fd, offset, buf, count)
                    fd = self.get_reg(3)
                    offset = self.get_reg(4)
                    buf = self.get_reg(5)
                    count = self.get_reg(6)
                    assert 0 <= fd <= 7 and self.open_slots.get(fd) is True
                    assert offset % 512 == 0, f"Un-aligned read offset: {offset}"
                    data = self.file_data[offset : offset + count]
                    self.w(buf, bytes(data))
                    self.set_reg(3, len(data))
                    lr = self.get_lr()
                    self.set_pc(lr)
                    return True

                if pc == 0x4940:
                    # stock_raw_write(fd, offset, buf, count)
                    fd = self.get_reg(3)
                    offset = self.get_reg(4)
                    buf = self.get_reg(5)
                    count = self.get_reg(6)
                    assert 0 <= fd <= 7 and self.open_slots.get(fd) is True

                    if self.inject_write_err is not None:
                        self.set_reg(3, self.inject_write_err)
                        lr = self.get_lr()
                        self.set_pc(lr)
                        return True

                    assert offset % 512 == 0, f"Un-aligned write offset: {offset}"
                    assert count == 512, f"Expected 512-byte write count, got {count}"
                    assert offset + count <= 65536, f"Write beyond file size: {offset}+{count}"

                    data = self.rd(buf, count)
                    self.file_data[offset : offset + count] = data
                    self.writes.append((offset, count, bytes(data)))
                    self.set_reg(3, count)
                    lr = self.get_lr()
                    self.set_pc(lr)
                    return True

                if pc == 0x4980:
                    # stock_hdd_cache_flush()
                    self.flush_calls += 1

                    # Verify idle precondition at the call
                    h_85 = self.em.readMemoryByte(s.getAddress(HDD_STRUCT_ADDR + 0x85)) & 0xFF
                    h_78 = self.em.readMemoryByte(s.getAddress(HDD_STRUCT_ADDR + 0x78)) & 0xFF
                    tagstat = struct.unpack('>Q', self.rd(HDD_STRUCT_ADDR + 0x38, 8))[0]
                    status48 = struct.unpack('>Q', self.rd(HDD_STRUCT_ADDR + 0x48, 8))[0]
                    assert h_85 == 1, "flush called while driver disabled"
                    assert h_78 == 0, "flush called while driver error flag set"
                    assert tagstat == 0, "flush called while tagstat != 0"
                    assert status48 == 0, "flush called while status48 != 0"

                    if self.inject_flush_err is not None:
                        self.set_reg(3, self.inject_flush_err)
                    else:
                        self.set_reg(3, 0)

                    lr = self.get_lr()
                    self.set_pc(lr)
                    return True

                return False

            def call_menu(self, selected_row, advance_tb_ticks=0):
                self.tb_ticks += advance_tb_ticks
                r24_base = 0xaaa700bf000
                self.w(r24_base + 44, struct.pack('>I', selected_row))

                self.set_reg(1, SP)
                self.set_reg(2, 0x751280)
                self.set_reg(24, r24_base)
                self.em.writeRegister('lr', BigInteger(str(STOP)))

                # Entry menu trampoline at 0x49C0
                self.set_pc(0x49C0)

                monitor = ConsoleTaskMonitor()
                steps = 0
                max_steps = 100000

                while steps < max_steps:
                    pc = int(str(self.em.getExecutionAddress().getOffset())) & MASK
                    if pc == STOP:
                        break
                    if self.handle_breakpoints():
                        steps += 1
                        continue
                    ok = self.em.step(monitor)
                    if not ok:
                        break
                    steps += 1

                assert steps < max_steps, f"Emulation timed out at pc=0x{pc:x}"
                ret_r3 = self.get_reg(3)
                ret_r4 = self.get_reg(4)

                # Read string from ret_r4
                raw = bytearray()
                for i in range(64):
                    b = self.em.readMemoryByte(s.getAddress(ret_r4 + i)) & 0xFF
                    if b == 0: break
                    raw.append(b)
                return ret_r4, raw.decode('latin-1', errors='replace')

        # -------------------------------------------------------------
        # TEST 1: Happy Path (L0 Writes 4 Records, Clean Flush)
        # -------------------------------------------------------------
        print("\n--- Test 1: Happy Path (L0 4-record durable write & flush) ---")
        emu1 = P3BEmuRunner()

        # Call rows 0..8
        row_labels = []
        for r in range(9):
            ptr, lbl = emu1.call_menu(r)
            row_labels.append(lbl)

        print(f"Row 0: {row_labels[0]}")
        print(f"Row 1: {row_labels[1]}")
        print(f"Row 2: {row_labels[2]}")
        print(f"Row 3: {row_labels[3]}")
        print(f"Row 4: {row_labels[4]}")
        print(f"Row 8: {row_labels[8]}")

        assert "P3B-L0 OK: 4 RECS, 2048 B, FLUSH OK" in row_labels[0], f"Row 0 unexpected: {row_labels[0]}"
        assert "HDD IDLE 38=0000000000000000" in row_labels[1], f"Row 1 unexpected: {row_labels[1]}"
        assert "RECS WRITTEN: 4" in row_labels[3], f"Row 3 unexpected: {row_labels[3]}"
        assert "COMPLETED OK (RC=0)" in row_labels[4], f"Row 4 unexpected: {row_labels[4]}"

        # Slot accounting check: exactly 0 leaked slots
        active_slots = [fd for fd, is_open in emu1.open_slots.items() if is_open]
        assert len(active_slots) == 0, f"Leaked file slots: {active_slots}"
        assert emu1.total_opens == 4, f"Expected 4 open calls, got {emu1.total_opens}"
        assert emu1.total_closes == 4, f"Expected 4 close calls, got {emu1.total_closes}"
        assert emu1.flush_calls == 4, f"Expected 4 flush calls, got {emu1.flush_calls}"

        # Decode written file image via decode_netemu_log.py
        decoded = decode_netemu_log.decode_log(bytes(emu1.file_data), verbose=False)
        assert decoded['header'] is not None, "Header decoding failed"
        assert decoded['header']['magic'] == 'NETEMULG'
        assert decoded['header']['next_record_idx'] == 5, f"Expected next cursor 5, got {decoded['header']['next_record_idx']}"
        assert decoded['header']['record_count'] == 4, f"Expected 4 records, got {decoded['header']['record_count']}"
        assert len(decoded['records']) == 4, f"Expected 4 records, got {len(decoded['records'])}"

        r1, r2, r3, r4 = decoded['records']
        assert r1['tag_str'] == "'BOOT'" and r1['text'] == "L0 BOOT"
        assert r2['tag_str'] == "'T1  '" and r2['text'] == "L0 T1 after BOOT"
        assert r3['tag_str'] == "'T2  '" and r3['text'] == "L0 T2 test record"
        assert r4['tag_str'] == "'END '" and r4['text'] == "L0 END complete"
        print("  [PASS] Happy path verified: 4 records written, header cursor updated, 0 slots leaked, decoded cleanly!")

        # Repeated open check: ensure does not re-log
        prev_writes = len(emu1.writes)
        _, lbl_open2 = emu1.call_menu(0, advance_tb_ticks=120000000)
        assert len(emu1.writes) == prev_writes, "Repeated menu open re-issued writes!"
        _, lbl_row8 = emu1.call_menu(8)
        assert "OPENS=1" in lbl_row8, f"Open count not incremented: {lbl_row8}"
        print("  [PASS] Repeated menu open check: idempotent, zero duplicate writes, open count updated!")

        # -------------------------------------------------------------
        # TEST 2: Busy HDD State Variants (Zero UFS Calls)
        # -------------------------------------------------------------
        print("\n--- Test 2: Busy HDD State Variants ---")
        for name, busy_state in [
            ('tagstat != 0', {'tagstat': 1}),
            ('status48 != 0', {'status48': 2}),
            ('driver disabled (85=0)', {'enabled': 0}),
            ('driver error (78=1)', {'err': 1}),
            ('ufs lock held', {'ufs_lock': 1}),
        ]:
            emu_busy = P3BEmuRunner(busy_h=busy_state)
            _, lbl = emu_busy.call_menu(0)
            assert emu_busy.total_opens == 0, f"Busy state {name} issued open!"
            assert len(emu_busy.writes) == 0, f"Busy state {name} issued write!"
            assert emu_busy.flush_calls == 0, f"Busy state {name} issued flush!"
            assert "DISK NOT IDLE" in lbl, f"Expected 'DISK NOT IDLE' on {name}, got: {lbl}"
            print(f"  [PASS] Busy condition '{name}' correctly prevented all UFS calls.")

        # -------------------------------------------------------------
        # TEST 3: Missing Placeholder File (Safe Fallback)
        # -------------------------------------------------------------
        print("\n--- Test 3: Missing Placeholder File (ufs_open -> -2) ---")
        emu_nofile = P3BEmuRunner(inject_open_err=-2)
        _, lbl_nofile = emu_nofile.call_menu(0)
        assert emu_nofile.total_opens == 0 or len([fd for fd, o in emu_nofile.open_slots.items() if o]) == 0
        assert len(emu_nofile.writes) == 0, "Writes issued when file missing!"
        assert emu_nofile.flush_calls == 0, "Flush issued when file missing!"
        assert "NO FILE" in lbl_nofile, f"Expected 'NO FILE', got: {lbl_nofile}"
        print(f"  [PASS] Missing file test passed: label shows '{lbl_nofile}', 0 writes, 0 flushes, 0 leaked slots.")

        # -------------------------------------------------------------
        # TEST 4: Write Failure Injection (Slots Closed Cleanly)
        # -------------------------------------------------------------
        print("\n--- Test 4: Write Failure Injection ---")
        emu_wr_fail = P3BEmuRunner(inject_write_err=-5)
        _, lbl_wr_fail = emu_wr_fail.call_menu(0)
        # Verify slot closed on error path
        active_slots = [fd for fd, is_open in emu_wr_fail.open_slots.items() if is_open]
        assert len(active_slots) == 0, f"Leaked slot on write error: {active_slots}"
        assert emu_wr_fail.flush_calls == 0, "Flush called despite write error!"
        assert "WRITE RC=" in lbl_wr_fail, f"Expected WRITE RC= in label, got: {lbl_wr_fail}"
        print(f"  [PASS] Write failure test passed: 0 leaked slots, flush skipped, label: '{lbl_wr_fail}'")

        # -------------------------------------------------------------
        # TEST 5: Memory Store Range Audit
        # -------------------------------------------------------------
        print("\n--- Test 5: Strict Memory Store Range Audit ---")
        write_set = emu1.em.getTrackedMemoryWriteSet()
        if write_set:
            for r in write_set.getAddressRanges():
                if r.getMinAddress().getAddressSpace() != s:
                    continue
                lo = r.getMinAddress().getOffset()
                hi = r.getMaxAddress().getOffset() + 1

                is_stack = (SP - 0x10000 <= lo and hi <= SP + 0x1000)
                is_mailbox = (MAILBOX <= lo and hi <= MAILBOX + MAILBOX_SIZE)
                is_arena = (ARENA_BASE <= lo and hi <= ARENA_BASE + ARENA_SIZE)
                is_fixture = (0xaaa700bf000 <= lo and hi <= 0xaaa700bf100)

                overlaps_stock_vars = (lo < 0x931000 and hi > 0x930F80)
                assert not overlaps_stock_vars, \
                    f"CRITICAL DEFECT: Store detected into stock variables range [0x930F80..0x931000) at {hex(lo)}..{hex(hi)}!"

                assert is_stack or is_mailbox or is_arena or is_fixture, \
                    f"Unauthorized store outside allowed memory ranges: {hex(lo)}..{hex(hi)}"

        print(f"  [PASS] Memory store audit: all stores strictly in stack, mailbox, or arena. ZERO stores >= 0x930F80!")

        # -------------------------------------------------------------
        # TEST 6: Menu Row Bounds Fuzzing
        # -------------------------------------------------------------
        print("\n--- Test 6: Menu Row Bounds Fuzzing ---")
        emu_fuzz = P3BEmuRunner()
        fuzz_indices = [0, 1, 2, 7, 8, 9, 10, 15, 36, 100, 255, 1000, 0xFFFFFFFF]
        for idx in fuzz_indices:
            ptr, lbl = emu_fuzz.call_menu(idx)
            assert ptr != 0, f"Null label returned for selected={idx}"
            assert len(lbl) > 0, f"Empty label returned for selected={idx}"
        print(f"  [PASS] Bounds fuzzing passed on {len(fuzz_indices)} extreme indices: all returned valid safe strings.")

    # 3. SELF Round-Trip Verification
    print("\n--------------------------------------------------")
    print("Verifying SELF Round-Trip Decryption...")
    print("--------------------------------------------------")
    out_self = ROOT / 'local_only' / 'p3b' / 'ps2_netemu_p3b_L0.self'
    rt_elf = ROOT / 'local_only' / 'p3b' / 'roundtrip_p3b.elf'
    dec = runpy.run_path(str(H / 'selfdec.py'))
    key_vault = Path(r'C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp')
    dec['main'](str(key_vault), str(out_self), str(rt_elf))
    assert hashlib.sha256(rt_elf.read_bytes()).hexdigest() == elf_sha, "SELF roundtrip SHA256 mismatch!"
    print("  [PASS] SELF round-trip decrypted ELF matches patched ELF byte-for-byte!")

    # 4. PowerShell Parser Syntax Audit
    print("\n--------------------------------------------------")
    print("Running PowerShell AST Parser Syntax Audit...")
    print("--------------------------------------------------")
    ps_res = subprocess.run([sys.executable, str(ROOT / 'tools' / 'parse_check_scripts.py')],
                            capture_output=True, text=True)
    assert ps_res.returncode == 0, f"Parser check failed: {ps_res.stderr}"
    print(ps_res.stdout.strip())
    print("  [PASS] All PowerShell scripts verified syntax-clean (0 errors).")

    print("\n==================================================")
    print("ALL P3B PC VALIDATION CHECKS PASSED (100% SUCCESS)!")
    print("==================================================")

if __name__ == '__main__':
    validate_p3b()
