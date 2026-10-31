/* Freestanding PPC64 BE, compiled for ISA 2.02 (970). No mutable globals.
 * P2C Netemu LPAR Memory Diagnostics (Zero-Hypercall Build):
 *
 * GOAL:
 *   Read and dump stock LPAR memory descriptors, heap block, mapped-EA cursor,
 *   HDD driver state, allocator pool descriptors, and runtime TOC onto the
 *   in-game menu labels across 4 menu pages (36 items total: 4 opens * 9 rows).
 *
 * ZERO HYPERCALLS:
 *   Issues exactly 0 hypercalls (no open, no close, no storage calls).
 *   Only reads mapped stock memory and formats menu labels via the pager.
 *
 * SAFETY DISCIPLINE (P2C):
 *   - Mailbox strictly 96 bytes at [0x930F20, 0x930F80). Zero writes to 0x930F80 or above.
 *   - Arena 4096 bytes allocated via native_alloc(4096, 3, 0) and validated against pool descriptors.
 *   - All reads are from verified mapped stock RW/RO data.
 *   - Fail-open: returns STOCK_LABEL if allocator fails.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef long long s64;
typedef int s32;

/* Native allocator trampoline in code slot: branches to stock 0x0b9848 */
extern u64 native_alloc(u64 size, u64 arg2, u64 arg3);

/* Native TOC reader trampoline in code slot: mr r3, 2; blr */
extern u64 get_r2(void);

/* Native timebase reader trampoline: branches to stock 0xb9cd0 (mftb r3) */
extern u64 native_clock(void);

/* 96-byte Mailbox at 0x930F20 (struct ProbeMailbox) */
struct ProbeMailbox {
    u32 status;            /* 0..3: bit 0: started, bit 1: done, bit 2: alloc_ok, bit 3: alloc_failed */
    u32 total_hypercalls;  /* 4..7: count of hypercalls made (0 in P2C) */
    u32 timeouts;          /* 8..11 */
    u32 step_failed;       /* 12..15 */
    s32 first_err_rc;      /* 16..19 */
    u32 open_count;        /* 20..23: count of menu open cycles (detected via >1.5s TB gap) */

    u64 arena_ptr;         /* 24..31: pointer to 4 KiB arena from native_alloc */

    u8  rom_bus_idx;       /* 32 */
    u8  rom_dev_idx;       /* 33 */
    u8  rom_port;          /* 34 */
    u8  storage_bus_idx;   /* 35 */

    u8  hdd_bus_idx;       /* 36 */
    u8  hdd_dev_idx;       /* 37 */
    u8  hdd_port;          /* 38 */
    u8  phat_match;        /* 39 */

    u32 rom_count;         /* 40..43 */
    u32 hdd_found;         /* 44..47 */

    u64 rom_bus_id;        /* 48..55 */
    u64 rom_dev_id;        /* 56..63 */

    u64 last_eval_tb;      /* 64..71: timebase of last hook evaluation */
    u64 pad1;              /* 72..79: padding to offset 80 */

    u64 raw_val1;          /* 80..87 */
    u64 raw_val2;          /* 88..95 */
};

_Static_assert(sizeof(struct ProbeMailbox) == 96, "ProbeMailbox must be exactly 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, open_count) == 20, "open_count offset 20");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, arena_ptr) == 24, "arena_ptr offset 24");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, last_eval_tb) == 64, "last_eval_tb offset 64");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, raw_val1) == 80, "raw_val1 offset 80");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, raw_val2) == 88, "raw_val2 offset 88");

#define S ((volatile struct ProbeMailbox *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED          (1U << 0)
#define STATUS_DONE             (1U << 1)
#define STATUS_ALLOC_OK         (1U << 2)
#define STATUS_ALLOC_FAILED     (1U << 3)

#define ARENA_BYTES 4096U

/* Allocator-backed 4 KiB Arena Structure */
struct ProbeArena {
    u64 heap_words[16];          /* 0x000..0x07f: 128 bytes (first 0x80 bytes of 0x930F80) */
    u32 heap_cursor;             /* 0x080..0x083: cursor read from 0x930f80 + 0x58 */
    u32 heap_limit;              /* 0x084..0x087: limit read from 0x930f80 + 0x5c */
    u32 heap_free;               /* 0x088..0x08b: computed free bytes (limit - cursor) */
    u32 pad0;                    /* 0x08c..0x08f */
    u64 mapped_ea;               /* 0x090..0x097: mapped EA cursor at *(u64*)0xb28a10 */
    u64 hdd_words[10];           /* 0x098..0x0e7: 80 bytes from HDD driver H=0x241c850 */
    u64 pool_934980;             /* 0x0e8..0x0ef */
    u64 pool_24565b8;            /* 0x0f0..0x0f7 */
    u64 pool_2446588;            /* 0x0f8..0x0ff */
    u64 arena_ea;                /* 0x100..0x107: EA of 4 KiB arena from native_alloc */
    u64 runtime_r2;              /* 0x108..0x10f: runtime TOC r2 */
    u64 toc_mapped_ea_addr;      /* 0x110..0x117: r2 - 0x7b30 */
    u64 toc_heap_addr;           /* 0x118..0x11f: r2 - 0x7e50 */
    u64 toc_hdd_addr;            /* 0x120..0x127: r2 - 0x6f58 */
    u64 pad1;                    /* 0x128..0x12f */
    char row_strings[9][64];     /* 0x130..0x36f: 576 bytes (dedicated buffers for rows 0..8) */
};

_Static_assert(sizeof(struct ProbeArena) <= ARENA_BYTES, "ProbeArena must fit in 4 KiB arena");

/* Memory validation checks */
static __attribute__((noinline)) int arena_rw(u64 a) {
    u64 base = *(const volatile u64*)0x934980ULL;
    return (base & ~0xf800000ULL) == 0x80000000ULL &&
           *(const volatile u64*)0x24565b8ULL == base &&
           *(const volatile u64*)0x2446588ULL == base + 0x20000ULL &&
           !(a & 63) && a >= (base + 0x20000ULL) &&
           (a + ARENA_BYTES) <= (base + 0x60000ULL);
}

static __attribute__((noinline)) volatile struct ProbeArena* get_arena(void) {
    u64 a = S->arena_ptr;
    if (!arena_rw(a)) return 0;
    return (volatile struct ProbeArena*)a;
}

/* One-time diagnostic snapshot: LOADS ONLY, ZERO HYPERCALLS */
static void run_probe(u64 stock_r2) {
    /* 1. Allocate 4 KiB arena */
    u64 arena_raw = native_alloc(ARENA_BYTES, 3, 0);
    if (!arena_rw(arena_raw)) {
        S->status |= STATUS_ALLOC_FAILED;
        return;
    }
    S->arena_ptr = arena_raw;
    S->status |= STATUS_ALLOC_OK;

    volatile struct ProbeArena *arena = (volatile struct ProbeArena *)arena_raw;

    /* 2. Read first 0x80 bytes of stock global heap block at 0x930F80 */
    volatile const u64 *heap_block = (volatile const u64 *)0x930F80ULL;
    for (int i = 0; i < 16; i++) {
        arena->heap_words[i] = heap_block[i];
    }

    /* Read cursor, limit, and compute free */
    volatile const u32 *heap_words32 = (volatile const u32 *)0x930F80ULL;
    u32 cursor = heap_words32[0x58 / 4];
    u32 limit  = heap_words32[0x5c / 4];
    arena->heap_cursor = cursor;
    arena->heap_limit  = limit;
    arena->heap_free   = (limit > cursor) ? (limit - cursor) : 0;

    /* 3. Read mapped-EA cursor at *(u64*)0xb28a10 */
    arena->mapped_ea = *(volatile const u64 *)0xB28A10ULL;

    /* 4. Read HDD driver state H = 0x241C850 */
    volatile const u64 *hdd = (volatile const u64 *)0x241C850ULL;
    for (int i = 0; i < 10; i++) {
        arena->hdd_words[i] = hdd[i];
    }

    /* 5. Read pool descriptors */
    arena->pool_934980  = *(volatile const u64 *)0x934980ULL;
    arena->pool_24565b8 = *(volatile const u64 *)0x24565B8ULL;
    arena->pool_2446588 = *(volatile const u64 *)0x2446588ULL;
    arena->arena_ea     = arena_raw;

    /* 6. Read runtime r2 (TOC) */
    arena->runtime_r2 = stock_r2 ? stock_r2 : get_r2();

    /* Resolved TOC addresses */
    arena->toc_mapped_ea_addr = arena->runtime_r2 - 0x7b30ULL;
    arena->toc_heap_addr      = arena->runtime_r2 - 0x7e50ULL;
    arena->toc_hdd_addr       = arena->runtime_r2 - 0x6f58ULL;
}

/* Format one of the 36 items into the row's buffer */
static void format_item(char *dst, u32 item_idx, volatile struct ProbeArena *arena) {
    const char hex[] = "0123456789abcdef";

    if (item_idx < 16) {
        /* Items 0..15: Heap block 0x930F80 offsets 0x00..0x78 */
        u32 off = item_idx * 8;
        u64 val = arena->heap_words[item_idx];
        char *p = dst;
        *p++ = 'P'; *p++ = '2'; *p++ = 'C'; *p++ = ' ';
        *p++ = 'H'; *p++ = '+';
        *p++ = hex[(off >> 4) & 0xF];
        *p++ = hex[off & 0xF];
        *p++ = ':'; *p++ = ' ';
        for (int i = 60; i >= 0; i -= 4) {
            *p++ = hex[(val >> i) & 0xF];
        }
        *p = '\0';
        return;
    }

    if (item_idx == 16) {
        /* Item 16: Heap cursor and limit */
        char *p = dst;
        const char prefix[] = "HEAP CUR=0x";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u32 cur = arena->heap_cursor;
        for (int i = 28; i >= 0; i -= 4) *p++ = hex[(cur >> i) & 0xF];
        const char mid[] = " LIM=0x";
        for (int i = 0; mid[i]; i++) *p++ = mid[i];
        u32 lim = arena->heap_limit;
        for (int i = 28; i >= 0; i -= 4) *p++ = hex[(lim >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 17) {
        /* Item 17: Heap free bytes */
        char *p = dst;
        const char prefix[] = "HEAP FREE=0x";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u32 fr = arena->heap_free;
        for (int i = 28; i >= 0; i -= 4) *p++ = hex[(fr >> i) & 0xF];
        *p++ = ' '; *p++ = '(';
        u32 kb = fr / 1024;
        char dec[12];
        int dpos = 0;
        if (kb == 0) dec[dpos++] = '0';
        else {
            u32 tmp = kb;
            while (tmp > 0) {
                dec[dpos++] = '0' + (tmp % 10);
                tmp /= 10;
            }
        }
        for (int i = dpos - 1; i >= 0; i--) *p++ = dec[i];
        const char suffix[] = " KB)";
        for (int i = 0; suffix[i]; i++) *p++ = suffix[i];
        *p = '\0';
        return;
    }

    if (item_idx == 18) {
        /* Item 18: Mapped EA */
        char *p = dst;
        const char prefix[] = "MAPPED_EA 0xB28A10=";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->mapped_ea;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx >= 19 && item_idx <= 26) {
        /* Items 19..26: HDD driver state H=241c850 */
        u32 hdd_idx = item_idx - 19;
        static const u8 hdd_word_indices[8] = { 1, 2, 4, 5, 6, 7, 8, 9 };
        static const char * const hdd_tags[8] = {
            "H+08 BUS/DEV  =",
            "H+10 DEV_ID   =",
            "H+20 BUF_EA   =",
            "H+28 LPARBUF  =",
            "H+30 DMA_RGN  =",
            "H+38 TAGSTAT  =",
            "H+40 STATUS   =",
            "H+48 STATUS   ="
        };
        char *p = dst;
        const char *tag = hdd_tags[hdd_idx];
        while (*tag) *p++ = *tag++;
        u64 val = arena->hdd_words[hdd_word_indices[hdd_idx]];
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 27) {
        /* Item 27: Pool 934980 */
        char *p = dst;
        const char prefix[] = "POOL 934980   =";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->pool_934980;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 28) {
        /* Item 28: Pool 24565b8 */
        char *p = dst;
        const char prefix[] = "POOL 24565B8  =";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->pool_24565b8;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 29) {
        /* Item 29: Pool 2446588 */
        char *p = dst;
        const char prefix[] = "POOL 2446588  =";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->pool_2446588;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 30) {
        /* Item 30: Arena EA */
        char *p = dst;
        const char prefix[] = "ARENA 0xB9848 =";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->arena_ea;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 31) {
        /* Item 31: Runtime TOC r2 */
        char *p = dst;
        const char prefix[] = "RUNTIME TOC r2=";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->runtime_r2;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 32) {
        /* Item 32: TOC -7B30 resolved addr */
        char *p = dst;
        const char prefix[] = "TOC -7B30 ADDR=";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->toc_mapped_ea_addr;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 33) {
        /* Item 33: TOC -7E50 resolved addr */
        char *p = dst;
        const char prefix[] = "TOC -7E50 ADDR=";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->toc_heap_addr;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 34) {
        /* Item 34: TOC -6F58 resolved addr */
        char *p = dst;
        const char prefix[] = "TOC -6F58 ADDR=";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u64 val = arena->toc_hdd_addr;
        for (int i = 60; i >= 0; i -= 4) *p++ = hex[(val >> i) & 0xF];
        *p = '\0';
        return;
    }

    if (item_idx == 35) {
        /* Item 35: Summary */
        char *p = dst;
        const char prefix[] = "P2C DIAG OK HC=0 OPENS=";
        for (int i = 0; prefix[i]; i++) *p++ = prefix[i];
        u32 oc = S->open_count;
        for (int i = 12; i >= 0; i -= 4) *p++ = hex[(oc >> i) & 0xF];
        *p = '\0';
        return;
    }

    dst[0] = '\0';
}

/* 79.8 MHz timebase gap: 1.5 seconds = 119,700,000 cycles */
#define TB_GAP_TICKS 119700000ULL

/* Menu hook called from 0x270FFC (trampoline at 0x4880) */
const u8* s4_menu(u64 selected, u64 stock_r2) {
    if (!(S->status & STATUS_STARTED)) {
        S->status |= STATUS_STARTED;
        run_probe(stock_r2);
        S->status |= STATUS_DONE;
    }

    if ((S->status & STATUS_ALLOC_FAILED) || !(S->status & STATUS_DONE)) {
        return STOCK_LABEL;
    }

    volatile struct ProbeArena *arena = get_arena();
    if (!arena) {
        return STOCK_LABEL;
    }

    /* Timebase gap detection for menu open */
    u64 now = native_clock();
    u64 last = S->last_eval_tb;
    if (last != 0 && now > last && (now - last) > TB_GAP_TICKS) {
        S->open_count++;
    }
    S->last_eval_tb = now;

    /* Row index r clamped to 0..8 */
    u32 r = (u32)(selected > 8 ? 8 : selected);

    /* 36 items across 4 menu opens (page = (open_count * 9 + r) % 36) */
    u32 item_idx = (S->open_count * 9 + r) % 36;

    char *dst = (char *)arena->row_strings[r];
    format_item(dst, item_idx, arena);

    return (const u8 *)dst;
}
