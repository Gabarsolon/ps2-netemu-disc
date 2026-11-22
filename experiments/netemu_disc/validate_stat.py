"""Execute the compiled PPC stat hook offline, with the native 48-byte buffer.

This proves only stat buffer bounds/delegation. It does not validate optical
access or authorize installing this unfinished backend on the console.
"""
from pathlib import Path
import hashlib
import json
import os
import struct
import sys

H = Path(__file__).resolve().parent
ROOT = H.parent.parent
OUT = ROOT / 'local_only' / 'disc_stat_validation'
for name in ('tmp', 'settings', 'projects'):
    (OUT / name).mkdir(parents=True, exist_ok=True)
for name in ('TEMP', 'TMP', 'TMPDIR', 'APPDATA', 'LOCALAPPDATA'):
    os.environ[name] = str(OUT / ('tmp' if name in ('TEMP', 'TMP', 'TMPDIR') else 'settings'))
os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot'
os.environ['GHIDRA_INSTALL_DIR'] = r'C:\ghidra_12.1.3_PUBLIC'
sys.path = [p for p in sys.path if Path(p or '.').resolve().name.lower() != 'local_only']

import pyghidra
from pyghidra.launcher import HeadlessPyGhidraLauncher
launcher = HeadlessPyGhidraLauncher()
launcher.java_home = os.environ['JAVA_HOME']
launcher.add_vmargs('-Xmx3G', '-Duser.home=' + str(OUT / 'settings'),
                    '-Dapplication.settingsdir=' + str(OUT / 'settings'),
                    '-Djava.io.tmpdir=' + str(OUT / 'tmp'))
launcher.start()
from ghidra.app.emulator import EmulatorHelper
from ghidra.util.task import TimeoutTaskMonitor
from java.math import BigInteger
from java.util.concurrent import TimeUnit

MASK = (1 << 64) - 1
SP, STOP, BUFFER = 0xAAA700BFE00, 0x7FF0, 0xAAA700BFE78
DISC_SIZE = 0x1234567800


def execute(program, entry, fd, pointer):
    space = program.getAddressFactory().getDefaultAddressSpace()
    em = EmulatorHelper(program)
    def write(address, data):
        em.writeMemory(space.getAddress(address), data)
    def read(address, size):
        return bytes(em.readMemoryByte(space.getAddress(address + i)) & 255 for i in range(size))
    def reg(name, value=None):
        if value is None:
            return int(str(em.readRegister(name))) & MASK
        em.writeRegister(name, BigInteger(str(value & MASK)))
    try:
        write(BUFFER - 16, b'\x6d' * 16 + b'\xa5' * 48 + b'\x7e' * 64)
        write(0x930F20, bytes(96))
        write(0x930F30, struct.pack('>Q', DISC_SIZE))
        write(0x3174C88, b'\x3c' * 8)
        reg('r1', SP)
        reg('r2', 0x751280)
        reg('r3', fd)
        reg('r4', pointer)
        reg('LR', STOP)
        em.writeRegister(em.getPCRegister(), BigInteger(str(entry)))
        monitor = TimeoutTaskMonitor.timeoutIn(10, TimeUnit.SECONDS)
        calls = []
        for steps in range(10000):
            pc = em.getExecutionAddress().getOffset()
            if pc == STOP:
                break
            if pc == 0x39B0:
                calls.append((reg('r3'), reg('r4'), reg('r2')))
                reg('r3', MASK - 18)  # Model a native Cobra error return (-19).
                em.writeRegister(em.getPCRegister(), BigInteger(str(reg('LR'))))
                continue
            if not em.step(monitor):
                raise AssertionError(f'PPC step failed at {pc:#x}: {em.getLastError()}')
        else:
            raise AssertionError('Stat PPC execution exceeded instruction bound')
        return dict(result=reg('r3'), buffer=read(BUFFER, 48),
                    before=read(BUFFER - 16, 16), after=read(BUFFER + 48, 64),
                    global_size=read(0x3174C88, 8), calls=calls, steps=steps)
    finally:
        em.dispose()


def validate(elf, table, name, baseline=False):
    symbols = json.loads(table.read_text())['symbols']
    with pyghidra.open_program(str(elf), project_location=str(OUT / 'projects'),
                              project_name=name, analyze=False,
                              language='PowerPC:BE:64:default') as flat:
        program = flat.getCurrentProgram()
        valid = execute(program, symbols['entry_stat'], 0xBD00, BUFFER)
        expected = bytearray(48)
        struct.pack_into('>I', expected, 0, 0o100444)
        struct.pack_into('>Q', expected, 40, DISC_SIZE)
        fence_ok = valid['before'] == b'\x6d' * 16 and valid['after'] == b'\x7e' * 64
        if baseline:
            print('BASELINE caller fence preserved:', fence_ok, flush=True)
            return dict(elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
                        caller_fence_preserved=fence_ok,
                        bytes_after_buffer=valid['after'].hex())
        assert fence_ok, 'Native caller saved-register fence was overwritten'
        assert valid['result'] == 0 and valid['buffer'] == expected and not valid['calls']
        assert valid['global_size'] == struct.pack('>Q', DISC_SIZE)
        print('PASS actual PPC: 48-byte native stat, size/mode and caller fences', flush=True)
        for pointer in (0, 0x7FFFFF):
            rejected = execute(program, symbols['entry_stat'], 0xBD00, pointer)
            assert rejected['result'] & 0xFFFFFFFF == 0xFFFFFFFF
            assert rejected['buffer'] == b'\xa5' * 48 and not rejected['calls']
            assert rejected['before'] == b'\x6d' * 16 and rejected['after'] == b'\x7e' * 64
            assert rejected['global_size'] == b'\x3c' * 8
        print('PASS actual PPC: null/below-range rejection leaves fixtures unchanged', flush=True)
        delegated = execute(program, symbols['entry_stat'], 7, BUFFER)
        assert delegated['result'] & 0xFFFFFFFF == (-19 & 0xFFFFFFFF)
        assert delegated['calls'] == [(7, BUFFER, 0x751280)]
        assert delegated['buffer'] == b'\xa5' * 48
        assert delegated['before'] == b'\x6d' * 16 and delegated['after'] == b'\x7e' * 64
        print('PASS actual PPC: nonvirtual fd preserves Cobra arguments, TOC and error', flush=True)
        return dict(elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
                    caller_fence_preserved=True, cases_passed=4,
                    scope='Stat hook only; optical backend remains unvalidated')


if __name__ == '__main__':
    evidence = {'current': validate(ROOT / 'local_only/disc/ps2_netemu_disc.elf',
                                   H / 'evidence/disc_patch_table.json', 'stat_current')}
    prior = ROOT / 'local_only/backups/disc_before_stat_build_20261122'
    if prior.is_dir():
        evidence['baseline'] = validate(prior / 'disc/ps2_netemu_disc.elf',
                                        prior / 'evidence/disc_patch_table.json', 'stat_baseline', baseline=True)
    (H / 'evidence/stat_validation.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print('STAT HOOK VALIDATED OFFLINE; NO CONSOLE INSTALLATION', flush=True)
