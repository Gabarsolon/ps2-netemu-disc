"""Report P0G constant hypercalls, addresses and direct caller lower bounds."""
from pathlib import Path
import collections
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'local_only/analysis/p0g'
names = {}
abi = ROOT/'local_only/research/lv1call_web.txt'
if abi.exists():
    names.update({int(n):s for s,n in re.findall(r'LV1_CALL\((\w+),\s*\d+,\s*\d+,\s*(\d+)\s*\)',abi.read_text(encoding='utf-8'))})
names.update({178:'read_pci_config',179:'write_pci_config'})
inventories = {}
for variant in ['ps2_softemu','ps2_gxemu','ps2_emu','netemu']:
    p = BASE/variant/'sc_inventory.json'
    if variant == 'netemu' and not p.exists(): p = ROOT/'local_only/analysis/sc_inventory.json'
    if not p.exists(): continue
    rows = json.loads(p.read_text())
    for r in rows:
        if variant == 'netemu': r['lev'] = 1 if 'lev=1' in r.get('scan','') else 0
    inventories[variant] = rows
summary = {}
for v, rows in inventories.items():
    kept = [r for r in rows if r.get('hypercall') is not None and (r['lev']==1 or r.get('forwarded')) and not (v=='netemu' and int(r['site'],16)==0x13730)]
    summary[v] = {'raw_sc':len(rows),'sc1':sum(r['lev']==1 for r in rows),'forwarded':sum(bool(r.get('forwarded')) for r in rows),
                  'constant_counts':dict(sorted(collections.Counter(r['hypercall'] for r in kept).items())),
                  'unresolved_sc1':[r['site'] for r in rows if r['lev']==1 and r.get('hypercall') is None]}
lines = ['# P0G hypercall inventory', '', '**PROVEN (PC):** raw opcode counts; **INFERRED:** locally reconstructed constant numbers, wrapper grouping and names. These are static candidates, not execution counts or permission grants. Indirect callers and dynamic numbers remain **UNKNOWN**. Official 3.55 inputs are distinct from P0D community inputs. The stock-netemu inventory is reused from P0 and excludes opcode template 0x13730.', '', '| LV1 / name | softemu 3.55 | gxemu 3.55 | emu 3.55 | stock netemu |','|---|---:|---:|---:|---:|']
alln = sorted({int(n) for v in summary.values() for n in v['constant_counts']})
for n in alln:
    lines.append(f'| {n} `{names.get(n,"UNKNOWN name")}` | '+' | '.join(str(summary[v]['constant_counts'].get(n,0)) for v in inventories)+' |')
v = 'ps2_softemu'
rows = inventories[v]
b = (ROOT/'local_only/fw355/out/ps2_softemu.elf').read_bytes()
segs = [struct.unpack_from('>IIQQQQQQ',b,struct.unpack_from('>Q',b,32)[0]+56*i) for i in range(struct.unpack_from('>H',b,56)[0])]
callers = collections.defaultdict(set)
for typ,flags,off,va,pa,sz,ms,al in segs:
    if typ != 1 or not flags & 1: continue
    for p in range(off,off+sz-3,4):
        w = struct.unpack_from('>I',b,p)[0]
        if w >> 26 != 18 or not w & 1: continue
        disp = w & 0x3fffffc
        if disp & 0x2000000: disp -= 0x4000000
        addr = va+p-off
        dst = disp if w & 2 else addr+disp
        callers[dst].add(addr)
groups = collections.defaultdict(list)
for r in rows:
    if r['lev']==1 or r.get('forwarded'):
        groups[(r.get('function'),r.get('hypercall'),r['lev'])].append(r)
lines += ['', '**INFERRED:** all softemu LV1 candidates grouped by containing Ghidra function and constant number. Direct-call counts are raw `bl` references to that entry (lower bounds); an unknown boundary has no count. A row can contain several sites. No high-bit guest forwarding was recovered.', '', '| Wrapper | LV1 | Direct calls | Sites |','|---|---|---:|---|']
for (f,n,lev), group in sorted(groups.items(),key=lambda x:(x[0][0] or '',x[0][1] if x[0][1] is not None else -1)):
    lines.append(f'| {"0x"+f if f else "UNKNOWN boundary"} | {n if n is not None else "UNKNOWN dynamic"} | {len(callers[int(f,16)]) if f else "UNKNOWN"} | '+', '.join(r['site'] for r in group)+' |')
(ROOT/'docs/P0G_HYPERCALLS.md').write_text(chr(10).join(lines)+chr(10),encoding='utf-8')
(BASE/'inventory_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
