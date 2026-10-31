from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()

# Let's inspect around 0x1f0000
for base in range(0x1e0000, 0x200000, 0x1000):
    count, payload = struct.unpack_from('>II', elf, base)
    if 1 <= count <= 50 and 0x50 <= payload <= 0x1000:
        print(f"Possible fs header at 0x{base:x}: count={count}, payload=0x{payload:x}")
        # let's try reading entries
        valid = True
        names = []
        for i in range(count):
            nameoff, off, size = struct.unpack_from('>III', elf, base + 8 + 12 * i)
            p = base + 8 + 12 * count + nameoff
            nul = elf.find(b'\0', p)
            if nul == -1 or nul - p > 64:
                valid = False
                break
            try:
                name = elf[p:nul].decode('ascii')
                names.append((name, hex(off), hex(size)))
            except:
                valid = False
                break
        if valid:
            print(f"  Valid fs at 0x{base:x} with {count} files:")
            for n in names:
                print(f"    {n}")
