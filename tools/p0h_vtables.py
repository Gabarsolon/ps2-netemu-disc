"""Resolve LV1 vtable slots which point at a specified function descriptor."""
from pathlib import Path
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
d = (ROOT / 'local_only/fw355/out/lv1.elf').read_bytes()
descs = json.loads((BASE / 'descriptors.json').read_text())
ph = json.loads((BASE / 'raw.json').read_text())['segments']


def q(a):
    for s in ph:
        if s[3] <= a < s[3] + s[5] - 7:
            return struct.unpack_from('>Q', d, s[2] + a - s[3])[0]
    return 0


for item in sys.argv[1:]:
    target = int(item, 16)
    opds = {r['address'] for r in descs if r['entry'] == target and r['toc'] == 0x351198}
    print('FUNCTION', hex(target), 'descriptors', [hex(a) for a in opds])
    for s in ph:
        for pos in range(s[2], s[2] + s[5] - 7, 8):
            if struct.unpack_from('>Q', d, pos)[0] in opds:
                address = s[3] + pos - s[2]
                print('pointer', hex(address), 'nearby')
                bases = [(off, q(0x351198 + off)) for off in range(-0x8000, 0, 8)
                         if address - 0x200 <= q(0x351198 + off) <= address]
                print('nearby TOC bases', [(hex(off), hex(base)) for off, base in bases])
                for a in range(address - 40, address + 64, 8):
                    v = q(a)
                    print(hex(a), hex(v), '->', hex(q(v)))
