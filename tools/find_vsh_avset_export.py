from pathlib import Path
import struct
import re

data = Path('local_only/fw355/out/vsh.elf').read_bytes()
# String 'avset_setvideomode' is at file off 0x6a36d8
# In Sony PRX export table:
# Export lib stub contains pointers to function names and OPDs
# Let's search for 0x6a36d8 or VA 0x6b36d8 or 32-bit offset
# Let's search 32-bit integer:
target32 = struct.pack('>I', 0x6b36d8)
target64 = struct.pack('>Q', 0x6b36d8)

print("32-bit refs to string VA:")
pos = 0
while True:
    pos = data.find(target32, pos)
    if pos == -1: break
    print(f"  at off {hex(pos)}")
    # inspect surrounding
    for k in range(-8, 16, 4):
        val = struct.unpack_from('>I', data, pos + k)[0]
        print(f"    {hex(pos+k)}: 0x{val:08x}")
    pos += 1

print("64-bit refs to string VA:")
pos = 0
while True:
    pos = data.find(target64, pos)
    if pos == -1: break
    print(f"  at off {hex(pos)}")
    pos += 1
