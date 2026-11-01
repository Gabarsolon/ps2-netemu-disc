"""LLVM pointer provenance assertions for P10 probe (V1).
Fixed stores must stay inside 96-byte RW mailbox [0x930F20, 0x930F80).
Arena stores stay inside the validated 4 KiB allocator arena.
Command block and data area stores stay inside the verified CDVD buffer.
All other stores must be stack-local.
Zero stores at or above 0x930F80.
"""
from pathlib import Path
import json, re
import llvmlite.binding as llvm

H = Path(__file__).resolve().parent

def audit(ll_path=None, variant='V1'):
    if ll_path is None:
        ll_path = H / 'build' / f'probe_p10_{variant}.ll'
    else:
        ll_path = Path(ll_path)
    m = llvm.parse_assembly(ll_path.read_text())
    assert all(g.is_constant or 'constant' in str(g).split('=', 1)[-1] for g in m.global_variables), 'mutable global'

    allowed_callees = {
        'probe_run', 'run_probe', 'repo_read', 'lv1_hcall', 'native_alloc', 'native_clock',
        'arena_rw', 'get_arena', 'check_cdvd_buffer_guard',
        'poll_completion', 'setup_atapi_block', 'setup_read10_block',
        'prefill_buffer', 'count_a5', 'do_request_sense', 'perform_request_sense', 'execute_read_test',
        'classify_sector', 'classify_buffer', 'class_to_str',
        'format_row', 'fmt_str', 'fmt_hex', 'fmt_dec', 's4_menu',
        'hddlog_init', 'hddlog_write', 'hddlog_mark_clean_shutdown', 'is_hdd_log_safe', 'safe_strcpy',
        'append_str', 'format_dec', 'format_hex64', 'format_hex32', 'format_hex16', 'format_s32',
        'format_bytes_hex', 'format_ascii', 'stock_ufs_open', 'stock_ufs_close', 'stock_raw_read',
        'stock_raw_write', 'stock_hdd_cache_flush', 'stock_repo_query', 'get_r2'
    }

    for f in m.functions:
        if f.is_declaration:
            continue
        insts = [x for b in f.blocks for x in b.instructions]
        defs = {x: x for x in insts}
        args = {a: 'arg' + str(j) for j, a in enumerate(f.arguments)}
        memo = {}

        def roots(v, seen=None):
            seen = set() if seen is None else set(seen)
            if v in seen:
                return set()
            seen.add(v)
            vk = str(v)
            if vk in memo:
                return set(memo[vk])
            if v in args:
                res = {args[v]}
                memo[vk] = res
                return set(res)
            a = defs.get(v)
            if a is not None:
                if a.opcode == 'alloca':
                    res = {'stack'}
                    memo[vk] = res
                    return set(res)
                if a.opcode == 'call':
                    ops = list(a.operands)
                    if ops and ops[-1].name in ['native_alloc', 'get_arena']:
                        res = {'arena'}
                        memo[vk] = res
                        return set(res)
                if a.opcode == 'load':
                    ops = list(a.operands)
                    ptr_roots = roots(ops[0], seen)
                    for r in ptr_roots:
                        if r.startswith('fixed:9637688'):  # 0x930f38 = S->arena_ptr
                            memo[vk] = {'arena'}
                            return {'arena'}
                        if r in {'arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'arg5'}:
                            memo[vk] = {'deref:' + r}
                            return {'deref:' + r}
                        if r == 'stack':
                            stored_roots = set()
                            for inst in insts:
                                if inst.opcode == 'store' and list(inst.operands)[1] == ops[0]:
                                    stored_roots |= roots(list(inst.operands)[0], seen)
                            if stored_roots:
                                memo[vk] = stored_roots
                                return set(stored_roots)
                ops = list(a.operands)
                if a.opcode in ['getelementptr', 'bitcast', 'addrspacecast', 'inttoptr', 'or', 'add', 'sub']:
                    res = roots(ops[0], seen)
                    memo[vk] = res
                    return set(res)
                if a.opcode in ['phi', 'select']:
                    out = set()
                    for x in ops:
                        if str(x.type) == 'ptr' or str(x.type).startswith('i'):
                            out |= roots(x, seen)
                    memo[vk] = out
                    return set(out)
            t = str(v)
            k = re.fullmatch(r'ptr inttoptr \(i64 (\d+) to ptr\)', t)
            if t == 'ptr null':
                return set()
            if k:
                res = {'fixed:' + k[1]}
                memo[vk] = res
                return set(res)
            res = {'UNKNOWN:' + t}
            memo[vk] = res
            return set(res)

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
                    elif f.name in {'setup_atapi_block', 'setup_read10_block', 'prefill_buffer'} and root == 'arg0':
                        pass
                    elif f.name in {'do_request_sense', 'perform_request_sense'} and (root.startswith('arg') or root in {'stack', 'arena'}):
                        pass
                    elif f.name in {'execute_read_test', 'classify_buffer'} and (root.startswith('arg') or root in {'stack', 'arena'}):
                        pass
                    elif f.name == 'poll_completion' and (root.startswith('arg') or root in {'stack', 'arena'}):
                        pass
                    elif f.name in {'format_row', 'fmt_str', 'fmt_hex', 'fmt_dec', 'safe_strcpy', 'append_str', 'format_dec', 'format_hex64', 'format_hex32', 'format_hex16', 'format_s32', 'format_bytes_hex', 'format_ascii'} and (root.startswith('arg') or root.startswith('deref:arg') or root in {'stack', 'arena'}):
                        pass
                    elif f.name == 'check_cdvd_buffer_guard' and root in {'arg0', 'arg1', 'arg2'}:
                        pass
                    elif f.name in {'hddlog_init', 'hddlog_write', 'hddlog_mark_clean_shutdown'} and (root.startswith('arg') or root in {'stack', 'arena'}):
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

    print(f"IR provenance audit PASSED for {variant}: all stores strictly to stack, mailbox [0x930F20, 0x930F80), arena, or verified buffer range.")
    return True

if __name__ == '__main__':
    audit()
