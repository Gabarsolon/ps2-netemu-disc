import struct

b = open('C:/Users/remus/ps2-netemu-disc/local_only/analysis/p0i/modules/ss_server1.elf', 'rb').read()

targets = {
    0x8001fa14: "Function 1 (0xFF70)",
    0x80020280: "Function 2 (0xFF70)",
    0x80020638: "Function 3 (0xFF60 - PS2)"
}

for off in range(0, len(b) - 8, 8):
    w = struct.unpack('>Q', b[off:off+8])[0]
    if w in targets:
        print(f"64-bit pointer to {targets[w]} at file offset {hex(off)}")

for off in range(0x10000, 0x56ea0 - 4, 4):
    va = 0x80000000 + off - 0x10000
    instr = struct.unpack('>I', b[off:off+4])[0]
    if (instr >> 26) in (18,):
        li = (instr & 0x03fffffc)
        if li & 0x02000000:
            li -= 0x04000000
        target = va + li
        if target in targets:
            print(f"Branch to {targets[target]} at VA {hex(va)} (file off {hex(off)})")
