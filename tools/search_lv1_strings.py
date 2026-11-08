from pathlib import Path
import re

def search_strings(path, patterns):
    data = Path(path).read_bytes()
    print(f"\n=================== Strings in {path} ===================")
    for pat in patterns:
        matches = [m.start() for m in re.finditer(pat.encode('ascii', errors='ignore'), data, re.IGNORECASE)]
        print(f"Pattern '{pat}': {len(matches)} occurrences")
        for m in matches[:10]:
            # Extract surrounding ASCII string
            s = m
            while s > 0 and data[s-1] >= 0x20 and data[s-1] <= 0x7e:
                s -= 1
            e = m
            while e < len(data) and data[e] >= 0x20 and data[e] <= 0x7e:
                e += 1
            str_val = data[s:e].decode('ascii', errors='ignore')
            va = m - 0x20000 + 0x200000
            print(f"  off={hex(m)} (VA {hex(va)}): \"{str_val}\"")

patterns = ['ps3av', 'cxm', 'dve', 'hdmi', 'video_mode', 'display_mode', 'video_out', 'avset', 'avmulti']
search_strings('local_only/fw355/out/lv1.elf', patterns)
search_strings('local_only/fw493/lv1.elf', patterns)
