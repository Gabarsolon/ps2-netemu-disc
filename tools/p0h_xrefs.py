"""Raw TOC-load and branch-reference search to guide Ghidra; not a decoder."""
from pathlib import Path
import bisect
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
module = sys.argv[1]
path = ROOT / 'local_only/fw355/out/lv1.elf' if module == 'lv1' else BASE / 'modules' / (module + '.elf')
d = path.read_bytes()
ph = [struct.unpack_from('>IIQQQQQQ', d, struct.unpack_from('>Q', d, 32)[0] + 56 * i)
      for i in range(struct.unpack_from('>H', d, 56)[0])]


def read(n, size):
    for s in ph:
        if s[3] <= n and n + size <= s[3] + s[5]:
            return d[s[2] + n - s[3]:s[2] + n - s[3] + size]
    return bytes(size)


entry = struct.unpack_from('>Q', d, 24)[0]
toc = 0x351198 if module == 'lv1' else struct.unpack('>Q', read(entry + 8, 8))[0]
descs = []
for s in ph:
    for pos in range(s[2], s[2] + s[5] - 24, 8):
        fn, t, env = struct.unpack_from('>QQQ', d, pos)
        if t == toc and env == 0 and fn % 4 == 0 and any(x[1] & 1 and x[3] <= fn < x[3] + x[5] for x in ph):
            descs.append(fn)
descs = sorted(set(descs))


def containing(n):
    p = bisect.bisect_right(descs, n) - 1
    return hex(descs[p]) if p >= 0 else None


report = {'module': module, 'toc': hex(toc), 'descriptor_count': len(descs), 'targets': {}}
for item in sys.argv[2:]:
    target = int(item, 16)
    slots = []
    for off in range(-0x8000, 0x8000, 8):
        if struct.unpack('>Q', read(toc + off, 8))[0] == target:
            slots.append(off)
    refs = []
    for s in ph:
        if not s[1] & 1:
            continue
        for pos in range(s[2], s[2] + s[5] - 4, 4):
            word = struct.unpack_from('>I', d, pos)[0]
            n = s[3] + pos - s[2]
            imm = (word & 0xfffc) - (0x10000 if word & 0x8000 else 0)
            kind = None
            if word & 0xfc1f0003 == 0xe8020000 and imm in slots:
                kind = 'TOC load'
            if word >> 26 == 18:
                delta = (word & 0x3fffffc) - (0x4000000 if word & 0x2000000 else 0)
                dest = delta if word & 2 else n + delta
                if dest == target:
                    kind = 'direct branch'
            if kind:
                refs.append({'address': hex(n), 'word': hex(word), 'kind': kind,
                             'preceding_descriptor_entry': containing(n)})
    report['targets'][item] = {'toc_offsets': [hex(x) for x in slots], 'references': refs}
(BASE / (module + '_raw_xrefs_' + sys.argv[2] + '.json')).write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
