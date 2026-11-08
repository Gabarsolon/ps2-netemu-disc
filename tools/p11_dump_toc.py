from pathlib import Path
import struct

elf_path = Path('local_only/fw355/out/ps2_softemu.elf')
data = elf_path.read_bytes()

e_phoff = struct.unpack_from('>Q', data, 0x20)[0]
e_phnum = struct.unpack_from('>H', data, 0x38)[0]

phdrs = []
for i in range(e_phnum):
    off = e_phoff + i * 56
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from('>IIQQQQQQ', data, off)
    if p_type == 1:
        phdrs.append((p_vaddr, p_filesz, p_offset))

def va2off(va):
    for vaddr, filesz, offset in phdrs:
        if vaddr <= va < vaddr + filesz:
            return offset + (va - vaddr)
    return None

e_entry = struct.unpack_from('>Q', data, 0x18)[0]
entry_off = va2off(e_entry)
entry_ip = struct.unpack_from('>Q', data, entry_off)[0]
entry_r2 = struct.unpack_from('>Q', data, entry_off + 8)[0]
print(f"Entry descriptor at VA {hex(e_entry)}: entry_ip={hex(entry_ip)}, entry_r2={hex(entry_r2)}")

toc = entry_r2

for name, off in [('-0x5840', -0x5840), ('-0x5858', -0x5858), ('-0x5830', -0x5830), ('-0x5848', -0x5848), ('-0x5838', -0x5838), ('-0x5860', -0x5860)]:
    va = toc + off
    foff = va2off(va)
    if foff is not None:
        val = struct.unpack_from('>Q', data, foff)[0]
        print(f"TOC {name} (VA {hex(va)}): {hex(val)}")
    else:
        print(f"TOC {name} (VA {hex(va)}): unmapped!")
