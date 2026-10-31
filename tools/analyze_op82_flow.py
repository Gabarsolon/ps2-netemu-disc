from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()

# Let's inspect strings loaded from TOC in this function:
toc = 0xc0012f40
def toc_str(disp):
    va = toc + disp
    off = va - 0xc0000000 + 0x50000
    ptr = struct.unpack_from('>Q', elf, off)[0]
    # resolve ptr
    if 0x80000000 <= ptr < 0x80040000:
        poff = ptr - 0x80000000 + 0x10000
    elif 0xc0000000 <= ptr < 0xc0010000:
        poff = ptr - 0xc0000000 + 0x50000
    else:
        return f"ptr:{hex(ptr)}"
    nul = elf.find(b'\0', poff)
    if nul != -1 and nul - poff < 100:
        try:
            return f"\"{elf[poff:nul].decode('ascii')}\""
        except:
            pass
    return f"ptr:{hex(ptr)}"

disps = [-29328, -29320, -29312, -29304, -29296, -29288, -29280, -29272, -29264, -29256, -29248]
for d in disps:
    print(f"disp {d} ({hex(d & 0xffff)}): {toc_str(d)}")
