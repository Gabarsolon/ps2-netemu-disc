/* Stack-only observation. No mapping change, allocation, pointer chasing,
 * optical I/O, cache operation or interpretation of failed syscall outputs.
 * All output pointers at stock_query95 calls are local fixed 5-qword arrays.
 * Formula is checked against stock instructions by evidence.py (no JVM).
 */
extern u64 stock_query95(u64 handle,u64 first_index,volatile u64 *five_outputs);
enum { BAD_TUPLE=0, BAD_HTAB=1, HTAB_CHANGED=2, CALL_ERROR=3,
       NO_MATCH=4, AMBIGUOUS=5, UNIQUE=6 };

/* Expanded separately for each of the two fixed stack-sector records so
 * every explicit store resolves to a constant offset in a bounded alloca.
 * A full scan is four calls even after a match, to detect duplicates.
 * On error/change the low-R and matched index remain uninterpretable.
 */
#define SCAN_MAPPING(BASE,EA,VALID) do { \
    u64 ea=(EA), virt=0, expected=0, primary=0, secondary=0; \
    u64 outcome=BAD_TUPLE, rc=0, queries=0, matches=0; \
    u64 index=0, low=0; \
    if (VALID) { \
        virt=ea-0x10000000ULL; \
        expected=((virt>>23)<<7)|5; \
        outcome=BAD_HTAB; \
        if (bytes==0x40000 || bytes==0x80000 || bytes==0x100000) { \
            u64 mask=(bytes>>7)-1; \
            u64 hash=((virt>>20)&255)^7; \
            primary=(hash&mask)*8; secondary=(~hash&mask)*8; \
            outcome=NO_MATCH; \
            _Pragma("clang loop unroll(full)") \
            for (u32 k=0;k<4;++k) { \
                u64 first=(k<2 ? primary : secondary)+(k&1)*4; \
                /* Four-entry coverage plus complete group coverage. */ \
                if (primary+8>bytes/16 || secondary+8>bytes/16 || \
                    first+4>bytes/16 || R64(0x930f98)!=handle || R64(0x930fb0)!=bytes) { \
                    outcome=HTAB_CHANGED; break; \
                } \
                volatile u64 q[5]; \
                rc=stock_query95(handle,first,q); ++queries; \
                if (rc!=0) { outcome=CALL_ERROR; break; } \
                /* Post-check also rejects a changed final-call context. */ \
                if (R64(0x930f98)!=handle || R64(0x930fb0)!=bytes) { \
                    outcome=HTAB_CHANGED; break; \
                } \
                _Pragma("clang loop unroll(full)") \
                for (u32 j=0;j<4;++j) { \
                    if (q[j]==(expected | (k<2 ? 0 : 2))) { \
                        ++matches; index=first+j; low=(q[4]>>(16*(3-j)))&65535; \
                    } \
                } \
            } \
            if (outcome==NO_MATCH && matches!=0) outcome=matches==1 ? UNIQUE : AMBIGUOUS; \
        } \
    } \
    sector[(BASE)+0]=ea; sector[(BASE)+1]=virt; sector[(BASE)+2]=expected; \
    sector[(BASE)+3]=(primary<<32)|secondary; sector[(BASE)+4]=outcome; \
    sector[(BASE)+5]=rc; sector[(BASE)+6]=(queries<<32)|matches; \
    sector[(BASE)+7]=outcome==UNIQUE ? (index<<32)|(low<<16)|(low&0x78) : 0xffffffff00000000ULL; \
} while (0)

/* Read fixed metadata only. None of these samples reserves an allocation.
 * Sentinel is H+10040, initialized to E+20000 (not a boolean).
 * The bank words are diagnostic only; no headroom/ownership gate uses them.
 */
#define MAPPING_SNAPSHOT() do { \
    u64 handle=R64(0x930f98), bytes=R64(0x930fb0); \
    sector[23]=handle; sector[24]=bytes; \
    sector[25]=R64(0x934960); sector[26]=R64(0x934968); \
    sector[27]=R64(0x934970); sector[28]=R64(0x934980); \
    sector[29]=R64(0x24565b8); sector[30]=R64(0x2446588); \
    sector[31]=R64(0x2446588); sector[32]=R64(0x24565a0); \
    sector[33]=R64(0x2446568); sector[34]=R64(0x2446598); \
    sector[35]=R64(0x2456568); \
    u64 e=sector[28], p=sector[27]; \
    int pool_ok=sector[25]==0x60000 && sector[26]==1 && \
        (e&~0x0f800000ULL)==0x80000000ULL && (e&0x7fffff)==0 && \
        sector[29]==e && sector[30]==e+0x20000 && sector[31]==e+0x20000 && \
        sector[32]==e+0x20000 && p!=0 && (p&0xfffff)==0 && \
        p<=~0ULL-0x100000 && e<=~0ULL-0x100000; \
    int cdvd_ok=MAIL[7]==0x84000000 && MAIL[8]==0x100000 && \
        MAIL[9]==0x500002c00000ULL && sector[20]==MAIL[7] && \
        sector[21]==MAIL[8] && sector[22]==MAIL[9]; \
    SCAN_MAPPING(40,MAIL[7],cdvd_ok); \
    SCAN_MAPPING(48,e,pool_ok); \
} while (0)
