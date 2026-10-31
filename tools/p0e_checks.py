"""Independent raw-word checks of P0E's constant-open inventory and anchors."""
from pathlib import Path
import hashlib, json, struct

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'local_only'/'analysis'/'p0e'
cases = {
 'ps2_emu': ('local_only/variants/ps2_emu.elf','3af1ba14806df8d71b277682dec4c60e20c9552a73b6612439c0d0e701981252', [0x1d4a0,0x22524,0x26a94,0x28e84,0x42f14,0xfbcdc]),
 'ps2_gxemu': ('local_only/variants/ps2_gxemu.elf','365769d75cb05c4c48602eb163e54593669834ede253d7c5d26e59795edde36c',[0x41494,0x56c74,0x6b884,0x8d600,0x92ad8,0x95fb0]),
 'netemu': ('local_only/stock.elf','63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3',[0x19d48,0x12bf8c,0x137b68,0x1e79a4])
}
result = {}
for variant,(path,digest,expected) in cases.items():
    b=(ROOT/path).read_bytes()
    assert hashlib.sha256(b).hexdigest() == digest
    segs=[struct.unpack_from('>IIQQQQQQ',b,struct.unpack_from('>Q',b,32)[0]+56*i) for i in range(struct.unpack_from('>H',b,56)[0])]
    def word(n):
        for typ,flags,off,va,pa,size,ms,align in segs:
            if typ==1 and va<=n and n+4<=va+size:
                return struct.unpack_from('>I',b,off+n-va)[0]
        raise ValueError(hex(n))
    found=[]
    for typ,flags,off,va,pa,size,ms,align in segs:
        if typ!=1 or not flags&1: continue
        for pos in range(off,off+size-4,4):
            w=struct.unpack_from('>I',b,pos)[0]
            if w not in (0x44000002,0x44000022): continue
            n=va+pos-off
            # A bounded raw constant-r11 walk; dynamic cases are not resolved.
            r11=None
            for pc in range(max(va,n-96),n,4):
                v=word(pc)
                if v>>16 == 0x3960: r11=v&0xffff
                elif v == 0x656b8000 and r11 is not None: r11|=0x80000000
                elif v in (0x44000002,0x44000022): r11=None
            if (w==0x44000022 and r11==170) or (w==0x44000002 and r11==0x800000aa):
                found.append(n)
    assert sorted(found)==sorted(expected),(variant,found)
    flags={}
    for n in found:
        candidates=[pc for pc in range(n-64,n,4) if word(pc)==0x38a00000]
        assert candidates,(variant,hex(n))
        flags[hex(n)]={'li_r5_zero_at':hex(max(candidates)),'open_opcode':hex(word(n))}
    if variant=='netemu':
        for n,w in {0x10578:0x39400002,0x10590:0x9949000c,0x114dc8:0x4e800020,0xf58:0x3860011f,0xf5c:0x396000ff,0xf60:0x44000022}.items():
            assert word(n)==w,(hex(n),hex(word(n)))
    result[variant]={'sha256':digest,'constant_170_sites':flags}
(OUT/'checks.json').write_text(json.dumps(result,indent=2))
print('PASS: hashes, all 16 constant-open sites, zero-flags anchors, bridge initializer/panic and HDD no-op helper')
