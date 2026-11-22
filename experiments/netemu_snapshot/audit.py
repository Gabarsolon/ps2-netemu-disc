"""Fail-closed store audits for this candidate; no native body claims."""
from pathlib import Path
import json
import re
import llvmlite.binding as llvm

def literal(s):
    m=re.fullmatch(r'ptr inttoptr \(i64 (\d+) to ptr\)',s)
    return int(m[1]) if m else None

def audit_ir(path):
    module=llvm.parse_assembly(Path(path).read_text()); module.verify()
    assert all(g.is_global and 'constant ' in str(g) for g in module.global_variables)
    permitted={'native_refresh','native_shutdown','native_clock','stock_ufs_open',
               'stock_ufs_stat','stock_raw_write','stock_ufs_close','ui_reason_ok',
               'hdd_idle','captured_guard','tick','write_snapshot',
               'llvm.umin.i64','llvm.readcyclecounter','llvm.lifetime.start.p0','llvm.lifetime.end.p0'}
    stores=[]; callees=set()
    for f in module.functions:
        definitions={str(i):i for b in f.blocks for i in b.instructions}
        def root(v):
            a=literal(str(v))
            if a is not None: return ('fixed',a,0)
            i=definitions.get(str(v))
            assert i is not None, ('unknown store pointer',str(v))
            if i.opcode=='alloca':
                m=re.search(r'alloca \[(\d+) x i64\]',str(i))
                assert m, str(i)
                return ('stack',0,int(m[1])*8)
            assert i.opcode=='getelementptr',str(i)
            ops=list(i.operands)
            base,offset,capacity=root(ops[0])
            if len(ops)==2:
                assert ops[1].is_constant,str(i)
                scale=1 if re.search(r'getelementptr .*?i8, ptr',str(i)) else 8 if re.search(r'getelementptr .*?i64, ptr',str(i)) else None
                assert scale is not None,str(i)
                offset+=ops[1].get_constant_value()*scale
            else:
                assert len(ops)==3 and ops[1].is_constant and ops[2].is_constant,str(i)
                assert ops[1].get_constant_value()==0,str(i)
                offset+=ops[2].get_constant_value()*8
            return base,offset,capacity
        for b in f.blocks:
            for i in b.instructions:
                ops=list(i.operands)
                if i.opcode=='store':
                    val,dst=ops
                    assert str(val.type) in ('i8','i32','i64'),str(i)
                    width=int(str(val.type)[1:])//8
                    base,offset,cap=root(dst)
                    if base=='fixed':
                        assert (0x930f20<=offset<offset+width<=0x930f80 or
                                offset==0x934161 and width==1),str(i)
                    else: assert 0<=offset<offset+width<=cap,str(i)
                    stores.append(dict(function=f.name,base=base,offset=hex(offset),width=width))
                elif i.opcode=='call':
                    name=ops[-1].name
                    assert name in permitted,('callee/inline asm',str(i))
                    callees.add(name)
                elif i.opcode in ('atomicrmw','cmpxchg','invoke','callbr'):
                    raise AssertionError(str(i))
                elif i.opcode=='fence': assert str(i).strip()=='fence seq_cst'
    result=dict(status='PASS',stores=stores,callees=sorted(callees),
                scope='Every payload IR store resolves to fixed mailbox/reason or bounded local alloca. Native callees excluded.')
    Path(path).with_name('ir_store_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def audit_assembly(path,trampolines):
    # Dataflow of exact constants and SP-derived pointers through the emitted
    # CFG. Unknown values may exist, but cannot be used as store addresses.
    functions={}; labels={}; current=None
    for number,line in enumerate(Path(path).read_text().splitlines(),1):
        stripped=line.split('#',1)[0].strip()
        if not line.startswith((' ','\t')) and re.fullmatch(r'[A-Za-z_]\w*:',stripped):
            current=stripped[:-1]; functions[current]=[]; labels[current]={}
        elif current and stripped.endswith(':') and stripped.startswith('.L'):
            labels[current][stripped[:-1]]=len(functions[current])
        elif current and line.startswith('\t') and stripped and not stripped.startswith(('.','#')):
            functions[current].append((number,stripped.split('#',1)[0].strip()))
    receipts=[]; frames={}
    for name,insns in functions.items():
        pending=[(0,{1:('stack',0)})]; seen={}
        while pending:
            index,regs=pending.pop()
            while index<len(insns):
                if index in seen:
                    merged={n:v for n,v in regs.items() if seen[index].get(n)==v}
                    if merged==seen[index]: break
                    regs=merged
                seen[index]=dict(regs)
                number,text=insns[index]; op,*rest=text.split(None,1)
                args=[a.strip() for a in rest[0].split(',')] if rest else []
                def reg(n): return regs.get(int(n))
                def constant(n):
                    x=reg(n); return x[1] if x and x[0]=='fixed' else None
                if op.startswith('st'):
                    m=re.fullmatch(r'(std|stdu|stw|stb|sth) (\d+), (-?\d+)\((\d+)\)',text)
                    assert m,('unreviewed store form',name,text)
                    kind,rt,disp,ra=m[1],int(m[2]),int(m[3]),int(m[4])
                    base=regs.get(ra); assert base,(name,text,regs)
                    origin,target=base[0],base[1]+disp
                    width={'std':8,'stdu':8,'stw':4,'stb':1,'sth':2}[kind]
                    if origin=='stack': assert -8192<=target<target+width<=32,(name,text,target)
                    else: assert (0x930f20<=target<target+width<=0x930f80 or target==0x934161 and width==1),(name,text,target)
                    receipts.append(dict(function=name,line=number,assembly=text,base=origin,target=hex(target),width=width))
                    if kind=='stdu':
                        assert rt==ra==1 and disp<0 and disp%16==0,(name,text)
                        regs[1]=(origin,target); frames[name]=-disp
                elif op in ('li','lis'):
                    regs[int(args[0])]=('fixed',int(args[1])*(65536 if op=='lis' else 1))
                elif op in ('addi','addis','ori','oris'):
                    dst,src=int(args[0]),int(args[1]); v=regs.get(src)
                    try: imm=int(args[2])
                    except ValueError:
                        regs.pop(dst,None); index+=1; continue
                    if v:
                        imm*=65536 if op in ('addis','oris') else 1
                        regs[dst]=(v[0],v[1]+imm if op.startswith('add') else (v[1]|imm))
                    else: regs.pop(dst,None)
                elif op=='mr':
                    if reg(args[1]): regs[int(args[0])]=reg(args[1])
                    else: regs.pop(int(args[0]),None)
                elif op in ('rldicr','sldi'):
                    v=constant(args[1]); dst=int(args[0])
                    if v is not None:
                        shift=int(args[2]); value=(v<<shift)&((1<<64)-1)
                        if op=='rldicr': value&=(((1<<64)-1) << (63-int(args[3])))&((1<<64)-1)
                        regs[dst]=('fixed',value)
                    else: regs.pop(dst,None)
                elif op in ('bl','blrl','bctrl'):
                    assert op=='bl',text
                    for n in [0,*range(3,13)]: regs.pop(n,None)
                elif op=='blr': break
                elif op=='b':
                    if args[0] not in labels[name]: break # external tail call
                    index=labels[name][args[0]]; continue
                elif op.startswith('b') and op not in ('blr',):
                    # Branch CR operands precede the final label.
                    dest=args[-1]
                    if dest in labels[name]: pending.append((labels[name][dest],dict(regs)))
                    elif op.endswith('lr'): pass
                    else: raise AssertionError((name,text))
                elif op not in ('cmpdi','cmpldi','cmpwi','cmplwi','cmpd','cmpld',
                                'sync','isync','eieio','nop','mtlr','mtcrf','mtocrf'):
                    if args and args[0].isdigit(): regs.pop(int(args[0]),None)
                index+=1
        assert len(seen)<100000,name
    for row in trampolines:
        if row['op'].startswith('st'):
            assert (row['op'],*row['args']) in [
                ('std','r0','16(r1)'),('std','r2','120(r1)'),
                ('stdu','r1','-128(r1)'),('stdu','r1','-320(r1)')],row
    assert frames and max(frames.values())<=2048,frames
    result=dict(status='PASS',stores=receipts,frames=frames,
                scope='CFG register provenance for every compiler store plus enumerated wrapper stores. Native bodies excluded.')
    Path(path).with_name('assembly_store_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
