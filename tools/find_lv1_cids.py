import struct
from pathlib import Path

def inspect_cids(elf_path, name):
    data = Path(elf_path).read_bytes()
    def off2va(off): return off - 0x20000 + 0x200000
    print(f"\n=================== {name} CID Matches ===================")
    cids = {
        0x01000002: "PS3AV_CID_VIDEO_MODE",
        0x04000001: "PS3AV_CID_AVB_PARAM",
        0x01000001: "PS3AV_CID_VIDEO_INIT",
        0x00000003: "PS3AV_CID_AV_GET_HW_CONF"
    }
    for cid_val, cid_name in cids.items():
        pat = struct.pack('>I', cid_val)
        pos = 0
        matches = []
        while True:
            pos = data.find(pat, pos)
            if pos == -1: break
            # check if pos is 4-byte aligned
            if pos % 4 == 0:
                va = off2va(pos)
                matches.append((pos, va))
            pos += 1
        print(f"{cid_name} ({hex(cid_val)}): {len(matches)} aligned matches")
        for pos, va in matches:
            # check surrounding 32 bytes
            s = max(0, pos - 16)
            words = [hex(struct.unpack_from('>I', data, s + k)[0]) for k in range(0, 36, 4)]
            print(f"  off={hex(pos)} (VA {hex(va)}): {' '.join(words)}")

inspect_cids('local_only/fw355/out/lv1.elf', 'FW 3.55 LV1')
inspect_cids('local_only/fw493/lv1.elf', 'FW 4.93 LV1')
