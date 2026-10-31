"""Inventory mapped module strings locally, printing only the chosen regex."""
from pathlib import Path
import json
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0h'
module = sys.argv[1]
d = (BASE / 'modules' / (module + '.elf')).read_bytes()
rows = []
for i in range(struct.unpack_from('>H', d, 56)[0]):
    s = struct.unpack_from('>IIQQQQQQ', d, struct.unpack_from('>Q', d, 32)[0] + 56 * i)
    for m in re.finditer(rb'[ -~]{4,}', d[s[2]:s[2] + s[5]]):
        row = {'address': hex(s[3] + m.start()), 'value': m[0].decode('ascii')}
        rows.append(row)
        if re.search(sys.argv[2], row['value'], re.I):
            print(row)
(BASE / (module + '_strings.json')).write_text(json.dumps(rows, indent=2))
