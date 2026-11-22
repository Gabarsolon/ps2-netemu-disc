"""Byte-checked existing evidence and exact bit-operation models; no JVM."""
from pathlib import Path
import hashlib
import json
import re
import struct

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'local_only/mapping_snapshot'
MASK=(1<<64)-1

def sha(b): return hashlib.sha256(b).hexdigest()
class Elf:
    def __init__(self,rel,want):
        self.b=(ROOT/rel).read_bytes(); assert sha(self.b)==want
        p=struct.unpack_from('>Q',self.b,32)[0]
        self.ph=[struct.unpack_from('>IIQQQQQQ',self.b,p+56*i)
                 for i in range(struct.unpack_from('>H',self.b,56)[0])]
    def rd(self,a,n):
        return next(self.b[p[2]+a-p[3]:p[2]+a-p[3]+n] for p in self.ph
                    if p[0]==1 and p[3]<=a and a+n<=p[3]+p[5])
    def q(self,a): return int.from_bytes(self.rd(a,8),'big')

def rol(x,n): return ((x<<n)|(x>>(64-n)))&MASK
def md(word,regs):
    """Decode MD operands from stock bytes, implementing only used forms."""
    assert word>>26==30
    rs,ra=(word>>21)&31,(word>>16)&31
    sh=((word>>11)&31)|((word&2)<<4)
    mb=((word>>6)&31)|(word&32)
    op=(word>>2)&7
    v=rol(regs[rs],sh)
    if op==0: mask=(1<<(64-mb))-1 # rldicl
    elif op==1: mask=(MASK<<(63-mb))&MASK # rldicr
    elif op==3: mask=((1<<(64-mb))-1)&((MASK<<sh)&MASK) # rldimi
    else: raise AssertionError(hex(word))
    regs[ra]=(v&mask)|((regs.get(ra,0)&~mask) if op==3 else 0)

def prove(bridge):
    stock=Elf('local_only/stock.elf','63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3')
    lv=Elf('local_only/fw493/lv1.elf','e8d0b532adf6ba6c6c1ea40a5c5b86407abe11ea7a3ab8624ca5b09d3e4c3d6b')
    hashes={}; checked={}; rows={}
    for rel,e in [('cache_mapping_review/pte_mapper.asm',stock),
                  ('cache_mapping_finish/lv1_002d1720.asm',lv),
                  ('cache_mapping_finish/lv1_002ecaf8.asm',lv),
                  ('private_staging_review/stock_b9000_selected.asm',stock),
                  ('private_staging_review/fn_00019900_selected.asm',stock)]:
        b=(ROOT/'local_only'/rel).read_bytes(); hashes[rel]=sha(b); n=0
        for line in b.decode('utf-8-sig').splitlines():
            m=re.match(r'^([0-9a-f]{8}): ([0-9a-f]{8}) (.*)',line)
            if m:
                pc=int(m[1],16); assert e.rd(pc,4).hex()==m[2],(rel,m[1])
                rows[pc]=m[3]; n+=1
        assert n; checked[rel]=n
    def word(pc): return int.from_bytes(stock.rd(pc,4),'big')
    assert [word(p) for p in (0x16990,0x16994,0x16998)]==[0x3960005f,0x656b8000,0x44000002]
    assert [word(p) for p in (0x16c20,0x16c24,0x16c28)]==[0x3960005f,0x656b8000,0x44000002]
    assert stock.q(0x751280-0x7e50)==0x930f80
    assert rows[0x16988]=='ld r3,0x18(r17)' # 930f98
    assert rows[0x16844]=='ld r9,0x30(r17)' # 930fb0
    assert rows[0x16a38]=='li r29,0x14' and rows[0x16a3c]=='li r18,0x2'
    assert rows[0x2d1810]=='lhz r0,0xe(r9)'
    assert rows[0x2d1800]=='rldicr r11,r7,0x10,0x2f'
    assert rows[0x2d1808]=='addi r10,r10,0x10'
    assert rows[0x2d1814]=='or r7,r11,r0'
    assert rows[0xb98d4]=='std r3,0x40(r29)' and rows[0xb98d8]=='std r3,0x28(r31)'
    assert rows[0xb98bc]=='addis r3,r3,0x2'
    gate=json.loads((ROOT/'local_only/private_staging_review/helper_gate.json').read_text())
    assert gate['hash_before']==sha(stock.b)
    assert sha((ROOT/gate['source']).read_bytes())==gate['source_sha256']
    assert gate['single_bank_gate']['root_slot']=='H+0x08'
    assert gate['single_bank_gate']['root']=='H+0x38'
    assert 'H+0x10008' in gate['single_bank_gate']['growth_marker']
    assert 0x2446560+0x10008==0x2456568 and 0x2446560+0x10040==0x24565a0
    assert 0x2446560+0x28==0x2446588
    # Exact stock MD words model all segment-8 1MiB virtual pages. Independent
    # fixed inputs at the arithmetic slice, not real mapper/HV execution.
    models=[]
    for ea in range(0x80000000,0x90000000,0x100000):
        v=ea-0x10000000; r={24:v,18:2,31:0,0:(-2)&MASK}
        md(word(0x16910),r); md(word(0x1691c),r)
        r[31]|=1
        md(word(0x16928),r); md(word(0x1692c),r); md(word(0x16934),r); md(word(0x1693c),r)
        assert r[31]==((v>>23)<<7)|5,(hex(ea),hex(r[31]))
        r[0]=v>>20; r[0]&=255; md(word(0x16964),r)
        h=r[0]^r[11]; assert h==((v>>20)&255)^7
        for size in (0x40000,0x80000,0x100000):
            mask=(size>>7)-1
            groups=((h&mask)*8,(~h&mask)*8)
            assert all(g%8==0 and g+8<=size//16 for g in groups)
        models.append(dict(EA=hex(ea),virtual=hex(v),V=hex(r[31]),hash=hex(h)))
    assert next(m for m in models if m['EA']=='0x84000000')['V']=='0x7405'
    # Audit EVERY bridge instruction against an exact reviewed sequence.
    expected=[('mflr',['r0']),('std',['r0','16(r1)']),('stdu',['r1','-128(r1)']),
              ('std',['r2','112(r1)']),('mfcr',['r0']),('std',['r0','104(r1)']),
              ('std',['r31','96(r1)']),('mr',['r31','r5']),('li',['r11','95']),
              ('oris',['r11','r11','32768']),('sc',['0'])]
    expected += [('std',['r'+str(i+4),str(8*i)+'(r31)']) for i in range(5)]
    expected += [('ld',['r31','96(r1)']),('ld',['r2','112(r1)']),('ld',['r0','104(r1)']),
                 ('mtcr',['r0']),('addi',['r1','r1','128']),('ld',['r0','16(r1)']),('mtlr',['r0']),('blr',[])]
    assert [(r['op'],r['args']) for r in bridge]==expected
    assert bridge[10]['word']=='44000002'
    for i,w in {0:0x7c0802a6,4:0x7c000026,7:0x7cbf2b78,8:0x3960005f,
                9:0x656b8000,10:0x44000002,19:0x7c0ff120,20:0x38210080,
                22:0x7c0803a6,23:0x4e800020}.items():
        assert int(bridge[i]['word'],16)==w,(i,bridge[i])
    assert all(r['address']==0x4a40+4*i for i,r in enumerate(bridge))
    # Exact inverse D-form encodings independent of the template encoder.
    for r in bridge:
        if r['op'] in ('std','stdu','ld'):
            rt=int(r['args'][0][1:]); m=re.fullmatch(r'(-?\d+)\(r(\d+)\)',r['args'][1])
            w=(58 if r['op']=='ld' else 62)<<26|rt<<21|int(m[2])<<16|(int(m[1])&65535)|(r['op']=='stdu')
            assert int(r['word'],16)==w
    result=dict(status='PASS_STATIC_BYTES_AND_ARITHMETIC',listing_words=checked,hashes=hashes,
                modeled_pages=models,bridge_instructions=bridge,
                bridge_contract='r3 handle, r4 covered index, r5 local 40-byte stack output; returns r3 status, captures BE r4..r8; preserves LR/SP/r2/CR/r31; other nonvolatiles untouched',
                bank_words='fixed metadata samples only; no geometry, ownership or headroom claim',
                limits='No compiled PPC execution, actual syscall/HV, live SLB/TLB or full RPN proof')
    (OUT/'mapping_evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
