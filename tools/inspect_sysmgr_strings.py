from pathlib import Path
data = Path('local_only/analysis/p0h/modules/sysmgr_ss.elf').read_bytes()
off = 0x490b8
s = max(0, off - 128)
e = min(len(data), off + 256)
# print ascii strings in this range
cur = []
for i in range(s, e):
    b = data[i]
    if 0x20 <= b <= 0x7e:
        cur.append(chr(b))
    else:
        if len(cur) >= 3:
            print(f"  {hex(i - len(cur))}: {''.join(cur)}")
        cur = []
