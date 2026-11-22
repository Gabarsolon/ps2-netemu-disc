/* Offline control experiment. NOT a proven exit API.
 * Only native refresh/clock may be called. No optical/backend/UI calls.
 * All persistent writes: mailbox [0x930f20,0x930f80), reason byte 0x934161.
 */
typedef unsigned long long u64;
typedef unsigned int u32;
typedef unsigned char u8;
#define R8(a) (*(const volatile u8 *)(a##ULL))
#define R32(a) (*(const volatile u32 *)(a##ULL))
#define R64(a) (*(const volatile u64 *)(a##ULL))
#define MAGIC 0x4155544f52544e31ULL
#define DELAY (20ULL * 79800000ULL)
struct State {
    u64 magic, start, last, count, phase, reserved[7];
};
_Static_assert(sizeof(struct State) == 96, "mailbox size");
#define S ((volatile struct State *)0x930f20ULL)
extern u64 native_refresh(u64, u64, u64, u64, u64, u64, u64, u64);
extern u64 native_clock(void);

/* Fixed addresses only; never dereference a loaded runtime pointer.
 * HDD predicate copied ONLY from p16 hddlog_busy_mask, without its logging.
 * This is a momentary idle sample, not a lock or a quiescence guarantee.
 */
static int ui_reason_ok(void) {
    return R8(0x934161) == 0 &&
           R64(0x306fc68) == 0x30700d0ULL &&
           R64(0x30700d0) == 0x949cb8ULL;
}
static int hdd_idle(void) {
    return R8(0x241c8d5) == 1 && R8(0x241c8c8) == 0 &&
           R64(0x241c860) == 3 && R64(0x241c888) == 0 &&
           R64(0x241c890) == 0 && R64(0x241c898) == 0 &&
           R32(0x3055180) == 0;
}
static void tick(void) {
    /* Unknown/stale state is not repaired. In particular a foreign magic or
     * a partially initialized mailbox cannot become armed through this code.
     */
    if (S->magic == 0) {
        const volatile u64 *words = (const volatile u64 *)S;
        for (u32 i = 0; i < 12; ++i)
            if (words[i] != 0) return;
        if (!ui_reason_ok() || !hdd_idle()) return;
        u64 now = native_clock();
        if (now == 0 || !ui_reason_ok() || !hdd_idle()) return;
        S->start = now;
        S->last = now;
        S->count = 0; /* Require 100 subsequent callbacks after arming. */
        S->phase = 1;
        __atomic_thread_fence(__ATOMIC_SEQ_CST);
        S->magic = MAGIC; /* publish complete initialized state last */
        return;
    }
    if (S->magic != MAGIC || S->phase != 1) return;
    for (u32 i = 0; i < 7; ++i)
        if (S->reserved[i] != 0) return;
    u64 start = S->start, last = S->last, count = S->count;
    if (start == 0 || last < start || count > 100) return;
    /* UI teardown or someone else's reason disarms this session permanently.
     * HDD busy is ordinary carrier traffic; it defers the final request.
     */
    if (!ui_reason_ok()) { S->phase = 3; return; }
    u64 now = native_clock();
    if (now < last) { S->phase = 3; return; }
    S->last = now;
    if (count < 100) ++count;
    S->count = count;
    if (now - start < DELAY || count < 100) return;
    if (!ui_reason_ok() || !hdd_idle()) return;
    /* Recheck mailbox identity before requesting. No concurrent owner is
     * supported: BC168 is assumed serialized by its native event loop.
     */
    if (S->magic != MAGIC || S->phase != 1) return;
    S->phase = 2;
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    if (R8(0x934161) != 0) return;
    *(volatile u8 *)0x934161ULL = 2;
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
}

u64 autoreturn_refresh(u64 a, u64 b, u64 c, u64 d,
                       u64 e, u64 f, u64 g, u64 h) {
    u64 result = native_refresh(a, b, c, d, e, f, g, h);
    tick();
    return result;
}
