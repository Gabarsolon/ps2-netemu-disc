"""Extract CORE_OS pieces (lv1.self, lv2_kernel.self, loaders) from any official PS3UPDAT.PUP and decrypt lv1.self.
usage: python -I tools/core_os_extract.py <PS3UPDAT.PUP> <out_dir>
Generalizes tools/p0h_extract.py (3.55 only). Output (Sony-derived) must stay under local_only/.
"""
import hashlib, io, json, struct, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KV = Path('C:/Users/remus/ps3buzz-console/raw_capture_debug11/dependencies/dl/key_vault.cpp')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    pup, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    template = (ROOT / 'tools/pup_extract.py').read_text()
    scope = {'__name__': 'core_os_sce'}
    exec(compile(template.rsplit('main()', 1)[0], 'pup_extract.py', 'exec'), scope)
    with pup.open('rb') as f:
        version = scope['pup_entry'](f, 0x100).decode().strip()
        tar = scope['pup_entry'](f, 0x300)
    print('PUP', pup.name, 'sha256', sha(pup.read_bytes()), 'version', version)
    t = tarfile.open(fileobj=io.BytesIO(tar))
    raw = t.extractfile('CORE_OS_PACKAGE.pkg').read()
    print('CORE_OS_PACKAGE.pkg header', raw[:16].hex())
    content = scope['sce_decrypt'](raw)
    ver, count, payload = struct.unpack_from('>IIQ', content)
    assert ver == 1 and payload == len(content), (ver, count, payload, len(content))
    files = []
    for i in range(count):
        offset, size, name = struct.unpack_from('>QQ32s', content, 16 + i * 48)
        name = name.split(b'\0', 1)[0].decode('ascii')
        data = content[offset:offset + size]
        (out / name).write_bytes(data)
        files.append((name, size, sha(data)[:16]))
        print('  ', name, size, sha(data)[:16])
    # decrypt lv1.self with the LV1 key family of the local vault
    dec = (ROOT / 'reference/buzz-netemu-build/selfdec.py').read_text()
    dec = dec.replace('LoadSelfLV2Keys()', 'LoadSelfLV1Keys()').replace('KEY_LV2', 'KEY_LV1')
    dec = dec.replace("assert self_type == 3, 'only LV2 type handled'", "assert self_type == 2, 'LV1 type required'")
    sc2 = {'__name__': 'lv1dec'}
    exec(compile(dec, 'selfdec_lv1.py', 'exec'), sc2)
    try:
        sc2['main'](str(KV), str(out / 'lv1.self'), str(out / 'lv1.elf'))
        e = (out / 'lv1.elf').read_bytes()
        print('lv1.elf', len(e), sha(e))
    except Exception as ex:
        print('LV1 DECRYPT FAILED:', type(ex).__name__, ex)
    (out / 'manifest.json').write_text(json.dumps({'pup_version': version, 'files': files}, indent=1))


main()
