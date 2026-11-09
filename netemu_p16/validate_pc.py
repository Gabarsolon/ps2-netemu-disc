"""Shared PPC emulation harness inherited from earlier diagnostics.

Imported by validate_logger.py, which runs the P16 executable and overrides
packet fixtures. Modeled device/profile values are test inputs, not console
findings. Run validate_logger.py for the actual P16 validation matrix.
"""
from pathlib import Path
import json, hashlib, os, struct, subprocess, sys, warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

H = Path(__file__).resolve().parent
ROOT = H.parent
GH = ROOT / 'local_only' / 'ghidra_p16'

for d in ['evidence', 'tmp', 'settings']:
    (H / d).mkdir(exist_ok=True)
(GH / 'projects').mkdir(parents=True, exist_ok=True)

for k in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
    os.environ[k] = str(H / ('tmp' if k in ['TEMP', 'TMP', 'TMPDIR'] else 'settings'))
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'

# Sanitize sys.path
sys.path = [p for p in sys.path if not Path(p).resolve().name.lower() == 'local_only']

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
from java.math import BigInteger
from java.util.concurrent import TimeUnit

MASK = (1 << 64) - 1
SP = 0xaaa700bfe00
STOP = 0x7FF0

CDVD_LPAR = 0x0000500002c00000  # Physical LPAR address (at 0x2458438)
CDVD_EA   = 0x0000000084000000  # CPU Effective Address (at 0x2458428)
CDVD_SZ   = 0x0000000000100000  # 1 MiB (at 0x2458430)

HDD_LPAR  = 0x0000500002d00000  # Physical LPAR address
HDD_EA    = 0x0000000084800000  # CPU Effective Address

MAILBOX = 0x930F20
MAILBOX_SIZE = 96
ARENA_BASE = 0x80020000
ARENA_SIZE = 4096

KEY_TYPE = 0x7479706500000000
KEY_ID   = 0x6964000000000000
KEY_PORT = 0x706f727400000000
KEY_REG0 = 0x726567696f6e0000
def TAG_BUS(b): return 0x62757300 | (b & 0xFF)
def KEY_DEV(d): return 0x6465760000000000 | (d & 0xFF)

fake_repo_console = {
    (TAG_BUS(4), KEY_TYPE, 0, 0): (5, 0),         # bus 4 type = 5 (STORAGE)
    (TAG_BUS(4), KEY_ID, 0, 0): (4, 0),           # bus 4 id = 4
    (TAG_BUS(4), KEY_DEV(2), KEY_TYPE, 0): (5, 0),       # type 5 (ROM)
    (TAG_BUS(4), KEY_DEV(2), KEY_ID, 0): (2, 0),         # dev id = 2
    (TAG_BUS(4), KEY_DEV(2), KEY_PORT, 0): (0, 0),       # port 0
    (TAG_BUS(4), KEY_DEV(2), KEY_REG0, KEY_ID): (0, 0),  # region 0 id = 0
    (TAG_BUS(4), KEY_DEV(3), KEY_TYPE, 0): (0, 0),       # type 0 (DISK)
    (TAG_BUS(4), KEY_DEV(3), KEY_ID, 0): (3, 0),         # dev id = 3
    (TAG_BUS(4), KEY_DEV(3), KEY_PORT, 0): (2, 0),       # port 2 (HDD control)
}

def classify_sector_buffer(data):
    """Buffer classification logic:
    - UNCHANGED: all 2048 bytes are 0xA5
    - ZEROS: all 2048 bytes are 0x00
    - DATA_OK: bytes 1..5 match b'CD001'
    - OTHER: any other pattern
    """
    if all(b == 0xA5 for b in data):
        return 'UNCHANGED'
    if data[1:6] == b'CD001':
        return 'DATA_OK'
    if all(b == 0x00 for b in data):
        return 'ZEROS'
    return 'OTHER'

def verify_wrapper_bytes(elf_path):
    stock_path = ROOT / 'local_only' / 'stock.elf'
    stock_bytes = stock_path.read_bytes()
    elf_bytes = elf_path.read_bytes()

    stock_off = 0x121eb8
    patched_off = 0x14800

    stock_wrapper = stock_bytes[stock_off : stock_off + 180]
    patched_wrapper = elf_bytes[patched_off : patched_off + 180]

    ident = sum(1 for i in range(0, 180, 4) if patched_wrapper[i:i+4] == stock_wrapper[i:i+4])
    assert ident == 29, f"Expected 29 identical instructions in wrapper, got {ident}"

    sc_val, = struct.unpack_from('>I', patched_wrapper, 0x58)
    assert sc_val == 0x44000002, f"Expected sc 0 at 0x4858 (+0x58), got {hex(sc_val)}"

    mr_r8_r9, = struct.unpack_from('>I', patched_wrapper, 0x48)
    assert mr_r8_r9 == 0x7D284B78, f"Expected mr r8, r9 at 0x4848, got {hex(mr_r8_r9)}"

# Expected 0x70-byte disc authentication request packet
def build_expected_auth_req():
    req = bytearray(0x70)
    struct.pack_into('>I', req, 0x00, 0x0000FACE)
    struct.pack_into('>I', req, 0x04, 0x00005000)
    struct.pack_into('>I', req, 0x08, 0x00000060)
    struct.pack_into('>I', req, 0x0C, 0x00000060)
    struct.pack_into('>Q', req, 0x10, 0x0000000000005005)
    struct.pack_into('>Q', req, 0x18, 0x0000000000005000)
    struct.pack_into('>Q', req, 0x30, 0x1020000401000001)
    req[0x38] = 0x00  # byte A
    req[0x39] = 0x13  # byte B (DVD-5)
    struct.pack_into('>I', req, 0x40, 0x0000004B)  # retries = 75
    return bytes(req)

class P11EmuRunner:
    def __init__(self, program, scenario='reply_ok', fail_cdvd_guard=False, fail_swapped_guard=False,
                 fail_block_size=False, atapi_timeout=False, hdd_busy=False, fail_ufs_open=False):
        self.p = program
        self.s = program.getAddressFactory().getDefaultAddressSpace()
        self.em = EmulatorHelper(program)
        self.em.enableMemoryWriteTracking(True)
        self.scenario = scenario
        self.fail_cdvd_guard = fail_cdvd_guard
        self.fail_swapped_guard = fail_swapped_guard
        self.fail_block_size = fail_block_size
        self.atapi_timeout = atapi_timeout
        self.hdd_busy = hdd_busy
        self.fail_ufs_open = fail_ufs_open

        self.hcalls_generic = []
        self.timebase_ticks = 1000000000
        self.ufs_open_count = 0
        self.ufs_close_count = 0
        self.is_fd_open = False
        self.disk_log = bytearray(65536)
        self.disk_writes = []

        self.next_async_tag = 0x100
        self.last_async_op = None
        self.last_read_lba = None
        self.last_read_proto = None

        self.captured_auth_req = None
        self.vuart_read_offset = 0
        self.rds_called = False

        # Setup breakpoints for hypercalls and trampolines
        for addr in [0x4858, 0x111f10, 0x0b9cd0, 0x0b9848, 0x1ecc5c, 0x1ecb10, 0x1ed5cc, 0x1ed458, 0x12cc98, STOP]:
            self.em.setBreakpoint(self.s.getAddress(addr))

        # Initialize RAM memory pools
        self.w(MAILBOX, bytes(MAILBOX_SIZE))
        self.w(ARENA_BASE, bytes(ARENA_SIZE))
        self.w(CDVD_EA, bytes(0x2000))

        # Pool descriptors for arena_rw()
        self.w(0x934980, struct.pack('>Q', 0x80000000))
        self.w(0x24565b8, struct.pack('>Q', 0x80000000))
        self.w(0x2446588, struct.pack('>Q', 0x80020000))

        # SB_CDVD buffer descriptors
        if self.fail_cdvd_guard:
            self.w(0x2458438, struct.pack('>Q', 0x0))
            self.w(0x2458428, struct.pack('>Q', 0x0))
            self.w(0x2458430, struct.pack('>Q', 0x0))
        elif self.fail_swapped_guard:
            self.w(0x2458438, struct.pack('>Q', CDVD_EA))
            self.w(0x2458428, struct.pack('>Q', CDVD_LPAR))
            self.w(0x2458430, struct.pack('>Q', CDVD_SZ))
        else:
            self.w(0x2458438, struct.pack('>Q', CDVD_LPAR))
            self.w(0x2458428, struct.pack('>Q', CDVD_EA))
            self.w(0x2458430, struct.pack('>Q', CDVD_SZ))

        # Stock HDD singleton H (0x241c850)
        h_ptr = 0x241c850
        h_buf = bytearray(256)
        h_buf[0x85] = 0 if self.hdd_busy else 1
        h_buf[0x78] = 1 if self.hdd_busy else 0
        struct.pack_into('>Q', h_buf, 0x10, 3)
        struct.pack_into('>Q', h_buf, 0x20, HDD_LPAR)
        struct.pack_into('>Q', h_buf, 0x28, HDD_EA)
        struct.pack_into('>Q', h_buf, 0x38, 1 if self.hdd_busy else 0)
        struct.pack_into('>Q', h_buf, 0x40, 1 if self.hdd_busy else 0)
        struct.pack_into('>Q', h_buf, 0x48, 1 if self.hdd_busy else 0)
        self.w(h_ptr, bytes(h_buf))
        self.w(0x3055180, struct.pack('>I', 1 if self.hdd_busy else 0))

    def w(self, addr, b):
        self.em.writeMemory(self.s.getAddress(addr), b)

    def r(self, addr, size):
        return bytes([self.em.readMemoryByte(self.s.getAddress(addr + i)) & 0xFF for i in range(size)])

    def get_reg(self, n):
        if n == 'pc':
            return self.em.getExecutionAddress().getOffset()
        name = f'r{n}' if isinstance(n, int) else n
        return int(str(self.em.readRegister(name))) & MASK

    def set_reg(self, n, val):
        if n == 'pc':
            self.em.writeRegister(self.em.getPCRegister(), BigInteger(str(val)))
        else:
            name = f'r{n}' if isinstance(n, int) else n
            self.em.writeRegister(name, BigInteger(str(val)))

    def handle_generic_hcall(self):
        num = self.get_reg(11) & 0x7FFFFFFF
        a1 = self.get_reg(3)
        a2 = self.get_reg(4)
        a3 = self.get_reg(5)
        a4 = self.get_reg(6)
        a5 = self.get_reg(7)
        a6 = self.get_reg(8)
        self.hcalls_generic.append((num, a1, a2, a3, a4, a5, a6))

        ret_rc = 0
        val1 = 0
        val2 = 0

        if num == 170:  # storage open
            ret_rc = 0
        elif num == 174:  # allocate DMA region
            val1 = 0xC0000000
            ret_rc = 0
        elif num == 176:  # map device DMA region
            lpar = a3
            if lpar != CDVD_LPAR:
                ret_rc = -17
            else:
                ret_rc = 0
                val1 = 0xC0000000
        elif num == 177:  # unmap
            ret_rc = 0
        elif num == 175:  # free DMA region
            ret_rc = 0
        elif num == 171:  # storage close
            ret_rc = 0
        elif num == 165:  # lv1_get_virtual_uart_param
            port = a1
            param_id = a2
            if port == 2:
                # Port 2 (Sysmgr channel)
                ret_rc = 0
                val1 = 0x800 if param_id == 3 else 0
            elif port == 10:
                # Port 10 (Secure service channel)
                if self.scenario == 'param_err':
                    ret_rc = -6  # LV1_NO_ENTRY
                    val1 = 0
                else:
                    ret_rc = 0
                    val1 = 0x1000 if param_id == 3 else 0
            else:
                ret_rc = -6
        elif num == 163:  # lv1_write_virtual_uart
            port = a1
            buf_lpar = a2
            buf_len = a3
            if port == 10:
                if self.scenario == 'write_err':
                    ret_rc = -1  # error
                    val1 = 0
                else:
                    assert buf_len == 0x70, f"Expected 0x70 byte write, got {buf_len}"
                    req_ea = buf_lpar - CDVD_LPAR + CDVD_EA
                    self.captured_auth_req = self.r(req_ea, buf_len)
                    ret_rc = 0
                    val1 = buf_len
            else:
                ret_rc = -6
        elif num == 162:  # lv1_read_virtual_uart
            port = a1
            buf_lpar = a2
            buf_len = a3
            if port == 10:
                if self.scenario == 'reply_ok':
                    reply = bytearray(0x70)
                    struct.pack_into('>I', reply, 0x00, 0xFACE5000)
                    struct.pack_into('>I', reply, 0x04, 0x00000060)
                    struct.pack_into('>H', reply, 0x22, 0x0000)  # Status: OK
                    reply[0x38] = 0x07  # Flags: keys valid
                    reply[0x40:0x70] = b'\xEE' * 0x30  # Dummy keys (MUST NOT LEAK)
                    chunk = min(buf_len, len(reply) - self.vuart_read_offset)
                    if chunk > 0:
                        dest_ea = buf_lpar - CDVD_LPAR + CDVD_EA
                        self.w(dest_ea, reply[self.vuart_read_offset : self.vuart_read_offset + chunk])
                        self.vuart_read_offset += chunk
                        ret_rc = 0
                        val1 = chunk
                    else:
                        ret_rc = 0
                        val1 = 0
                elif self.scenario == 'nonzero_status':
                    reply = bytearray(0x70)
                    struct.pack_into('>I', reply, 0x00, 0xFACE5000)
                    struct.pack_into('>H', reply, 0x22, 0x0016)  # Status: 0x0016 (HW: not ps2 disc)
                    reply[0x38] = 0x00  # Flags: 0
                    reply[0x40:0x70] = b'\xEE' * 0x30
                    chunk = min(buf_len, len(reply) - self.vuart_read_offset)
                    if chunk > 0:
                        dest_ea = buf_lpar - CDVD_LPAR + CDVD_EA
                        self.w(dest_ea, reply[self.vuart_read_offset : self.vuart_read_offset + chunk])
                        self.vuart_read_offset += chunk
                        ret_rc = 0
                        val1 = chunk
                    else:
                        ret_rc = 0
                        val1 = 0
                elif self.scenario == 'short_reply':
                    # Only return 0x20 bytes total, then stops
                    reply = bytearray(0x20)
                    struct.pack_into('>I', reply, 0x00, 0xFACE5000)
                    chunk = min(buf_len, max(0, len(reply) - self.vuart_read_offset))
                    if chunk > 0:
                        dest_ea = buf_lpar - CDVD_LPAR + CDVD_EA
                        self.w(dest_ea, reply[self.vuart_read_offset : self.vuart_read_offset + chunk])
                        self.vuart_read_offset += chunk
                        ret_rc = 0
                        val1 = chunk
                    else:
                        # Advance timebase past 2.0s limit to end polling
                        self.timebase_ticks += 200000000
                        ret_rc = 0
                        val1 = 0
                elif self.scenario == 'timeout':
                    # Advance timebase past 2.0s limit
                    self.timebase_ticks += 200000000
                    ret_rc = 0
                    val1 = 0
                else:
                    ret_rc = 0
                    val1 = 0
            else:
                ret_rc = -6
        elif num == 248:  # storage_send_device_command (ATAPI)
            dev = a1
            cmnd_block_lpar = a3
            buf_lpar = a5
            buf_len = a6

            assert cmnd_block_lpar == CDVD_LPAR, f"cmnd_block_lpar must be 0x500002c00000, got {hex(cmnd_block_lpar)}"
            if buf_len > 0:
                assert buf_lpar == CDVD_LPAR + 0x1000, f"buf_lpar must be 0x500002c01000, got {hex(buf_lpar)}"

            cdb = self.r(CDVD_EA, 12)
            cdb_op = cdb[0]
            self.last_async_op = cdb_op
            self.next_async_tag += 1
            val1 = self.next_async_tag
            ret_rc = 0

            if cdb_op == 0x12:  # INQUIRY (PIO)
                inq = bytearray(36)
                inq[0] = 0x05
                inq[1] = 0x80
                inq[4] = 31
                inq[8:16] = b'SONY    '
                inq[16:32] = b'PS3 CD/DVD-ROM  '
                inq[32:36] = b'1.00'
                self.w(CDVD_EA + 0x1000, bytes(inq))

            elif cdb_op == 0x25:  # READ CAPACITY (PIO)
                bsz = 512 if self.fail_block_size else 2048
                cap = struct.pack('>II', 0x001da34f, bsz)
                self.w(CDVD_EA + 0x1000, cap)

            elif cdb_op == 0x46:  # GET CONFIGURATION (PIO)
                # First query returns default DVD-ROM profile (0x0010);
                # after READ DISC STRUCTURE (or second query) returns PS2 DVD (0xFF61)
                cfg = bytearray(32)
                struct.pack_into('>I', cfg, 0, 28)
                prof = 0xFF61 if self.rds_called else 0x0010
                struct.pack_into('>H', cfg, 6, prof)
                self.w(CDVD_EA + 0x1000, bytes(cfg))

            elif cdb_op == 0xAD:  # READ DISC STRUCTURE (PIO)
                self.rds_called = True
                rds = bytearray(2048)
                struct.pack_into('>H', rds, 0, 2046)
                rds[4] = 0x01  # DVD-ROM book type
                self.w(CDVD_EA + 0x1000, bytes(rds))

            elif cdb_op == 0x28:  # READ(10)
                lba = (cdb[2] << 24) | (cdb[3] << 16) | (cdb[4] << 8) | cdb[5]
                proto = struct.unpack_from('>I', self.r(CDVD_EA, 64), 0x2C)[0]
                self.last_read_lba = lba
                self.last_read_proto = proto

                if proto == 1:  # PIO DATA-IN protocol: delivers data into buffer
                    sec_data = bytearray(2048)
                    if lba == 16:
                        # ISO9660 Primary Volume Descriptor (PVD)
                        sec_data[0:8] = b'\x01CD001\x01\x00'
                        sec_data[8:40] = b'TEST_DRIVE_UNLIMITED_PAL        '
                        sec_data[40:48] = b'TDU_TEST'
                    elif lba == 17:
                        # Volume Descriptor Terminator
                        sec_data[0:8] = b'\xFFCD001\x01\x00'
                        sec_data[40:48] = b'TDU_TERM'
                    elif lba == 0:
                        # Lead-in Sector 0 (all zeros)
                        pass
                    self.w(CDVD_EA + 0x1000, bytes(sec_data))
                elif proto == 3:  # DMA protocol: ground truth simulation (no data delivered)
                    pass

            elif cdb_op == 0x03:  # REQUEST SENSE
                sns = bytearray(18)
                sns[0] = 0x70
                self.w(CDVD_EA + 0x1000, bytes(sns))

        elif num == 254:  # storage_check_async_status
            dev = a1
            tag = a2
            if self.atapi_timeout:
                self.timebase_ticks += 200000000
                ret_rc = 1  # status pending (causes timeout)
                val1 = 0
            else:
                ret_rc = 0
                val1 = 0  # SUCCESS

        self.set_reg(3, ret_rc)
        self.set_reg(4, val1)
        self.set_reg(5, val2)
        self.w(0x930F70, struct.pack('>Q', val1))
        self.w(0x930F78, struct.pack('>Q', val2))
        self.set_reg('pc', 0x485C)

    def step(self, monitor):
        pc = self.em.getExecutionAddress().getOffset()

        if pc == 0x111f10:  # repo_read
            b = self.get_reg(3)
            d = self.get_reg(4)
            k = self.get_reg(5)
            v = self.get_reg(6)
            val = fake_repo_console.get((b, d, k, v), (0, 0))
            self.set_reg(3, 0)
            self.set_reg(4, val[0])
            self.set_reg(5, val[1])
            self.set_reg('pc', 0x111f14)
            return True

        if pc == 0x4858:  # lv1_hcall
            self.handle_generic_hcall()
            return True

        if pc == 0x0b9cd0:  # native_clock
            self.timebase_ticks += 50000
            self.set_reg(3, self.timebase_ticks)
            self.set_reg('pc', self.get_reg('lr'))
            return True

        if pc == 0x0b9848:  # native_alloc
            sz = self.get_reg(3)
            self.set_reg(3, ARENA_BASE)
            self.set_reg('pc', self.get_reg('lr'))
            return True

        if pc == 0x1ecc5c:  # stock_ufs_open
            self.ufs_open_count += 1
            if self.fail_ufs_open:
                self.set_reg(3, -1)
            else:
                self.is_fd_open = True
                self.set_reg(3, 3)
            self.set_reg('pc', self.get_reg('lr'))
            return True

        if pc == 0x1ecb10:  # stock_ufs_close
            self.ufs_close_count += 1
            self.is_fd_open = False
            self.set_reg(3, 0)
            self.set_reg('pc', self.get_reg('lr'))
            return True

        if pc == 0x1ed458:  # stock_raw_write
            fd = self.get_reg(3)
            off = self.get_reg(4)
            buf_ea = self.get_reg(5)
            sz = self.get_reg(6)
            assert self.is_fd_open, "Write attempted while fd is closed!"
            assert (off % 512) == 0 and (sz % 512) == 0, f"UFS write not 512-aligned: off={off}, sz={sz}"
            assert off + sz <= len(self.disk_log), f"Write out of bounds: off={off}, sz={sz}"
            data = self.r(buf_ea, sz)
            self.disk_log[off : off + sz] = data
            self.disk_writes.append((off, sz, bytes(data)))
            self.set_reg(3, sz)
            self.set_reg('pc', self.get_reg('lr'))
            return True

        if pc == 0x1ed5cc:  # stock_raw_read
            fd = self.get_reg(3)
            off = self.get_reg(4)
            buf_ea = self.get_reg(5)
            sz = self.get_reg(6)
            assert self.is_fd_open, "Read attempted while fd is closed!"
            assert (off % 512) == 0 and (sz % 512) == 0, f"UFS read not 512-aligned: off={off}, sz={sz}"
            assert off + sz <= len(self.disk_log), f"Read out of bounds: off={off}, sz={sz}"
            self.w(buf_ea, bytes(self.disk_log[off : off + sz]))
            self.set_reg(3, sz)
            self.set_reg('pc', self.get_reg('lr'))
            return True

        if pc == 0x12cc98:  # stock_hdd_cache_flush
            self.set_reg(3, 0)
            self.set_reg('pc', self.get_reg('lr'))
            return True

        self.em.step(monitor)
        return True

    def run(self, max_steps=400000):
        ctx_addr = ARENA_BASE + 0xE00
        self.w(ctx_addr + 44, struct.pack('>I', 0))
        self.set_reg('pc', 0x4AC0)  # entry_menu
        self.set_reg('r1', SP)
        self.set_reg('r2', 0x751280)
        self.set_reg('r24', ctx_addr)
        self.set_reg('lr', STOP)

        monitor = TimeoutTaskMonitor.timeoutIn(30, TimeUnit.SECONDS)
        steps = 0
        while steps < max_steps:
            pc = self.em.getExecutionAddress().getOffset()
            if pc == STOP:
                break
            self.step(monitor)
            steps += 1
        assert steps < max_steps, f"Execution timed out after {steps} steps"

    def get_menu_row(self, row_idx):
        ctx_addr = ARENA_BASE + 0xE00
        self.w(ctx_addr + 44, struct.pack('>I', row_idx))
        self.set_reg('pc', 0x4AC0)
        self.set_reg('r1', SP)
        self.set_reg('r2', 0x751280)
        self.set_reg('r24', ctx_addr)
        self.set_reg('lr', STOP)
        monitor = TimeoutTaskMonitor.timeoutIn(5, TimeUnit.SECONDS)
        steps = 0
        while steps < 10000:
            pc = self.em.getExecutionAddress().getOffset()
            if pc == STOP:
                break
            self.step(monitor)
            steps += 1
        return self.r(ARENA_BASE + 0x400 + row_idx * 64, 64).split(b'\x00')[0].decode('ascii', errors='ignore')

def decode_wal_log(disk_log):
    sec0 = disk_log[:512]
    magic = sec0[:8]
    assert magic == b'NETEMULG', f"Sector 0 magic mismatch: {magic}"
    version, hdr_sz, file_sz, sec_sz, max_rec, next_idx, boot_tb, shutdown, rec_count = struct.unpack_from('>IIIIIIQII', sec0, 8)
    records = []
    for i in range(1, next_idx):
        r_bytes = disk_log[i * 512 : (i + 1) * 512]
        assert r_bytes[:4] == b'LOGR', f"Record magic mismatch at sector {i}"
        seq, tag, flags, tb, a, b, bid = struct.unpack_from('>IIIQQQQ', r_bytes, 4)
        assert bid == boot_tb, f"boot_id mismatch at sector {i}: {hex(bid)} vs {hex(boot_tb)}"
        text_str = r_bytes[72:512].split(b'\x00')[0].decode('ascii', errors='ignore')
        records.append((tag.to_bytes(4, 'big').decode('ascii', errors='ignore'), text_str, a, b))
    return shutdown, boot_tb, records
