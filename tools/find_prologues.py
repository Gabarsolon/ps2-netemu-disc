import struct

b = open('C:/Users/remus/ps2-netemu-disc/local_only/analysis/p0i/modules/ss_server1.elf', 'rb').read()

def find_prologue(target_va):
    target_off = 0x10000 + (target_va - 0x80000000)
    for off in range(target_off, target_off - 0x1000, -4):
        instr = struct.unpack('>I', b[off:off+4])[0]
        # stdu r1, -N(r1) -> 0xf821... or mflr r0 -> 0x7c0802a6
        if instr == 0x7c0802a6 or (instr & 0xffff0003) == 0xf8210001:
            va = 0x80000000 + off - 0x10000
            print(f"Prologue before {hex(target_va)} at VA {hex(va)} (file off {hex(off)}): {hex(instr)}")
            return va
    return None

find_prologue(0x8001fb90)
find_prologue(0x80020410)
