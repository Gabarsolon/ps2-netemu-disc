"""Extract LV1's embedded read-only filesystem and unencrypted FSELF modules."""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
OUT = BASE / 'modules'
OUT.mkdir(parents=True, exist_ok=True)
d = (ROOT / 'local_only/fw355/out/lv1.elf').read_bytes()
fs = d[0x1d0000:0x3d0000]
count, payload = struct.unpack_from('>II', fs)
manifest = []
for i in range(count):
    nameoff, off, size = struct.unpack_from('>III', fs, 8 + 12 * i)
    p = 8 + 12 * count + nameoff
    name = fs[p:fs.index(bytes([0]), p)].decode('ascii')
    blob = fs[payload + off:payload + off + size]
    assert len(blob) == size
    (OUT / name).write_bytes(blob)
    row = {'name': name, 'lv1_address': hex(0x400000 + payload + off),
           'size': size, 'sha256': hashlib.sha256(blob).hexdigest()}
    if blob[:4] == bytes([127,69,76,70]):
        (OUT / (name + '.elf')).write_bytes(blob)
    elif blob[:4] == b'SCE' + bytes([0]):
        app, elf, phdr, shdr, sec = struct.unpack_from('>5Q', blob, 0x28)
        e = blob[elf:elf + 64]
        assert e[:4] == bytes([127,69,76,70])
        eph, esh = struct.unpack_from('>QQ', e, 32)
        phentsz, phnum, shentsz, shnum = struct.unpack_from('>HHHH', e, 54)
        ph = [struct.unpack_from('>IIQQQQQQ', blob, phdr + j * 56) for j in range(phnum)]
        info = [struct.unpack_from('>QQIIII', blob, sec + j * 32) for j in range(phnum)]
        out = bytearray(max([64, eph + phnum * phentsz, esh + shnum * shentsz] + [x[2] + x[5] for x in ph]))
        out[:64] = e
        out[eph:eph + phnum * phentsz] = blob[phdr:phdr + phnum * phentsz]
        if shnum and shdr:
            out[esh:esh + shnum * shentsz] = blob[shdr:shdr + shnum * shentsz]
        for j, x in enumerate(ph):
            boff, bsize, comp, _, _, enc = info[j]
            assert comp == 1 and enc in (0, 2), (name, info)
            assert bsize == x[5]
            out[x[2]:x[2] + bsize] = blob[boff:boff + bsize]
        target = name.removesuffix('.fself') + '.elf'
        (OUT / target).write_bytes(out)
        row['elf'] = target
        row['elf_sha256'] = hashlib.sha256(out).hexdigest()
    manifest.append(row)
(BASE / 'modules.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
