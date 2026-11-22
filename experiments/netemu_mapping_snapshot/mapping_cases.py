"""Compiled PPC cases invoked only by parent validate_pc.py --allow-jvm."""
import struct

def run_mapping_cases(case,SP,MASK):
    for target,ea in [(0,0x84000000),(1,0x80000000)]:
        for slot in range(16):
            def matched(m,target=target,ea=ea,slot=slot):
                m.entries.clear()
                low=[0x1014,0x1024,0x102c,0xab78][slot%4]
                m.install_entry(ea,slot,low)
                p,s=m.groups(ea); index=(p if slot<8 else s)+slot%8
                m.expected_queries=[]
                for address in (0x84000000,m.pool_ea):
                    gp,gs=m.groups(address); m.expected_queries += [gp,gp+4,gs,gs+4]
                m.finish(); m.call(True)
                m.assert_record(ea,target,index=index,low=low)
                m.assert_record(m.pool_ea if target==0 else 0x84000000,1-target,code=4,matches=0)
            case('unique_target_%d_slot_%d'%(target,slot),matched)
        def duplicate(m,target=target,ea=ea):
            m.entries.clear(); m.install_entry(ea,0,0x1014); m.install_entry(ea,15,0x102c)
            m.finish(); m.call(True); m.assert_record(ea,target,code=5,matches=2)
        case('ambiguous_across_groups_target_'+str(target),duplicate)
        def absent(m,target=target,ea=ea):
            m.entries.clear(); m.finish(); m.call(True)
            m.assert_record(ea,target,code=4,matches=0)
        case('absent_target_'+str(target),absent)
    def wrong_v(m):
        m.entries.clear(); p,s=m.groups(0x84000000); v=0x7405
        m.entries[p]=(v^1,0x1014); m.entries[p+1]=(v|2,0x1014); m.entries[s]=(v,0x1014)
        m.finish(); m.call(True); m.assert_record(0x84000000,code=4,matches=0)
    case('exact_V_and_group_marker_required',wrong_v)
    for failure in range(8):
        def hcall_error(m,failure=failure):
            m.query_fail=failure; m.finish(); m.call(True)
            target=0 if failure<4 else 1; ea=0x84000000 if target==0 else m.pool_ea
            n=failure%4+1
            m.assert_record(ea,target,code=3,queries=n,matches=0 if n==1 else 1,status=MASK-4)
            assert len(m.queries)==n+4
        case('query_nonzero_status_'+str(failure),hcall_error)
    for address in (0x930f98,0x930fb0):
        for after in range(8):
            def changed(m,address=address,after=after):
                def mutate(x,n):
                    if n==after: x.fixture(address,x.q(address)+1)
                m.query_effect=mutate; m.finish(); m.call(True)
                target=0 if after<4 else 1; ea=0x84000000 if target==0 else m.pool_ea
                n=after%4+1
                m.assert_record(ea,target,code=2,queries=n,matches=0 if n==1 else 1)
                assert len(m.queries)==after+1
                if target==0: m.assert_record(m.pool_ea,1,code=2,queries=0,matches=0)
            case('HTAB_mutation_%x_after_%d'%(address,after),changed)
    for size in (0x40000,0x80000,0x100000):
        def valid_size(m,size=size):
            m.htab_size=size; m.fixture(0x930fb0,size); m.entries.clear()
            m.install_entry(0x84000000,15,0x1024); m.install_entry(m.pool_ea,15,0x1014)
            m.finish(); m.call(True)
            for target,ea,low in [(0,0x84000000,0x1024),(1,m.pool_ea,0x1014)]:
                m.assert_record(ea,target,index=m.groups(ea)[1]+7,low=low)
        case('supported_HTAB_size_'+hex(size),valid_size)
    def zero_handle(m):
        m.htab=0; m.fixture(0x930f98,0); m.finish(); m.call(True)
        assert len(m.queries)==8
        m.assert_record(0x84000000,0,index=m.groups(0x84000000)[0],low=0x1014)
        m.assert_record(m.pool_ea,1,index=m.groups(m.pool_ea)[0],low=0x102c)
    case('zero_current_HTAB_handle_supported_by_stock_handler',zero_handle)
    def zero_handle_error(m):
        m.htab=0; m.fixture(0x930f98,0); m.query_fail=0; m.finish(); m.call(True)
        assert len(m.queries)==5
        m.assert_record(0x84000000,0,code=3,queries=1,matches=0,status=MASK-4)
        m.assert_record(m.pool_ea,1,index=m.groups(m.pool_ea)[0],low=0x102c)
    case('zero_current_handle_error_outputs_remain_uninterpreted',zero_handle_error)
    for address,value in [(0x930fb0,0),(0x930fb0,0x20000),(0x930fb0,0x40001),
                          (0x930fb0,0x200000)]:
        def bad_htab(m,address=address,value=value):
            m.fixture(address,value); m.finish(); m.call(True); assert not m.queries
            for target,ea in [(0,0x84000000),(1,m.pool_ea)]:
                m.assert_record(ea,target,code=1,queries=0,matches=0)
            assert struct.unpack('>64Q',m.snapshots[-1])[24]==m.q(0x930fb0)
        case('bad_HTAB_%x_%x'%(address,value),bad_htab)
    for address,value in [(0x934960,0x60001),(0x934968,0),(0x934970,0),
                          (0x934970,0x40000001),(0x934970,0xfffffffffff00000),
                          (0x934980,0x90000000),(0x934980,0x80001000),
                          (0x24565b8,0),(0x2446588,0),(0x24565a0,1)]:
        def invalid_pool(m,address=address,value=value):
            m.fixture(address,value); m.finish(); m.call(True)
            m.assert_record(m.q(0x934980),1,code=0,queries=0,matches=0); assert len(m.queries)==4
        case('pool_metadata_reject_%x_%x'%(address,value),invalid_pool)
    for ea in range(0x80000000,0x90000000,0x800000):
        def pool_slot(m,ea=ea):
            for a,v in [(0x934980,ea),(0x24565b8,ea),(0x2446588,ea+0x20000),(0x24565a0,ea+0x20000)]: m.fixture(a,v)
            m.entries.clear(); m.install_entry(ea,9,0x1014)
            m.finish(); m.call(True); m.assert_record(ea,1,index=m.groups(ea)[1]+1,low=0x1014)
        case('pool_native_slot_'+hex(ea),pool_slot)
    def banks_raw(m):
        for a in (0x2446568,0x2446598,0x2456568): m.fixture(a,MASK)
        m.finish(); m.call(True); assert len(m.queries)==8
        assert struct.unpack('>64Q',m.snapshots[-1])[33:36]==(MASK,)*3
    case('bank_words_are_samples_not_ownership_guard',banks_raw)
    for address,value in [(0x2458428,0xffff000000000001),(0x2458430,0x200000),(0x2458438,0)]:
        def cdvd_invalid(m,address=address,value=value):
            m.fixture(address,value); m.finish(); m.call(True)
            m.assert_record(m.state()[7],code=0,queries=0,matches=0); assert len(m.queries)==4
        case('captured_CDVD_tuple_reject_'+hex(address),cdvd_invalid)
    def live_cdvd_changed(m):
        m.finish(); m.original_effect=lambda x:x.fixture(0x2458428,0x85000000)
        m.call(True); m.assert_record(0x84000000,code=0,queries=0,matches=0); assert len(m.queries)==4
    case('shutdown_CDVD_tuple_changed',live_cdvd_changed)
    for status_failure in (False,True):
        def bridge_full(m,status_failure=status_failure):
            m.entries={i:(0x123456789abcdef0+i,0xab10+i) for i in range(4)}
            m.query_fail=0 if status_failure else None
            m.call(args=[m.htab,0,SP-256,4,5,6,7,8],bridge=True)
        case('bridge_full_ABI_and_five_outputs_'+str(status_failure),bridge_full)
