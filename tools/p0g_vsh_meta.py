"""Survey VSH's 32-bit function descriptors, without executing any code."""
from pathlib import Path
import collections
import json
import struct

root = Path(__file__).resolve().parents[1]
b = (root/'local_only/fw355/out/vsh.elf').read_bytes()
shoff = struct.unpack_from('>Q',b,40)[0]
n = struct.unpack_from('>H',b,60)[0]
sections = [struct.unpack_from('>IIQQQQIIQQ',b,shoff+64*i) for i in range(n)]
st = sections[struct.unpack_from('>H',b,62)[0]]
strings = b[st[4]:st[4]+st[5]]
for s in sections:
    label = strings[s[0]:].split(bytes([0]))[0].decode(errors='replace')
    print(label,hex(s[3]),hex(s[4]),hex(s[5]))
counts = collections.Counter()
descriptors = {}
for p in range(0,len(b)-8,4):
    entry,toc = struct.unpack_from('>II',b,p)
    if 0x10000 <= entry < 0x650000 and entry % 4 == 0 and 0x6c0000 <= toc < 0x770000:
        counts[toc] += 1
        if toc == 0x6f7370: descriptors[entry] = p
print('TOC candidates',[(hex(t),n) for t,n in counts.most_common(8)])
(root/'local_only/analysis/p0g/vsh_meta.json').write_text(json.dumps({'sections':sections,'toc32':counts.most_common(8)},indent=2))
(root/'local_only/analysis/p0g/vsh_descriptors32.json').write_text(json.dumps({hex(k):hex(v) for k,v in sorted(descriptors.items())},indent=2))
print('Launch-near entries', [hex(x) for x in sorted(descriptors) if 0x1ab000 <= x < 0x1ac000])
print('Launch containing descriptor candidate', hex(max(x for x in descriptors if x <= 0x1abc44)))
manifest_path = root/'local_only/analysis/p0g/vsh/manifest.json'
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())
    manifest['toc'] = '0x6f7370'
    manifest['descriptor_count'] = len(descriptors)
    manifest['descriptor_format'] = '32-bit entry/toc pairs; raw candidates, not full analysis'
    manifest_path.write_text(json.dumps(manifest,indent=2))
