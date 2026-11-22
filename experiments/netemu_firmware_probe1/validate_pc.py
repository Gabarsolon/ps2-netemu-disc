"""One exclusive Ghidra 12.1.3 JVM; real compiled hooks and native allocator.

No device/console/network/tool execution in this harness. Explicit model
boundaries: B9D54 body, refresh body, shutdown body, UFS, TB, MSR/PIR, trap5/6.
Interactive retry keeps the SAME JVM alive to diagnose harness errors; 'quit'
always closes it. Successful/failing receipts stay in ignored owned_control.
"""
from pathlib import Path
import hashlib, json, os, struct, sys, traceback
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'local_only/owned_control'
H,T,E,P=0x2446560,0x2446598,0x80000000,0x03b00000
PAYLOAD=E+0x20000
MAIL,REASON,SP,STOP,TOC=0x930f20,0x934161,0xaaa7013fcf0,0x7ff0,0x751280
MASK=(1<<64)-1; BUSY=1<<63; META_SIZE=0x10048; DELAY=20*79800000
MAGIC=0x4f574e3100000000
STOCK_SHA='63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
REPORT={}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')

def run_suite(pyghidra,EmulatorHelper,ConsoleTaskMonitor,BigInteger):
    global REPORT
    review=json.loads((OUT/'build_review.json').read_text())
    elf=OUT/'ps2_netemu_owned_control.elf'
    assert sha(elf)==review['elf_sha256'] and sha(ROOT/'local_only/stock.elf')==STOCK_SHA
    for name,digest in review['source_inputs'].items(): assert sha(ROOT/name)==digest,(name,'changed since build')
    REPORT=dict(status='RUNNING',elf_sha256=sha(elf),cases=[],calls=[],jvm_done=False,
        original_before=sha(ROOT/'local_only/stock.elf'),model_boundaries=[
        'B9D54 normal body result; post-return heap comes from actual lazy B9848 + 23D0 and 18 allocations.',
        'BC16C after relocated prologue and 11B9BC original bodies; hostile ABI volatile clobbers.',
        'mfmsr/mfspr088 leaves and mftb return synthetic values. Leaves verified bytes; no MSR write executes.',
        '11A608/11A5FC sc intercepted with verified privileged trap5/6 semantics and exact nested tokens.',
        'Native UFS open/stat/write/close are instant boundary models, not native HDD or scheduling.'])
    gate=json.loads((ROOT/'local_only/private_staging_review/helper_gate.json').read_text())
    helper_path=list(map(lambda x:int(x,16),gate['single_bank_gate']['helper_path_pcs']))
    with pyghidra.open_program(str(elf),project_location=str(OUT/'pc/projects'),
            project_name='owned_'+review['elf_sha256'][:12],analyze=False,language='PowerPC:BE:64:default') as flat:
        program=flat.getCurrentProgram(); space=program.getAddressFactory().getDefaultAddressSpace()
        class Machine:
            def __init__(self,snapshot=None,irq=0x9032,pir=0x80000000):
                self.em=EmulatorHelper(program); self.monitor=ConsoleTaskMonitor()
                self.irq=irq; self.pir=pir; self.depth=[]; self.traps=[]
                self.now=79800000*1000; self.calls=[]; self.allocations=[]
                self.heapreads=0; self.heapwrites=0; self.nativewrites=0; self.payloadwrites=0
                self.sites={}; self.loads={}; self.barriers=0; self.reason_stores=0
                self.fd=2; self.size=65536; self.stat_rc=0; self.write_rc=512; self.close_rc=0
                self.sectors=[]; self.effect=None; self.original_effect=None; self.clock_effect=None
                self.return_fault=None; self.native_return=None; self.native_lr=None; self.active_helper=[]
                self.fixture(H,snapshot if snapshot is not None else bytes(META_SIZE))
                self.fixture(MAIL,bytes(96)); self.fixture(SP-8192,bytes(8224))
                for a,v,w in [(0x934960,0x60000,8),(0x934968,1,8),(0x934970,P,8),(0x934980,E,8),
                    (0x24565b8,E,8),(0x930f80,0,4),(0x930f84,0,4),
                    (REASON,0,1),(0x306fc68,0x30700d0,8),(0x30700d0,0x949cb8,8),
                    (0x241c8d5,1,1),(0x241c8c8,0,1),(0x241c860,3,8),
                    (0x241c888,0,8),(0x241c890,0,8),(0x241c898,0,8),(0x3055180,0,4),
                    (0x241c850,2,4),(0x241c8a8,7,4)]: self.fq(a,v,w)
                self.em.enableMemoryWriteTracking(True)
            def dispose(self): self.em.dispose()
            def put(self,n,v): self.em.writeRegister(n,BigInteger(str(v&MASK)))
            def get(self,n): return int(str(self.em.readRegister(n)))&MASK
            def pc(self,p): self.put(self.em.getPCRegister(),p)
            def rd(self,a,n): return bytes(self.em.readMemory(space.getAddress(a),n))
            def q(self,a): return int.from_bytes(self.rd(a,8),'big')
            def fixture(self,a,data):
                self.em.enableMemoryWriteTracking(False); self.em.writeMemory(space.getAddress(a),data)
                self.em.enableMemoryWriteTracking(True)
            def fq(self,a,v,n=8): self.fixture(a,(v&((1<<(8*n))-1)).to_bytes(n,'big'))
            def state(self): return list(struct.unpack('>12Q',self.rd(MAIL,96)))
            def status(self): return self.q(MAIL+8)>>32
            def phase(self): return self.q(MAIL+8)&0xffffffff
            def seal(self):
                m=self.state(); x=m[2]^m[3]^m[4]^m[5]^m[9]^m[10]^m[11]^(m[1]>>32)
                x^=x>>33; x=x*0xff51afd7ed558ccd&MASK; x^=x>>33
                self.fq(MAIL,MAGIC|((x^(x>>32))&0xffffffff))
            def owned(self,a,n): return any(lo<=a and a+n<=lo+size for lo,size in self.allocations)
            def payload_region(self,a,n):
                for lo,size in self.allocations:
                    c=(lo+0x107f)&~127;d=c+128
                    if any(x<=a and a+n<=x+length for x,length in [(lo,4096),(c,64),(d,2048)]):return True
                return False
            def stack(self,a,n): return SP-8192<=a and a+n<=SP+32
            def allowed_store(self,a,n,native):
                if self.stack(a,n): return True
                if native: return H<=a and a+n<=H+META_SIZE
                return MAIL<=a and a+n<=MAIL+96 or a==REASON and n==1 or self.payload_region(a,n)
            def allowed_read(self,a,n):
                # Read-only program/TOC, exact fixed RW fields, metadata,
                # modeled stack, or an ACTUAL fresh native allocation only.
                fixed=[(MAIL,104),(0x934960,0x28),(0x24565b8,8),(REASON,1),
                    (0x306fc68,8),(0x30700d0,8),(0x241c8d5,1),(0x241c8c8,1),
                    (0x241c860,8),(0x241c888,0x18),(0x3055180,4),(0x241c850,4),(0x241c8a8,4)]
                return (0<=a<a+n<=0x800000 or self.stack(a,n) or H<=a<a+n<=H+META_SIZE or
                    any(lo<=a<a+n<=lo+size for lo,size in fixed) or self.payload_region(a,n))
            def ret(self,v):
                target=self.get('lr')
                for r in [0,*range(3,13)]: self.put('r'+str(r),0xdad0000000000000+r)
                for c in (0,1,5,6,7): self.put('cr'+str(c),15-c)
                self.put('ctr',0xaabbccdd); self.put('xer',0); self.put('r3',v); self.pc(target)
            def records(self):
                b=self.q(H+0x18); assert 1<=b<=4092
                result=[]; off=0
                for i in range(4096):
                    nxt,attr=struct.unpack('>QQ',self.rd(H+0x40+16*i,16))
                    assert nxt==(H+0x50+16*i if i<4095 else 0)
                    assert not attr&0x00008000ffffffff
                    n,o,busy=(attr>>32)&0x7fff,(attr>>48)&0x7fff,bool(attr&BUSY)
                    if i<b:
                        assert n and o==off and n<=4096-off
                        result.append((o,n,busy)); off+=n
                    else: assert not attr
                assert off==4096
                return result
            def access(self,pc,w,native):
                op=w>>26; ra=w>>16&31; rt=w>>21&31; rb=w>>11&31
                base=self.get('r'+str(ra)) if ra else 0
                load=False; store=False; width=0; a=0
                if op in (32,34,40,42,58,36,38,44,62):
                    load=op in (32,34,40,42,58); store=not load
                    width={32:4,34:1,40:2,42:2,58:8,36:4,38:1,44:2,62:8}[op]
                    disp=w&(0xfffc if op in (58,62) else 0xffff)
                    if disp&0x8000: disp-=0x10000
                    a=(base+disp)&MASK
                elif op==31:
                    xo=w>>1&1023
                    indexed={21:(True,8),23:(True,4),87:(True,1),279:(True,2),
                             149:(False,8),151:(False,4),215:(False,1),407:(False,2)}
                    if xo in indexed:
                        load,width=indexed[xo]; store=not load; a=(base+self.get('r'+str(rb)))&MASK
                    else:
                        # No reservation/store conditional/cache operation in this slice.
                        assert xo not in (20,84,150,214,246,278,470,598,854,982,1014) or xo==598,('unexpected memory opcode',hex(pc),xo)
                if store:
                    assert self.allowed_store(a,width,native),('store fence',hex(pc),hex(a),width,native)
                    self.sites.setdefault(pc,set()).add((a,width,'native' if native else 'payload'))
                    if not self.stack(a,width):
                        if native: self.nativewrites+=1
                        else: self.payloadwrites+=1
                    if self.owned(a,width):
                        assert not native and self.native_return is not None and not self.irq&0x8000
                        self.heapwrites+=1
                    if a==REASON:
                        assert self.phase()==3 and self.get('r'+str(rt))&255==2 and self.rd(REASON,1)==bytes([0])
                        self.reason_stores+=1
                    if pc in helper_path: assert (pc,a,width)==(0xb8928,H+0x20,8)
                if load:
                    assert self.allowed_read(a,width),('read fence',hex(pc),hex(a),width,native)
                    self.loads[pc]=self.loads.get(pc,0)+1
                    if H<=a<H+META_SIZE and not native:
                        # Any admission/bank read in startup requires the OUTER save.
                        if self.kind=='startup': assert self.depth and not self.irq&0xc000,('unprotected metadata read',hex(pc))
                    if E<=a<E+0x100000:
                        assert self.owned(a,width),('heap read before ownership / invalid ptr',hex(pc),hex(a))
                        self.heapreads+=1
                    # CPU reads of an LPAR value as pointer are forbidden.
                    assert not (P<=a<P+0x100000),('LPAR dereference',hex(pc),hex(a))
                return store
            def call(self,kind='startup',size=0x2000,wrong_epoch=False,args=None):
                self.kind=kind
                args=args or ([0xb46100,2,3,4,5,6,7,8] if kind=='shutdown' else list(range(0x101,0x109)))
                saved={**{'r'+str(r):0xabcd000000000000+r for r in range(13,32)},**{'cr'+str(c):c+2 for c in (2,3,4)}}
                for n,v in saved.items(): self.put(n,v)
                incoming=0x123456780000 if kind=='refresh' else TOC
                self.put('r1',SP); self.put('r2',incoming); self.put('lr',STOP)
                for i,v in enumerate(args,3): self.put('r'+str(i),v)
                initial_irq=self.irq; initial_depth=len(self.depth); original=0; initialmail=self.rd(MAIL,96)
                if kind=='native':
                    self.put('r3',size); self.put('r4',3); self.put('r5',0); self.pc(0xb9848); stop=STOP
                elif kind=='startup':
                    if wrong_epoch: self.put('lr',0x18cbc); self.pc(0x4b00); stop=0x18cbc
                    else: self.pc(0x18cb4); stop=0x18cb8
                elif kind=='shutdown': self.pc(0x11243c); stop=0x112440
                else: self.pc(0xbc168); stop=STOP
                expected=0xfedcba9876543210; relsp=None; allocs=0; steps=0; helper=[]; minsp=SP
                startcalls=len(self.calls); starttraps=len(self.traps); preexisting=None; true_result=None
                countreads=self.heapreads; countwrites=self.heapwrites
                for steps in range(650000):
                    pc=self.em.getExecutionAddress().getOffset()&MASK
                    if self.effect: self.effect(self,pc)
                    minsp=min(minsp,self.get('r1'))
                    if self.native_lr==pc:
                        true_result=self.get('r3'); self.native_return=true_result
                        rounded=(size+63)//64*64 if kind=='native' else 0x2000
                        post=self.records()
                        assert {(o,n) for o,n,b in preexisting if b}<={(o,n) for o,n,b in post if b}
                        if true_result:
                            assert ((true_result-PAYLOAD)//64,rounded//64,True) in post
                            self.allocations.append((true_result,rounded))
                        assert helper==helper_path
                        self.active_helper=helper[:]; self.native_lr=None
                        if self.return_fault is not None:
                            self.put('r3',self.return_fault)
                    if pc==stop: break
                    if pc in (0xb9d54,0xbc16c,0x11b9bc):
                        assert kind!='native' and original==0 and self.get('r2')==TOC
                        assert [self.get('r'+str(i)) for i in range(3,11)]==args
                        assert self.rd(MAIL,96)==initialmail and not allocs
                        if pc==0xbc16c:
                            assert kind=='refresh' and self.get('r1')==relsp-320 and self.q(relsp-320)==relsp
                            self.put('r1',relsp)
                        elif pc==0xb9d54: assert kind=='startup'
                        else: assert kind=='shutdown'
                        original+=1; self.calls.append('original_'+kind)
                        if self.original_effect: self.original_effect(self)
                        self.ret(expected); continue
                    if pc in (0x4c40,0x4c50):
                        assert self.rd(pc,8)==bytes.fromhex('7c6000a64e800020' if pc==0x4c40 else '7c6822a64e800020')
                        # Model only mfmsr/mfspr instruction, execute its blr natively.
                        self.put('r3',self.irq if pc==0x4c40 else self.pir); self.pc(pc+4); continue
                    if pc in (0x4c60,0x4c78):
                        # Firmware-route probe LV1 hypercall leaf stubs: li r11,HV; sc 1; blr.
                        assert self.rd(pc,12)==bytes.fromhex('396000aa440000224e800020' if pc==0x4c60 else '396000ab440000224e800020')
                        self.put('r3',getattr(self,'lv1_open_ret',0) if pc==0x4c60 else getattr(self,'lv1_close_ret',0))
                        self.pc(pc+8); continue
                    if pc==0xb9cd0:
                        assert kind=='refresh' and original==1 and self.get('r2')==TOC and not self.depth
                        self.calls.append('clock')
                        if self.clock_effect: self.clock_effect(self)
                        self.ret(self.now); continue
                    boundary={0x1ecc5c:'open',0x1ec760:'stat',0x1ed458:'write',0x1ecb10:'close'}.get(pc)
                    if boundary:
                        assert kind=='shutdown' and original==1 and not self.depth and self.phase()==4
                        assert self.get('r2')==TOC; self.calls.append(boundary)
                        if boundary=='open':
                            path=b'/tmp/netemu_owned_snapshot.bin\0'
                            assert self.get('r3')==0 and self.rd(self.get('r4'),len(path))==path
                            self.ret(self.fd)
                        elif boundary=='stat':
                            assert self.get('r3')==self.fd; ptr=self.get('r4'); assert self.stack(ptr,48)
                            self.fixture(ptr,struct.pack('>6Q',11,22,33,44,55,self.size)); self.ret(self.stat_rc)
                        elif boundary=='write':
                            assert (self.get('r3'),self.get('r4'),self.get('r6'))==(self.fd,0,512)
                            ptr=self.get('r5'); assert self.stack(ptr,512)
                            sec=self.rd(ptr,512); q=struct.unpack('>64Q',sec)
                            assert q[0:2]==(0x4f574e5345433100,0x1000000000200) and q[4:7]==(0xb46100,2,expected)
                            assert q[8:20]==tuple(self.state()) and q[62:]==(0,0)
                            self.sectors.append(sec); self.ret(self.write_rc)
                        else: assert self.get('r3')==self.fd; self.ret(self.close_rc)
                        continue
                    native=(0xb9848<=pc<0xb99a0 or 0xb9470<=pc<0xb9624 or
                        0xb9bcc<=pc<0xb9bf0 or 0xb9c24<=pc<0xb9c30 or
                        0xba0d8<=pc<0xba0fc or 0xba124<=pc<0xba148 or 0x11a5f8<=pc<0x11a610 or pc in helper_path)
                    assert native or 0x4800<=pc<int(review['code_end'],16) or pc in (0xbc168,0x11243c,0x18cb4),('unexpected PC / growth',hex(pc))
                    if native: assert self.get('r2')==TOC
                    if pc==0xb9848:
                        assert kind=='native' or kind=='startup' and original==1 and len(self.depth)==1 and not self.irq&0xc000
                        allocs+=1; assert allocs==1
                        if kind!='native': assert (self.get('r3'),self.get('r4'),self.get('r5'))==(0x2000,3,0)
                        self.native_lr=self.get('lr'); preexisting=self.records() if self.q(H) else None
                    if pc==0xb9470:
                        assert self.get('r4')==0
                        if preexisting is None:
                            preexisting=self.records(); self.initial_geometry=self.rd(H,META_SIZE)
                    if pc in helper_path:
                        assert pc==helper_path[len(helper)] and not self.irq&0x8000
                        helper.append(pc)
                    w=int.from_bytes(self.rd(pc,4),'big'); op=w>>26
                    if op==17:
                        assert pc in (0x11a608,0x11a5fc) and w==0x44000002
                        old=self.irq; assert not old&0x4000
                        if pc==0x11a608:
                            assert self.get('r11')==5; self.depth.append(old); self.irq&=~0x8000; self.put('r3',old)
                        else:
                            assert self.get('r11')==6 and self.depth
                            token=self.depth.pop(); assert self.get('r3')==token
                            self.irq=(self.irq&~0x8000)|(token&0x8000)
                        self.put('r11',self.irq); self.pc(pc+4)
                        self.traps.append(dict(pc=hex(pc),before=hex(old),after=hex(self.irq),depth=len(self.depth))); continue
                    if pc==0x4ac0: relsp=self.get('r1')
                    if w==0x7c0004ac:
                        # Ghidra's sync CALLOTHER has no memory-order execution
                        # model. Verify/count the fence word; advance explicitly.
                        self.barriers+=1; self.pc(pc+4); continue
                    # Read TB's compiler-selected destination, before stepping.
                    if op==31 and (w>>1&1023) in (339,371) and ((w>>16&31)|((w>>11&31)<<5)) in (268,269):
                        self.put('r'+str(w>>21&31),self.now); self.pc(pc+4); continue
                    self.access(pc,w,native)
                    assert self.em.step(self.monitor),(hex(pc),str(self.em.getLastError()))
                else: raise AssertionError(('instruction cap',kind,hex(pc)))
                assert self.get('r1')==SP and self.get('r2')==incoming
                assert all(self.get(n)==v for n,v in saved.items()),('nonvolatile ABI',kind)
                assert self.irq==initial_irq and len(self.depth)==initial_depth,('outer restore',kind)
                assert self.get('lr')==(STOP if kind in ('native','refresh') else stop)
                if kind!='native': assert original==1 and self.get('r3')==expected
                for span in self.em.getTrackedMemoryWriteSet().getAddressRanges():
                    if span.getMinAddress().getAddressSpace()==space:
                        lo=span.getMinAddress().getOffset(); end=span.getMaxAddress().getOffset()+1
                        assert self.stack(lo,end-lo) or H<=lo<end<=H+META_SIZE or MAIL<=lo<end<=MAIL+96 or lo==REASON and end==REASON+1 or self.owned(lo,end-lo),('tracked write',hex(lo),hex(end))
                receipt=dict(kind=kind,steps=steps,allocator_calls=allocs,original_calls=original,
                    original_result_preserved=True,abi_preserved=True,irq_restored=True,
                    traps=self.traps[starttraps:],helper_pcs=list(map(hex,helper)),
                    native_result=None if true_result is None else hex(true_result),
                    heap_reads=self.heapreads-countreads,heap_writes=self.heapwrites-countwrites,
                    stack_depth=SP-minsp,calls=self.calls[startcalls:])
                REPORT['calls'].append(receipt)
                return self.get('r3')

        # Establish all fixture geometry with real lazy initialization and both
        # native B9D54 allocations. B9D54 itself is a clearly modeled boundary.
        m=Machine()
        try:
            assert m.call('native',0x23d0)==PAYLOAD
            template=m.initial_geometry
            assert m.call('native',0x18)==PAYLOAD+0x2400
            prior=m.rd(H,META_SIZE)
            assert m.records()==[(0,144,True),(144,1,True),(145,3951,False)]
            dump('native_fixture_origin.json',dict(initial_sha256=hashlib.sha256(template).hexdigest(),
                 post_B9D54_model_sha256=hashlib.sha256(prior).hexdigest(),allocations=m.allocations))
        finally: m.dispose()
        print('PASS actual lazy geometry and native 23D0/18 post-return fixture',flush=True)

        def fixture(records):
            data=bytearray(template); struct.pack_into('>Q',data,0x18,len(records)); offset=0
            for i in range(4096):
                attr=0
                if i<len(records):
                    n,busy=records[i]; attr=(BUSY if busy else 0)|(offset<<48)|(n<<32); offset+=n
                struct.pack_into('>Q',data,0x48+16*i,attr)
            assert offset==4096
            return bytes(data)
        def case(name,fn,snapshot=prior,irq=0x9032,pir=0x80000000):
            m=Machine(snapshot,irq,pir)
            try:
                fn(m)
                REPORT['cases'].append(dict(name=name,status='PASS',payload_heap_writes=m.heapwrites,
                    payload_heap_reads=m.heapreads,native_metadata_stores=m.nativewrites,
                    reason_stores=m.reason_stores,barriers=m.barriers))
            finally:
                # The inventories are exact PCs; ranges are only receipts of
                # observed addresses, never a broad >=800000 allowance.
                REPORT.setdefault('store_sites',{}).update({hex(k):sorted([list(v) for v in vals]) for k,vals in m.sites.items()})
                m.dispose()
        def startup(m,status=1):
            m.call(); assert m.status()==status and m.phase()==1
            assert sum(c['allocator_calls'] for c in REPORT['calls'][-1:])==(1 if status in (1,4,5,6) else 0)
            if status==1:
                a=m.q(MAIL+16); assert a==m.native_return and m.q(a+24)==0x2000
                assert m.heapwrites and len(m.allocations)==1
        def arm(m):
            m.now+=1; m.call('refresh'); assert m.phase()==2
        def terminal(m):
            arm(m); m.fq(MAIL+64,99); m.now+=DELAY; m.call('refresh')
            assert m.phase()==3 and m.reason_stores==1
        def successful(m):
            startup(m); a=m.q(MAIL+16); terminal(m); m.call('shutdown')
            assert m.phase()==4 and len(m.sectors)==1
            q=struct.unpack('>64Q',m.sectors[0]); assert q[23]==0x2000 and q[26]==P+a-E
            assert q[7]==a
            assert q[42]==1 and q[47:53]==(0x30700d0,0x949cb8,3,0,0,0)
            (OUT/'pc_success_snapshot.bin').write_bytes(m.sectors[0])
            n=len(m.calls); m.call('shutdown'); assert m.calls[n:]==['original_shutdown']
            m.call('refresh'); assert m.reason_stores==1
        case('owned_full_normal_return_snapshot_oneshot',successful)
        print('PASS compiled startup + refresh + shutdown normal return control',flush=True)
        specs=[('split',[(64,True),(512,False),(3520,True)],1),
            ('exact',[(64,True),(128,False),(3904,True)],1),
            ('fragmented',[(64,False),(1,True)]*63+[(1,True)],4),
            ('B4091_nofit',[(1,bool(i%2)) for i in range(4090)]+[(6,True)],4),
            ('max_exact_B3969',[(1,True)]*3968+[(128,False)],1),
            ('max_split_head_B3968',[(129,False)]+[(1,True)]*3967,1),
            ('max_split_tail_B3968',[(1,True)]*3967+[(129,False)],1),
            ('firstfit_second',[(1,True),(64,False),(1,True),(256,False),(3774,True)],1),
            ('busy_nofit',[(4096,True)],4)]
        for irq in (0x1032,0x9032):
            for pir in (0x80000000,0xc0000000):
                for name,records,status in specs:
                    def test(m,status=status):
                        startup(m,status)
                        assert len(REPORT['calls'][-1]['traps'])==4
                        assert all(not int(t['after'],16)&0x8000 for t in REPORT['calls'][-1]['traps'][:-1])
                        if status==4:
                            assert not m.heapreads and not m.heapwrites
                            terminal(m); m.call('shutdown'); assert len(m.sectors)==1
                            assert struct.unpack('>64Q',m.sectors[0])[20:47]==(0,)*27
                    case(name+'_EE'+hex(irq)+'_h'+str(pir>>30&1),test,fixture(records),irq,pir)
                print('PASS allocation matrix',hex(irq),hex(pir),flush=True)
        # All 26 independently established corruption classes are injected at
        # the ORIGINAL RETURN boundary, not before the modeled original body.
        rejects=[('B4092',fixture([(1,True)]*4091+[(5,True)]),None),
            ('B4093',fixture([(1,True)]*4092+[(4,True)]),None),
            ('multibank',prior,(T,PAYLOAD)),('bank_cycle',prior,(T,T)),('bad_root',prior,(H+8,T+8)),
            ('bad_record_link',prior,(H+0x40,0x12345678)),('self_cycle',prior,(H+0x40,H+0x40)),
            ('back_cycle',prior,(H+0x60,H+0x40)),('premature_null',prior,(H+0x50,0)),
            ('missing_null',prior,(H+0x10030,H+0x40)),('count_low',prior,(H+0x18,2)),
            ('count_high',prior,(H+0x18,4)),('count_zero',prior,(H+0x18,0)),
            ('prefix_zero',prior,(H+0x58,144<<48)),('suffix_nonzero',prior,(H+0x78,1<<32)),
            ('overlap',prior,(H+0x58,BUSY|(143<<48)|(1<<32))),('gap',prior,(H+0x58,BUSY|(145<<48)|(1<<32))),
            ('overrun',prior,(H+0x68,(145<<48)|(4096<<32))),('reserved',prior,(H+0x48,BUSY|(144<<32)|1)),
            ('sentinel',prior,(H+0x10040,PAYLOAD+64)),('payloadbase',prior,(H+0x28,PAYLOAD+64)),
            ('payloadextent',prior,(H,0x50000)),('publishedE',prior,(0x24565b8,E+0x800000)),
            ('descriptorE',prior,(0x934980,E+64)),('descriptorextent',prior,(0x934960,0x70000)),
            ('zeroP',prior,(0x934970,0))]
        for name,snap,mutation in rejects:
            def test(m,snap=snap,mutation=mutation):
                def effect(x):
                    x.fixture(H,snap)
                    if mutation:x.fq(*mutation)
                m.original_effect=effect; startup(m,3)
                assert not m.heapreads and not m.heapwrites and not m.nativewrites
                m.original_effect=None; terminal(m); m.call('shutdown'); assert len(m.sectors)==1
            case('reject_'+name,test)
        print('PASS all 26 compiled fixed-bank admission rejections + declined snapshots',flush=True)
        for name,a,v,w in [('flags0',0x930f80,1,4),('flags1',0x930f84,1,4),
            ('flags_large',0x930f84,0x80000000,4)]:
            def test(m,a=a,v=v,w=w): m.fq(a,v,w); startup(m,2); assert not m.traps
            case(name,test)
        case('wrong_PR',lambda m:startup(m,2),irq=0xd032)
        case('secondary_PIR',lambda m:startup(m,2),pir=0x40000000)
        def epoch(m): m.call(wrong_epoch=True); assert m.status()==2 and not m.traps
        case('wrong_startup_epoch',epoch)
        def changing_pir(m):
            count=[0]
            def effect(x,pc):
                if pc==0x4c50:
                    count[0]+=1
                    if count[0]==2:x.pir^=0x40000000
            m.effect=effect; startup(m,2); assert len(m.traps)==2 and not m.nativewrites
        case('PIR_changes_inside_outer',changing_pir)
        for name,addr,val in [('Pmisalign',0x934970,P+1),('Poverflow',0x934970,0xfffffffffff00000),
                ('flags',0x934968,2),('Eslot',0x934980,0x7f800000),('hugecount',H+0x18,MASK)]:
            def test(m,addr=addr,val=val): m.original_effect=lambda x:x.fq(addr,val); startup(m,3)
            case('guard_'+name,test)
        for value in (0,1,E,E+0x20000,PAYLOAD+0x2441,PAYLOAD+0x40000-64,MASK-0x1000):
            def test(m,value=value):
                m.return_fault=value; startup(m,4 if not value else 5)
                assert not m.heapreads and not m.heapwrites
                assert m.q(MAIL+16)==value
                terminal(m); m.call('shutdown'); assert len(m.sectors)==1
                assert struct.unpack('>64Q',m.sectors[0])[7]==value
                if value==MASK-0x1000:(OUT/'pc_declined_snapshot.bin').write_bytes(m.sectors[0])
            case('fault_injected_return_'+hex(value),test)
        def changedpool(m):
            done=[False]
            def effect(x,pc):
                if x.native_return and not done[0]:x.fq(0x934970,P+0x100000); done[0]=True
            m.effect=effect; startup(m,6); assert not m.heapreads and not m.heapwrites
            m.effect=None;terminal(m);m.call('shutdown');assert len(m.sectors)==1
            assert struct.unpack('>64Q',m.sectors[0])[7]==m.native_return
        case('pool_changes_after_native_return',changedpool)
        for index in range(12):
            def test(m,index=index):
                m.fq(MAIL+index*8,1); before=m.rd(MAIL,96); m.call(); m.call('refresh'); m.call('shutdown')
                assert m.rd(MAIL,96)==before and not m.allocations and not m.sectors
            case('foreign_or_partial_mail_'+str(index),test)
        def reentry(m):
            startup(m); before=m.rd(MAIL,96); m.call(); assert m.rd(MAIL,96)==before and len(m.allocations)==1
        case('second_startup_never_reallocates',reentry)
        for ptr in (0,1,0x1000,0x400000,E,PAYLOAD,PAYLOAD+0x1000,E+0x60000,MASK-31):
            def test(m,ptr=ptr):
                startup(m); m.fq(MAIL+16,ptr); before=m.heapreads
                m.call('refresh'); m.call('shutdown')
                assert m.heapreads==before and not m.sectors and not m.reason_stores
            case('malformed_published_pointer_'+hex(ptr),test)
        # Deliberately recompute the non-security publication checksum for
        # invalid pointer/range inputs, proving range checks independently.
        for ptr in (0,1,0x1000,E,PAYLOAD+1,E+0x60000-64,MASK-31):
            def test(m,ptr=ptr):
                startup(m);m.fq(MAIL+16,ptr);m.seal();before=m.heapreads
                m.call('refresh');m.call('shutdown');assert m.heapreads==before and not m.reason_stores and not m.sectors
            case('resigned_invalid_pointer_'+hex(ptr),test)
        for offset,value in [(0,0),(8,0),(24,0),(32,1),(40,0),(72,0),(80,0x4000),(88,0x8000)]:
            def test(m,offset=offset,value=value):
                startup(m);m.fq(MAIL+offset,value);before=m.heapreads
                m.call('refresh');m.call('shutdown');assert m.heapreads==before and not m.reason_stores and not m.sectors
            case('malformed_published_field_'+str(offset),test)
        def counterwrap(m):m.fq(H+0x20,MASK);startup(m);assert m.q(H+0x20)==0
        case('native_maintenance_counter_wrap',counterwrap)
        def leasecookie(m):
            startup(m);m.fq(m.q(MAIL+16)+8,0);m.call('refresh');m.call('shutdown');assert not m.reason_stores and not m.sectors
        case('owned_cookie_mismatch',leasecookie)
        def guards(m):
            startup(m); arm(m); m.fq(MAIL+64,99); m.now+=DELAY-1; m.call('refresh'); assert not m.reason_stores
            m.now+=1; m.call('refresh'); assert m.reason_stores==1
        case('time_threshold',guards)
        def callback(m):
            startup(m); arm(m); m.now+=DELAY; m.call('refresh'); assert m.q(MAIL+64)==1 and not m.reason_stores
        case('callback_threshold',callback)
        fixed=[(REASON,3,1),(0x306fc68,0,8),(0x30700d0,0,8),
            (0x241c8d5,0,1),(0x241c8c8,1,1),(0x241c860,4,8),(0x241c888,1,8),
            (0x241c890,1,8),(0x241c898,1,8),(0x3055180,1,4)]
        for a,v,w in fixed:
            for stage in ('arm','timer','clock','shutdown'):
                def test(m,a=a,v=v,w=w,stage=stage):
                    startup(m)
                    if stage!='arm':arm(m)
                    if stage=='shutdown':
                        m.fq(MAIL+64,99);m.now+=DELAY;m.call('refresh'); assert m.reason_stores==1
                        m.fq(a,v,w); m.call('shutdown'); assert not m.sectors
                    else:
                        m.fq(MAIL+64,99 if stage!='arm' else 0);m.now+=DELAY
                        if stage=='clock':m.clock_effect=lambda x:x.fq(a,v,w)
                        else:m.fq(a,v,w)
                        m.call('refresh');assert not m.reason_stores
                case('guard_'+hex(a)+'_'+stage,test)
        for offset,val in [(48,0),(48,MASK),(56,0),(56,MASK),(64,101),(8,(1<<32)|7)]:
            def test(m,offset=offset,val=val):
                startup(m);arm(m);m.fq(MAIL+offset,val);m.now+=DELAY;m.call('refresh');assert not m.reason_stores
            case('malformed_timer_'+str(offset)+'_'+hex(val),test)
        def regression(m):startup(m);arm(m);m.now-=1;m.call('refresh');assert m.phase()==5
        case('clock_regression',regression)
        def patterns_bad(m):
            startup(m);a=m.q(MAIL+16);c=(a+0x107f)&~127;m.fq(c,0);terminal_expected=False
            arm(m);m.fq(MAIL+64,99);m.now+=DELAY;m.call('refresh');assert m.phase()==5 and not m.reason_stores
        case('corrupt_own_pattern_disarms',patterns_bad)
        def pubrace(m):
            startup(m);arm(m);m.fq(MAIL+64,99);m.now+=DELAY;done=[False]
            def effect(x,pc):
                if x.phase()==6 and not done[0]:x.fq(REASON,3,1);done[0]=True
            m.effect=effect;m.call('refresh');assert done[0] and not m.reason_stores
        case('publication_reason_race',pubrace)
        for status in ('owned','declined'):
            for name,fd,size,statrc,writerc,closerc,expectedcalls in [
                ('fdneg',-1,65536,0,512,0,['open']),('fd8',8,65536,0,512,0,['open']),
                ('fd0',0,65536,0,512,0,['open','stat','write','close']),
                ('fd7',7,65536,0,512,0,['open','stat','write','close']),
                ('staterr',2,65536,-1,512,0,['open','stat','close']),
                ('wrongsize',2,65535,0,512,0,['open','stat','close']),
                ('writeerr',2,65536,0,-1,0,['open','stat','write','close']),
                ('shortwrite',2,65536,0,511,0,['open','stat','write','close']),
                ('closeerr',2,65536,0,512,-1,['open','stat','write','close'])]:
                def test(m,fd=fd,size=size,statrc=statrc,writerc=writerc,closerc=closerc,expectedcalls=expectedcalls,status=status):
                    if status=='declined':m.original_effect=lambda x:x.fq(H+8,0)
                    startup(m,3 if status=='declined' else 1);m.original_effect=None;terminal(m)
                    m.fd,m.size,m.stat_rc,m.write_rc,m.close_rc=fd,size,statrc,writerc,closerc
                    n=len(m.calls);m.call('shutdown');assert m.calls[n:]==['original_shutdown']+expectedcalls
                    n=len(m.calls);m.call('shutdown');assert m.calls[n:]==['original_shutdown']
                case(status+'_file_'+name,test)
        def ordinary(m):m.call('shutdown');assert m.calls==['original_shutdown'] and not m.sectors
        case('ordinary_shutdown',ordinary)
        for age in (-1,120*(1<<26)+1):
            def test(m,age=age):startup(m);terminal(m);m.now+=age;m.call('shutdown');assert not m.sectors
            case('shutdown_session_age_'+str(age),test)
        print('PASS publication, pointers, timer/UI/HDD/session/oneshot and UFS error matrices',flush=True)
        inventory=json.loads((OUT/'assembly_store_audit.json').read_text())
        needed={x['pc'] for x in inventory['stores']}
        observed=set(REPORT['store_sites'])
        missing=needed-observed
        REPORT['compiled_store_site_coverage']=dict(total=len(needed),observed=len(needed&observed),missing=sorted(missing))
        assert not missing,('unexecuted payload store site',missing)
        REPORT['status']='PASS'
        REPORT['original_after']=sha(ROOT/'local_only/stock.elf');assert REPORT['original_after']==STOCK_SHA
        REPORT['counts']=dict(cases=len(REPORT['cases']),hook_native_calls=len(REPORT['calls']),
            instructions=sum(c['steps'] for c in REPORT['calls']),
            fresh_allocator_calls=sum(c['allocator_calls'] for c in REPORT['calls']),
            trap_intercepts=sum(len(c['traps']) for c in REPORT['calls']),
            real_sc_executed=0)
        dump('pc_results.json',REPORT)
        print('COMPLETE',REPORT['counts'],flush=True)

def main():
    assert '--allow-jvm' in sys.argv
    for d in ('tmp','settings','projects'):(OUT/'pc'/d).mkdir(parents=True,exist_ok=True)
    for k in ('TEMP','TMP','TMPDIR','APPDATA','LOCALAPPDATA'):
        os.environ[k]=str(OUT/'pc'/('tmp' if k in ('TEMP','TMP','TMPDIR') else 'settings'))
    os.environ['JAVA_HOME']='C:/Program Files/Microsoft/jdk-21.0.12.101-hotspot'
    os.environ['GHIDRA_INSTALL_DIR']='C:/ghidra_12.1.3_PUBLIC'
    from pyghidra.launcher import HeadlessPyGhidraLauncher
    import pyghidra,jpype
    launcher=HeadlessPyGhidraLauncher();launcher.java_home=os.environ['JAVA_HOME']
    launcher.add_vmargs('-Xmx3G','-Duser.home='+str(OUT/'pc/settings'),
        '-Dapplication.settingsdir='+str(OUT/'pc/settings'),'-Djava.io.tmpdir='+str(OUT/'pc/tmp'))
    launcher.start()
    from ghidra.app.emulator import EmulatorHelper
    from ghidra.util.task import ConsoleTaskMonitor
    from java.math import BigInteger
    runs=0
    try:
        while True:
            runs+=1
            try:
                # Reload the suite text for same-JVM harness corrections.
                scope={'__file__':__file__,'__name__':'suite'}
                exec(compile(Path(__file__).read_text(),__file__,'exec'),scope)
                scope['run_suite'](pyghidra,EmulatorHelper,ConsoleTaskMonitor,BigInteger)
                REPORT.update(scope['REPORT']);break
            except BaseException:
                error=traceback.format_exc();print(error,flush=True)
                if 'scope' in locals(): REPORT.update(scope.get('REPORT',{}))
                REPORT.update(status='FAIL',error=error);dump('pc_results.json',REPORT)
                dump('pc_attempt_'+str(runs)+'.json',REPORT)
                if '--retry-file' in sys.argv:
                    import time
                    command_path=OUT/'jvm_command.txt'
                    command_path.write_text('waiting\n')
                    print('SAME_JVM_WAIT: owned_control/jvm_command.txt accepts run or quit (10 minute limit)',flush=True)
                    deadline=time.monotonic()+600
                    while time.monotonic()<deadline:
                        command=command_path.read_text().strip()
                        if command in ('run','quit'):break
                        time.sleep(0.5)
                    else:command='quit'
                    if command=='run':continue
                    break
                if '--interactive' not in sys.argv:raise
                print('SAME_JVM_WAIT: run retries suite; quit closes JVM',flush=True)
                try: command=input().strip()
                except EOFError: command='quit'
                if command!='run':break
    finally:
        if jpype.isJVMStarted():jpype.shutdownJVM()
        REPORT['jvm_done']=not jpype.isJVMStarted();REPORT['jvm_starts']=1;REPORT['suite_attempts']=runs
        dump('pc_results.json',REPORT)
        print('JVM_DONE',REPORT['jvm_done'],'SLOT_RELEASED',flush=True)

if __name__=='__main__':main()
