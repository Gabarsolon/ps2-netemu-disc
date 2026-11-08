import struct

b = open('C:/Users/remus/ps2-netemu-disc/local_only/analysis/p0i/modules/ss_server1.elf', 'rb').read()

# sth rX, 0x22(rY) -> opcode 44 (sth), d = 0x0022
# In PPC: sth rS, d(rA) -> 44 (6 bits) | rS (5 bits) | rA (5 bits) | d (16 bits)
# 44 << 26 = 0xb0000000
for off in range(0x10000, 0x56ea0 - 4, 4):
    va = 0x80000000 + off - 0x10000
    instr = struct.unpack('>I', b[off:off+4])[0]
    op = instr >> 26
    d = instr & 0xffff
    if d & 0x8000:
        d -= 0x10000
    if op == 44 and d == 0x22: # sth rS, 0x22(rA)
        rS = (instr >> 21) & 0x1f
        rA = (instr >> 16) & 0x1f
        print(f"sth r{rS}, 0x22(r{rA}) at VA {hex(va)} (file off {hex(off)})")
    if op == 36 and d == 0x20: # stw rS, 0x20(rA)
        rS = (instr >> 21) & 0x1f
        rA = (instr >> 16) & 0x1f
        print(f"stw r{rS}, 0x20(r{rA}) at VA {hex(va)} (file off {hex(off)})")
