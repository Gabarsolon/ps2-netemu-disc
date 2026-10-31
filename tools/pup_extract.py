"""Extract dev_flash files from an official PS3UPDAT.PUP (reading only; output stays in local_only/).
usage: python -I tools/pup_extract.py <PS3UPDAT.PUP> <out_dir> [path_substring ...]
Steps: PUP entry 0x300 = update_files.tar; dev_flash_NNN.tar.aa.* are SCE (type 3) files, decrypted with the
public SCEPKG ERK/RIV constants (same as RPCS3's firmware installer); each decrypts to a tar chunk.
Only members whose path contains one of the substrings are written (default: ps2emu).
"""
import io, struct, sys, tarfile, zlib, hashlib
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util import Counter

ERK = bytes([0xA9,0x78,0x18,0xBD,0x19,0x3A,0x67,0xA1,0x6F,0xE8,0x3A,0x85,0x5E,0x1B,0xE9,0xFB,0x56,0x40,0x93,0x8D,
             0x4D,0xBC,0xB2,0xCB,0x52,0xC5,0xA2,0xF8,0xB0,0x2B,0x10,0x31])
RIV = bytes([0x4A,0xCE,0xF0,0x12,0x24,0xFB,0xEE,0xDF,0x82,0x45,0xF8,0xFF,0x10,0x21,0x1E,0x6E])


def ctr(key, iv, data):
    c = AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, 'big')))
    return c.decrypt(data)


def pup_entry(f, want):
    f.seek(0)
    magic, ver, imgver, cnt, hlen, dlen = struct.unpack('>8sQQQQQ', f.read(0x30))
    assert magic == b'SCEUF\0\0\0', 'not a PUP'
    for i in range(cnt):
        eid, off, ln, _ = struct.unpack('>QQQQ', f.read(0x20))
        if eid == want:
            f.seek(off)
            return f.read(ln)
    raise KeyError(hex(want))


def sce_decrypt(d):
    magic, ver, keyrev, htype, meta_off, hlen, dlen = struct.unpack_from('>4sIHHIQQ', d, 0)
    assert magic == b'SCE\0', 'not SCE'
    mi_off = 0x20 + meta_off
    mi = AES.new(ERK, AES.MODE_CBC, RIV).decrypt(d[mi_off:mi_off + 0x40])
    mkey, mkpad, miv, mivpad = mi[0:16], mi[16:32], mi[32:48], mi[48:64]
    assert mkpad[0] == 0 and mivpad[0] == 0, 'metadata decrypt failed'
    hdrs = ctr(mkey, miv, d[mi_off + 0x40:hlen])
    _, _, nsec, nkey, _, _, _ = struct.unpack_from('>QIIIIII', hdrs, 0)
    secs = [struct.unpack_from('>QQIIIIIIII', hdrs, 0x20 + i * 0x30) for i in range(nsec)]
    kbase = 0x20 + nsec * 0x30
    keys = [hdrs[kbase + i * 16:kbase + i * 16 + 16] for i in range(nkey)]
    out = bytearray()
    for (off, sz, typ, pidx, hashed, sha, enc, kidx, ividx, comp) in secs:
        if typ != 3:   # type 1/2 are 64-byte info blocks; type 3 holds the data (a tar chunk)
            continue
        blob = d[off:off + sz]
        if enc == 3:
            blob = ctr(keys[kidx], keys[ividx], blob)
        if comp == 2:
            blob = zlib.decompress(blob)
        out += blob
    return bytes(out)


def main():
    pup, outdir = sys.argv[1], Path(sys.argv[2])
    subs = sys.argv[3:] or ['ps2emu']
    outdir.mkdir(parents=True, exist_ok=True)
    with open(pup, 'rb') as f:
        print('PUP sha256', hashlib.sha256(Path(pup).read_bytes()).hexdigest())
        ver = pup_entry(f, 0x100).decode().strip()
        print('version.txt', ver)
        outer = tarfile.open(fileobj=io.BytesIO(pup_entry(f, 0x300)))
    found = 0
    for m in outer.getmembers():
        if not m.name.startswith('dev_flash_'):
            continue
        raw = outer.extractfile(m).read()
        try:
            chunk = sce_decrypt(raw)
        except Exception as e:
            print('skip', m.name, e); continue
        try:
            t = tarfile.open(fileobj=io.BytesIO(chunk))
            names = t.getmembers()
        except Exception as e:
            print('not a tar:', m.name, e, chunk[:16].hex()); continue
        for tm in names:
            if tm.isfile() and any(s in tm.name for s in subs):
                data = t.extractfile(tm).read()
                dst = outdir / tm.name.lstrip('./')
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
                found += 1
                print('extracted', tm.name, len(data), hashlib.md5(data).hexdigest(), hashlib.sha256(data).hexdigest()[:16])
    print('files extracted:', found)


main()
