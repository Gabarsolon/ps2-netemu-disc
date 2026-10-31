"""Independent P0G evidence checks. Never contacts or writes to hardware."""
from pathlib import Path
import hashlib
import json
import struct

root = Path(__file__).resolve().parents[1]
base = root/'local_only/analysis/p0g'
checks = {}
for name in ['ps2_softemu','ps2_gxemu','ps2_emu']:
    b = (root/'local_only/fw355/out'/f'{name}.elf').read_bytes()
    manifest = json.loads((base/name/'manifest.json').read_text())
    assert hashlib.sha256(b).hexdigest() == manifest['sha256']
    raw = json.loads((base/f'{name}_raw.json').read_text())
    rows = json.loads((base/name/'sc_inventory.json').read_text())
    assert [(x['site'],x['lev']) for x in raw['sc']] == [(x['site'],x['lev']) for x in rows]
    assert not any(x.get('forwarded') for x in rows)
    checks[name] = {'sha256':manifest['sha256'],'sc':len(rows),'sc1':sum(x['lev']==1 for x in rows),'constant_sites':sum(x.get('hypercall') is not None for x in rows)}
b = (root/'local_only/fw355/out/ps2_softemu.elf').read_bytes()
def word(va): return struct.unpack_from('>I',b,0x10000+va)[0]
anchors = {0x88800:0x396000aa,0x88808:0x38a00000,0x88814:0x44000022,
           0x88bf8:0x396000f8,0x88c0c:0x44000022,0x88d44:0x396000f8,0x88d54:0x44000022,
           0x42ca0:0x396000a3,0x42cb0:0x44000022,0x89f0c:0x4e800020,
           0x88960:0x4e800020,0x221354:0x4be69f69}
for va, expected in anchors.items():
    assert word(va)==expected, (hex(va),hex(word(va)),hex(expected))
assert b[0x10000+0xc50:0x10000+0xcb0] == bytes(0x60)
modes = {}
for mode in range(33):
    target = 0x89758+struct.unpack_from('>i',b,0x10000+0x89758+mode*4)[0]
    if target != 0x89730: modes[mode] = hex(target)
assert modes == {0:'0x897dc',1:'0x89888',2:'0x8989c',16:'0x898b0',17:'0x898c4',32:'0x898dc'}
checks['anchors'] = {hex(k):hex(v) for k,v in anchors.items()}
checks['read_modes'] = modes
checks['soft_c50_zero'] = True
selfb = (root/'local_only/fw355/out/dev_flash/ps2emu/ps2_softemu.self').read_bytes()
assert hashlib.md5(selfb).hexdigest() == 'f95cc406bf1b4ec44481bae1195ca94c'
(base/'checks.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
