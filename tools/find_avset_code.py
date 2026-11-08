from pathlib import Path
import struct
import re

data = Path('local_only/fw355/out/vsh.elf').read_bytes()

# Search for any references to "avset_setvideomode" or related string offsets
# In VSH, code is in segment 0 (file off 0x0 -> VA 0x10000)
# So VA 0x5ee3e4 is at file off 0x5de3e4!
# Let's verify:
va = 0x5ee3e4
off = va - 0x10000
print(f"File off for VA 0x5ee3e4 is {hex(off)}")

# Let's see what functions call or reference avset functions or string pointers:
# Where is string 0x6b36d8 ("avset_setvideomode") referenced?
# Earlier we found it referenced at file off 0x6eb4a0 (VA 0x6fb4a0)
# In PRX, this is an export table. Let's see what is at file off 0x6eb4a0:
# [2] avset_setvideomode is index 2.
# Where is the function pointer for index 2?
# Let's find the table of function pointers:
# Often it precedes or follows the name table.
# Let's search for references to 0x5e... in that region.
for k in range(0x6eb000, 0x6eb500, 4):
    v = struct.unpack_from('>I', data, k)[0]
    if 0x5ee000 <= v <= 0x5f5000:
        print(f"  off {hex(k)}: pointer to code {hex(v)}")
