from pathlib import Path
import struct

data = Path('local_only/fw355/out/vsh.elf').read_bytes()
# Search for pointer to 0x6fb4a0 or file offset
# In PRX, pointers inside data segment (file off 0x6b0000 -> VA 0x6c0000)
# So file offset 0x6eb4a0 corresponds to VA: 0x6eb4a0 - 0x6b0000 + 0x6c0000 = 0x6fb4a0!
target_va = 0x6fb4a0
p32 = struct.pack('>I', target_va)
p64 = struct.pack('>Q', target_va)

print(f"Searching for references to fn name array VA {hex(target_va)}:")
for p, size in [(p32, 4), (p64, 8)]:
    pos = 0
    while True:
        pos = data.find(p, pos)
        if pos == -1: break
        print(f"  found at off {hex(pos)}")
        # print surrounding 40 bytes
        for k in range(-16, 24, 4):
            v = struct.unpack_from('>I', data, pos + k)[0]
            print(f"    off {hex(pos+k)}: 0x{v:08x}")
        pos += 1
