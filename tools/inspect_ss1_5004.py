import capstone

cs = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_64 | capstone.CS_MODE_BIG_ENDIAN)

with open(r'C:\Users\remus\ps2-netemu-disc\local_only\analysis\p0h\modules\ss_server1.elf', 'rb') as f:
    f.seek(65536)
    code = f.read(0x59d10)

base_va = 0x80000000

for start in [0x1fd70, 0x1fdc0]:
    print(f"=== Disassembly of 0x{base_va+start:x} ===")
    for ins in cs.disasm(code[start:start+0x40], base_va + start):
        print(f"0x{ins.address:08x}: {ins.bytes.hex()} {ins.mnemonic} {ins.op_str}")
