#!/usr/bin/env python3
import struct
import re
from pathlib import Path

dump_path = Path(r"C:\Users\remus\ps2-netemu-disc\local_only\lv1_mem_300000_700000.bin")
dump = dump_path.read_bytes()

for phys in [0x6C0168, 0x6DC8E8]:
    off = phys - 0x300000
    hdr = dump[off:off+64]
    print(f"\n--- ELF at phys 0x{phys:06X} ---")
    print("  Hex:", hdr[:16].hex())
    magic, bits, endian, ver, osabi = struct.unpack(">4sBBBB", hdr[:8])
    bits_str = "64-bit" if bits == 2 else "32-bit"
    endian_str = "BE" if endian == 2 else "LE"
    print(f"  Class: {bits_str}, Endian: {endian_str}")
    if bits == 2:
        e_type, e_mach, e_ver, e_entry, e_phoff, e_shoff = struct.unpack_from(">HHIQQQ", hdr, 16)
        print(f"  e_type: {e_type}, e_machine: {e_mach}, e_entry: 0x{e_entry:016X}")
        print(f"  e_phoff: 0x{e_phoff:X}, e_shoff: 0x{e_shoff:X}")
    else:
        e_type, e_mach, e_ver, e_entry, e_phoff, e_shoff = struct.unpack_from(">HHIIII", hdr, 16)
        print(f"  e_type: {e_type}, e_machine: {e_mach}, e_entry: 0x{e_entry:08X}")
        print(f"  e_phoff: 0x{e_phoff:X}, e_shoff: 0x{e_shoff:X}")

    # Check for string table or section names nearby
    strings_chunk = dump[off:off+4096]
    ascii_strings = [s.decode('ascii') for s in re.findall(b"[\x20-\x7E]{5,}", strings_chunk)]
    print(f"  Sample strings in first 4KB: {ascii_strings[:8]}")
