"""Decrypt exact 0.80--3.55 public SPP key and inventory profile records.

Key provenance: psdevwiki Keys, Spp verifier, 0.80--3.55 row.
Layout cross-check: naehrwert/scetool spp.h and spp.cpp.
"""
from pathlib import Path
import hashlib
import json
import re
import struct
from Crypto.Cipher import AES
from Crypto.Util import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
d = (ROOT / 'local_only/fw355/core_os/default.spp').read_bytes()
erk = bytes.fromhex('56C655747A4B6957A2D8BB9AC605C297E6AC9871932BFECDDE066CEE5B29470A')
riv = bytes.fromhex('007E6B268EF1E986D10A9889CF93A8CB')
_, _, rev, typ, mo, hlen, dlen = struct.unpack_from('>4sIHHIQQ', d)
assert typ == 4 and rev == 0
mo += 32
mi = AES.new(erk, AES.MODE_CBC, riv).decrypt(d[mo:mo + 64])
assert mi[16:32] == bytes(16) and mi[48:64] == bytes(16)


def ctr(key, iv, data):
    return AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, 'big'))).decrypt(data)


meta = ctr(mi[:16], mi[32:48], d[mo + 64:hlen])
_, _, nsec, nkey, _, _, _ = struct.unpack_from('>QIIIIII', meta)
sections = [struct.unpack_from('>QQIIIIIIII', meta, 32 + i * 48) for i in range(nsec)]
kbase = 32 + nsec * 48
keys = [meta[kbase + 16 * i:kbase + 16 * (i + 1)] for i in range(nkey)]
chunks = []
for off, size, styp, idx, hashed, sha, enc, ki, ivi, comp in sections:
    blob = d[off:off + size]
    assert comp == 1
    if enc == 3:
        blob = ctr(keys[ki], keys[ivi], blob)
    chunks.append(blob)
plain = b''.join(chunks)
(BASE / 'default.spp.plain').write_bytes(plain)
(BASE / 'spp_sections.json').write_text(json.dumps(sections, indent=2))
header = struct.unpack_from('>HHIIIQII', plain)
print('header', header)
records = []
p = 32
for i in range(header[-2]):
    size, styp, laid, paid, name = struct.unpack_from('>IIQQ32s', plain, p)
    assert size >= 56 and p + size <= len(plain)
    row = {'offset': hex(p), 'size': size, 'type': styp, 'laid': hex(laid), 'paid': hex(paid),
           'name': name.split(bytes([0]), 1)[0].decode('ascii')}
    strings = [{'offset': hex(p + m.start()), 'value': m[0].decode('ascii')}
               for m in re.finditer(rb'[ -~]{5,}', plain[p:p + size])]
    row['strings'] = strings
    records.append(row)
    p += size
report = {'sha256': hashlib.sha256(plain).hexdigest(), 'header': header, 'records': records}
(BASE / 'spp.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
