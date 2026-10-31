from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()

# Find string offsets
s_ps2_ne = elf.find(b'PS2_NE_LPAR')
s_ps2_sw = elf.find(b'PS2_SW_LPAR')
s_ps2_gx = elf.find(b'PS2_GX_LPAR')
s_ps2_hw = elf.find(b'PS2_LPAR\0')
s_sce_ne = elf.find(b'SCE_CELLOS_SYSTEM_MGR_PS2_NE')
s_netemu_1st = elf.find(b'sysmgr.boot.ps2netemu.1st')

print(f"PS2_NE_LPAR string offset: {hex(s_ps2_ne)}")
print(f"SCE_CELLOS_SYSTEM_MGR_PS2_NE string offset: {hex(s_sce_ne)}")
print(f"sysmgr.boot.ps2netemu.1st string offset: {hex(s_netemu_1st)}")

# Search for xrefs to s_ps2_ne, s_sce_ne, s_netemu_1st in sysmgr_ss.elf
# Note: sysmgr_ss ELF program headers virtual address
phoff = struct.unpack_from('>Q', elf, 32)[0]
phentsz, phnum = struct.unpack_from('>HH', elf, 54)
print(f"ELF program headers: {phnum} headers at {hex(phoff)}")
for i in range(phnum):
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', elf, phoff + i * phentsz)
    print(f"  PH {i}: type={p_type}, vaddr={hex(p_vaddr)}, filesz={hex(p_filesz)}, offset={hex(p_offset)}")

# In 3.55 sysmgr_ss: loaded at 0x80000000. Let's check vaddr for 4.93.
