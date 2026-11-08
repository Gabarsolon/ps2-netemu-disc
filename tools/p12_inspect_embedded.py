import struct
from pathlib import Path

lv1 = Path('local_only/fw493/lv1.elf')
data = lv1.read_bytes()

off = 0x397010
print("Bytes at 0x397010:")
print(repr(data[off : off + 64]))
