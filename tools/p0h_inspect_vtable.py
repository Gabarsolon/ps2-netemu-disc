import struct

d = open('local_only/analysis/p0h/modules/ss_server2.elf', 'rb').read()
phoff, phnum = struct.unpack_from('>QI', d, 32)[0], struct.unpack_from('>H', d, 56)[0]
segs = []
for i in range(phnum):
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', d, phoff + i*56)
    segs.append((p_vaddr, p_offset, p_filesz))

va, fo, sz = segs[0]
for off in range(0, sz, 4):
    w = struct.unpack_from('>I', d, fo + off)[0]
    if (w >> 26) == 18:
        imm = (w & 0x03fffffc)
        if imm & 0x02000000:
            imm -= 0x04000000
        dest = va + off + imm
        if dest == 0x8000b800:
            print(f"Call from {hex(va + off)} to 0x8000b800")
