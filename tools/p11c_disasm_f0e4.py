import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

ss1_elf = Path('local_only/analysis/p0i/modules/ss_server1.elf')
data = ss1_elf.read_bytes()

# 0x8001f0e4 to 0x8001f3a0
start_va = 0x8001F0E4
end_va = 0x8001F3A0

off_base = 0x10000 - 0x80000000
code_bytes = data[start_va + off_base : end_va + off_base]

# Let's write a targeted disassembler or use capstone if available, or write a tiny disassembler for stack stores
for i in range(0, len(code_bytes), 4):
    va = start_va + i
    w, = struct.unpack('>I', code_bytes[i:i+4])
    op = w >> 26
    # print instructions that store bytes/words to stack (stb, sth, stw, std)
    # stb: 38 (0x26), stb: op=38
    # sth: 44 (0x2c)
    # stw: 36 (0x24)
    # std: 62 (0x3e)
    # li/addi: 14 (0x0e)
    # lis: 15 (0x0f)
    rs = (w >> 21) & 0x1f
    ra = (w >> 16) & 0x1f
    imm = w & 0xffff
    if imm >= 0x8000:
        simm = imm - 0x10000
    else:
        simm = imm
    
    disasm = f"0x{w:08x}"
    if op == 38: # stb
        disasm = f"stb r{rs}, {simm}(r{ra})"
    elif op == 44: # sth
        disasm = f"sth r{rs}, {simm}(r{ra})"
    elif op == 36: # stw
        disasm = f"stw r{rs}, {simm}(r{ra})"
    elif op == 62 and (w & 3) == 0: # std
        disasm = f"std r{rs}, {simm & ~3}(r{ra})"
    elif op == 14: # addi / li
        if ra == 0:
            disasm = f"li r{rs}, {simm}"
        else:
            disasm = f"addi r{rs}, r{ra}, {simm}"
    elif op == 15: # addis / lis
        if ra == 0:
            disasm = f"lis r{rs}, {simm}"
        else:
            disasm = f"addis r{rs}, r{ra}, {simm}"
    elif op == 18: # b/bl
        li = w & 0x03fffffc
        if li >= 0x02000000:
            li -= 0x04000000
        target = va + li
        disasm = f"bl 0x{target:x}" if (w & 1) else f"b 0x{target:x}"
    elif op == 31: # special
        xo = (w >> 1) & 0x3ff
        if xo == 444:
            disasm = f"mr r{ra}, r{rs}"
    
    print(f"0x{va:x}: {disasm}")
