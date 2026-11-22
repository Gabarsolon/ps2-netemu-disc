/* OWNSEC1/OWNCTL01 v1. No optical operation belongs in this control. */
typedef unsigned char u8;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef signed int s32;
typedef signed long long s64;
#define Q(a) (*(const volatile u64 *)(u64)(a))
#define W(a) (*(const volatile u32 *)(u64)(a))
#define Y(a) (*(const volatile u8 *)(u64)(a))
#define H 0x2446560ULL
#define T (H+0x38)
#define N 0x2000ULL
#define MAGIC 0x4f574e3100000000ULL
#define LEASE 0x4f574e4c45415331ULL
#define SALT 0xb56d847ace390f21ULL
#define DELAY (20ULL*79800000ULL)
/* control = status<<32 | phase. Phases: ready, timer, terminal, consumed,
 * aborted, publishing. Status: owned, context, heap, zero, return, changed. */
struct Mail { u64 magic,control,a,p,e,boot,start,last,count,diag,saved,inside; };
_Static_assert(sizeof(struct Mail)==96,"mailbox");
#define M ((volatile struct Mail *)0x930f20ULL)
#define MQ ((volatile u64 *)0x930f20ULL)
enum { OWNED=1, CONTEXT, HEAP, ZERO, BAD_RETURN, CHANGED };
enum { READY=1, TIMER, TERMINAL, CONSUMED, ABORTED, PUBLISHING };
enum { L_MAGIC,L_COOKIE,L_A,L_N,L_P,L_E,L_ALPAR,L_C,L_CLPAR,L_DATA,
       L_DLPAR,L_BOOT,L_RESULT,L_DIAG,L_SAVED,L_INSIDE,L_PIR,L_FLAGS,
       L_COUNT,L_HEADROOM,L_CMDSUM,L_DATASUM,L_END };
extern u64 native_refresh(u64,u64,u64,u64,u64,u64,u64,u64);
extern u64 native_shutdown(u64,u64,u64,u64,u64,u64,u64,u64);
extern u64 native_startup(u64,u64,u64,u64,u64,u64,u64,u64);
extern u64 native_alloc(u64,u64,u64);
extern u64 irq_save(void);
extern u64 irq_restore(u64);
extern u64 read_msr(void);
extern u64 read_pir(void);
extern u64 native_clock(void);
extern s32 stock_ufs_open(u64,const char *);
extern s32 stock_ufs_stat(s32,void *);
extern s64 stock_raw_write(s32,u64,const void *,u64);
extern s32 stock_ufs_close(s32);
/* Firmware-route probe: LV1 hypercalls (sc 1). HV 170 open_device(bus,dev,flags),
 * HV 171 close_device(bus,dev). Tests whether external sysmgr_ss A+B patches make
 * opening the optical drive (bus 4, dev 2) survivable instead of powering off. */
extern u64 lv1_open_device(u64,u64,u64);
extern u64 lv1_close_device(u64,u64);
/* Probe result slots in the owned block, past the validated lease fields. */
#define L_OPEN  L_END
#define L_CLOSE (L_END+1)
#define L_PMARK (L_END+2)
#define PROBE_MARK 0x50524f4245303101ULL /* "PROBE01" + 1 */
