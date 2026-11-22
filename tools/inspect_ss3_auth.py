import capstone

cs = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN)

with open(r'C:\Users\remus\ps2-netemu-disc\local_only\analysis\p0h\modules\ss_server3.elf', 'rb') as f:
    f.seek(65536)
    code = f.read(0x16e0c)

base_va = 0x80000000
start = 0xa128
end = start + 0x60

for ins in cs.disasm(code[start:end], base_va + start):
    print(f"0x{ins.address:08x}: {ins.bytes.hex()} {ins.mnemonic} {ins.op_str}")
