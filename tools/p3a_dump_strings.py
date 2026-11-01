import struct
from pathlib import Path

ROOT = Path(r'C:\Users\remus\ps2-netemu-disc')
stock_elf = ROOT / 'local_only' / 'stock.elf'
data = stock_elf.read_bytes()

# Load segments
phoff = struct.unpack_from('>Q', data, 32)[0]
phnum = struct.unpack_from('>H', data, 56)[0]
segs = []
for i in range(phnum):
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, phoff + i * 56)
    if p_type == 1:
        segs.append((p_vaddr, p_offset, p_filesz))

def va_to_off(va):
    for vaddr, off, sz in segs:
        if vaddr <= va < vaddr + sz:
            return off + (va - vaddr)
    return None

off = va_to_off(0x300b00)
chunk = data[off:off+0x1000]
pos = 0
while pos < len(chunk):
    # find next null
    end = chunk.find(b'\0', pos)
    if end == -1: break
    s = chunk[pos:end]
    if len(s) >= 3 and all(32 <= b < 127 for b in s):
        print(f"0x{0x300b00 + pos:x}: {s.decode()}")
    pos = end + 1
