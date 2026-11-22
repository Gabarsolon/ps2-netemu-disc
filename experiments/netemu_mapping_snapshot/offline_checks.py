"""One offline compile/audit pass; never imports or starts pyghidra/JVM."""
from pathlib import Path
import ast
import hashlib
import json
import runpy
import struct

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'local_only/mapping_snapshot'

def main():
    for p in HERE.rglob('*.py'): ast.parse(p.read_text(),filename=str(p))
    baseline=ROOT/'experiments/netemu_snapshot/src/snapshot.c'
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()=='bd1da7fa70ed2c34cea6674e8cad61378e452f43ad29775d3b93fb99180bc094'
    before=baseline.read_text(); after=(HERE/'src/snapshot.c').read_text()
    for start,end in [('static int ui_reason_ok','static __attribute__((noinline)) void write_snapshot'),
                      ('u64 snapshot_shutdown',None)]:
        a=before[before.index(start):]; b=after[after.index(start):]
        if end: a=a[:a.index(end)]; b=b[:b.index(end)]
        assert a==b,(start,'baseline behavior changed')
    runpy.run_path(str(HERE/'build.py'))['build']()
    decoder=runpy.run_path(str(HERE/'decode.py'))['decode']
    q=[0]*64
    q[0]=0x4d41505345433100; q[1]=0x1000000000200; q[4]=0xb46100; q[5]=2
    cases=[]
    for code in range(7):
        for base,ea in [(40,0x84000000),(48,0x80000000)]:
            v=ea-0x10000000; mask=(0x40000>>7)-1; h=((v>>20)&255)^7
            p,s=(h&mask)*8,(~h&mask)*8
            q[base:base+8]=[ea,v,((v>>23)<<7)|5,p<<32|s,code,
                            (1<<64)-5 if code==3 else 0,
                            (4<<32)|1 if code==6 else 0,0xffffffff00000000]
            if code==6: q[base+7]=p<<32|0x102c<<16|0x28
        decoded=decoder(struct.pack('>64Q',*q))
        assert all(m['WIMG']==('0x28' if code==6 else None) for m in decoded['mappings'])
        cases.append(dict(outcome=code,decoded=decoded['mappings']))
    errors=[]
    for label,word,value in [('wrong_magic',0,0),('wrong_version',1,0),('reserved',7,1),
                             ('false_unique',46,0),('bad_mask',47,0),('unknown_outcome',44,7)]:
        bad=q.copy(); bad[word]=value
        try: decoder(struct.pack('>64Q',*bad))
        except ValueError: errors.append(label)
        else: raise AssertionError(('decoder accepted',label))
    registered=[]
    runpy.run_path(str(HERE/'mapping_cases.py'))['run_mapping_cases'](
        lambda name,fn:registered.append(name),0xaaa7013fcf0,(1<<64)-1)
    assert len(registered)==len(set(registered))
    result=dict(status='PASS_OFFLINE_COMPILE_STATIC_AND_DECODER_ONLY',
                syntax='all new Python parsed',baseline_timer_refresh_shutdown='byte-identical source slices',
                decoder_synthetic_cases=cases,decoder_rejections=errors,
                parent_mapping_cases_registered_only=registered,
                parent_PPC='NOT RUN',hardware='NOT RUN',JVM='NOT STARTED')
    (OUT/'offline_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS offline compile/static audits/decoder;',len(registered),'mapping cases prepared, NOT RUN; JVM NOT STARTED')

if __name__=='__main__': main()
