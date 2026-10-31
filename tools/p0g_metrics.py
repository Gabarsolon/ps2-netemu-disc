"""Measure address spans and recovered functions, without guessing port size."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
base = root/'local_only/analysis/p0g'
rows = []
for line in (base/'ps2_softemu/functions.tsv').read_text().splitlines():
    address,name,size = line.split()
    rows.append((int(address,16),int(size)))
spans = {'physical_driver':(0x88724,0x89f0c),'controller_and_physical_driver':(0x84160,0x89f0c),
         'auth_request':(0x8b2bc,0x8b3bc),'auth_caller_and_callback':(0x22130c,0x2215fc),
         'vuart_receive':(0x8ae28,0x8af00),'vuart_read_write':(0x42c74,0x42d88)}
result = {}
for label,(lo,hi) in spans.items():
    result[label] = {'low':hex(lo),'high_exclusive':hex(hi),'span_bytes':hi-lo,'recovered_entries':sum(lo<=a<hi for a,s in rows),'function_body_bytes':sum(s for a,s in rows if lo<=a<hi)}
(base/'metrics.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
