"""Execute the final PPC payload with fault-injected stock UFS/hypercall stubs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import struct
import subprocess

H = Path(__file__).resolve().parent
ROOT = H.parent
spec = importlib.util.spec_from_file_location('p16_harness', H / 'validate_pc.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

table = json.loads((H / 'evidence/p16_patch_table.json').read_text())['L1']
symbols = table['symbols']
ARENA = base.ARENA_BASE

# Derived by clang's record-layout pass, checked below against the source.
offsets = {
    'is_log_initialized': 1668, 'log_cursor': 1672, 'log_seq': 1676,
    'log_session_started': 2224, 'log_busy_last': 2228, 'log_busy_seen': 2232,
    'summary_attempts': 2236, 'summary_pending': 2240, 'summary_committed': 2244,
    'sector_attempted': 2248, 'sector_rc': 2252, 'summary_last_tb': 2256,
    'final_summary': 2264, 'auth_reply_opcode': 2704,
    'log_tagstat': 2712, 'log_expected_tag': 2720, 'log_status40': 2728,
    'log_hdd_state': 2736, 'log_command_type': 2740,
}


class Runner(base.P11EmuRunner):
    def __init__(self, program, **kwargs):
        self.faults = []
        self.busy_after_25 = False
        self.hit_busy = False
        self.completed_tags = False
        self.deliver_dma_data = False
        self.reply_opcode = 0x5005
        super().__init__(program, **kwargs)

    def u32(self, name):
        return struct.unpack('>I', self.r(ARENA + offsets[name], 4))[0]

    def set32(self, name, value):
        self.w(ARENA + offsets[name], struct.pack('>I', value & 0xffffffff))

    def clear_busy(self):
        self.w(0x241c850 + 0x85, b'\x01')
        self.w(0x241c850 + 0x78, b'\x00')
        self.w(0x241c850 + 0x10, struct.pack('>Q', 3))
        for off in [0x38, 0x40, 0x48]: self.w(0x241c850 + off, bytes(8))
        self.w(0x3055180, bytes(4))

    def call(self, name, args=(), max_steps=900000):
        self.set_reg('pc', symbols[name])
        self.set_reg('r1', base.SP)
        self.set_reg('r2', symbols['.TOC.'])
        self.set_reg('lr', base.STOP)
        for i, arg in enumerate(args): self.set_reg(3 + i, arg)
        monitor = base.TimeoutTaskMonitor.timeoutIn(45, base.TimeUnit.SECONDS)
        for step in range(max_steps):
            if self.get_reg('pc') == base.STOP: return self.get_reg(3)
            self.step(monitor)
        raise AssertionError('step budget exhausted in ' + name)

    def unit_seed(self):
        self.w(base.MAILBOX + 24, struct.pack('>Q', ARENA))
        self.clear_busy()

    def handle_generic_hcall(self):
        number = self.get_reg(11) & 0x7fffffff
        dest = self.get_reg(4)
        super().handle_generic_hcall()
        if number == 162 and self.get_reg(4) >= 0x18:
            ea = dest - base.CDVD_LPAR + base.CDVD_EA
            self.w(ea, struct.pack('>I', 0x0000face))
            self.w(ea + 0x10, struct.pack('>Q', self.reply_opcode))
            self.w(ea + 0x18, struct.pack('>Q', 0x5000))
        if number == 248 and self.last_async_op == 0x28 and self.deliver_dma_data:
            self.w(base.CDVD_EA + 0x1000, b'\x01CD001\x01' + bytes(2041))

    def step(self, monitor):
        pc = self.get_reg('pc')
        if self.busy_after_25 and not self.hit_busy:
            written = struct.unpack('>I', self.r(base.MAILBOX + 72, 4))[0]
            if written >= 25:
                self.w(0x3055180, struct.pack('>I', 1))
                self.hit_busy = True
        operation = {0x1ed458: 'write', 0x1ecb10: 'close', 0x12cc98: 'flush'}.get(pc)
        fault = self.faults[0] if self.faults else None
        if fault == 'header' and operation == 'write' and self.get_reg(4) == 0:
            fault = 'write'
        if self.faults and operation == fault:
            self.faults.pop(0)
            if operation == 'close': self.is_fd_open = False
            self.set_reg(3, 511 if operation == 'write' else -1)
            self.set_reg('pc', self.get_reg('lr'))
            return True
        result = super().step(monitor)
        if operation == 'flush' and self.completed_tags:
            self.w(0x241c850 + 0x38, struct.pack('>Q', 0x123))
            self.w(0x241c850 + 0x48, struct.pack('>Q', 0x123))
        return result


def assert_bounds(runner):
    ranges = runner.em.getTrackedMemoryWriteSet().getAddressRanges()
    while ranges.hasNext():
        region = ranges.next()
        if region.getMinAddress().getAddressSpace().getName() != 'ram': continue
        lo, hi = region.getMinAddress().getOffset(), region.getMaxAddress().getOffset()
        allowed = [
            (base.SP - 0x100000, base.SP + 0x100000),
            (base.MAILBOX, base.MAILBOX + 95), (ARENA, ARENA + 4095),
            (base.CDVD_EA, base.CDVD_EA + 0x1fff),
            (0x934980, 0x93498f), (0x24565b8, 0x24565c7),
            (0x2446588, 0x2446597), (0x2458428, 0x245843f),
            (0x241c850, 0x241c94f), (0x3055180, 0x305518f),
        ]
        assert any(a <= lo <= hi <= b for a, b in allowed), (hex(lo), hex(hi))


def summary(runner):
    end, boot, records = base.decode_wal_log(runner.disk_log)
    matches = [record for record in records if record[0] == 'SUM ']
    assert len(matches) == 1, matches
    assert end == 1
    assert records[-1][0] == 'END '
    assert runner.u32('summary_pending') == 0
    assert runner.u32('summary_committed') == 1
    assert not runner.is_fd_open
    assert b'\xee' * 16 not in bytes(runner.disk_log)
    assert len(matches[0][1]) < 440
    return matches[0][1]


def check_layout():
    command = [r'C:\Program Files\LLVM\bin\clang.exe', '-target', 'powerpc64-unknown-linux-gnu',
               '-mcpu=970', '-mabi=elfv2', '-ffreestanding', '-fsyntax-only',
               '-Xclang', '-fdump-record-layouts', str(H / 'src/probe.c')]
    data = subprocess.check_output(command, text=True)
    for name, offset in offsets.items():
        assert re.search(r'^\s*' + str(offset) + r' \|.*\b' + name + r'\b', data, re.M), name
    assert '| [sizeof=2744, align=8]' in data


def run():
    check_layout()
    elf = ROOT / 'local_only/p16/ps2_netemu_p16_L1.elf'
    stock = (ROOT / 'local_only/stock.elf').read_bytes()
    image = elf.read_bytes()
    assert image[0x13bac:0x13bb0] == stock[0x13bac:0x13bb0], 'CDVD read hook must remain stock'
    patches = table['patches']
    assert len(patches) == 2, 'Only slot and menu hook may differ'
    code = image[0x14800:0x14800 + table['code_size']]
    sc = [0x4800 + offset for offset in range(0, len(code) - 3, 4)
          if code[offset:offset + 4] in (b'\x44\x00\x00\x02', b'\x44\x00\x00\x22')]
    assert sc == [0x4858], sc
    base.verify_wrapper_bytes(elf)
    evidence = []
    with base.pyghidra.open_program(str(elf), project_location=str(base.GH / 'projects'),
                                    project_name='p16_l1_' + hashlib.sha256(image).hexdigest()[:10],
                                    analyze=False, language='PowerPC:BE:64:default') as flat:
        program = flat.getCurrentProgram()
        for scenario in ['reply_ok', 'nonzero_status', 'short_reply', 'timeout', 'write_err', 'param_err']:
            r = Runner(program, scenario=scenario)
            r.run(max_steps=900000)
            text = summary(r)
            assert 'P16L1 auth=' in text and 'send_rc=' in text and 'sample=' in text and 'mag=' in text and 'op=' in text
            assert 'sector_rc=0' in text
            assert 'class=UNCHANGED' in text and 'a5=2048' in text
            if scenario == 'nonzero_status': assert 'st=00000016' in text
            if scenario in ['reply_ok', 'nonzero_status', 'short_reply']:
                assert 'mag=0000face op=0000000000005005' in text
            if scenario == 'reply_ok': assert r.captured_auth_req == base.build_expected_auth_req()
            assert r.r(base.CDVD_EA + 0x1940, 0x30) == bytes(0x30)
            assert_bounds(r)
            evidence.append({'scenario': scenario, 'summary': text})
            print('PASS', scenario, text, flush=True)

        r = Runner(program); r.deliver_dma_data = True; r.run(max_steps=900000)
        assert 'class=DATA_OK' in summary(r) and 'sample=01434430303101' in summary(r)
        assert_bounds(r)
        print('PASS actual PVD bytes are distinguished from unchanged buffer', flush=True)

        r = Runner(program); r.reply_opcode = 0x1234; r.run(max_steps=900000)
        assert 'op=0000000000001234' in summary(r)
        print('PASS unrelated reply opcode is captured verbatim (no new auth policy)', flush=True)

        r = Runner(program, scenario='nonzero_status')
        r.busy_after_25 = True
        r.run(max_steps=900000)
        assert r.hit_busy and r.u32('summary_pending') == 1
        calls = len(r.hcalls_generic)
        attempts = r.u32('summary_attempts')
        r.get_menu_row(4)
        assert r.u32('summary_attempts') == attempts, '250ms gate did not hold'
        r.clear_busy(); r.timebase_ticks += 20000000
        r.get_menu_row(4)
        text = summary(r)
        assert 'st=00000016' in text and 'busy=00000040' in text
        assert len(r.hcalls_generic) == calls, 'summary retry reran drive probe'
        assert_bounds(r)
        print('PASS busy-after-record25 recovery', text, flush=True)
        evidence.append({'scenario': 'busy_after_25', 'summary': text})

        r = Runner(program, hdd_busy=True)
        r.run(max_steps=900000)
        assert not r.disk_writes and r.ufs_open_count == 0
        assert r.u32('is_log_initialized') == 0
        calls = len(r.hcalls_generic)
        for index in range(20):
            r.timebase_ticks += 20000000; r.get_menu_row(4)
        assert r.u32('summary_attempts') == 16
        assert len(r.hcalls_generic) == calls and r.ufs_open_count == 0
        print('PASS permanently busy: zero UFS calls; retry limit 16', flush=True)

        r = Runner(program); r.completed_tags = True
        r.w(0x241c850, struct.pack('>I', 2)); r.w(0x241c850 + 0x58, struct.pack('>I', 2))
        r.run(max_steps=900000)
        assert r.u32('log_busy_last') == 0x28
        assert r.r(ARENA + offsets['log_tagstat'], 8) == struct.pack('>Q', 0x123)
        for index in range(20):
            r.timebase_ticks += 20000000; r.get_menu_row(4)
        assert r.u32('summary_attempts') == 16 and r.u32('summary_pending') == 1
        assert r.ufs_open_count == 1, 'strict guard must not issue writes after nonzero tags'
        assert 'Q=02/02' in r.get_menu_row(5)
        print('PASS stock-flush nonzero completed tags: strict busy=0x28, safe refusal', flush=True)

        r = Runner(program, hdd_busy=True)
        r.run(max_steps=900000)
        boot = r.r(ARENA + 0x6f8, 8)
        r.clear_busy(); r.timebase_ticks += 20000000; r.get_menu_row(4)
        assert r.r(ARENA + 0x6f8, 8) == boot
        assert 'busy=0000007b' in summary(r)
        print('PASS init-busy recovery preserves boot ID', flush=True)

        for operation in ['write', 'header', 'close', 'flush']:
            r = Runner(program); r.unit_seed(); r.faults = [operation]
            r.call('hddlog_init')
            assert r.u32('is_log_initialized') == 0
            boot = r.r(ARENA + 0x6f8, 8)
            assert r.call('hddlog_init') == 0
            assert r.u32('is_log_initialized') == 1
            assert r.r(ARENA + 0x6f8, 8) == boot
            assert not r.is_fd_open
            print('PASS init failure recovery:', operation, flush=True)

        for operation in ['write', 'header', 'close', 'flush']:
            r = Runner(program); r.unit_seed(); assert r.call('hddlog_init') == 0
            r.w(ARENA + 3000, b'fault test\x00')
            r.faults = [operation]
            result = r.call('hddlog_write', (int.from_bytes(b'SUM ', 'big'), 1, 2, ARENA + 3000))
            assert result == base.MASK and r.u32('log_cursor') == 1 and r.u32('log_seq') == 0
            assert r.r(base.MAILBOX + 79, 1) == b'\x00'
            assert r.call('hddlog_write', (int.from_bytes(b'SUM ', 'big'), 1, 2, ARENA + 3000)) == 0
            assert r.u32('log_cursor') == 2 and r.u32('log_seq') == 1
            assert not r.is_fd_open
            print('PASS record failure retries same sector/sequence:', operation, flush=True)

        r = Runner(program); r.unit_seed(); assert r.call('hddlog_init') == 0
        r.w(ARENA + 3000, b'end fault\x00'); r.faults = ['flush']
        args = (int.from_bytes(b'END ', 'big'), 0, 0, ARENA + 3000)
        assert r.call('hddlog_write', args) == base.MASK
        assert r.r(base.MAILBOX + 79, 1) == b'\x00'
        assert r.u32('log_cursor') == 1
        assert r.call('hddlog_write', args) == 0
        assert r.r(base.MAILBOX + 79, 1) == b'\x01'
        print('PASS END flush failure never acknowledged clean; retry succeeds', flush=True)

        for options in [{'fail_cdvd_guard': True}, {'atapi_timeout': True}]:
            r = Runner(program, **options); r.run(max_steps=900000)
            text = summary(r)
            assert 'class=NOT_READ' in text
            calls = [call[0] for call in r.hcalls_generic]
            if options.get('fail_cdvd_guard'): assert not calls
            else: assert not any(call in calls for call in [177, 175, 171])
            assert_bounds(r)
            print('PASS guard/timeout safe stop:', options, flush=True)

        # Exercise worst-width fields in the compiled formatter, with sentinels.
        r = Runner(program); r.unit_seed()
        r.w(ARENA, b'\xff' * 2744)
        r.w(ARENA + 2744, b'\xa6' * 64)
        r.w(ARENA + 2252, struct.pack('>i', -2147483648))
        # s32 request/read/send fields; offsets verified from clang layout output.
        for offset in [1640, 2084, 2092]: r.w(ARENA + offset, struct.pack('>i', -2147483648))
        r.call('format_summary', (ARENA,))
        text = r.r(ARENA + 2264, 440).split(b'\x00')[0]
        assert len(text) < 440 and r.r(ARENA + 2744, 64) == b'\xa6' * 64
        assert b'-2147483648' in text
        for row in range(9):
            r.w(ARENA + 3000, b'\xa6' * 128)
            r.call('format_row', (ARENA + 3000, row, ARENA))
            text_row = r.r(ARENA + 3000, 128).split(b'\x00')[0]
            assert len(text_row) < 64 and r.r(ARENA + 3064, 64) == b'\xa6' * 64, (row, text_row)
        print('PASS maximum-width summary and all menu rows preserve sentinels', flush=True)

    (H / 'evidence/validation.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print('ALL P16 COMPILED PPC LOGGER VALIDATIONS PASSED', flush=True)


if __name__ == '__main__': run()
