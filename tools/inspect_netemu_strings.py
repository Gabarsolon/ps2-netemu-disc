from pathlib import Path

data = Path('local_only/stock.elf').read_bytes()
s = 0x314af0
e = 0x314c00
cur = []
for i in range(s, e):
    b = data[i]
    if 0x20 <= b <= 0x7e:
        cur.append(chr(b))
    else:
        if len(cur) >= 2:
            print(f"  {hex(i - len(cur))}: {''.join(cur)}")
        cur = []
