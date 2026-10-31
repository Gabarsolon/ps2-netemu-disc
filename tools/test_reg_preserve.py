import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH = ROOT / 'local_only' / 'ghidra_p1g'
stock_elf = ROOT / 'local_only' / 'p1g' / 'ps2_netemu_p1g_G0.elf'

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

from ghidra.app.emulator import EmulatorHelper
from ghidra.util.task import TimeoutTaskMonitor
from java.math import BigInteger
from java.util.concurrent import TimeUnit

MASK = (1 << 64) - 1
SP = 0xaaa700bfe00
STOP = 0x7FF0
MAILBOX = 0x930F20

with pyghidra.open_program(str(stock_elf), project_location=str(GH / 'projects'),
                           project_name='test_reg_preserve', analyze=False,
                           language='PowerPC:BE:64:default') as flat:
    p = flat.getCurrentProgram()
    s = p.getAddressFactory().getDefaultAddressSpace()

    funcs = [
        ('Stock Helper', 0x111eb8, 0x111f10, 0x111f14),
        ('Generic Wrapper (lv1_hcall)', 0x4800, 0x4858, 0x485C)
    ]

    for fname, entry_addr, sc_addr, post_sc_pc in funcs:
        print(f"\nTesting {fname} (entry={hex(entry_addr)}, sc={hex(sc_addr)})...")
        em = EmulatorHelper(p)
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
