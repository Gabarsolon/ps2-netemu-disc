from pathlib import Path
import struct

data = Path('local_only/fw355/out/vsh.elf').read_bytes()
off = 0x6eb4a0
print(f"Around 0x6eb4a0:")
# Let's see the index of avset_setvideomode in this array:
# Find start of array:
start = off
while start >= 4:
    val = struct.unpack_from('>I', data, start - 4)[0]
    if 0x6b0000 <= val < 0x6b5000:
        start -= 4
    else:
        break

end = off
while end + 4 <= len(data):
    val = struct.unpack_from('>I', data, end)[0]
    if 0x6b0000 <= val < 0x6b5000:
        end += 4
    else:
        break

count = (end - start) // 4
idx = (off - start) // 4
print(f"Function name array from file {hex(start)} to {hex(end)}: {count} entries. 'avset_setvideomode' is index {idx}!")

# Print all names in order:
names = []
for i in range(count):
    str_va = struct.unpack_from('>I', data, start + i*4)[0]
    str_off = str_va - 0x10000
    s_end = data.find(b'\x00', str_off)
    name = data[str_off:s_end].decode('ascii', errors='ignore')
    names.append(name)
    if 'setvideomode' in name:
        print(f"  [{i}] {name} (index {i})")

# In PRX format, right before the names table or right after it is the NID table (4 bytes each)
# and the function pointer / OPD table (4 bytes or 8 bytes each)!
# Let's inspect the 512 bytes before `start`
print(f"\nChecking 512 bytes before start ({hex(start - 512)}..{hex(start)}):")
for k in range(start - count*8 - 64, start, 8):
    q = struct.unpack_from('>Q', data, k)[0]
    # check if q looks like a VA (e.g. 0x10000..0x6b0000)
    print(f"  {hex(k)}: 0x{q:016x}")
