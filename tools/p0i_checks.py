"""Verify 4.93 LV1 extraction against SELF section HMACs and ELF program headers."""
from pathlib import Path
import hashlib
import hmac
import json
import re
import struct
import zlib
from Crypto.Cipher import AES
from Crypto.Util import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0i'
BASE.mkdir(parents=True, exist_ok=True)

kv = Path('C:/Users/remus/ps3buzz-console/raw_capture_debug11/dependencies/dl/key_vault.cpp').read_text()
body = kv.split('void KeyVault::LoadSelfLV1Keys()', 1)[1].split('\n}', 1)[0]
pattern = r'emplace_back\((0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*KEY_LV1,\s*"([0-9A-F]+)",\s*"([0-9A-F]+)"'
rows = list(re.finditer(pattern, body))

d = (ROOT / 'local_only/fw493/lv1.self').read_bytes()
elf = (ROOT / 'local_only/fw493/lv1.elf').read_bytes()
mo = 32 + struct.unpack_from('>I', d, 12)[0]
hlen = struct.unpack_from('>Q', d, 16)[0]
app = struct.unpack_from('>Q', d, 40)[0]
version = struct.unpack_from('>Q', d, app + 16)[0]
rev = struct.unpack_from('>H', d, 8)[0]
print(f"LV1.self version: {hex(version)}, rev: {hex(rev)}, hlen: {hex(hlen)}, mo: {hex(mo)}")

key = next(r for r in rows if int(r[1], 16) <= version <= int(r[2], 16) and int(r[3], 16) == rev)
print(f"Found key row: {key[1]} .. {key[2]}, rev {key[3]}")
mi = AES.new(bytes.fromhex(key[4]), AES.MODE_CBC, bytes.fromhex(key[5])).decrypt(d[mo:mo + 64])
assert mi[16:32] == bytes(16) and mi[48:64] == bytes(16), "Metadata info zero padding check failed"


def ctr(k, iv, data):
    return AES.new(k, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, 'big'))).decrypt(data)


meta = ctr(mi[:16], mi[32:48], d[mo + 64:hlen])
_, _, nsec, nkey, _, _, _ = struct.unpack_from('>QIIIIII', meta)
kbase = 32 + nsec * 48
keys = meta[kbase:kbase + nkey * 16]
checks = []
for i in range(nsec):
    off, size, typ, idx, hashed, shi, enc, ki, ivi, comp = struct.unpack_from('>QQIIIIIIII', meta, 32 + i * 48)
    blob = d[off:off + size]
    if enc == 3:
        blob = ctr(keys[ki * 16:ki * 16 + 16], keys[ivi * 16:ivi * 16 + 16], blob)
    if hashed == 2:
        expected = keys[shi * 16:shi * 16 + 20]
        hkey = keys[shi * 16 + 32:shi * 16 + 96]
        assert hmac.new(hkey, blob, hashlib.sha1).digest() == expected, ('section HMAC failed', i)
    if comp == 2:
        blob = zlib.decompress(blob)
    if typ == 2:
        phoff = struct.unpack_from('>Q', elf, 32)[0]
        ph = struct.unpack_from('>IIQQQQQQ', elf, phoff + idx * 56)
        assert len(blob) == ph[5], f"Segment {idx} size mismatch: {len(blob)} vs {ph[5]}"
        assert elf[ph[2]:ph[2] + ph[5]] == blob, f"Segment {idx} data mismatch"
    checks.append({
        'section': i,
        'type': typ,
        'program_header': idx,
        'hmac_verified': hashed == 2,
        'plaintext_size': len(blob)
    })

expected_elf_sha = hashlib.sha256(elf).hexdigest()
print(f"ELF SHA-256: {expected_elf_sha}, size: {len(elf)}")
report = {
    'status': 'PASS',
    'version': hex(version),
    'rev': hex(rev),
    'lv1_elf_sha256': expected_elf_sha,
    'lv1_elf_size': len(elf),
    'lv1_metadata_full_zero_padding': True,
    'checks': checks
}
(BASE / 'checks.json').write_text(json.dumps(report, indent=2))
print("Extraction and HMAC check: SUCCESS!")
