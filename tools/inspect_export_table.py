from pathlib import Path
import struct

data = Path('local_only/fw355/out/vsh.elf').read_bytes()
# Let's inspect 0x6eb300..0x6eb440
print("0x6eb300..0x6eb440 (file):")
for off in range(0x6eb380, 0x6eb440, 4):
    v = struct.unpack_from('>I', data, off)[0]
    va = off + 0x10000
    # check if v points to code (e.g. 0x10000..0x600000)
    is_code = (0x10000 <= v <= 0x600000)
    print(f"  off {hex(off)} (VA {hex(va)}): 0x{v:08x}{' [CODE]' if is_code else ''}")
