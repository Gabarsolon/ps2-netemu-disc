"""Independent byte inventory of LV1; Sony-derived output stays local_only."""
from pathlib import Path
import collections
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'local_only/analysis/p0h'
d = (ROOT / 'local_only/fw355/out/lv1.elf').read_bytes()
phoff = struct.unpack_from('>Q', d, 32)[0]
segments = [struct.unpack_from('>IIQQQQQQ', d, phoff + i * 56)
            for i in range(struct.unpack_from('>H', d, 56)[0])]
toc_counts = collections.Counter()
descriptors = []
strings = []
constants = []
for typ, flags, off, va, pa, size, memsize, align in segments:
    if typ != 1:
        continue
    for p in range(off, off + size - 24, 8):
        entry, toc, env = struct.unpack_from('>QQQ', d, p)
        if entry % 4 == 0 and any(s[1] & 1 and s[3] <= entry < s[3] + s[5] for s in segments) and any(s[3] <= toc < s[3] + s[6] for s in segments) and env == 0:
            toc_counts[toc] += 1
            descriptors.append({'address': va + p - off, 'entry': entry, 'toc': toc})
    for m in re.finditer(rb'[ -~]{4,}', d[off:off + size]):
        strings.append({'address': va + m.start(), 'value': m[0].decode('ascii')})
    for p in range(off, off + size - 4, 4):
        word = struct.unpack_from('>I', d, p)[0]
        if word & 0xffff in [0x8201, 0x8202, 0x8203, 0x8204, 0x5005, 0x5000]:
            constants.append({'address': va + p - off, 'word': hex(word)})
report = {'sha256': hashlib.sha256(d).hexdigest(), 'segments': segments,
          'toc_counts': toc_counts.most_common(20), 'constants': constants}
(OUT / 'raw.json').write_text(json.dumps(report, indent=2))
(OUT / 'descriptors.json').write_text(json.dumps(descriptors, indent=2))
(OUT / 'strings.json').write_text(json.dumps(strings, indent=2))
print(json.dumps(report, indent=2))
print('Relevant strings')
for row in strings:
    if re.search('ps2|emu|lpar|panic|vuart|uart|5005|storage|auth|shutdown|partition|repository|open_device|close_device', row['value'], re.I):
        print(hex(row['address']), row['value'])
