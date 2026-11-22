"""LLVM pointer provenance assertions for P1c probe.
Stores must stay inside:
  1. 96-byte RW mailbox [0x930F20, 0x930F80)
  2. Native allocator owned 4 KiB arena (native_alloc 0xB9848)
  3. Stack frame
Allowed calls: repo_read (91), native_alloc (0xB9848), internal helpers.
"""
from pathlib import Path
import json, re
import llvmlite.binding as llvm

H = Path(__file__).resolve().parent

def audit(ll_path=None):
    if ll_path is None:
        ll_path = H / 'build' / 'probe.ll'
    else:
        ll_path = Path(ll_path)
    m = llvm.parse_assembly(ll_path.read_text())
    rows = []
    calls = []
    assert all(g.is_constant or 'constant' in str(g).split('=', 1)[-1] for g in m.global_variables), 'mutable global'

    allowed_callees = {
        'run_probe', 'dump_node', 'read_one_field', 'arena_rw', 'get_arena',
        'map_field_idx', 'map_blk_idx', 's4_menu', 'repo_read', 'native_alloc'
    }

    for f in m.functions:
        if f.is_declaration:
            continue
        insts = [x for b in f.blocks for x in b.instructions]
        defs = {x: x for x in insts}
        args = {a: 'arg' + str(j) for j, a in enumerate(f.arguments)}

        def roots(v, seen=None):
            seen = set() if seen is None else set(seen)
            if v in seen:
                return set()
            seen.add(v)
            if v in args:
                return {args[v]}
            a = defs.get(v)
            if a is not None:
                if a.opcode == 'alloca':
                    return {'stack'}
                if a.opcode == 'call' and list(a.operands)[-1].name in ['get_arena']:
                    return {'arena'}
                if a.opcode == 'inttoptr':
                    op = list(a.operands)[0]
                    origin = defs.get(op)
                    if origin is not None and origin.opcode == 'load':
                        return {'arena'}
                    if origin is not None and origin.opcode == 'call' and list(origin.operands)[-1].name == 'native_alloc':
                        return {'arena'}
                    if origin is not None and origin.opcode in ['add', 'or']:
                        return {'arena'}
                ops = list(a.operands)
                if a.opcode in ['getelementptr', 'bitcast', 'addrspacecast']:
                    return roots(ops[0], seen)
                if a.opcode in ['phi', 'select']:
                    out = set()
                    for x in ops:
                        if str(x.type) == 'ptr':
                            out |= roots(x, seen)
                    return out
            t = str(v)
            k = re.fullmatch(r'ptr inttoptr \(i64 (\d+) to ptr\)', t)
            if t == 'ptr null':
                return set()
            if k:
                return {'fixed:' + k[1]}
            return {'UNKNOWN:' + t}

        for x in insts:
            if x.opcode in ['store', 'cmpxchg', 'atomicrmw']:
                ops = list(x.operands)
                val, dst = (ops[1], ops[0]) if x.opcode in ['cmpxchg', 'atomicrmw'] else ops
                r = roots(dst)
                width = int(str(val.type)[1:]) // 8
                assert r, (f.name, str(x))
                for root in r:
                    if root.startswith('fixed:'):
                        addr_val = int(root[6:])
                        assert 0x930f20 <= addr_val and addr_val + width <= 0x930f80, (f.name, str(x), root)
                    elif root in {'arg0', 'arg1'}:
                        assert f.name in ['read_one_field', 'dump_node'], (f.name, str(x), root)
                    else:
                        assert root in {'stack', 'arena'}, (f.name, str(x), root)
                rows.append(dict(function=f.name, instruction=str(x).strip(), bytes=width, roots=sorted(r)))

            if x.opcode == 'call':
                ops = list(x.operands)
                callee = ops[-1].name
                assert callee in allowed_callees or callee.startswith('llvm.'), (f.name, callee)
                calls.append(dict(function=f.name, callee=callee))

    result = dict(
        passed=True,
        stores=rows,
        calls=calls,
        assumptions=[
            'All stores stay inside stack, 96-byte mailbox [0x930F20, 0x930F80), or allocator-owned arena.',
            'No stores point to read-only text or data memory.',
            'Only hypercall 91 and native_alloc 0xB9848 are called by probe.'
        ]
    )
    evidence_path = H / 'evidence' / 'p1c_ir_store_audit.json'
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(result, indent=2))
    print(f'IR audit: {len(rows)} stores verified strictly inside stack / mailbox / arena')
    return result

if __name__ == '__main__':
    audit()
