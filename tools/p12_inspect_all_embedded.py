from pathlib import Path
from elftools.elf.elffile import ELFFile
import io

data = Path('local_only/fw493/lv1.elf').read_bytes()

offsets = [0x1f00e8, 0x211950, 0x211d40, 0x2716a8, 0x271a98, 0x2a6700, 0x2a6b70, 0x2ca490, 0x2ca880, 0x34bf40, 0x34c330, 0x396c20, 0x397010]

for off in offsets:
    # try reading as ELF
    try:
        e = ELFFile(io.BytesIO(data[off:]))
        print(f"\n=== Embedded ELF at 0x{off:x} ===")
        print(f"  Entry: 0x{e.header['e_entry']:x}, Segments: {e.num_segments()}, Sections: {e.num_sections()}")
        # search for module name in rodata / text
        slice_data = data[off : off + 0x10000]
        # find strings like ss_server, sysmgr, etc.
        for kw in [b'ss_server', b'sysmgr', b'manager', b'lpar']:
            pos = slice_data.find(kw)
            if pos != -1:
                end = slice_data.find(b'\x00', pos)
                print(f"  Found string: {slice_data[pos:end]}")
    except Exception as ex:
        print(f"  0x{off:x}: failed to parse: {ex}")
