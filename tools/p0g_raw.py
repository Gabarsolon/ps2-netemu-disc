"""Independent raw ELF word/branch survey, with detailed evidence kept local."""
from pathlib import Path
import collections
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'local_only/analysis/p0g'
for name in ['ps2_softemu', 'ps2_gxemu', 'ps2_emu', 'netemu', 'vsh']:
    path = ROOT / 'local_only' / ('stock.elf' if name == 'netemu' else 'fw355/out/' + name + '.elf')
    if not path.exists(): continue
    b = path.read_bytes()
    segs = [struct.unpack_from('>IIQQQQQQ', b, struct.unpack_from('>Q',b,32)[0]+56*i) for i in range(struct.unpack_from('>H',b,56)[0])]
    sc, immediates, strings = [], [], []
    for typ,fl,off,va,pa,sz,ms,al in segs:
        if typ != 1: continue
        if fl & 1:
            for p in range(off,off+sz-3,4):
                w = struct.unpack_from('>I',b,p)[0]
                n = va+p-off
                if w in [0x44000002,0x44000022]:
                    val = None
                    for q in range(max(off,p-96),p,4):
                        x = struct.unpack_from('>I',b,q)[0]
                        if x & 0xffff0000 == 0x39600000:
                            val = x & 0xffff
                            if val & 0x8000: val -= 0x10000
                        elif x == 0x656b8000 and val is not None: val |= 0x80000000
                        elif x in [0x44000002,0x44000022]: val = None
                    sc.append({'site':hex(n),'lev':(w>>5)&1,'r11':val})
                if w & 0xffff in [0x8202,0x8204,0x4f0] and w >> 26 in [14,24,28,10,11]:
                    immediates.append({'site':hex(n),'word':hex(w)})
        for m in re.finditer(rb'[ -~]{5,}', b[off:off+sz]):
            s = m.group().decode()
            if re.search('ps2.*self|ps2boot|shutdown|bootparam',s,re.I): strings.append({'address':hex(va+m.start()),'value':s})
    result = {'sha256':hashlib.sha256(b).hexdigest(),'sc':sc,'immediates':immediates,'strings':strings}
    (OUT/(name+'_raw.json')).write_text(json.dumps(result,indent=2))
    print(name,'sc',dict(collections.Counter(x['lev'] for x in sc)), 'selected immediates',immediates, 'launch strings',strings)
