"""Inspect P0G ELF evidence without network access or additional JVMs."""
from pathlib import Path
import argparse
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0g'
ap = argparse.ArgumentParser()
ap.add_argument('variant')
ap.add_argument('--range', nargs=2)
ap.add_argument('--calls', nargs='*')
ap.add_argument('--data', nargs=2)
ap.add_argument('--strings', nargs='*')
ap.add_argument('--refs', nargs='*')
ap.add_argument('--decomp', nargs='*')
a = ap.parse_args()
elf = ROOT / 'local_only' / ('stock.elf' if a.variant == 'netemu' else 'fw355/out/' + a.variant + '.elf')
b = elf.read_bytes()
segs = [struct.unpack_from('>IIQQQQQQ', b, struct.unpack_from('>Q', b, 32)[0] + 56*i) for i in range(struct.unpack_from('>H', b, 56)[0])]
def read(n, size):
    for typ, flags, off, va, pa, sz, ms, al in segs:
        if typ == 1 and va <= n and n + size <= va + sz:
            return b[off+n-va:off+n-va+size]
    raise ValueError(hex(n))
toc = int(json.loads((BASE/a.variant/'manifest.json').read_text())['toc'], 16)
if a.variant == 'vsh': toc = 0x6f7370
lines = {}
for p in [BASE/a.variant/'text.asm', *sorted((BASE/a.variant).glob('range_*.asm'))]:
    if not p.exists(): continue
    for line in p.read_text().splitlines():
        m = re.match(r'([0-9a-f]+): (.*)', line)
        if m: lines[int(m[1],16)] = m[2]
if a.range:
    lo, hi = [int(x,16) for x in a.range]
    for n in sorted(lines):
        if not lo <= n < hi: continue
        ins, extra = lines[n], ''
        m = re.search(r'ld r\d+,(-?0x[0-9a-f]+)\(r2\)', ins)
        if m:
            try:
                v = int.from_bytes(read(toc+int(m[1],16),8), 'big')
                extra = f' ; TOC={v:#x}'
                s = read(v,128).split(bytes([0]))[0]
                if s and all(32 <= c < 127 for c in s): extra += ' ' + repr(s)
            except ValueError: pass
        print(f'{n:08x}: {ins}{extra}')
if a.calls is not None:
    targets = {int(x,16) for x in a.calls}
    for typ, flags, off, va, pa, sz, ms, al in segs:
        if typ != 1 or not flags & 1: continue
        for p in range(off,off+sz-3,4):
            w = struct.unpack_from('>I',b,p)[0]
            if w >> 26 != 18: continue
            disp = w & 0x3fffffc
            if disp & 0x2000000: disp -= 0x4000000
            n = va+p-off
            dst = disp if w & 2 else n+disp
            if dst in targets: print(f'{n:08x}: {"bl" if w & 1 else "b"} {dst:#x}')
if a.data:
    n, size = int(a.data[0],16),int(a.data[1],0)
    for p in range(n,n+size,8):
        v = int.from_bytes(read(p,8),'big')
        try: s = repr(read(v,80).split(bytes([0]))[0])
        except ValueError: s = ''
        print(f'{p:08x}: {v:016x} {s}')
if a.strings is not None:
    for word in a.strings:
        needle = word.encode()
        for m in re.finditer(re.escape(needle),b):
            pos = m.start()
            for typ,fl,off,va,pa,sz,ms,al in segs:
                if typ == 1 and off <= pos < off+sz:
                    print(word, hex(va+pos-off), repr(b[max(off,pos-35):pos+120].split(bytes([0]))))
if a.refs is not None:
    for item in a.refs:
        n = int(item,16)
        needle = n.to_bytes(8,'big')
        print(item,[hex(va+m.start()-off) for m in re.finditer(re.escape(needle),b) for typ,fl,off,va,pa,sz,ms,al in segs if typ==1 and off <= m.start() < off+sz])
if a.decomp is not None:
    for item in a.decomp:
        p = BASE/a.variant/f'fn_{int(item,16):08x}.c'
        print('FUNCTION',item)
        print(chr(10).join(line for line in p.read_text().splitlines() if line.strip()) if p.exists() else 'MISSING')
