"""Offline PPC proof: virtual read errors/short counts survive Cobra's epilogue.

Execute the real patched call site, entry shim, compiled s1_read and stock
epilogue. Only the physical sector-provider/native UFS boundaries are modeled;
this does not establish that the drive delivers sectors.
"""
from pathlib import Path
import hashlib
import json
import struct

# Shared JVM setup only. validate_stat has no execution outside its main guard.
import validate_stat as base

H, ROOT, OUT = base.H, base.ROOT, base.OUT
SP, STOP, DEST, EA = base.SP, base.STOP, 0x80022000, 0x84000000
REQUESTED = 2048
SAVED = (0x123456789ABCDEF0, 0x23456789ABCDEF01,
         0x3456789ABCDEF012, 0x456789ABCDEF0123)


def execute(program, symbols, mode, *, direct=False, sector_local_entry=0):
    space = program.getAddressFactory().getDefaultAddressSpace()
    em = base.EmulatorHelper(program)
    em.enableMemoryWriteTracking(True)
    def write(address, data):
        em.writeMemory(space.getAddress(address), data)
    def read(address, size):
        return bytes(em.readMemoryByte(space.getAddress(address + i)) & 255 for i in range(size))
    def reg(name, value=None):
        if value is None:
            return int(str(em.readRegister(name))) & base.MASK
        em.writeRegister(name, base.BigInteger(str(value & base.MASK)))
    def pc(value):
        em.writeRegister(em.getPCRegister(), base.BigInteger(str(value)))
    fd, offset = (7, 123) if mode == 'native_error' else (0xBD00, 0)
    flags = 0 if mode == 'virtual_error' else 1
    size = 13 if mode == 'short' else 0
    sector = bytes(i % 251 for i in range(2048))
    calls = []
    try:
        write(SP - 0x2000, bytes(0x2200))
        write(SP + 0x28, struct.pack('>Q', 0x751280))
        for index, value in enumerate(SAVED):
            write(SP + 0x70 + 8 * index, struct.pack('>Q', value))
        write(SP + 0xA0, struct.pack('>Q', STOP))
        write(DEST - 32, b'\x6d' * 32 + b'\xa5' * REQUESTED + b'\x7e' * 32)
        write(0x930F20, bytes(96))
        write(0x930F24, struct.pack('>I', flags))
        write(0x930F30, struct.pack('>Q', size))
        write(0x930F50, struct.pack('>Q', EA))
        write(EA + 0x1000, sector)
        for name, value in [('r1', SP), ('r2', 0x751280), ('r3', fd), ('r4', offset),
                            ('r5', DEST), ('r6', REQUESTED), ('r30', REQUESTED),
                            ('r31', DEST), ('LR', STOP)]:
            reg(name, value)
        pc(symbols['entry_read'] if direct else 0x3CFC)
        monitor = base.TimeoutTaskMonitor.timeoutIn(15, base.TimeUnit.SECONDS)
        for steps in range(30000):
            current = em.getExecutionAddress().getOffset()
            if current == STOP:
                break
            if current == 0x1ED5CC:
                calls.append(('native', tuple(reg(f'r{i}') for i in range(3, 7))))
                reg('r3', -19)
                pc(reg('LR'))
                continue
            if current in (symbols['read_atapi_sectors'], symbols['read_atapi_sectors'] + sector_local_entry):
                assert mode == 'short', 'Unexpected optical-provider call'
                calls.append(('sector_fixture', (reg('r3'), reg('r4'))))
                reg('r3', 0)
                pc(reg('LR'))
                continue
            if not em.step(monitor):
                raise AssertionError(f'PPC step failed at {current:#x}: {em.getLastError()}')
        else:
            raise AssertionError('Read-return PPC execution exceeded bound')
        assert read(DEST - 32, 32) == b'\x6d' * 32
        assert read(DEST + REQUESTED, 32) == b'\x7e' * 32
        if mode == 'short':
            assert read(DEST, REQUESTED) == sector[:13] + b'\xa5' * (REQUESTED - 13)
            assert calls == [('sector_fixture', (0, 1))]
        else:
            assert read(DEST, REQUESTED) == b'\xa5' * REQUESTED
        if mode == 'native_error':
            assert calls == [('native', (7, 123, DEST, REQUESTED))]
        elif mode != 'short':
            assert not calls
        assert reg('r2') == 0x751280
        assert reg('r1') == SP + (0 if direct else 0x90)
        if direct:
            assert reg('r30') == REQUESTED, 'Unexpected caller must retain callee-saved r30'
        else:
            assert tuple(reg(f'r{i}') for i in range(28, 32)) == SAVED
        for span in em.getTrackedMemoryWriteSet().getAddressRanges():
            if span.getMinAddress().getAddressSpace() != space:
                continue  # Ghidra's unique temporaries are not guest RAM stores.
            lo, hi = span.getMinAddress().getOffset(), span.getMaxAddress().getOffset() + 1
            assert ((SP - 0x2000 <= lo < hi <= SP + 0x100) or
                    (0x930F20 <= lo < hi <= 0x930F80) or
                    (DEST <= lo < hi <= DEST + REQUESTED)), (str(span.getMinAddress().getAddressSpace()), hex(lo), hex(hi), reg('r3'))
        return dict(result=reg('r3'), steps=steps)
    finally:
        em.dispose()


def validate(elf, table, name, *, baseline=False):
    symbols = json.loads(table.read_text())['symbols']
    from elftools.elf.elffile import ELFFile
    with (table.parent.parent / 'build/payload_disc.elf').open('rb') as stream:
        payload = ELFFile(stream)
        symbol = payload.get_section_by_name('.symtab').get_symbol_by_name('read_atapi_sectors')[0]
        assert symbol['st_value'] == symbols['read_atapi_sectors']
        # ELFv2 st_other upper field encodes the local entry as 0/0/4/8/16/...
        local_entry = (1 << symbol['st_other']['local']) & ~3
    with base.pyghidra.open_program(str(elf), project_location=str(OUT / 'projects'),
                                   project_name=name, analyze=False,
                                   language='PowerPC:BE:64:default') as flat:
        results = {}
        for mode, wanted in [('virtual_error', base.MASK), ('eof', 0),
                             ('short', 13), ('native_error', REQUESTED)]:
            result = execute(flat.getCurrentProgram(), symbols, mode, sector_local_entry=local_entry)
            assert result['result'] == (REQUESTED if baseline else wanted), (mode, result)
            results[mode] = result
            print(('BASELINE' if baseline else 'PASS') + f' actual PPC {mode}: {result["result"]:#x}', flush=True)
        direct = execute(flat.getCurrentProgram(), symbols, 'virtual_error', direct=True)
        assert direct['result'] & 0xFFFFFFFF == 0xFFFFFFFF
        results['unexpected_caller_preserves_r30'] = True
    return dict(elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(), cases=results,
                scope='Read return/ABI only; optical sector delivery is a modeled boundary')


if __name__ == '__main__':
    current = validate(ROOT / 'local_only/disc/ps2_netemu_disc.elf',
                       H / 'evidence/disc_patch_table.json', 'read_return_current')
    prior = ROOT / 'local_only/backups/disc_before_read_return_20261122'
    baseline = validate(prior / 'disc/ps2_netemu_disc.elf',
                        prior / 'evidence/disc_patch_table.json', 'read_return_baseline', baseline=True)
    (H / 'evidence/read_return_validation.json').write_text(
        json.dumps(dict(current=current, baseline=baseline), indent=2) + '\n')
    print('READ RETURN SHIM VALIDATED OFFLINE; NO CONSOLE INSTALLATION', flush=True)
