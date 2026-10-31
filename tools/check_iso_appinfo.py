from pathlib import Path
import struct

def check(name):
    d = Path(f'local_only/fw493/{name}').read_bytes()
    header = struct.unpack_from('>4sIHHIQQ', d)
    appinfo_off = struct.unpack_from('>Q', d, 0x20)[0]
    auth_id, vendor, self_type, app_ver = struct.unpack_from('>QIIQ', d, appinfo_off)
    print(f"{name}: rev={hex(header[2])}, type={header[3]}, self_type={self_type}, auth_id={hex(auth_id)}, app_ver={hex(app_ver)}")

check('me_iso_for_ps2emu.self')
check('sv_iso_for_ps2emu.self')
