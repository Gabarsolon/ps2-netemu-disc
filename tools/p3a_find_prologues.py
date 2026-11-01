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

def find_prologue(va):
    cur = va
    while cur > va - 0x1000:
        off = va_to_off(cur)
        w = struct.unpack_from('>I', data, off)[0]
        # stdu r1, -X(r1): opcode 62, rs=1, ra=1, ds=negative
        # 0xf821...
        if (w & 0xffff0000) == 0xf8210000 or (w & 0xffff0003) == 0xf8210001:
            return cur
        cur -= 4
    return None

sites = [0x12c588, 0x12c858, 0x12ca78, 0x12cd48, 0x12cfb0, 0x12d4e8]
for s in sites:
    pro = find_prologue(s)
    print(f"Site 0x{s:x} -> Prologue at 0x{pro:x} (delta +0x{s-pro:x})")

