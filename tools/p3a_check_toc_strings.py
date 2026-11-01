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

def read_u64(va):
    for vaddr, off, sz in segs:
        if vaddr <= va <= vaddr + sz - 8:
            return struct.unpack_from('>Q', data, off + (va - vaddr))[0]
    return None

def read_str(va):
    for vaddr, off, sz in segs:
        if vaddr <= va < vaddr + sz:
            b = data[off + (va - vaddr): off + sz]
            return b.split(b'\0')[0].decode('utf-8', errors='replace')
    return None

toc = 0x751280
for name, off in [("-0x7820", -0x7820), ("-0x7818", -0x7818), ("-0x77f0", -0x77f0)]:
    ptr = read_u64(toc + off)
    s = read_str(ptr) if ptr else None
    print(f"{name}: va=0x{toc+off:x} -> ptr=0x{ptr:x} -> str={repr(s)}")

