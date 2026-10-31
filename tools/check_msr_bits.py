def rldicl(val, shift, mb):
    rot = ((val << shift) | (val >> (64 - shift))) & 0xFFFFFFFFFFFFFFFF
    mask = (1 << (64 - mb)) - 1
    return rot & mask

# Check for single bit at position k:
for k in range(64):
    val = 1 << (63 - k) # PPC bit k
    res = rldicl(val, 0x32, 0x3f)
    if res == 1:
        print(f"PPC bit {k} maps to bit 63! LE bit index: {63 - k}")

# In PPC:
# bit 0 is MSB (bit 63 in LE), bit 63 is LSB (bit 0 in LE).
# Let's check MSR.PR bit:
# In PowerPC Architecture Book I/III:
# MSR[49] is PR (Problem State).
# If bit 49 is 1, user mode (PR=1). If bit 49 is 0, supervisor mode (PR=0).
