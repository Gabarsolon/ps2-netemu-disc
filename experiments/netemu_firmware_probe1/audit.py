"""Explicit store inventories; dynamic sites need compiled execution fences too.

This does not certify native helpers by treating their memory as payload-owned.
"""
from pathlib import Path
import json
import re
import llvmlite.binding as llvm

def audit_ir(path):
    mod=llvm.parse_assembly(Path(path).read_text()); mod.verify()
    assert all('constant ' in str(g) for g in mod.global_variables)
    stores=[]; calls=set(); bounds=[]
    native={'native_startup','native_refresh','native_shutdown','native_alloc',
            'irq_save','irq_restore','read_msr','read_pir','native_clock',
            'stock_ufs_open','stock_ufs_stat','stock_raw_write','stock_ufs_close',
            'lv1_open_device','lv1_close_device','lv1_event_rx_port','lv1_connect_irq_event',
            'native_repo_enum','native_repo_devid','native_repo_busid','lv1_alloc_dma',
            'lv1_map_dma','lv1_storage_read','lv1_get_async_status','dcache_flush',
            'lv1_send_device_command','lv1_connect_irq_plug'}
    defined={f.name for f in mod.functions if not f.is_declaration}
    for f in mod.functions:
        definitions={str(i):i for b in f.blocks for i in b.instructions}
        args={str(a):n for n,a in enumerate(f.arguments)}
        allins=[i for b in f.blocks for i in b.instructions]
        # Derive the simple forward loop induction bounds from THIS IR. The
        # compared induction variable controls a header's true exit / false
        # body; every indexed store is in that false body. No Python copy of
        # the allocator admission decides whether a native call can execute.
        induction={}
        block_of={str(i):b for b in f.blocks for i in b.instructions}
        for i in allins:
            if i.opcode!='phi':continue
            ops=list(i.operands)
            if len(ops)!=2 or not any(v.is_constant and v.get_constant_value()==0 for v in ops):continue
            inc=next((definitions.get(str(v)) for v in ops if not v.is_constant),None)
            if inc is None or inc.opcode!='add':continue
            vv=list(inc.operands)
            if len(vv)!=2 or str(vv[0])!=str(i) or not vv[1].is_constant or vv[1].get_constant_value()!=1:continue
            tests=[x for x in block_of[str(i)].instructions if x.opcode=='icmp' and 'icmp eq ' in str(x) and str(list(x.operands)[0])==str(i)]
            if len(tests)!=1:continue
            cap=list(tests[0].operands)[1]
            if not cap.is_constant:continue
            branch=list(block_of[str(i)].instructions)[-1]
            assert branch.opcode=='br' and len(list(branch.operands))==3
            # LLVM ValueRef presents successors in false, true order.
            false_block=list(branch.operands)[1]
            induction[str(i)]=(int(cap.get_constant_value()),str(false_block))
        def interval(v,store_block):
            key=str(v)
            if key in args:
                n=args[key]
                if f.name in ('initialize','probe_store','build_atapi') and n==0:return ('owned',0,0,8192)
                assert f.name=='admit' and n in (2,3),(f.name,key)
                return ('caller_stack_'+str(n),0,0,8)
            if v.is_constant:
                m=re.fullmatch(r'ptr inttoptr \(i64 (\d+) to ptr\)',key)
                if m:return ('fixed',int(m[1]),int(m[1]),0)
                assert str(v.type).startswith('i'),key
                n=v.get_constant_value();return ('number',n,n,0)
            i=definitions[key];ops=list(i.operands)
            if i.opcode=='alloca':
                m=re.search(r'alloca (?:\[(\d+) x i64\]|i64)',str(i));assert m,str(i)
                return ('stack_'+key.split('=')[0].strip(),0,0,(int(m[1]) if m[1] else 1)*8)
            if i.opcode=='inttoptr':
                origin,lo,hi,cap=interval(ops[0],store_block)
                if origin=='number':origin='fixed'
                return origin,lo,hi,cap
            if i.opcode=='phi':
                assert key in induction,(f.name,key)
                cap,body=induction[key]
                assert str(store_block)==body,(f.name,'indexed store outside proved false body',key)
                return ('number',0,cap-1,0)
            if i.opcode=='getelementptr':
                origin,lo,hi,cap=interval(ops[0],store_block)
                indices=ops[1:]
                if len(indices)==2:
                    assert indices[0].is_constant and indices[0].get_constant_value()==0,str(i)
                    indices=indices[1:];scale=8
                else:
                    assert len(indices)==1,str(i)
                    scale=8 if '[8 x i8]' in str(i) or re.search(r'getelementptr.*? i64, ptr',str(i)) else 1
                o,l,h,_=interval(indices[0],store_block);assert o=='number',str(i)
                return origin,lo+l*scale,hi+h*scale,cap
            if i.opcode=='add':
                left=interval(ops[0],store_block);right=interval(ops[1],store_block)
                if left[0]=='number':left,right=right,left
                assert right[0]=='number',str(i)
                return left[0],left[1]+right[1],left[2]+right[2],left[3]
            if i.opcode=='and':
                # C=align_up(A+1000,128), A is 64-byte aligned. No
                # generalized bitmask or unknown pointer is accepted.
                base=interval(ops[0],store_block)
                assert base==('owned',4223,4223,8192) and ops[1].is_constant and ops[1].get_constant_value()==(1<<64)-128,str(i)
                return ('owned',4096,4160,8192)
            raise AssertionError((f.name,'unproved store pointer',str(i)))
        def roots(v,seen=None):
            seen=set() if seen is None else set(seen)
            key=str(v)
            if key in args: return {'arg'+str(args[key])}
            if v.is_constant:
                return {'fixed:'+str(v)}
            if key in seen: return {'loop'}
            seen.add(key)
            i=definitions.get(key); assert i is not None,str(v)
            if i.opcode=='alloca': return {'stack'}
            assert i.opcode in ('getelementptr','inttoptr','add','and','phi','or','shl','zext'),str(i)
            return set().union(*(roots(x,seen) for x in i.operands))
        for b in f.blocks:
            for i in b.instructions:
                ops=list(i.operands)
                if i.opcode=='store':
                    assert str(ops[0].type) in ('i8','i32','i64'),str(i)
                    r=roots(ops[1]); dynamic=any(x.startswith('arg') for x in r)
                    if dynamic:
                        if f.name in ('initialize','probe_store','build_atapi'):
                            assert {x for x in r if x.startswith('arg')}=={'arg0'},r
                            category='fresh_owned_A: state[0,1000), C[0,40), data[0,800)'
                        else:
                            assert f.name=='admit' and r in ({'arg2'},{'arg3'}),(f.name,r,str(i))
                            category='caller_stack_output'
                    else:
                        category='fixed_or_stack'
                        for x in r:
                            if x.startswith('fixed:ptr inttoptr'):
                                m=re.search(r'i64 (\d+)',x); a=int(m[1]);
                                assert 0x930f20<=a<0x930f80 or a==0x934161,(f.name,x)
                    stores.append(dict(function=f.name,ir=str(i),roots=sorted(r),category=category))
                    origin,lo,hi,cap=interval(ops[1],b)
                    width=int(str(ops[0].type)[1:])//8
                    if origin=='fixed':
                        assert 0x930f20<=lo<=hi and hi+width<=0x930f80 or lo==hi==0x934161 and width==1,(f.name,origin,lo,hi)
                    else:assert 0<=lo<=hi and hi+width<=cap,(f.name,origin,lo,hi,cap)
                    bounds.append(dict(function=f.name,origin=origin,min_offset=lo,max_offset=hi,width=width,capacity=cap))
                elif i.opcode=='call':
                    callee=ops[-1].name
                    assert callee in native|defined or callee.startswith(('llvm.lifetime.','llvm.umin.','llvm.readcyclecounter')),str(i)
                    calls.add(callee)
                elif i.opcode in ('atomicrmw','cmpxchg','invoke','callbr'): raise AssertionError(str(i))
                elif i.opcode=='fence': assert str(i).strip()=='fence seq_cst'
    result=dict(status='PASS_BOUNDED_STORE_POINTERS',stores=stores,bounds=bounds,callees=sorted(calls),
        scope='Every IR store pointer bounded to exact mailbox/reason, local alloca, admit caller-stack output, or fresh initialize A+offset within 8192. Induction and alignment expressions fail closed on other IR. Caller admission/fresh-result dominance additionally checked in source and actual PPC; native effects excluded.')
    Path(path).with_name('ir_store_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def audit_assembly(path,trampolines):
    from elftools.elf.elffile import ELFFile
    with Path(path).with_name('payload.elf').open('rb') as f:
        elf=ELFFile(f);syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        sections=[(s['sh_addr'],s.data()) for s in elf.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS']
    def word(a):return next(int.from_bytes(b[a-base:a-base+4],'big') for base,b in sections if base<=a<a+4<=base+len(b))
    text=Path(path).read_text(); frames={}; stores=[]; name=None;pc=None
    for number,line in enumerate(text.splitlines(),1):
        s=line.split('#',1)[0].strip()
        if re.fullmatch(r'[A-Za-z_]\w*:',s):name=s[:-1];pc=syms[name]
        if s.startswith('st'):
            m=re.fullmatch(r'(std|stdu|stw|stb|sth|stdx)\s+(.*)',s)
            assert m,('store form',name,s)
            parts=re.fullmatch(r'(std|stdu|stw|stb|sth) (\d+), (-?\d+)\((\d+)\)',s)
            assert parts,('unreviewed indexed store',name,s)
            op,rt,disp,ra=parts[1],int(parts[2]),int(parts[3]),int(parts[4])
            expected={'std':62,'stdu':62,'stw':36,'stb':38,'sth':44}[op]<<26|rt<<21|ra<<16|(disp&0xffff)
            if op=='stdu':expected|=1
            actual=word(pc);assert actual==expected,(name,s,hex(pc),hex(actual),hex(expected))
            stores.append(dict(function=name,line=number,assembly=s,pc=hex(pc),word=hex(actual)))
            fm=re.fullmatch(r'stdu\s+1, (-\d+)\(1\)',s)
            if fm: frames[name]=-int(fm[1]); assert frames[name]<=2048
        if line.startswith('\t') and s and not s.startswith(('.','#')):pc+=4
    for row in trampolines:
        if row['op'].startswith('st'):
            assert (row['op'],*row['args']) in [
                ('std','r0','16(r1)'),('std','r2','120(r1)'),('std','r12','120(r1)'),('std','r0','96(r1)'),
                ('stdu','r1','-128(r1)'),('stdu','r1','-320(r1)')],row
    result=dict(status='PASS_ALL_STORE_WORDS_MATCH_BOUNDED_IR_TRANSLATION',stores=stores,frames=frames,
        scope='Every compiler assembly store is operand-encoded against its linked PPC instruction word; wrapper stores restricted separately. IR supplies pointer bounds. Actual execution separately fences native metadata, payload-owned ranges, mailbox/reason and stack.')
    Path(path).with_name('assembly_store_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
