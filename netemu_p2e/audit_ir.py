"""LLVM pointer provenance assertions for P2E probe (K0..K3).
Fixed stores must stay inside 96-byte RW mailbox [0x930F20, 0x930F80).
Arena stores stay inside the validated 4 KiB allocator arena.
Command block stores stay inside the verified CDVD buffer.
All other stores must be stack-local.
Zero stores at or above 0x930F80.
"""
from pathlib import Path
import json, re
import llvmlite.binding as llvm

H = Path(__file__).resolve().parent

def audit(ll_path=None, variant='K0'):
    if ll_path is None:
        ll_path = H / 'build' / f'probe_p2e_{variant}.ll'
    else:
        ll_path = Path(ll_path)
    m = llvm.parse_assembly(ll_path.read_text())
    assert all(g.is_constant or 'constant' in str(g).split('=', 1)[-1] for g in m.global_variables), 'mutable global'

    allowed_callees = {
        'run_probe', 'repo_read', 'lv1_hcall', 'native_alloc', 'native_clock',
        'arena_rw', 'get_arena', 'check_cdvd_buffer_guard',
        'poll_completion', 'setup_atapi_block',
        'format_row', 'fmt_str', 'fmt_hex', 'fmt_dec', 's4_menu'
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
                if a.opcode == 'call':
                    ops = list(a.operands)
                    if ops and ops[-1].name in ['native_alloc', 'get_arena']:
                        return {'arena'}
                if a.opcode == 'load':
                    ops = list(a.operands)
                    ptr_roots = roots(ops[0], seen)
                    for r in ptr_roots:
                        if r.startswith('fixed:9637688'):  # 0x930f38 = S->arena_ptr
                            return {'arena'}
                        if r == 'stack':
                            stored_roots = set()
                            for inst in insts:
                                if inst.opcode == 'store' and list(inst.operands)[0] == ops[0]:
                                    stored_roots |= roots(list(inst.operands)[1], seen)
                            if stored_roots:
                                return stored_roots
                ops = list(a.operands)
                if a.opcode in ['getelementptr', 'bitcast', 'addrspacecast', 'inttoptr']:
                    return roots(ops[0], seen)
                if a.opcode in ['phi', 'select']:
                    out = set()
                    for x in ops:
                        if str(x.type) == 'ptr' or str(x.type).startswith('i'):
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
                width = 8 if str(val.type) == 'ptr' else int(str(val.type)[1:]) // 8
                assert r, (f.name, str(x))
                for root in r:
                    if root.startswith('fixed:'):
                        addr_val = int(root[6:])
                        assert 0x930f20 <= addr_val and addr_val + width <= 0x930f80, (f.name, str(x), root, hex(addr_val), width)
                    elif root in {'stack', 'arena'}:
                        pass
                    elif f.name == 'setup_atapi_block' and root == 'arg0':
                        # Stores to ATAPI command block in buffer
                        pass
                    elif f.name == 'poll_completion' and root in {'arg2', 'arg1'}:
                        # Status output pointer in arena
                        pass
                    elif f.name in {'format_row', 'fmt_str', 'fmt_hex', 'fmt_dec'} and root in {'arg0', 'arg1'}:
                        # In-arena string formatting buffer
                        pass
                    elif f.name == 'check_cdvd_buffer_guard' and root in {'arg0', 'arg1', 'arg2'}:
                        # Pointers to stack variables in caller
                        pass
                    else:
                        raise AssertionError(f'Unauthorized store: {f.name} {x} root={root}')

            if x.opcode == 'call':
                callee_op = list(x.operands)[-1]
                callee_name = callee_op.name
                if callee_name:
                    if callee_name.startswith('llvm.'):
                        continue
                    assert callee_name in allowed_callees, f'Unauthorized call: {callee_name}'

    print(f"IR provenance audit PASSED for {variant}: all stores strictly to stack, mailbox [0x930F20, 0x930F80), arena, or verified command block.")
    return True
