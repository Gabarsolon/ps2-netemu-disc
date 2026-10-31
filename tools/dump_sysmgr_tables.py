from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()

def off_to_va(off):
    if 0x10000 <= off < 0x10000 + 0x3f6c8:
        return off - 0x10000 + 0x80000000
    if 0x50000 <= off < 0x50000 + 0xce88:
        return off - 0x50000 + 0xc0000000
    return None

def va_to_str(va):
    if 0x80000000 <= va < 0x8003f6c8:
        off = va - 0x80000000 + 0x10000
    elif 0xc0000000 <= va < 0xc000ce88:
        off = va - 0xc0000000 + 0x50000
    else:
        return f"va:{hex(va)}"
    nul = elf.find(b'\0', off)
    if nul != -1 and nul - off < 100:
        try:
            return f"\"{elf[off:nul].decode('ascii')}\""
        except:
            pass
    return f"va:{hex(va)}"

print("=== Table around 0xc000bf00 ===")
base_off = 0x5bf00
for i in range(0, 0x100, 8):
    va = 0xc000bf00 + i
    val = struct.unpack_from('>Q', elf, base_off + i)[0]
    s = va_to_str(val) if (0x80000000 <= val < 0x80040000 or 0xc0000000 <= val < 0xc0010000) else ""
    print(f"  {hex(va)}: {hex(val)} {s}")

print("\n=== Table around 0xc000b040 ===")
base_off = 0x5b040
for i in range(0, 0x80, 8):
    va = 0xc000b040 + i
    val = struct.unpack_from('>Q', elf, base_off + i)[0]
    s = va_to_str(val) if (0x80000000 <= val < 0x80040000 or 0xc0000000 <= val < 0xc0010000) else ""
    print(f"  {hex(va)}: {hex(val)} {s}")
