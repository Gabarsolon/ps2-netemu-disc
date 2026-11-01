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

def find_branches_to(target):
    branches = []
    for vaddr, off, sz in segs:
        seg_bytes = data[off:off+sz]
        for pos in range(0, sz - 3, 4):
            w = struct.unpack_from('>I', seg_bytes, pos)[0]
            opcode = w >> 26
            if opcode == 18:
                lk = w & 1
                aa = w & 2
                li = (w & 0x03fffffc)
                if li & 0x02000000:
                    li -= 0x04000000
                cur_va = vaddr + pos
                dest = cur_va + li if aa == 0 else li
                if dest == target:
                    branches.append((cur_va, lk))
    return branches

# 1. Callers of raw_write (0x1ed458)
print("=== Callers of raw_write (0x1ed458) ===")
for va, lk in find_branches_to(0x1ed458):
    print(f"Branch at 0x{va:x} (lk={lk})")

# Also search for function descriptors or pointers to 0x1ed458
print("\n=== Pointers to 0x1ed458 ===")
target_bytes = struct.pack('>Q', 0x1ed458)
for vaddr, off, sz in segs:
    seg_bytes = data[off:off+sz]
    idx = 0
    while True:
        idx = seg_bytes.find(target_bytes, idx)
        if idx == -1: break
        print(f"Pointer at 0x{vaddr + idx:x}")
        idx += 8

# 2. Search for strings: vmc, savedata, .VM2
print("\n=== String occurrences in ELF ===")
for needle in [b'vmc', b'savedata', b'.VM2', b'.vm2', b'mc0', b'mc1', b'/dev_hdd0']:
    idx = 0
    found = 0
    while True:
        idx = data.find(needle, idx)
        if idx == -1: break
        va = None
        for vaddr, off, sz in segs:
            if off <= idx < off + sz:
                va = vaddr + (idx - off)
                break
        if va:
            # print surrounding 40 bytes
            surr = data[max(0, idx-10):min(len(data), idx+30)]
            print(f"'{needle.decode()}' at VA 0x{va:x} (file 0x{idx:x}): {repr(surr)}")
            found += 1
            if found >= 10:
                print("  ... and more")
                break
        idx += len(needle)
