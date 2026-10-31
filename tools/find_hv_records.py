from pathlib import Path
import struct

elf = Path('local_only/fw493/lv1.elf').read_bytes()

# Search for hypercall table records:
# A table of 16-byte records where record[0] is hypercall number
# Let's search for 170 followed by pointer, 171 followed by pointer
p170 = struct.pack('>Q', 170)
p171 = struct.pack('>Q', 171)

pos = 0
while True:
    idx = elf.find(p170, pos)
    if idx == -1: break
    # check if idx + 16 has 171
    if idx + 16 < len(elf) and elf[idx + 16:idx + 24] == p171:
        va = idx - 0x20000 + 0x200000
        print(f"Found contiguous HV records 170, 171 at file off {hex(idx)} (va {hex(va)})")
        # let's scan backwards to find start of table
        start_idx = idx
        while start_idx >= 16:
            prev_num = struct.unpack_from('>Q', elf, start_idx - 16)[0]
            if 0 <= prev_num < 256:
                start_idx -= 16
            else:
                break
        # let's scan forwards to find end of table
        end_idx = idx
        while end_idx + 16 < len(elf):
            next_num = struct.unpack_from('>Q', elf, end_idx + 16)[0]
            if 0 <= next_num < 256:
                end_idx += 16
            else:
                break
        count = (end_idx - start_idx) // 16 + 1
        start_va = start_idx - 0x20000 + 0x200000
        end_va = end_idx - 0x20000 + 0x200000
        print(f"  HV registration table from {hex(start_va)} to {hex(end_va)}: {count} records!")
        # list some records
        for k in range(start_idx, end_idx + 16, 16):
            num, p_val = struct.unpack_from('>QQ', elf, k)
            k_va = k - 0x20000 + 0x200000
            if num in (91, 162, 163, 170, 171, 197, 245, 246, 248, 249):
                print(f"    HV {num}: at {hex(k_va)}, initial ptr: {hex(p_val)}")
    pos = idx + 1
