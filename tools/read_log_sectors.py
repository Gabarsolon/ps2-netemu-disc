import struct

b = open(r'C:\Users\remus\ps2-netemu-disc\local_only\run_test_log.bin', 'rb').read()
for s in range(28, 40):
    off = s * 512
    rec = b[off:off+512]
    seq, tag, bid, tb, a, b_val = struct.unpack_from('>IIQQQQ', rec, 0)
    tag_str = struct.pack('>I', tag).decode('latin1', errors='replace')
    end_msg = rec.find(b'\x00', 40)
    msg = rec[40:end_msg].decode('latin1', errors='replace')
    print(f'Sector {s:02d}: tag={tag_str} A=0x{a:016x} B=0x{b_val:016x} msg="{msg}"')
