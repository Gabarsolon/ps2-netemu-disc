"""PARENT LATER: actual compiled PPC/hooks/trampolines with native UFS models.

Requires explicitly free sole JVM. No installer, network, device access, or
existing harness imports. Modeled instant UFS cannot prove cold-cache IRQ
liveness, native lock concurrency, hardware flush, or XMB recovery.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'local_only/mapping_snapshot'
MAIL,REASON,SP,STOP=0x930f20,0x934161,0xaaa7013fcf0,0x7ff0
MASK=(1<<64)-1
TIMER=0x53544d5230303031
PUBLISHING=0x5350554230303031
TERMINAL=0x534e503100000000
CONSUMED=0x534e433100000000
DELAY=20*79800000
HDD=[(0x241c8d5,1,1),(0x241c8c8,0,1),(0x241c860,3,8),
     (0x241c888,0,8),(0x241c890,0,8),(0x241c898,0,8),(0x3055180,0,4)]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-jvm',required=True,action='store_true')
    parser.parse_args()
    review=json.loads((OUT/'build_review.json').read_text())
    elf=OUT/'ps2_netemu_mapping_snapshot.elf'
    assert hashlib.sha256(elf.read_bytes()).hexdigest()==review['elf_sha256']
    assert hashlib.sha256((HERE/'src/snapshot.c').read_bytes()).hexdigest()==review['source_sha256']
    for rel,want in review['sources'].items():
        assert hashlib.sha256((HERE/rel).read_bytes()).hexdigest()==want,rel
    work=OUT/'pc'
    for d in ('tmp','settings','projects'): (work/d).mkdir(parents=True,exist_ok=True)
    for k in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA'):
        os.environ[k]=str(work/('tmp' if k in ('TEMP','TMP','TMPDIR') else 'settings'))
    os.environ['JAVA_HOME']='C:/Program Files/Microsoft/jdk-21.0.12.101-hotspot'
    os.environ['GHIDRA_INSTALL_DIR']='C:/ghidra_12.1.3_PUBLIC'
    from pyghidra.launcher import HeadlessPyGhidraLauncher
    import pyghidra
    launcher=HeadlessPyGhidraLauncher(); launcher.java_home=os.environ['JAVA_HOME']
    launcher.add_vmargs('-Xmx3G','-Duser.home='+str(work/'settings'),
                       '-Dapplication.settingsdir='+str(work/'settings'),'-Djava.io.tmpdir='+str(work/'tmp'))
    launcher.start()
    from ghidra.app.emulator import EmulatorHelper
    from ghidra.util.task import ConsoleTaskMonitor
    from java.math import BigInteger
    results=[]
    with pyghidra.open_program(str(elf),project_location=str(work/'projects'),
                              project_name='mapping_snapshot_'+review['elf_sha256'][:12],
                              analyze=False,language='PowerPC:BE:64:default') as flat:
        program=flat.getCurrentProgram(); space=program.getAddressFactory().getDefaultAddressSpace()
        class Machine:
            def __init__(self):
                self.em=EmulatorHelper(program); self.monitor=ConsoleTaskMonitor()
                self.now=79800000*1000; self.calls=[]; self.native_refreshes=0; self.native_shutdowns=0
                self.reason_stores=0; self.snapshots=[]; self.stores=set(); self.barriers=0
                self.fd=2; self.size=65536; self.stat_rc=0; self.write_rc=512; self.close_rc=0
                self.effect=None; self.clock_effect=None; self.original_effect=None
                self.queries=[]; self.query_fail=None; self.query_effect=None
                self.htab=0x12345000; self.htab_size=0x40000; self.pool_ea=0x80000000
                self.entries={}; self.raw_queries=[]; self.expected_queries=None
                self.bridge_saved=None; self.bridge_only=False
                self.fixture_bytes(MAIL,bytes(96))
                for a,v,w in HDD: self.fixture(a,v,w)
                for a,v,w in [(REASON,0,1),(0x306fc68,0x30700d0,8),(0x30700d0,0x949cb8,8),
                              (0x241c850,2,4),(0x241c8a8,7,4),(0x2458428,0x84000000,8),
                              (0x2458430,0x100000,8),(0x2458438,0x500002c00000,8)]: self.fixture(a,v,w)
                for a,v in [(0x930f98,self.htab),(0x930fb0,self.htab_size),
                            (0x934960,0x60000),(0x934968,1),(0x934970,0x40000000),
                            (0x934980,self.pool_ea),(0x24565b8,self.pool_ea),
                            (0x2446588,self.pool_ea+0x20000),(0x24565a0,self.pool_ea+0x20000),
                            (0x2446568,0x2446598),(0x2446598,0),(0x2456568,0)]: self.fixture(a,v)
                self.install_entry(0x84000000,0,0x1014)
                self.install_entry(self.pool_ea,0,0x102c)
                self.em.enableMemoryWriteTracking(True)
            def groups(self,ea):
                v=ea-0x10000000; h=((v>>20)&255)^7; mask=(self.htab_size>>7)-1
                return (h&mask)*8,(~h&mask)*8
            def install_entry(self,ea,slot,low):
                p,s=self.groups(ea); v=(((ea-0x10000000)>>23)<<7)|5
                self.entries[(p if slot<8 else s)+(slot%8)]=(v|(2 if slot>=8 else 0),low)
            def record(self,target=0):
                q=struct.unpack('>64Q',self.snapshots[-1]); b=40+8*target
                return q[b:b+8]
            def assert_record(self,ea,target=0,code=6,queries=4,matches=1,status=0,index=None,low=None):
                r=self.record(target)
                assert r[0]==ea and r[4:7]==(code,status,queries<<32|matches),r
                if code==6:
                    assert index is not None and low is not None
                    assert r[7]==index<<32|low<<16|(low&0x78),r
                else: assert r[7]==0xffffffff00000000,r
            def put(self,n,v): self.em.writeRegister(n,BigInteger(str(v&MASK)))
            def get(self,n): return int(str(self.em.readRegister(n)))&MASK
            def pc(self,p): self.put(self.em.getPCRegister(),p)
            def rd(self,a,n): return bytes(self.em.readMemory(space.getAddress(a),n))
            def q(self,a): return int.from_bytes(self.rd(a,8),'big')
            def fixture_bytes(self,a,b):
                self.em.enableMemoryWriteTracking(False); self.em.writeMemory(space.getAddress(a),b)
                self.em.enableMemoryWriteTracking(True)
            def fixture(self,a,v,n=8): self.fixture_bytes(a,(v&((1<<(n*8))-1)).to_bytes(n,'big'))
            def state(self): return struct.unpack('>12Q',self.rd(MAIL,96))
            def active(self,count=99):
                self.start=self.now-DELAY
                self.fixture_bytes(MAIL,struct.pack('>12Q',TIMER,self.start,self.start,count,1,*([0]*7)))
            def allowed(self,lo,hi):
                return MAIL<=lo<hi<=MAIL+96 or lo==REASON and hi==REASON+1 or SP-8192<=lo<hi<=SP+32
            def ret(self,v):
                target=self.get('lr')
                for r in [0,*range(3,13)]: self.put('r'+str(r),0xdad0000000000000+r)
                for r in (0,1,5,6,7): self.put('cr'+str(r),15-r)
                self.put('ctr',0x12345678); self.put('xer',0); self.put('r3',v); self.pc(target)
            def call(self,shutdown=False,args=None,bridge=False):
                args=args or ([0xb46100,2,3,4,5,6,7,8] if shutdown else [0x8100000000000000+i for i in range(8)])
                expected=0xfedcba9876543210
                incoming=0x751280 if shutdown else 0x123456780000
                saved={**{'r'+str(r):0xabcd000000000000+r for r in range(13,32)},
                       **{'cr'+str(r):r+2 for r in (2,3,4)}}
                for n,v in saved.items(): self.put(n,v)
                self.put('r1',SP); self.put('r2',incoming); self.put('lr',STOP)
                for i,v in enumerate(args,3): self.put('r'+str(i),v)
                if bridge:
                    self.pc(0x4a40); return_to=STOP
                elif shutdown:
                    # Execute the actual patched BL, then stop at its unmodified
                    # return instruction. Do not execute cleanup at 112444.
                    self.pc(0x11243c)
                    assert self.em.step(self.monitor)
                    return_to=0x112440
                else:
                    self.pc(0xbc168); return_to=STOP
                first=len(self.calls); initial_mail=self.rd(MAIL,96); initial_reason=self.rd(REASON,1)
                rel_sp=None; original_count=0
                bridge_before=None
                for step in range(16000):
                    pc=self.em.getExecutionAddress().getOffset()&MASK
                    if pc==return_to: break
                    if self.effect: self.effect(self,pc)
                    if pc==0x4a40:
                        ptr=self.get('r5')
                        assert ptr%8==0 and SP-8192<=ptr<ptr+40<=SP
                        assert self.get('r3')==self.htab
                        bridge_before={n:self.get(n) for n in ['r1','r2','lr',*['r'+str(i) for i in range(13,32)],'cr2','cr3','cr4']}
                        self.bridge_saved=ptr
                    if pc==0x4aa0: # 24-instruction bridge returns to real caller
                        raise AssertionError('bridge exceeds reviewed extent')
                    if bridge_before is not None and pc==bridge_before['lr']:
                        assert all(self.get(n)==v for n,v in bridge_before.items()),'call95 bridge ABI'
                        bridge_before=None
                    if pc in (0xbc16c,0x11b9bc):
                        assert self.get('r2')==0x751280
                        assert [self.get('r'+str(i)) for i in range(3,11)]==args
                        assert self.rd(MAIL,96)==initial_mail and self.rd(REASON,1)==initial_reason, 'original must precede payload stores'
                        assert len(self.calls)==first
                        if pc==0xbc16c:
                            assert not shutdown and rel_sp is not None
                            assert self.get('r1')==rel_sp-320 and self.q(rel_sp-320)==rel_sp
                            self.put('r1',rel_sp); self.native_refreshes+=1
                        else:
                            assert shutdown; self.native_shutdowns+=1
                            if self.original_effect: self.original_effect(self)
                        self.calls.append('original'); original_count+=1; self.ret(expected); continue
                    if pc==0xb9cd0:
                        assert not shutdown and original_count==1 and self.get('r2')==0x751280
                        self.calls.append('clock')
                        if self.clock_effect: self.clock_effect(self)
                        self.ret(self.now); continue
                    boundary={0x1ecc5c:'open',0x1ec760:'stat',0x1ed458:'write',0x1ecb10:'close'}.get(pc)
                    if boundary:
                        assert shutdown and original_count==1 and self.get('r2')==0x751280
                        assert self.q(MAIL)&0xffffffff00000000==CONSUMED
                        self.calls.append(boundary)
                        if boundary=='open':
                            assert self.get('r3')==0
                            pointer=self.get('r4'); path=self.rd(pointer,33).split(bytes([0]))[0]
                            assert path==b'/tmp/netemu_mapping_snapshot.bin'
                            self.ret(self.fd)
                        elif boundary=='stat':
                            assert self.get('r3')==self.fd
                            p=self.get('r4'); assert p%8==0 and self.allowed(p,p+48)
                            self.fixture_bytes(p,struct.pack('>6Q',11,22,33,44,55,self.size)); self.ret(self.stat_rc)
                        elif boundary=='write':
                            assert self.get('r3')==self.fd and self.get('r4')==0 and self.get('r6')==512
                            p=self.get('r5'); assert p%8==0 and self.allowed(p,p+512)
                            sector=self.rd(p,512); q=struct.unpack('>64Q',sector)
                            assert q[0]==0x4d41505345433100 and q[1]==0x1000000000200
                            assert q[4:7]==(0xb46100,2,expected)
                            assert q[8]==q[2] and q[9:20]==self.state()[1:12]
                            assert q[36:38]==(self.size,self.fd)
                            assert q[38:40]==(0,0) and q[56:]==(0,)*8 and q[7]==0
                            assert all(c=='original' or c=='clock' or c=='query95' for c in self.calls[:self.calls.index('open')])
                            self.snapshots.append(sector); self.ret(self.write_rc)
                        else:
                            assert self.get('r3')==self.fd; self.ret(self.close_rc)
                        continue
                    assert pc in (0xbc168,0x11243c) or 0x4800<=pc<int(review['code_end'],16),('unexpected execution',hex(pc))
                    if pc==0x4ac0: rel_sp=self.get('r1')
                    w=int.from_bytes(self.rd(pc,4),'big'); op=w>>26
                    if op==17:
                        assert pc==0x4a68 and w==0x44000002
                        assert bridge or shutdown and original_count==1
                        assert self.get('r11')==0x8000005f
                        assert self.get('r3')==self.htab==self.q(0x930f98)
                        first_index=self.get('r4')
                        assert self.q(0x930fb0)==self.htab_size
                        assert first_index%4==0 and first_index+4<=self.htab_size//16
                        assert self.get('r5')==self.bridge_saved
                        if not bridge:
                            assert self.q(MAIL)&0xffffffff00000000==CONSUMED
                            assert self.calls[-1] in ('original','query95')
                        if self.expected_queries is not None:
                            assert first_index==self.expected_queries[len(self.queries)]
                        qn=len(self.queries); rc=0 if self.query_fail!=qn else 0xfffffffffffffffb
                        vs=[self.entries.get(first_index+j,(0,0))[0] for j in range(4)]
                        lows=[self.entries.get(first_index+j,(0,0))[1] for j in range(4)]
                        packed=sum(low<<(16*(3-j)) for j,low in enumerate(lows))
                        values=[*vs,packed] if rc==0 else [MASK]*5
                        self.queries.append(first_index); self.calls.append('query95')
                        # Emulate only syscall boundary. Poison volatile state,
                        # including TOC/CR to prove bridge restoration; retain
                        # kernel ABI SP/LR/nonvolatile GPRs. Real HV NOT run.
                        for rr in [0,*range(3,13)]: self.put('r'+str(rr),0xeeee000000000000+rr)
                        for rr in range(8): self.put('cr'+str(rr),15-rr)
                        self.put('r2',0xdeadbeef); self.put('ctr',MASK); self.put('xer',0)
                        self.put('r3',rc)
                        for rr,v in enumerate(values,4): self.put('r'+str(rr),v)
                        self.raw_queries.append(dict(index=first_index,status=rc,outputs=values))
                        if self.query_effect: self.query_effect(self,qn)
                        self.pc(pc+4); continue
                    # Catch every emitted payload store before execution.
                    if op in (36,37,38,39,44,45,47,62):
                        assert op in (36,38,44,62),('unreviewed store',hex(pc),hex(w))
                        rt,ra=w>>21&31,w>>16&31
                        width={36:4,38:1,44:2,62:8}[op]
                        disp=w&(0xfffc if op==62 else 0xffff)
                        if disp&0x8000: disp-=0x10000
                        a=((self.get('r'+str(ra)) if ra else 0)+disp)&MASK
                        assert self.allowed(a,a+width),('store bound',hex(pc),hex(a),width)
                        self.stores.add((a,a+width))
                        if a==REASON:
                            assert self.q(MAIL)&0xffffffff00000000==TERMINAL
                            assert self.rd(REASON,1)==bytes([0]) and self.get('r'+str(rt))&255==2
                            assert self.state()[1:7]==(0x30700d0,0x949cb8,3,0,0,0)
                            assert self.state()[7:10]==tuple(self.q(a) for a in (0x2458428,0x2458430,0x2458438))
                            assert self.state()[11]==0x10000
                            self.reason_stores+=1
                    if op in (52,53,54,55): raise AssertionError(('FP store',hex(pc)))
                    if op==31:
                        xo=w>>1&1023
                        assert xo not in (149,150,151,181,183,214,215,231,247,407,439,487,663,695,727,759),('indexed store',hex(pc))
                        spr=(w>>16&31)|(w>>6&0x3e0)
                        if xo in (339,371) and spr==268:
                            assert shutdown # inline clock, no stock helper
                            self.put('r'+str(w>>21&31),self.now); self.pc(pc+4); continue
                    if w in (0x7c0004ac,0x7c2004ac,0x4c00012c):
                        self.barriers+=1; self.pc(pc+4)
                    else: assert self.em.step(self.monitor),(hex(pc),str(self.em.getLastError()))
                else: raise AssertionError('bounded PPC instruction budget exhausted')
                if bridge:
                    assert original_count==0 and len(self.queries)==1
                    assert self.rd(args[2],40)==struct.pack('>5Q',*self.raw_queries[-1]['outputs'])
                    assert self.get('r3')==self.raw_queries[-1]['status']
                else:
                    assert original_count==1 and self.get('r3')==expected
                assert self.get('r1')==SP and self.get('r2')==incoming
                # The patched callsite itself changes LR to 112440, as stock BL did.
                assert self.get('lr')==return_to
                assert all(self.get(n)==v for n,v in saved.items()),'nonvolatile ABI changed'
                for r in self.em.getTrackedMemoryWriteSet().getAddressRanges():
                    if r.getMinAddress().getAddressSpace()==space:
                        lo=r.getMinAddress().getOffset()&MASK; hi=(r.getMaxAddress().getOffset()&MASK)+1
                        assert self.allowed(lo,hi),('tracked RAM bound',hex(lo),hex(hi))
                return self.state()
            def finish(self):
                self.active(); self.call(); assert self.reason_stores==1
                assert self.q(MAIL)&0xffffffff00000000==TERMINAL
            def close(self): self.em.dispose()

        def case(name,fn):
            m=Machine()
            try:
                fn(m)
                results.append(dict(case=name,status='PASS',calls=m.calls,reason_stores=m.reason_stores,
                                    snapshots=len(m.snapshots),query_evidence=m.raw_queries,
                                    RAM_stores=[[hex(a),hex(b)] for a,b in sorted(m.stores)]))
            finally: m.close()

        def complete(m):
            m.finish(); before=m.native_refreshes; m.call(); assert m.native_refreshes==before+1 and m.reason_stores==1
            m.call(True); assert m.calls[-4:]==['open','stat','write','close'] and len(m.snapshots)==1
            count=len(m.calls); m.call(True); assert m.calls[count:]==['original'] and len(m.snapshots)==1
            m.call(); assert m.reason_stores==1
            assert len(m.queries)==8
            for target,ea,low in [(0,0x84000000,0x1014),(1,m.pool_ea,0x102c)]:
                p,s=m.groups(ea)
                assert m.queries[target*4:target*4+4]==[p,p+4,s,s+4]
                m.assert_record(ea,target,index=p,low=low)
        case('end_to_end_models_one_shot_and_late_refresh',complete)
        def thresholds(m):
            m.call(); assert m.state()[0]==TIMER and m.state()[3]==0
            m.now+=DELAY
            for _ in range(99): m.call()
            assert m.reason_stores==0 and m.state()[3]==99
            m.call(); assert m.reason_stores==1
        case('20_seconds_and_100_subsequent_callbacks',thresholds)
        def time_threshold(m):
            m.active(100); m.now-=1; m.call(); assert m.reason_stores==0
            m.now+=1; m.call(); assert m.reason_stores==1
        case('time_threshold_exact_boundary',time_threshold)
        for address,value,width in [(0x306fc68,0,8),(0x30700d0,0,8),*[(a,v+1,w) for a,v,w in HDD],(REASON,3,1)]:
            def reject(m,a=address,v=value,w=width):
                m.fixture(a,v,w); m.call(); assert m.q(MAIL)==0 and m.reason_stores==0
            case('arm_guard_'+hex(address),reject)
        for label,words in [('foreign',[1]+[0]*11),('old_autoreturn',[0x4155544f52544e31]+[0]*11),
                            ('partial',[0,1]+[0]*10),('publishing',[PUBLISHING]+[0]*11)]:
            def stale(m,words=words):
                image=struct.pack('>12Q',*words); m.fixture_bytes(MAIL,image)
                m.call(); assert m.rd(MAIL,96)==image and m.reason_stores==0
                m.fixture(REASON,2,1); m.call(True); assert m.calls[-1:]==['original']
            case(label,stale)
        def regress(m):
            m.active(); m.fixture(MAIL+16,m.now+1); m.call(); assert m.state()[4]==3 and m.reason_stores==0
        case('clock_regression_disarms',regress)
        for a,v,w in [(REASON,3,1),(0x306fc68,0,8),(0x241c888,1,8)]:
            def clock_race(m,a=a,v=v,w=w):
                m.active(); m.clock_effect=lambda x:x.fixture(a,v,w); m.call(); assert m.reason_stores==0
            case('guard_changes_at_clock_'+hex(a),clock_race)
        def publication_race(m):
            m.active(); done=[False]
            def inject(x,pc):
                if not done[0] and x.q(MAIL)&0xffffffff00000000==TERMINAL:
                    done[0]=True; x.fixture(REASON,3,1)
            m.effect=inject; m.call(); assert done[0] and m.reason_stores==0
            assert m.q(MAIL)&0xffffffff00000000!=TERMINAL
        case('reason_changes_after_terminal_commit',publication_race)
        def sample_race(m):
            m.active(); done=[False]
            def inject(x,pc):
                if not done[0] and x.q(MAIL)==PUBLISHING:
                    done[0]=True; x.fixture(0x30700d0,0,8)
            m.effect=inject; m.call(); assert done[0] and m.reason_stores==0
        case('UI_changes_during_field_capture',sample_race)
        def mapping(m):
            m.active(); m.fixture(0x2458428,0xffff000000000001); m.call()
            assert m.reason_stores==1 and m.state()[7]==0xffff000000000001
        case('captured_EA_never_dereferenced_or_used_as_guard',mapping)
        def ordinary(m):
            m.fixture(REASON,2,1); m.call(True); assert m.calls==['original']
        case('ordinary_shutdown_without_snapshot',ordinary)
        def expired(m):
            m.finish(); m.now+=121*(1<<26); n=len(m.calls); m.call(True)
            assert m.calls[n:]==['original'] and not m.snapshots
        case('expired_terminal_no_extra_native_calls',expired)
        for args in [[0,2,3,4,5,6,7,8],[0xb46100,3,3,4,5,6,7,8]]:
            def wrong(m,args=args):
                m.finish(); n=len(m.calls); m.call(True,args); assert m.calls[n:]==['original']
            case('wrong_shutdown_arguments_'+str(args[:2]),wrong)
        def reason_changed(m):
            m.finish(); m.fixture(REASON,3,1); n=len(m.calls); m.call(True); assert m.calls[n:]==['original']
        case('shutdown_reason_changed',reason_changed)
        def retained_tags(m):
            m.finish()
            def original(x): x.fixture(0x241c888,0x123); x.fixture(0x241c898,0x123)
            m.original_effect=original; m.call(True); assert len(m.snapshots)==1
        case('native_original_retained_nonzero_completion_tags',retained_tags)
        from mapping_cases import run_mapping_cases
        run_mapping_cases(case,SP,MASK)
        for name,field,value,expected_ops in [
            ('missing','fd',-2,['open']),('full_slots','fd',-1,['open']),
            ('out_of_range','fd',8,['open']),('large_fd','fd',256,['open']),
            ('wrong_size','size',65535,['open','stat','close']),
            ('larger_file','size',65537,['open','stat','close']),
            ('stat_failure','stat_rc',-1,['open','stat','close']),
            ('short_write','write_rc',511,['open','stat','write','close']),
            ('write_failure','write_rc',-1,['open','stat','write','close']),
            ('close_failure','close_rc',-1,['open','stat','write','close']),
            ('last_valid_fd','fd',7,['open','stat','write','close'])]:
            def fault(m,field=field,value=value,ops=expected_ops):
                m.finish(); setattr(m,field,value); n=len(m.calls); m.call(True)
                assert m.calls[n:]==['original']+['query95']*8+ops
                n=len(m.calls); m.call(True); assert m.calls[n:]==['original']
            case(name,fault)
        report=dict(status='PASS',elf_sha256=review['elf_sha256'],cases=results,
                    modeled=['native refresh body after real stack relocation','11B9BC original boundary',
                             'native clock and inline TB value','UFS open/stat/copy/write/close',
                             'call95 forwarded sc0 status/five outputs; no actual HV','ordering without concurrency'],
                    not_proven=['cold-cache/IRQ scheduling','native UFS transitive stores or liveness',
                                'concurrent last-recheck/reason-store race','durability','hardware return',
                                'active CPU SLB/TLB','full RPN/LPAR identity'])
        (OUT/'pc_validation_results.json').write_text(json.dumps(report,indent=2)+'\n')
        print('PASS',len(results),'compiled PPC cases; modeled native boundaries; hardware NOT RUN')

if __name__=='__main__': main()
