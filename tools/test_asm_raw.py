import runpy

a = runpy.run_path('netemu_p1d/ppcasm.py')
asm = a['Assembler'](0x4800)
source = """
stdu r1, -64(r1)
std r7, 32(r1)
std r8, 40(r1)
mr r7, r6
mr r6, r5
mr r5, r4
mr r4, r3
li r3, 1
li r11, 0x5b
oris r11, r11, 0x8000
sc 0
ld r7, 32(r1)
ld r8, 40(r1)
std r4, 0(r7)
std r5, 0(r8)
addi r1, r1, 64
blr
"""
asm.asm(source)
b, rows = asm.finish()
print(f"Encoded {len(b)} bytes:")
for pc, hexval, line in rows:
    print(f"  {hex(pc)}: {hexval:08x}  {line}")
