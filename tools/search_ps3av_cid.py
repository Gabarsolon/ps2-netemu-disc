from pathlib import Path
import struct

cid = b'\x01\x00\x00\x02' # PS3AV_CID_VIDEO_MODE
cid_avb = b'\x04\x00\x00\x01' # PS3AV_CID_AVB_PARAM

print(f"Searching for PS3AV_CID_VIDEO_MODE ({cid.hex()}) and AVB_PARAM ({cid_avb.hex()}):")
for root_dir in [Path('local_only/fw355'), Path('local_only/fw493'), Path('local_only/analysis')]:
    if not root_dir.exists(): continue
    for f in root_dir.rglob('*'):
        if f.is_file() and f.suffix in ('.elf', '.self', '.bin', ''):
            try:
                data = f.read_bytes()
                c1 = data.count(cid)
                c2 = data.count(cid_avb)
                if c1 > 0 or c2 > 0:
                    print(f"  {f}: VIDEO_MODE={c1}, AVB_PARAM={c2}")
            except Exception:
                pass
