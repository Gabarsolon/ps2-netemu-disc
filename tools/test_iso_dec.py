from pathlib import Path
import re
import struct
from Crypto.Cipher import AES
from Crypto.Util import Counter

kv = Path('C:/Users/remus/ps3buzz-console/raw_capture_debug11/dependencies/dl/key_vault.cpp').read_text()
pattern = r'sk_ISO_arr\.emplace_back\((0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*KEY_ISO,\s*"([0-9A-F]+)",\s*"([0-9A-F]+)"'
iso_keys = []
for m in re.finditer(pattern, kv):
    iso_keys.append((int(m[1], 16), int(m[2], 16), int(m[3], 16), bytes.fromhex(m[4]), bytes.fromhex(m[5])))

def ctr(k, iv, data):
    return AES.new(k, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, 'big'))).decrypt(data)

def try_decrypt(self_path):
    d = Path(self_path).read_bytes()
    magic, ver, keyrev, htype, meta_off, hlen, dlen = struct.unpack_from('>4sIHHIQQ', d, 0)
    appinfo_off = struct.unpack_from('>Q', d, 0x20)[0]
    auth_id, vendor, self_type, app_ver = struct.unpack_from('>QIIQ', d, appinfo_off)
    print(f"{Path(self_path).name}: keyrev={hex(keyrev)}, app_ver={hex(app_ver)}, auth_id={hex(auth_id)}, self_type={hex(self_type)}")
    matching = [k for k in iso_keys if k[0] <= app_ver <= k[1] and k[2] == keyrev]
    if not matching:
        print(f"  No direct key match for app_ver={hex(app_ver)}, keyrev={hex(keyrev)}")
        matching = [k for k in iso_keys if k[2] == keyrev]
        print(f"  Candidates with matching keyrev ({len(matching)}):")
    for k in matching:
        mi = AES.new(k[3], AES.MODE_CBC, k[4]).decrypt(d[meta_off:meta_off + 64])
        if mi[16:32] == bytes(16) and mi[48:64] == bytes(16):
            print(f"  SUCCESS! Key match: range {hex(k[0])}..{hex(k[1])}, rev {hex(k[2])}")
            meta = ctr(mi[:16], mi[32:48], d[meta_off + 64:hlen])
            # let's decrypt sections
            _, _, nsec, nkey, _, _, _ = struct.unpack_from('>QIIIIII', meta)
            kbase = 32 + nsec * 48
            keys = meta[kbase:kbase + nkey * 16]
            plain = bytearray()
            for i in range(nsec):
                off, size, typ, idx, hashed, shi, enc, ki, ivi, comp = struct.unpack_from('>QQIIIIIIII', meta, 32 + i * 48)
                blob = d[off:off + size]
                if enc == 3:
                    blob = ctr(keys[ki * 16:ki * 16 + 16], keys[ivi * 16:ivi * 16 + 16], blob)
                plain += blob
            print(f"  Decrypted payload size: {len(plain)}")
            # look for strings in plain
            strings = [m.group(0).decode('ascii', errors='ignore') for m in re.finditer(rb'[ -~]{5,}', plain)]
            print(f"  Found {len(strings)} strings. First 15:")
            for s in strings[:15]:
                print(f"    {s}")
            return plain
    print("  Failed to decrypt.")
    return None

try_decrypt('local_only/fw493/me_iso_for_ps2emu.self')
try_decrypt('local_only/fw493/sv_iso_for_ps2emu.self')
