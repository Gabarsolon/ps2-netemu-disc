# Fixed call 95 only. C passes &local_qwords[0], audited as a 40-byte alloca.
# Forwarded sc 0 ABI matches stock 16988..169C8. No native TOC load needed.
# Return r3=status; capture r4..r8 before restoring CR/TOC/nonvolatile r31.
mflr r0
std r0,16(r1)
stdu r1,-128(r1)
std r2,112(r1)
mfcr r0
std r0,104(r1)
std r31,96(r1)
mr r31,r5
li r11,95
oris r11,r11,32768
sc 0
std r4,0(r31)
std r5,8(r31)
std r6,16(r31)
std r7,24(r31)
std r8,32(r31)
ld r31,96(r1)
ld r2,112(r1)
ld r0,104(r1)
mtcr r0
addi r1,r1,128
ld r0,16(r1)
mtlr r0
blr
