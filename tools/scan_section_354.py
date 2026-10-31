from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()

# Let's inspect 0x354400 to 0x354600
base = 0x354400
off = base - 0x200000 + 0x20000

print("=== 0x354400 .. 0x354600 ===")
for i in range(0, 0x200, 8):
    va = base + i
    val = struct.unpack_from('>Q', elf, off + i)[0]
    s = ""
    if 0x200000 <= val < 0x3c0000:
        poff = val - 0x200000 + 0x20000
        nul = elf.find(b'\0', poff)
        if nul != -1 and nul - poff < 64:
            try: s = elf[poff:nul].decode('ascii', errors='ignore')
            except: pass
    if s or (0x200000 <= val < 0x3c0000):
        print(f"  {hex(va)}: {hex(val)} \"{s}\"")
    elif val != 0:
        print(f"  {hex(va)}: {hex(val)}")
