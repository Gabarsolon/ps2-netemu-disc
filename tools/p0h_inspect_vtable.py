import struct

d = open('local_only/fw355/out/lv1.elf', 'rb').read()

def disasm(addr, n_words):
    for i in range(n_words):
        pc = addr + i * 4
        w = struct.unpack_from('>I', d, pc - 0x1e0000)[0]
        print(f'{pc:08x}: {w:08x}')

disasm(0x2b37d4, 16)

