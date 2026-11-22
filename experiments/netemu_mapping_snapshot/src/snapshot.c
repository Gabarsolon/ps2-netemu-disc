/* INERT diagnostic. No optical requests or staging-buffer accesses.
 * Persistent payload stores: 96-byte mailbox and exact stock reason byte.
 * Native UFS helpers may wait indefinitely; no watchdog/recovery claim.
 */
typedef unsigned char u8;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef signed int s32;
typedef signed long long s64;
#define R8(a) (*(const volatile u8 *)(a##ULL))
#define R32(a) (*(const volatile u32 *)(a##ULL))
#define R64(a) (*(const volatile u64 *)(a##ULL))
#define TIMER_MAGIC 0x53544d5230303031ULL
#define PUBLISHING 0x5350554230303031ULL
#define ABORTED 0x5341425430303031ULL
#define TERMINAL_PREFIX 0x534e503100000000ULL
#define CONSUMED_PREFIX 0x534e433100000000ULL
#define DELAY (20ULL * 79800000ULL)
#define MAIL ((volatile u64 *)0x930f20ULL)
struct Timer { u64 magic, start, last, count, phase, reserved[7]; };
_Static_assert(sizeof(struct Timer) == 96, "mailbox");
#define S ((volatile struct Timer *)0x930f20ULL)
extern u64 native_refresh(u64,u64,u64,u64,u64,u64,u64,u64);
extern u64 native_shutdown(u64,u64,u64,u64,u64,u64,u64,u64);
extern u64 native_clock(void);
extern s32 stock_ufs_open(u64,const char *);
extern s32 stock_ufs_stat(s32,void *);
extern s64 stock_raw_write(s32,u64,const void *,u64);
extern s32 stock_ufs_close(s32);
#include "mapping.h"

static int ui_reason_ok(void) {
    return R8(0x934161)==0 && R64(0x306fc68)==0x30700d0ULL &&
           R64(0x30700d0)==0x949cb8ULL;
}
static int hdd_idle(void) {
    return R8(0x241c8d5)==1 && R8(0x241c8c8)==0 &&
           R64(0x241c860)==3 && R64(0x241c888)==0 &&
           R64(0x241c890)==0 && R64(0x241c898)==0 && R32(0x3055180)==0;
}
static int captured_guard(void) {
    return MAIL[1]==0x30700d0ULL && MAIL[2]==0x949cb8ULL &&
           MAIL[3]==3 && MAIL[4]==0 && MAIL[5]==0 && MAIL[6]==0 &&
           MAIL[11]==0x10000ULL;
}
static void tick(void) {
    if (S->magic==0) {
        for (u32 i=0;i<12;++i) if (MAIL[i]!=0) return;
        if (!ui_reason_ok() || !hdd_idle()) return;
        u64 now=native_clock();
        if (now==0 || !ui_reason_ok() || !hdd_idle()) return;
        S->start=now; S->last=now; S->count=0; S->phase=1;
        __atomic_thread_fence(__ATOMIC_SEQ_CST);
        S->magic=TIMER_MAGIC;
        return;
    }
    if (S->magic!=TIMER_MAGIC || S->phase!=1) return;
    for (u32 i=0;i<7;++i) if (S->reserved[i]!=0) return;
    u64 start=S->start, last=S->last, count=S->count;
    if (start==0 || last<start || count>100) return;
    if (!ui_reason_ok()) { S->phase=3; return; }
    u64 now=native_clock();
    if (now<last) { S->phase=3; return; }
    S->last=now;
    if (count<100) ++count;
    S->count=count;
    if (now-start<DELAY || count<100) return;
    if (!ui_reason_ok() || !hdd_idle()) return;
    if (S->magic!=TIMER_MAGIC || S->phase!=1) return;
    S->phase=2;
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    /* Invalidate timer schema BEFORE overwriting any timer fields. */
    S->magic=PUBLISHING;
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    MAIL[1]=R64(0x306fc68); MAIL[2]=R64(0x30700d0);
    MAIL[3]=R64(0x241c860); MAIL[4]=R64(0x241c888);
    MAIL[5]=R64(0x241c890); MAIL[6]=R64(0x241c898);
    MAIL[7]=R64(0x2458428); MAIL[8]=R64(0x2458430); MAIL[9]=R64(0x2458438);
    MAIL[10]=((u64)R32(0x241c850)<<32)|R32(0x241c8a8);
    MAIL[11]=((u64)R32(0x3055180)<<32)|((u64)R8(0x241c8c8)<<24)|
             ((u64)R8(0x241c8d5)<<16)|((u64)R8(0x934161)<<8);
    if (!captured_guard() || !ui_reason_ok() || !hdd_idle()) {
        S->magic=ABORTED; return;
    }
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    /* One aligned 64-bit commit publishes completed data, not an atomic
     * 96-byte sampling operation. Low word is a coarse timebase session. */
    S->magic=TERMINAL_PREFIX | (u32)((now>>26)+1);
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    if (R8(0x934161)!=0) { S->magic=ABORTED; return; }
    *(volatile u8 *)0x934161ULL=2;
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
}

u64 snapshot_refresh(u64 a,u64 b,u64 c,u64 d,u64 e,u64 f,u64 g,u64 h) {
    u64 result=native_refresh(a,b,c,d,e,f,g,h);
    tick();
    return result;
}

static __attribute__((noinline)) void write_snapshot(u64 result) {
    u64 marker=MAIL[0];
    if ((marker & 0xffffffff00000000ULL)!=TERMINAL_PREFIX ||
        !captured_guard() || R8(0x934161)!=2) return;
    /* Inline mftb intrinsic: same timebase as stock B9CD0, no native call.
     * Reject old/future coarse sessions before invoking any UFS helper.
     * Publication lifetime: <121 ticks of 2^26 TB cycles (~101.8 seconds).
     */
    u64 now=__builtin_readcyclecounter();
    u32 epoch=(u32)(now>>26), session=(u32)marker-1;
    if ((u32)(epoch-session)>120) return;
    if (MAIL[0]!=marker || R8(0x934161)!=2 ||
        R64(0x306fc68)!=0x30700d0ULL || R64(0x30700d0)!=0x949cb8ULL ||
        R8(0x241c8d5)!=1 || R8(0x241c8c8)!=0 || R64(0x241c860)!=3 ||
        R32(0x3055180)!=0) return;
    /* Consume before first native helper: failure cannot cause retries. */
    MAIL[0]=CONSUMED_PREFIX | (u32)marker;
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    volatile u64 sector[64];
    volatile u64 statbuf[6];
    #pragma clang loop unroll(full)
    for (u32 i=0;i<64;++i) sector[i]=0;
    #pragma clang loop unroll(full)
    for (u32 i=0;i<6;++i) statbuf[i]=0;
    sector[0]=0x4d41505345433100ULL; /* MAPSEC1 + NUL; distinct file/schema */
    sector[1]=0x0001000000000200ULL;
    sector[2]=marker; sector[3]=now;
    sector[4]=0xb46100; sector[5]=2; sector[6]=result;
    sector[8]=marker;
    #pragma clang loop unroll(full)
    for (u32 i=1;i<12;++i) sector[8+i]=MAIL[i];
    sector[20]=R64(0x2458428); sector[21]=R64(0x2458430); sector[22]=R64(0x2458438);
    MAPPING_SNAPSHOT(); /* Only here: native-first shutdown; before UFS. */
    s32 fd=stock_ufs_open(0,"/tmp/netemu_mapping_snapshot.bin");
    if (fd<0 || fd>7) return; /* out-of-range result is not a valid handle */
    if (stock_ufs_stat(fd,(void *)statbuf)==0 && statbuf[5]==65536) {
        sector[36]=statbuf[5]; sector[37]=(u32)fd;
        /* The native 48-byte stat's first word is NOT established as mode.
         * Native raw_write enforces regular-file eligibility (slot+4).
         * Returned byte count/close success do not prove durable delivery. */
        (void)stock_raw_write(fd,0,(const void *)sector,512);
    }
    (void)stock_ufs_close(fd);
}

u64 snapshot_shutdown(u64 a,u64 b,u64 c,u64 d,u64 e,u64 f,u64 g,u64 h) {
    u64 result=native_shutdown(a,b,c,d,e,f,g,h);
    if (a==0xb46100 && b==2 && R8(0x934161)==2) write_snapshot(result);
    return result;
}
