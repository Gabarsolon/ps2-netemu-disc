import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

softemu = Path('local_only/fw355/out/ps2_softemu.elf')
data = softemu.read_bytes()

with open(softemu, 'rb') as f:
    e = ELFFile(f)
    segs = [(s['p_vaddr'], s['p_memsz'], s['p_offset']) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']

def off_to_va(off):
    for s_va, s_sz, s_off in segs:
        if s_off <= off < s_off + s_sz:
            return s_va + (off - s_off)
    return None

print("Scanning for 'sc 1' (hypercall) in ps2_softemu.elf...")
hcalls = {}
for i in range(0, len(data) - 4, 4):
    w, = struct.unpack_from('>I', data, i)
    if w == 0x44000022 or w == 0x44000002: # sc 1 or sc 0
        va = off_to_va(i)
        if not va: continue
        # Look backwards for li r11, N
        hnum = None
        for k in range(i - 4, max(0, i - 40), -4):
            prev_w, = struct.unpack_from('>I', data, k)
            if (prev_w >> 26) == 14 and ((prev_w >> 21) & 0x1f) == 11 and ((prev_w >> 16) & 0x1f) == 0:
                hnum = prev_w & 0xffff
                if hnum >= 0x8000: hnum -= 0x10000
                break
        sc_type = "sc 1 (HV)" if w == 0x44000022 else "sc 0 (LV2)"
        print(f"  VA 0x{va:x}: {sc_type}, hcall={hnum}")
        if hnum is not None:
            hcalls[hnum] = hcalls.get(hnum, 0) + 1

print("\nSummary of hypercall / syscall numbers in ps2_softemu.elf:")
for num, count in sorted(hcalls.items()):
    print(f"  hcall {num}: {count} occurrences")
