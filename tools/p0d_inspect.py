"""Read local Ghidra listings/ELF data; no alternative disassembler or network."""
from pathlib import Path
import argparse, hashlib, json, struct

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('variant', choices=['ps2_emu','ps2_gxemu'])
ap.add_argument('--slice', nargs=2)
ap.add_argument('--table', nargs=2)
args = ap.parse_args()
out = ROOT/'local_only'/'analysis'/'p0d'/args.variant
b = (ROOT/'local_only'/'variants'/(args.variant+'.elf')).read_bytes()
manifest = json.loads((out/'manifest.json').read_text())
def read(va, length):
    for typ,flags,off,base,pa,size,memsize,align in manifest['segments']:
        if base <= va and va+length <= base+size:
            return b[off+va-base:off+va-base+length]
    raise ValueError(hex(va))

if args.table:
    start, count = int(args.table[0],16),int(args.table[1],0)
    for i in range(count):
        value = struct.unpack('>i',read(start+4*i,4))[0]
        print(i,hex(start+value))
if args.slice:
    low,high=[int(x,16) for x in args.slice]
    lines={}
    for path in [out/'text.asm', *out.glob('range_*.asm')]:
        for line in path.read_text().splitlines():
            if ':' in line:
                try: n=int(line.split(':')[0],16)
                except ValueError: continue
                if low <= n < high: lines[n]=line
    print('\n'.join(line for n,line in sorted(lines.items())))
