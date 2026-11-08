import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ss1_elf = ROOT / 'local_only' / 'analysis' / 'p0i' / 'modules' / 'ss_server1.elf'
data = ss1_elf.read_bytes()

# Parse ELF64 BE
def phdrs(d):
    po, = struct.unpack_from('>Q', d, 32)
    pn, = struct.unpack_from('>H', d, 56)
    return [struct.unpack_from('>IIQQQQQQ', d, po + 56 * i) for i in range(pn)]

def shdrs(d):
    so, = struct.unpack_from('>Q', d, 40)
    sn, = struct.unpack_from('>H', d, 60)
    shstrndx, = struct.unpack_from('>H', d, 62)
    headers = [struct.unpack_from('>IIQQQQIIQQ', d, so + 64 * i) for i in range(sn)]
    shstr_off = headers[shstrndx][4]
    def get_name(idx):
        return d[shstr_off + idx : d.find(b'\0', shstr_off + idx)].decode('ascii', errors='ignore')
    return [(get_name(h[0]), h[3], h[4], h[5]) for h in headers] # name, va, file_off, size

sections = shdrs(data)
for sname, va, off, sz in sections:
    print(f"Section {sname}: va=0x{va:x}, off=0x{off:x}, sz=0x{sz:x}")

def read_va(va, sz):
    for sname, sva, off, ssz in sections:
        if sva <= va < sva + ssz:
            foff = off + (va - sva)
            return data[foff : foff + sz]
    return None

# Check TOC entries and string pointers from 0x80020638
print("\n--- TOC / Data Pointers around 0xc000e680 ---")
for offset in range(0xc000e670, 0xc000e6b0, 8):
    val = read_va(offset, 8)
    if val:
        v64, = struct.unpack('>Q', val)
        print(f"0x{offset:x}: 0x{v64:x}")

print("\n--- Strings logged in _opd_FUN_80020638 ---")
str_ptrs = [0xc000e4b8, 0xc000e2e0, 0xc000e428, 0xc000e2f8, 0xc000e420, 0xc000e4b0, 0xc000e368, 0xc000e370, 0xc000e378, 0xc000e380, 0xc000e388, 0xc000e390, 0xc000e398, 0xc000e3a0, 0xc000e3a8]
for ptr in str_ptrs:
    val = read_va(ptr, 8)
    if val:
        v64, = struct.unpack('>Q', val)
        s = read_va(v64, 64)
        if s:
            s_clean = s.split(b'\0')[0].decode('ascii', errors='ignore')
            print(f"0x{ptr:x} -> 0x{v64:x}: \"{s_clean}\"")
