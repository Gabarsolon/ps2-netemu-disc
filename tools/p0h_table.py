"""Recover numbered HV registration stores by conservative constant propagation.

This is static evaluation of TOC loads / immediate arithmetic / pointer stores,
not execution of LV1. Keep initializer addresses for Ghidra instruction checks.
"""
from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
d = (ROOT / 'local_only/fw355/out/lv1.elf').read_bytes()
toc = 0x351198


def q(a):
    if 0x200000 <= a < 0x3ac5a8:
        return struct.unpack_from('>Q', d, a - 0x1e0000)[0]
    return 0


lo, hi = q(toc - 0x2820), q(toc - 0x2818)
records = {a + 8: {'number': q(a), 'registration': hex(a), 'stores': []}
           for a in range(lo, hi, 16)}
entries = sorted({r['entry'] for r in json.loads((BASE / 'descriptors.json').read_text())
                  if r['toc'] == toc and r['entry'] >= 0x200000})
for i, start in enumerate(entries[:-1]):
    stop = min(entries[i + 1], start + 0x4000)
    regs = {2: toc}
    for a in range(start, stop, 4):
        w = struct.unpack_from('>I', d, a - 0x1e0000)[0]
        op, rt, ra, rb = w >> 26, (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31
        imm = (w & 0xffff) - (0x10000 if w & 0x8000 else 0)
        if op == 58 and w & 3 == 0:
            if ra == 2:
                regs[rt] = q(toc + imm)
            else:
                regs.pop(rt, None)
        elif op == 62:
            base = regs.get(ra)
            value = regs.get(rt)
            if base is not None and value is not None and base + (imm & ~3) in records:
                row = records[base + (imm & ~3)]
                row['stores'].append({'initializer': hex(start), 'store': hex(a),
                                      'descriptor': hex(value), 'handler': hex(q(value & ~1)),
                                      'tag': value & 1})
        elif op in (14, 15):
            base = 0 if ra == 0 else regs.get(ra)
            if base is not None:
                regs[rt] = base + (imm << 16 if op == 15 else imm)
            else:
                regs.pop(rt, None)
        elif op in (24, 25):
            value = regs.get(rt)
            if value is None:
                regs.pop(ra, None)
            else:
                regs[ra] = value | ((w & 0xffff) << (16 if op == 25 else 0))
        elif op == 31 and (w >> 1) & 1023 == 444 and rt == rb:
            if rt in regs:
                regs[ra] = regs[rt]
            else:
                regs.pop(ra, None)
        elif op in (7, 8, 12, 13, 32, 34, 40, 42):
            regs.pop(rt, None)
        elif op in (20, 21, 23, 26, 27, 28, 29, 30, 31):
            regs.pop(ra, None)
rows = list(records.values())
(BASE / 'hvcall_registrations.json').write_text(json.dumps(rows, indent=2))
for row in rows:
    if row['number'] in (44, 91, 162, 163, 170, 171, 197, 245, 246, 248, 249, 255):
        print(row)
