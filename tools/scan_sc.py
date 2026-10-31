"""Scan stock ELF for `sc` instructions and the preceding `li r11,N` (LV1 hypercall number).
usage: python -I tools/scan_sc.py local_only/stock.elf
"""
import struct, sys
d = open(sys.argv[1], 'rb').read()
e_phoff, = struct.unpack_from('>Q', d, 0x20)
phnum, = struct.unpack_from('>H', d, 0x38)
segs = [struct.unpack_from('>IIQQQQQQ', d, e_phoff + i * 0x38) for i in range(phnum)]
for t, fl, off, va, pa, fsz, msz, al in segs:
    if t != 1 or not (fl & 1):
        continue
    for o in range(off, off + fsz, 4):
        w, = struct.unpack_from('>I', d, o)
        if w & 0xFC000003 == 0x44000002:  # sc, any LEV
            lev = (w >> 5) & 0x7F
            addr = va + (o - off)
            # look back up to 8 insns for li r11,N  (addi r11,0,N = 0x3960xxxx) / lis r11
            r11 = None
            for k in range(1, 9):
                p, = struct.unpack_from('>I', d, o - 4 * k)
                if p & 0xFFFF0000 == 0x39600000:
                    r11 = p & 0xFFFF
                    break
            print(f'{addr:#x} lev={lev} r11={r11 if r11 is None else hex(r11)}')
