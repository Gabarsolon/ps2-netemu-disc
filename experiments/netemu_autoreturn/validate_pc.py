"""PARENT ONLY: execute final PPC entry/C with Ghidra; do not run with busy JVM.

No console, device, subprocess, network, or existing harness access. Native
refresh at BC16C and clock at B9CD0 are explicit modeled boundaries. This
cannot establish periodic scheduling, concurrency, or reason-only return.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT/'local_only/autoreturn'
MAIL, REASON, SP, STOP = 0x930f20, 0x934161, 0x3100000, 0x7ff0
MASK, MAGIC, DELAY = (1 << 64)-1, 0x4155544f52544e31, 20*79800000
HDD = [(0x241c8d5, 1, 1), (0x241c8c8, 1, 0), (0x241c860, 8, 3),
       (0x241c888, 8, 0), (0x241c890, 8, 0), (0x241c898, 8, 0),
       (0x3055180, 4, 0)]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-jvm', action='store_true', required=True,
                        help='Parent confirms the sole JVM is available')
    parser.parse_args()
    review = json.loads((OUT/'build_review.json').read_text())
    elfpath = OUT/'ps2_netemu_autoreturn.elf'
    data = elfpath.read_bytes()
    assert hashlib.sha256(data).hexdigest() == review['elf_sha256']
    assert hashlib.sha256((HERE/'src/autoreturn.c').read_bytes()).hexdigest() == review['source_sha256']
    work = OUT/'pc'
    for name in ['tmp', 'settings', 'projects']:
        (work/name).mkdir(parents=True, exist_ok=True)
    for name in ['TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA']:
        os.environ[name] = str(work/('tmp' if name in ['TEMP', 'TMP', 'TMPDIR'] else 'settings'))
    os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
    os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'
    import pyghidra
    from pyghidra.launcher import HeadlessPyGhidraLauncher
    launcher = HeadlessPyGhidraLauncher()
    launcher.java_home = os.environ['JAVA_HOME']
    launcher.add_vmargs('-Xmx3G', '-Duser.home='+str(work/'settings'),
                       '-Dapplication.settingsdir='+str(work/'settings'),
                       '-Djava.io.tmpdir='+str(work/'tmp'))
    launcher.start()
    from ghidra.app.emulator import EmulatorHelper
    from ghidra.util.task import ConsoleTaskMonitor
    from java.math import BigInteger
    from elftools.elf.elffile import ELFFile
    with (OUT/'payload.elf').open('rb') as f:
        payload = ELFFile(f)
        sec = payload.get_section_by_name('.text')
        c_lo, c_hi = sec['sh_addr'], sec['sh_addr']+sec['sh_size']
    results = []
    with pyghidra.open_program(str(elfpath), project_location=str(work/'projects'),
                              project_name='autoreturn_'+review['elf_sha256'][:12],
                              analyze=False, language='PowerPC:BE:64:default') as flat:
        program = flat.getCurrentProgram()
        space = program.getAddressFactory().getDefaultAddressSpace()

        class Machine:
            def __init__(self):
                self.em = EmulatorHelper(program)
                self.monitor = ConsoleTaskMonitor()
                self.now = 1000
                self.refreshes = self.clocks = self.reason_stores = self.calls = 0
                self.barriers = 0
                self.ranges = set()
                self.clock_effect = None
                self.w(MAIL, bytes(96))
                self.fixture(REASON, 0, 1)
                self.fixture(0x306fc68, 0x30700d0, 8)
                self.fixture(0x30700d0, 0x949cb8, 8)
                for address, width, value in HDD:
                    self.fixture(address, value, width)
                self.em.enableMemoryWriteTracking(True)

            def put(self, reg, value):
                self.em.writeRegister(reg, BigInteger(str(value & MASK)))

            def get(self, reg):
                return int(str(self.em.readRegister(reg))) & MASK

            def pc(self, address):
                self.put(self.em.getPCRegister(), address)

            def rd(self, address, size):
                return bytes(self.em.readMemory(space.getAddress(address), size))

            def w(self, address, data):
                self.em.writeMemory(space.getAddress(address), data)

            def fixture(self, address, value, width=8):
                # Fixture stores are not code under test. Do not count them.
                self.em.enableMemoryWriteTracking(False)
                self.w(address, value.to_bytes(width, 'big'))
                self.em.enableMemoryWriteTracking(True)

            def state(self):
                return struct.unpack('>12Q', self.rd(MAIL, 96))

            def active(self, count=99, start=1000, last=1000):
                for i, value in enumerate([MAGIC, start, last, count, 1]+[0]*7):
                    self.fixture(MAIL+8*i, value)

            def allowed_store(self, lo, hi):
                return (MAIL <= lo < hi <= MAIL+96 or
                        (lo == REASON and hi == REASON+1) or
                        SP-0x1000 <= lo < hi <= SP+0x20)

            def audit_store_instruction(self, pc, word):
                op = word >> 26
                if op not in [36, 37, 38, 39, 44, 45, 47, 62]:
                    # No FP/vector/atomic stores should exist in this build.
                    assert op not in [52, 53, 54, 55], ('FP store', hex(pc))
                    if op == 31:
                        assert (word >> 1 & 1023) not in [149, 150, 151, 181, 183, 214, 215, 231, 247, 407, 439, 487, 663, 695, 727, 759], ('indexed/atomic store', hex(pc))
                    return
                assert op in [38, 62], ('unexpected store form', hex(pc), hex(word))
                rt, ra = word >> 21 & 31, word >> 16 & 31
                width = 1 if op == 38 else 8
                disp = word & (0xffff if op == 38 else 0xfffc)
                if disp & 0x8000:
                    disp -= 0x10000
                address = ((self.get('r'+str(ra)) if ra else 0)+disp) & MASK
                assert self.allowed_store(address, address+width), ('bad RAM store', hex(pc), hex(address), width)
                self.ranges.add((address, address+width))
                if address == REASON:
                    assert width == 1 and self.get('r'+str(rt)) & 255 == 2
                    assert self.state()[4] == 2, 'requested marker must precede reason store'
                    assert self.rd(REASON, 1) == b'\0', 'do not overwrite existing reason'
                    self.reason_stores += 1

            def model_return(self, value):
                target = self.get('lr')
                # Aggressive ABI-legal volatile clobbers expose wrapper errors.
                for r in [0, *range(3, 13)]:
                    self.put('r'+str(r), 0xdad0000000000000+r)
                for r in [0, 1, 5, 6, 7]:
                    self.put('cr'+str(r), 15-r)
                self.put('ctr', 0x12345678)
                self.put('xer', 0)
                self.put('r3', value)
                self.pc(target)

            def call(self):
                args = [((0x8123456789abcdef*(i+1)) ^ (self.calls << (i+1))) & MASK for i in range(8)]
                expected = (0xfedcba9876543210 ^ self.calls) & MASK
                preserved = {**{'r'+str(r): 0xabcd000000000000+r for r in range(13, 32)},
                             **{'cr'+str(r): r+2 for r in [2, 3, 4]}}
                self.calls += 1
                for reg, value in preserved.items():
                    self.put(reg, value)
                self.put('r1', SP)
                # Deliberately non-native incoming TOC tests restoration.
                incoming_toc = 0x751280 if self.calls & 1 else 0x123456780000
                self.put('r2', incoming_toc)
                self.put('lr', STOP)
                for i, value in enumerate(args, 3):
                    self.put('r'+str(i), value)
                self.pc(0xbc168)  # execute the actual installed branch
                refreshes, clocks = self.refreshes, self.clocks
                initial_mail, initial_reason = self.rd(MAIL, 96), self.rd(REASON, 1)
                relocation_sp = None
                for _ in range(2500):
                    pc = self.em.getExecutionAddress().getOffset() & MASK
                    if pc == STOP:
                        break
                    if pc == 0xbc16c:
                        assert relocation_sp is not None
                        assert self.get('r1') == relocation_sp-320
                        assert int.from_bytes(self.rd(relocation_sp-320, 8), 'big') == relocation_sp
                        assert self.get('r2') == 0x751280
                        assert [self.get('r'+str(i)) for i in range(3, 11)] == args
                        assert self.rd(MAIL, 96) == initial_mail and self.rd(REASON, 1) == initial_reason
                        assert self.clocks == clocks, 'native refresh must be first'
                        self.refreshes += 1
                        # Model the untouched native body's epilogue and result.
                        self.put('r1', relocation_sp)
                        self.model_return(expected)
                        continue
                    if pc == 0xb9cd0:
                        assert self.refreshes == refreshes+1
                        assert self.get('r2') == 0x751280
                        self.clocks += 1
                        if self.clock_effect:
                            self.clock_effect(self)
                        self.model_return(self.now)
                        continue
                    assert pc == 0xbc168 or 0x4800 <= pc < 0x48c8 or c_lo <= pc < c_hi, ('unexpected execution', hex(pc))
                    if pc == 0x48c0:
                        relocation_sp = self.get('r1')
                    word = int.from_bytes(self.rd(pc, 4), 'big')
                    assert word >> 26 != 17, ('syscall forbidden', hex(pc))
                    self.audit_store_instruction(pc, word)
                    if word in [0x7c0004ac, 0x7c2004ac, 0x4c00012c]:
                        # Ghidra classic sync userop is not implemented. Only
                        # ISA ordering is modeled; no scheduling/concurrency.
                        self.barriers += 1
                        self.pc(pc+4)
                    else:
                        assert self.em.step(self.monitor), (hex(pc), str(self.em.getLastError()))
                else:
                    raise AssertionError('bounded instruction budget exhausted')
                assert self.refreshes == refreshes+1, 'exactly one native refresh'
                assert self.get('r3') == expected, 'native return changed'
                assert self.get('r1') == SP and self.get('r2') == incoming_toc
                assert self.get('lr') == STOP
                assert all(self.get(reg) == value for reg, value in preserved.items()), 'callee-saved ABI'
                for item in self.em.getTrackedMemoryWriteSet().getAddressRanges():
                    if item.getMinAddress().getAddressSpace() == space:
                        lo = item.getMinAddress().getOffset() & MASK
                        hi = (item.getMaxAddress().getOffset() & MASK)+1
                        assert self.allowed_store(lo, hi), ('tracked RAM store', hex(lo), hex(hi))
                return self.state()

            def close(self):
                self.em.dispose()

        def case(name, fn):
            m = Machine()
            try:
                fn(m)
                results.append(dict(case=name, status='PASS', callbacks=m.calls,
                                    native_refreshes=m.refreshes, clocks=m.clocks,
                                    reason_stores=m.reason_stores, modeled_barriers=m.barriers,
                                    RAM_stores=[[hex(a), hex(b)] for a, b in sorted(m.ranges)]))
            finally:
                m.close()

        def pristine(m):
            assert m.call() == (0,)*12 and m.reason_stores == 0

        # No controller fixture is present. Native refresh itself is modeled;
        # this says nothing about controller-free scheduling on hardware.
        for address, width, good in HDD:
            for bad in ([0, 2] if good == 1 else [1, MASK if width == 8 else 255]):
                def invalid_initial(m, a=address, w=width, v=bad):
                    m.fixture(a, v, w)
                    pristine(m)
                case(f'unarmed HDD guard {address:x}={bad}', invalid_initial)
        for address, width, bad in [(REASON, 1, 1), (REASON, 1, 2), (REASON, 1, 255),
                                    (0x306fc68, 8, 0), (0x306fc68, 8, MASK),
                                    (0x30700d0, 8, 0), (0x30700d0, 8, 0x949cb0)]:
            def invalid_initial(m, a=address, w=width, v=bad):
                m.fixture(a, v, w)
                pristine(m)
            case(f'unarmed UI/reason guard {address:x}={bad}', invalid_initial)
        for word in range(12):
            def corrupt_zero(m, word=word):
                m.fixture(MAIL+word*8, 1)
                before = m.state()
                assert m.call() == before and m.reason_stores == 0
            case(f'foreign/partial zero mailbox word {word}', corrupt_zero)
        def zero_clock(m):
            m.now = 0
            pristine(m)
        case('zero clock never arms', zero_clock)
        def late_arm(m):
            m.now = 100*DELAY
            state = m.call()
            assert state[:5] == (MAGIC, m.now, m.now, 0, 1)
            assert m.reason_stores == 0
        case('delay starts at guarded initialization, not boot', late_arm)
        def timer(m):
            assert m.call()[:5] == (MAGIC, 1000, 1000, 0, 1)
            m.now = 1000+DELAY-1
            for _ in range(100):
                m.call()
                assert m.reason_stores == 0
            assert m.state()[3] == 100
            m.now += 1
            assert m.call()[4] == 2 and m.reason_stores == 1
            m.fixture(REASON, 0, 1)  # cannot re-request even if reason clears
            before = m.state()
            for _ in range(3):
                assert m.call() == before and m.reason_stores == 1
        case('20s threshold, saturated callbacks, one shot', timer)
        def count_gate(m):
            m.call()
            m.now = 1000+DELAY
            for i in range(1, 100):
                assert m.call()[3] == i and m.reason_stores == 0
            assert m.call()[4] == 2 and m.reason_stores == 1
        case('elapsed 20s still requires 100 subsequent callbacks', count_gate)
        for address, width, good in HDD:
            def active_busy(m, a=address, w=width, v=good):
                m.active()
                m.now = 1000+DELAY
                m.fixture(a, 0 if v else 1, w)
                assert m.call()[4] == 1 and m.reason_stores == 0
                m.fixture(a, v, w)
                assert m.call()[4] == 2 and m.reason_stores == 1
            case(f'active HDD busy defers then retries {address:x}', active_busy)
        for address, width, bad in [(REASON, 1, 1), (0x306fc68, 8, 0), (0x30700d0, 8, 0)]:
            def active_bad(m, a=address, w=width, v=bad):
                m.active()
                m.now = 1000+DELAY
                m.fixture(a, v, w)
                assert m.call()[4] == 3 and m.reason_stores == 0
            case(f'active UI/reason invalid disarms {address:x}', active_bad)
        for address, width, bad in [(REASON, 1, 1), (0x306fc68, 8, 0),
                                    (0x30700d0, 8, 0), *[(a, w, 0 if v else 1) for a, w, v in HDD],
                                    (MAIL, 8, 7), (MAIL+32, 8, 2)]:
            def recheck(m, a=address, w=width, v=bad):
                m.active()
                m.now = 1000+DELAY
                m.clock_effect = lambda obj: obj.fixture(a, v, w)
                m.call()
                assert m.reason_stores == 0
            case(f'post-clock final guard recheck {address:x}', recheck)
        for word, bad in [(0, 9), (1, 0), (2, 999), (3, 101), (4, 0), (4, 2), (4, 3), (4, 99),
                          *[(w, 1) for w in range(5, 12)]]:
            def stale(m, word=word, bad=bad):
                m.active()
                m.fixture(MAIL+word*8, bad)
                before = m.state()
                m.now = 1000+DELAY
                assert m.call() == before and m.reason_stores == 0
            case(f'stale/invalid armed mailbox word {word}={bad}', stale)
        def backwards(m):
            m.active()
            m.now = 999
            assert m.call()[4] == 3 and m.reason_stores == 0
        case('backwards clock disarms', backwards)
        def wrap(m):
            m.active(start=MASK-10, last=MASK-5)
            m.now = 5
            assert m.call()[4] == 3 and m.reason_stores == 0
        case('clock wrap disarms instead of early request', wrap)
    report = dict(status='PASS', elf_sha256=review['elf_sha256'], cases=results,
                  modeled=['native BC168 body after relocated prologue', 'native clock return',
                           'synthetic UI/HDD/mailbox fixtures', 'sync ordering without concurrency'],
                  executed='Final BC168 branch, ELFv2 trampolines, relocated stdu, compiled C, guards and stores',
                  unproven=['periodic callback with no controller', 'real native refresh side effects',
                            'native serialization/concurrency', 'UI setup omission safety',
                            'reason2 worker observation, complete cleanup, GameOS/XMB return'])
    (OUT/'pc_validation_results.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS:', len(results), 'offline modeled cases; no hardware claim')

if __name__ == '__main__':
    main()
