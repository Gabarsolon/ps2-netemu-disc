"""Finish P0G documentation pointer while preserving the existing line endings."""
from pathlib import Path
import py_compile

root = Path(__file__).resolve().parents[1]
path = root/'docs/P0E_OPTICAL_OPEN_ANALYSIS.md'
data = path.read_bytes()
ending = bytes([13,10]) if bytes([13,10]) in data else bytes([10])
pointer = b'**INFERRED follow-up:** [P0G softemu analysis](P0G_SOFTEMU_ANALYSIS.md) independently traces official 3.55 softemu optical I/O, VUART-10 disc authentication, launch parameters, and portability limits.'
if pointer not in data:
    split = data.index(ending)
    data = data[:split] + ending + ending + pointer + data[split:]
    path.write_bytes(data)
for p in sorted((root/'tools').glob('p0g_*.py')):
    py_compile.compile(str(p),doraise=True)
report = (root/'docs/P0G_SOFTEMU_ANALYSIS.md').read_text(encoding='utf-8')
for token in ['## 1.','## 2.','## 3.','## 4.','## 5.','0x5005','0x8202','0x8204','6,120','23,980','14,320']:
    assert token in report, token
for name in ['P0G_HYPERCALLS.md','P0G_SOFTEMU_ANALYSIS.md']:
    p = root/'docs'/name
    assert p.exists()
print('P0E pointer added/present; P0G tools compile; report sections/anchors present.')
