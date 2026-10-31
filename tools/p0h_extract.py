"""Read official 3.55 CORE_OS and extract checked local-only artifacts.

The actual input is SCE type 3, not a retail 7fPKG install package.
SCE section decoding reuses pup_extract.py without running its CLI.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/fw355'
OUT = BASE / 'core_os'
REPORT = ROOT / 'local_only/analysis/p0h'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    template = (ROOT / 'tools/pup_extract.py').read_text()
    scope = {'__name__': 'p0h_sce'}
    exec(compile(template.rsplit('main()', 1)[0], 'pup_extract.py', 'exec'), scope)
    pup = Path('C:/Users/remus/Downloads/3.55-OFW-PS3UPDAT.PUP')
    digest = sha(pup.read_bytes())
    assert digest == '334e60a4ef5843a688c1c6aebf0951c3259429233c7a5aca5a24f0edad78a192'
    with pup.open('rb') as f:
        official_tar = scope['pup_entry'](f, 0x300)
    assert official_tar == (BASE / 'update_files.tar').read_bytes()
    with tarfile.open(BASE / 'update_files.tar') as t:
        raw = t.extractfile('CORE_OS_PACKAGE.pkg').read()
    (OUT / 'CORE_OS_PACKAGE.pkg').write_bytes(raw)
    print('CORE_OS header', raw[:32].hex(), flush=True)
    content = scope['sce_decrypt'](raw)
    (OUT / 'content').write_bytes(content)
    manifest = {'pup_sha256': digest, 'update_tar_sha256': sha(official_tar),
                'core_package_sha256': sha(raw), 'content_sha256': sha(content),
                'content_size': len(content), 'content_prefix': content[:128].hex()}
    version, count, payload_size = struct.unpack_from('>IIQ', content)
    assert version == 1 and payload_size == len(content)
    files = []
    for i in range(count):
        offset, size, name = struct.unpack_from('>QQ32s', content, 16 + i * 48)
        name = name.split(bytes([0]), 1)[0].decode('ascii')
        assert name and Path(name).name == name and ':' not in name
        assert offset >= 16 + count * 48 and offset + size <= len(content)
        data = content[offset:offset + size]
        (OUT / name).write_bytes(data)
        files.append({'name': name, 'offset': offset, 'size': size, 'sha256': sha(data)})
    manifest['files'] = files
    # Adapt the existing SELF decoder to the exact LV1 key family/version.
    decoder = (ROOT / 'reference/buzz-netemu-build/selfdec.py').read_text()
    decoder = decoder.replace('LoadSelfLV2Keys()', 'LoadSelfLV1Keys()')
    decoder = decoder.replace('KEY_LV2', 'KEY_LV1')
    decoder = decoder.replace("assert self_type == 3, 'only LV2 type handled'",
                              "assert self_type == 2, 'LV1 type required'")
    kv = Path('C:/Users/remus/ps3buzz-console/raw_capture_debug11/dependencies/dl/key_vault.cpp')
    scope2 = {'__name__': 'p0h_self'}
    exec(compile(decoder, 'selfdec_lv1_adapter.py', 'exec'), scope2)
    elf = BASE / 'out/lv1.elf'
    scope2['main'](str(kv), str(OUT / 'lv1.self'), str(elf))
    manifest['lv1_elf'] = {'size': elf.stat().st_size, 'sha256': sha(elf.read_bytes())}
    (REPORT / 'extraction.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == '__main__':
    main()
