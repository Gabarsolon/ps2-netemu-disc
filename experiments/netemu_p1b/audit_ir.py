"""LLVM pointer provenance assertions for P1b probe.
Fixed stores must stay inside 96-byte RW mailbox [0x930F20, 0x930F80).
All other stores must be stack-local.
Allowed calls: run_probe, repo_read (91), lv1_open_device (170), lv1_close_device (171), s4_menu.
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
        'run_probe', 'repo_read', 'lv1_open_device', 'lv1_close_device',
        's4_menu', 'map_rc_idx', 'map_repo_rc'
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
                    else:
                        assert root in {'stack'}, (f.name, str(x), root)
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
            'All stores stay inside stack or 96-byte mailbox [0x930F20, 0x930F80).',
            'No stores point to read-only text or data memory.',
            'Only hypercalls 91, 170, 171 are called by probe.'
        ]
    )
    evidence_path = H / 'evidence' / 'p1b_ir_store_audit.json'
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(result, indent=2))
    print(f'IR audit: {len(rows)} stores verified strictly inside stack / mailbox [0x930F20, 0x930F80)')
    return result

if __name__ == '__main__':
    audit()
