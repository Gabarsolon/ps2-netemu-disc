from pathlib import Path
import struct

data = Path('local_only/fw355/out/vsh.elf').read_bytes()
# Search for string "libavset\0"
pos = 0
while True:
    pos = data.find(b'libavset\x00', pos)
    if pos == -1: break
    va = pos + 0x10000
    print(f"'libavset' string at off {hex(pos)} (VA {hex(va)})")
    # Search for pointers to this string VA
    p32 = struct.pack('>I', va)
    pos2 = 0
    while True:
        pos2 = data.find(p32, pos2)
        if pos2 == -1: break
        print(f"  referenced at off {hex(pos2)}")
        # Dump export struct
        # Sony sceExportLibraryEntry is 28 or 32 bytes or 36 bytes:
        # u8 size, aux, u16 version, u16 flags, u16 num_funcs, u16 num_vars, u16 num_tls_vars, u8 reserved[4], u32 libname, u32 nid_table, u32 stub_table
        # Let's inspect the 48 bytes around pos2
        s = pos2 - 12
        for k in range(0, 48, 4):
            v = struct.unpack_from('>I', data, s + k)[0]
            print(f"    off {hex(s+k)}: 0x{v:08x}")
        # Parse it:
        size, aux, ver, flags, num_funcs, num_vars = struct.unpack_from('>BBHHHH', data, s)
        print(f"    size={size}, ver={hex(ver)}, flags={hex(flags)}, num_funcs={num_funcs}, num_vars={num_vars}")
        libname_va = struct.unpack_from('>I', data, s + 12)[0]
        nid_va = struct.unpack_from('>I', data, s + 16)[0]
        stub_va = struct.unpack_from('>I', data, s + 20)[0]
        print(f"    libname={hex(libname_va)}, nid_table={hex(nid_va)}, stub_table={hex(stub_va)}")
        # Let's read the stubs!
        nid_off = nid_va - 0x10000
        stub_off = stub_va - 0x10000
        for f in range(num_funcs):
            fnid = struct.unpack_from('>I', data, nid_off + f*4)[0]
            fstub = struct.unpack_from('>I', data, stub_off + f*4)[0]
            # fstub is pointer to function or OPD
            # Let's find name if available: name array is often at stub_table + num_funcs*4
            print(f"      func[{f:2d}]: NID=0x{fnid:08x} -> stub={hex(fstub)}")
        pos2 += 1
    pos += 1
