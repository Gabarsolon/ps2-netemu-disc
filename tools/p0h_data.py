"""Print mapped ELF qwords, resolving descriptor and string pointers locally."""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
module = sys.argv[1]
path = ROOT / 'local_only/fw355/out/lv1.elf' if module == 'lv1' else BASE / 'modules' / (module + '.elf')
d = path.read_bytes()
ph = [struct.unpack_from('>IIQQQQQQ', d, struct.unpack_from('>Q', d, 32)[0] + 56 * i)
      for i in range(struct.unpack_from('>H', d, 56)[0])]


def read(a, length):
    for s in ph:
        if s[3] <= a and a + length <= s[3] + s[5]:
            return d[s[2] + a - s[3]:s[2] + a - s[3] + length]
    return bytes(length)


for arg in sys.argv[2:]:
    parts = arg.split(':')
    a = int(parts[0], 16)
    size = int(parts[1], 16) if len(parts) > 1 else 0x80
    print('DATA', module, hex(a))
    for p in range(a, a + size, 8):
        value = struct.unpack('>Q', read(p, 8))[0]
        data = read(value & ~1, 24)
        indirect = struct.unpack('>QQQ', data)
        string = read(value, 96).split(bytes([0]), 1)[0]
        printable = string.decode('ascii') if string and all(32 <= x < 127 for x in string) else ''
        print(hex(p), hex(value), '/'.join(hex(v) for v in indirect), printable)
