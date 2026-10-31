"""Make an analysis copy with reconstructed section names (no PT_LOAD changes).

The SELF retains section headers but not the ELF section-name string bytes.
Section 5 is exactly 6695 PPC64 function descriptors, 24 bytes each.
Naming it .opd lets Ghidra recover function boundaries without speculative scans.
"""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
original = (ROOT / 'local_only/fw355/out/lv1.elf').read_bytes()
d = bytearray(original)
shoff = struct.unpack_from('>Q', d, 40)[0]
n = struct.unpack_from('>H', d, 60)[0]
names = bytes([0])
for i in range(n):
    label = '.opd' if i == 5 else '.shstrtab' if i == 17 else '.part_' + str(i)
    struct.pack_into('>I', d, shoff + 64 * i, len(names))
    names += label.encode() + bytes([0])
struct.pack_into('>QQ', d, shoff + 64 * 17 + 24, len(d), len(names))
d += names
phoff = struct.unpack_from('>Q', d, 32)[0]
for i in range(struct.unpack_from('>H', d, 56)[0]):
    s = struct.unpack_from('>IIQQQQQQ', d, phoff + 56 * i)
    assert original[s[2]:s[2] + s[5]] == d[s[2]:s[2] + s[5]]
(BASE / 'lv1_named.elf').write_bytes(d)
(BASE / 'named_sections.json').write_text(json.dumps({
    'original_sha256': hashlib.sha256(original).hexdigest(),
    'analysis_sha256': hashlib.sha256(d).hexdigest(), 'all_load_payloads_identical': True,
    'section_5_name': '.opd', 'descriptor_count': 6695}, indent=2))
print('Analysis section names restored; all load payloads unchanged')
