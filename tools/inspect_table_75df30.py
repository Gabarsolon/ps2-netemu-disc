from pathlib import Path
import struct

data = Path('local_only/stock.elf').read_bytes()
off = 0x75df30
print("Around 0x75df30:")
for k in range(-64, 96, 8):
    q = struct.unpack_from('>Q', data, off + k)[0]
    print(f"  off {hex(off+k)}: 0x{q:016x}")

# Find references to 0x74df30 or surrounding table
table_va = 0x74df30
p64 = struct.pack('>Q', table_va)
p32 = struct.pack('>I', table_va & 0xffffffff)
for p, size in [(p64, 8), (p32, 4)]:
    pos = 0
    while True:
        pos = data.find(p, pos)
        if pos == -1: break
        print(f"  ref {size*8} to {hex(table_va)} at off {hex(pos)}")
        pos += 1
