"""Read-only ELF/listing evidence checks; Sony-derived output stays local_only."""
from pathlib import Path
import argparse, hashlib, json, re, struct

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('variant', choices=['ps2_emu', 'ps2_gxemu', 'netemu'])
ap.add_argument('--range', nargs=2)
ap.add_argument('--verify', action='store_true')
ap.add_argument('--calls', nargs='*')
ap.add_argument('--data', nargs=2)
ap.add_argument('--strings', nargs='*')
ap.add_argument('--immediate', nargs='*')
a = ap.parse_args()
out = ROOT/'local_only'/'analysis'
base = out if a.variant == 'netemu' else out/'p0d'/a.variant
elf = ROOT/'local_only'/('stock.elf' if a.variant == 'netemu' else 'variants/'+a.variant+'.elf')
b = elf.read_bytes()
segs = [struct.unpack_from('>IIQQQQQQ', b, struct.unpack_from('>Q', b, 32)[0]+56*i) for i in range(struct.unpack_from('>H', b, 56)[0])]
def read(va, size):
    for typ, flags, off, start, pa, length, ms, align in segs:
        if typ == 1 and start <= va and va+size <= start+length:
            return b[off+va-start:off+va-start+size]
    raise ValueError(hex(va))
lines = {}
for p in [base/'text.asm', *base.glob('range_*.asm'), *base.glob('fn_*.asm'), *sorted((out/'p0e').glob(a.variant+'*.asm'))]:
    if not p.exists(): continue
    for line in p.read_text().splitlines():
        m = re.match(r'(?:0x)?([0-9a-f]{6,16}): (.*)', line)
        if m: lines[int(m[1],16)] = re.sub(r'^[0-9a-f]{8} ', '', m[2])
if a.verify:
    checked = []
    for row in json.loads((base/'sc_inventory.json').read_text()):
        n = int(row['site'],16)
        if row.get('hypercall') == 170:
            assert read(n,4) == bytes.fromhex('44000022' if a.variant != 'netemu' else '44000002')
            checked.append(row)
    print(json.dumps({'sha256':hashlib.sha256(b).hexdigest(), 'open_sites':checked},indent=2))
if a.range:
    low, high = [int(x,16) for x in a.range]
    for n, ins in sorted(lines.items()):
        if low <= n < high:
            extra = ''
            m = re.search(r'ld r\d+,(-?0x[0-9a-f]+)\(r2\)', ins)
            if m:
                toc = {'netemu':0x751280,'ps2_emu':0x4eb8c0,'ps2_gxemu':0x678548}[a.variant]
                v = int.from_bytes(read(toc+int(m[1],16),8),'big')
                extra = f' ; TOC={v:#x}'
                try:
                    s = read(v,64).split(bytes([0]))[0]
                    if s and all(32 <= c < 127 for c in s): extra += ' '+repr(s)
                except ValueError: pass
            print(f'{n:08x}: {read(n,4).hex()} {ins}{extra}')
if a.calls is not None:
    targets = {int(x,16) for x in a.calls}
    for n, ins in sorted(lines.items()):
        m = re.fullmatch(r'b[l]? 0x([0-9a-f]+)',ins)
        if m and int(m[1],16) in targets: print(f'{n:08x}: {ins}')
if a.data:
    n, size = int(a.data[0],16),int(a.data[1],0)
    for x in range(n,n+size,8):
        v = int.from_bytes(read(x,8),'big')
        try: s = repr(read(v,64).split(bytes([0]))[0])
        except ValueError: s = ''
        print(f'{x:08x}: {v:016x} {s}')
if a.strings is not None:
    for word in a.strings:
        needle = word.encode()+bytes([0])
        offsets = [m.start() for m in re.finditer(re.escape(needle), b)]
        vas = [hex(va+pos-off) for pos in offsets for typ,flags,off,va,pa,size,ms,align in segs if typ == 1 and off <= pos < off+size]
        print(word,vas)
if a.immediate is not None:
    targets = {int(x,16) for x in a.immediate}
    for typ,flags,off,va,pa,size,ms,align in segs:
        if typ != 1 or not flags & 1: continue
        for pos in range(off,off+size-4,4):
            word = int.from_bytes(b[pos:pos+4],'big')
            if word & 0xffff in targets:
                n = va+pos-off
                print(f'{n:08x}: {word:08x} {lines.get(n, "not in selected listings")}')
