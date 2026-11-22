"""Fail-closed audit for this tiny fixed-address payload, not a generic auditor.

No pointer arguments are accepted as store destinations. Optimized C stores
must resolve to literal fixed addresses; assembly stack stores are enumerated
separately in trampolines.json and compiler assembly for review.
"""
from pathlib import Path
import json
import re
import llvmlite.binding as llvm

def audit(path):
    path = Path(path)
    module = llvm.parse_assembly(path.read_text())
    module.verify()
    assert not list(module.global_variables), 'No globals permitted, even constants'
    stores, calls = [], []
    for f in module.functions:
        for b in f.blocks:
            for inst in b.instructions:
                ops = list(inst.operands)
                if inst.opcode == 'store':
                    value, dst = ops
                    match = re.fullmatch(r'ptr inttoptr \(i64 (\d+) to ptr\)', str(dst))
                    assert match, ('Nonliteral store destination', str(inst))
                    address = int(match[1])
                    assert re.fullmatch(r'i(?:8|32|64)', str(value.type)), str(inst)
                    width = int(str(value.type)[1:])//8
                    assert (0x930f20 <= address < address+width <= 0x930f80 or
                            (address == 0x934161 and width == 1)), str(inst)
                    stores.append(dict(function=f.name, address=hex(address), width=width,
                                       ir=str(inst).strip()))
                elif inst.opcode in ['atomicrmw', 'cmpxchg', 'alloca', 'invoke', 'callbr']:
                    raise AssertionError(('Unexpected instruction', str(inst)))
                elif inst.opcode == 'call':
                    callee = ops[-1]
                    if callee.name:
                        assert callee.name in ['native_refresh', 'native_clock', 'ui_reason_ok', 'hdd_idle', 'llvm.umin.i64'], str(inst)
                        calls.append(callee.name)
                    else:
                        raise AssertionError(('Inline asm/indirect call forbidden', str(inst)))
                elif inst.opcode == 'fence':
                    assert str(inst).strip() == 'fence seq_cst', str(inst)
    assert stores and 'native_refresh' in calls and 'native_clock' in calls
    report = dict(status='PASS', stores=stores, callees=sorted(set(calls)),
                  scope='Every optimized IR store has an exact literal destination; no mutable globals; assembly stack stores reviewed separately. Native refresh/clock bodies excluded.')
    path.with_name('ir_store_audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

def audit_assembly(path, trampolines):
    """Check backend-introduced spills too, without any disassembler or JVM.

    r28 is the literal mailbox+32, established once before the first native
    call; its only other definition is the epilogue restore. Native helpers
    preserve it by the existing native ABI. The validator tests that model.
    """
    path = Path(path)
    lines = path.read_text().splitlines()
    instructions = [line.strip() for line in lines if line.startswith('\t') and
                    not line.strip().startswith('.')]
    compact = [re.sub(r'\s+', '', line) for line in instructions]
    assert compact.count('lis11,147') == 1
    assert compact.count('ori28,11,3904') == 1  # 0x930f40
    for text in compact:
        if re.match(r'[a-z]+28,', text) and not text.startswith(('std28,', 'stb28,')):
            assert text in ['ori28,11,3904', 'ld28,-32(1)'], ('r28 definition', text)
    stores = []
    for number, line in enumerate(lines, 1):
        text = line.strip()
        if not re.match(r'st\w+\s', text):
            continue
        match = re.fullmatch(r'(std|stdu|stb)\s+(\d+),\s*(-?\d+)\((\d+)\)', text)
        assert match, ('unreviewed store form', text)
        op, rt, disp, ra = match[1], int(match[2]), int(match[3]), int(match[4])
        if ra == 1:
            assert ((op == 'std' and (disp in [-56, -48, -40, -32, -24, -16, 112])) or
                    (op == 'stdu' and rt == 1 and disp == -96)), text
            target = 'stack spill/backchain/LR'
        else:
            assert ra == 28, text
            address = 0x930f40+disp
            width = 1 if op == 'stb' else 8
            assert op != 'stdu'
            assert (0x930f20 <= address < address+width <= 0x930f80 or
                    address == 0x934161 and width == 1), text
            target = hex(address)
        stores.append(dict(line=number, assembly=text, destination=target))
    for row in trampolines:
        if row['op'].startswith('st'):
            assert (row['op'], row['args'][0], row['args'][1]) in [
                ('std', 'r0', '16(r1)'), ('std', 'r2', '120(r1)'),
                ('stdu', 'r1', '-128(r1)'), ('stdu', 'r1', '-320(r1)')], row
    report = dict(status='PASS', compiler_stores=stores,
                  trampoline_stores=[r for r in trampolines if r['op'].startswith('st')],
                  scope='Generated LLVM assembly and hand-encoded trampoline stores; native stock bodies excluded; PPC execution still NOT RUN.')
    path.with_name('assembly_store_audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report

if __name__ == '__main__':
    audit(Path(__file__).resolve().parents[2]/'local_only/autoreturn/payload.ll')
