#include "hddlog.h"

#define STR_HELPER(x) #x
#define STR(x) STR_HELPER(x)

#ifndef PROBE_VARIANT
#define PROBE_VARIANT 1
#endif

/* Native helper trampoline in code slot: calls stock 0x111eb8 (LV1 91) */
extern s64 repo_read(u64 *out1, u64 *out2, u64 node1, u64 node2, u64 node3, u64 node4);

/* Generic hypercall wrapper modeled on stock helper:
 * Linked into code slot at 0x4800 (sc 0 at 0x4858) */
extern s64 lv1_hcall(u64 num, u64 a1, u64 a2, u64 a3, u64 a4, u64 a5, u64 a6);

/* 96-byte Mailbox at 0x930F20 (struct ProbeMailbox) */
struct ProbeMailbox {
    u32 status;            /* 0..3: bit 0: started, bit 1: done, bit 2: alloc_ok, bit 3: alloc_failed */
    u32 total_hypercalls;  /* 4..7: count of hypercalls made */
    u32 timeouts;          /* 8..11: bit 0: TUR, bit 1: INQ, bit 2: CAP, bit 3: READ */
    u32 step_failed;       /* 12..15: step number that failed (0=none/success) */
    s32 first_err_rc;      /* 16..19: return code of first failed call */
    u32 open_count;        /* 20..23: count of menu open cycles (detected via >1.5s TB gap) */

    u64 arena_ptr;         /* 24..31: pointer to 4 KiB arena from native_alloc */

    u8  rom_bus_idx;       /* 32: bus index of first ROM device */
    u8  rom_dev_idx;       /* 33: dev index of first ROM device */
    u8  rom_port;          /* 34: port value of first ROM device */
    u8  storage_bus_idx;   /* 35: bus index that has bus_type == 5 */

    u8  hdd_bus_idx;       /* 36: bus index where HDD control was found */
    u8  hdd_dev_idx;       /* 37: dev index */
    u8  hdd_port;          /* 38: port value */
    u8  phat_match;        /* 39: bit 0: emu, bit 1: gxemu */

    u32 rom_count;         /* 40..43: count of type 5 (ROM) devices */
    u32 hdd_found;         /* 44..47: 1 if type 0 (DISK) device found on bus 4 port 2 */

    u64 rom_bus_id;        /* 48..55: 64-bit bus_id from repository */
    u64 rom_dev_id;        /* 56..63: 64-bit dev_id from repository */

    u64 last_eval_tb;      /* 64..71: timebase of last hook evaluation */

    /* P4 durable logging telemetry in formerly unused 8 bytes (72..79) */
    u32 log_records_written; /* 72..75: count of records written & flushed */
    u16 log_records_skipped; /* 76..77: count of records skipped due to disk busy */
    u8  log_fail_reason;     /* 78: fail reason code if logging stopped */
    u8  log_clean_shutdown;  /* 79: 1 if END record cleanly written */

    u64 raw_val1;          /* 80..87: val1 from lv1_hcall epilogue (address 0x930F70) */
    u64 raw_val2;          /* 88..95: val2 from lv1_hcall epilogue (address 0x930F78) */
};

_Static_assert(sizeof(struct ProbeMailbox) == 96, "ProbeMailbox must be exactly 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, open_count) == 20, "open_count offset 20");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, arena_ptr) == 24, "arena_ptr offset 24");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, rom_bus_id) == 48, "rom_bus_id offset 48");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, rom_dev_id) == 56, "rom_dev_id offset 56");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, log_records_written) == 72, "log_records_written offset 72");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, raw_val1) == 80, "raw_val1 offset 80");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, raw_val2) == 88, "raw_val2 offset 88");

#define S ((volatile struct ProbeMailbox *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED          (1U << 0)
#define STATUS_DONE             (1U << 1)
#define STATUS_ALLOC_OK         (1U << 2)
#define STATUS_ALLOC_FAILED     (1U << 3)

#define STEP_NONE               0
#define STEP_PREGUARD_FAILED    1
#define STEP_OPEN               2
#define STEP_DMA_ALLOC          3
#define STEP_MAP                4
#define STEP_UNMAP              5
#define STEP_FREE               6
#define STEP_CLOSE              7

#define ARENA_BYTES 4096U

/* Allocator-backed 4 KiB Arena Structure */
struct ProbeArena {
    u8   sec0_buf[512];          /* 0x000..0x1FF: 512-byte aligned buffer for Sector 0 Header */
    u8   rec_buf[512];           /* 0x200..0x3FF: 512-byte aligned buffer for Log Record */
    char row_strings[9][64];     /* 0x400..0x63F: 576 bytes dedicated string buffers for rows 0..8 */

    /* Telemetry and diagnostic state */
    s32 stock_rc;          /* 0x640: stock helper rc or pre-guard status */
    s32 open_rc;           /* 0x644: LV1 170 open rc */
    s32 dma_alloc_rc;      /* 0x648: LV1 174 alloc DMA region rc */
    s32 map_rc;            /* 0x64C: LV1 176 map DMA region rc */
    s32 unmap_rc;          /* 0x650: LV1 177 unmap DMA region rc */
    s32 free_rc;           /* 0x654: LV1 175 free DMA region rc */
    s32 close_rc;          /* 0x658: LV1 171 close rc */
    u32 rom_region_id;     /* 0x65C: region id for ROM device from repo */
    u32 total_devices;     /* 0x660: total devices discovered across all buses */
    u32 winning_cand;      /* 0x664: candidate ID (1..7) that succeeded (0 if none) */
    u32 total_cand_tested; /* 0x668: number of candidates evaluated */
    u32 is_log_initialized;/* 0x66C: 1 if hddlog_init succeeded */
    u32 log_cursor;        /* 0x670: next record index */
    u32 log_seq;           /* 0x674: monotonic log record sequence */

    u64 dma_region;        /* 0x678: DMA region ID from 174 */
    u64 dma_bus_addr;      /* 0x680: DMA bus address from 176 */
    u64 buf_lpar;          /* 0x688: buffer physical LPAR address from SB_CDVD */
    u64 buf_ea;            /* 0x690: buffer CPU effective address from SB_CDVD */
    u64 buf_sz;            /* 0x698: buffer size from SB_CDVD */
    u64 boot_tb;           /* 0x6A0: boot session timebase ID */
};

_Static_assert(sizeof(struct ProbeArena) <= ARENA_BYTES, "ProbeArena must fit in 4 KiB arena");

/* Memory validation checks: checks 0x934980, 0x24565b8, 0x2446588 (P1c2 console proven) */
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

#include "hddlog.c"

#define KEY_BUS(b)  (0x6275730000000000ULL | (u64)(b))
#define KEY_DEV(d)  (0x6465760000000000ULL | (u64)(d))
#define KEY_TYPE    0x7479706500000000ULL
#define KEY_ID      0x6964000000000000ULL
#define KEY_PORT    0x706f727400000000ULL
#define KEY_REG0    0x726567696f6e0000ULL

static void append_str(char **dst, const char *src) {
    while (*src) {
        *(*dst)++ = *src++;
    }
}

static void format_dec(char **dst, u32 val) {
    char buf[12];
    int i = 0;
    if (val == 0) {
        *(*dst)++ = '0';
        return;
    }
    while (val > 0) {
        buf[i++] = (char)('0' + (val % 10));
        val /= 10;
    }
    while (i > 0) {
        *(*dst)++ = buf[--i];
    }
}

static void format_hex64(char **dst, u64 val) {
    const char hex[] = "0123456789abcdef";
    for (int i = 60; i >= 0; i -= 4) {
        *(*dst)++ = hex[(val >> i) & 0xF];
    }
}

static void format_hex32(char **dst, u32 val) {
    const char hex[] = "0123456789abcdef";
    for (int i = 28; i >= 0; i -= 4) {
        *(*dst)++ = hex[(val >> i) & 0xF];
    }
}

/* Verified guard for SB_CDVD buffer source (P6 proven via stock.elf 0x133cb0 and 0x19900):
 * - Physical LPAR address at 0x2458438 (0x2456fe0 + 0x1458)
 * - Buffer size at 0x2458430 (0x2456fe0 + 0x1450)
 * - CPU EA at 0x2458428 (0x2456fe0 + 0x1448)
 *
 * Runtime Sanity Requirements:
 * 1. Physical LPAR must be strictly 64-bit (>= 0x1_0000_0000), match 0x5000_0000_0000 pattern, and 1 MiB aligned.
 * 2. CPU EA must be strictly 32-bit (< 0x1_0000_0000), >= 0x80000000, and 1 MiB aligned.
 * 3. Size must be at least 512 KiB (0x80000).
 */
static int check_cdvd_buffer_guard(u64 *p_lpar, u64 *p_ea, u64 *p_sz) {
    u64 raw_lpar = *(const volatile u64 *)0x2458438ULL;
    u64 raw_ea   = *(const volatile u64 *)0x2458428ULL;
    u64 raw_sz   = *(const volatile u64 *)0x2458430ULL;

    *p_lpar = raw_lpar;
    *p_ea   = raw_ea;
    *p_sz   = raw_sz;

    /* 1. Physical LPAR must be >= 0x1_0000_0000, match 0x5000_0000_0000 pattern, and 1 MiB aligned */
    if (raw_lpar < 0x100000000ULL || (raw_lpar & 0xFFFF00000000ULL) != 0x500000000000ULL || (raw_lpar & 0xFFFFFULL) != 0) {
        return 0;
    }

    /* 2. CPU EA must be 32-bit (< 0x1_0000_0000), >= 0x80000000, and 1 MiB aligned */
    if (raw_ea >= 0x100000000ULL || raw_ea < 0x80000000ULL || (raw_ea & 0xFFFFFULL) != 0 || raw_ea == raw_lpar) {
        return 0;
    }

    /* 3. Size must be at least 512 KiB */
    if (raw_sz < 0x80000ULL) {
        return 0;
    }

    return 1;
}

/* Candidate argument set definition for R1 search */
struct MapCandidate {
    u8  id;
    u8  source_type; /* 0: CDVD LPAR (0x2458438), 1: HDD LPAR (H+0x20), 2: HDD EA (H+0x28), 3: CDVD EA (0x2458428) */
    u8  alloc_exp;
    u32 alloc_size;
    u32 map_len;
    u64 map_flags;
};

static const struct MapCandidate candidates[7] = {
    /* Group A: CDVD Real Physical LPAR (0x2458438) - Top Hypotheses */
    { 1, 0, 20, 0x100000, 0x100000, 0xe000000000000800ULL }, /* #1: Rank 1 - Official emulator standard with real LPAR */
    { 2, 0, 16, 0x100000,  0x80000, 0xe000000000000800ULL }, /* #2: Rank 2 - 64 KiB page exponent, 512 KiB length */
    { 3, 0, 12,  0x80000,  0x80000, 0xe000000000000800ULL }, /* #3: Rank 3 - 4 KiB page exponent, 512 KiB length */

    /* Group B: Stock HDD Buffer Real Physical LPAR (H+0x20) - Cross-device mapping */
    { 4, 1, 16,  0x80000,  0x80000, 0xe000000000000800ULL }, /* #4: Rank 4 - HDD driver's LPAR mapped to optical region */
    { 5, 1, 12,  0x80000,  0x80000, 0xe000000000000800ULL }, /* #5: Rank 5 - HDD driver's LPAR with 4 KiB pages */

    /* Group C: Negative Controls (Passing CPU Effective Addresses) */
    { 6, 2, 16,  0x80000,  0x80000, 0xe000000000000800ULL }, /* #6: Control - HDD driver CPU EA (0x84800000) */
    { 7, 3, 20, 0x100000, 0x100000, 0xe000000000000800ULL }  /* #7: Control - CDVD CPU EA (0x84000000) */
};

/* Core probe sequence */
static void run_probe(volatile struct ProbeArena *arena) {
    char msg[128];
    char *mp;

    /* Initialize durable write-ahead HDD logger */
    hddlog_init();

    /* 1. Log Session BOOT Record */
    mp = msg;
    append_str(&mp, "boot: ps2_netemu_p6_r1");
    *mp = '\0';
    HDDLOG(TAG_BOOT, (u64)sizeof(struct ProbeArena), (u64)PROBE_VARIANT, msg);

    /* Enumerate Repository (Bus 4) */
    u32 rom_cnt = 0;
    u32 hdd_fnd = 0;
    u64 opt_bus = 4;
    u64 opt_dev = 2;
    u32 total_devs = 0;

    for (u64 d = 0; d < 8; d++) {
        u64 val1 = 0, val2 = 0;
        s64 rc = repo_read(&val1, &val2, KEY_BUS(4), KEY_DEV(d), KEY_TYPE, 0);
        if (rc == 0) {
            total_devs++;
            if (val1 == 5) { /* ROM */
                rom_cnt++;
                opt_dev = d;
                u64 reg_v1 = 0, reg_v2 = 0;
                if (repo_read(&reg_v1, &reg_v2, KEY_BUS(4), KEY_DEV(d), KEY_REG0, 0) == 0) {
                    arena->rom_region_id = (u32)reg_v1;
                }
            } else if (val1 == 0) { /* DISK */
                hdd_fnd = 1;
            }
        }
    }
    arena->total_devices = total_devs;
    S->rom_count = rom_cnt;
    S->hdd_found = hdd_fnd;

    /* Log SCAN Record */
    mp = msg;
    append_str(&mp, "scan: rom_cnt=");
    format_dec(&mp, rom_cnt);
    append_str(&mp, " hdd=");
    format_dec(&mp, hdd_fnd);
    append_str(&mp, " bus=4 dev=2");
    *mp = '\0';
    HDDLOG(TAG_SCAN, (u64)rom_cnt, (u64)hdd_fnd, msg);

    /* Evaluate CDVD buffer sanity guard */
    u64 cdvd_lpar = 0, cdvd_ea = 0, cdvd_sz = 0;
    int guard_ok = check_cdvd_buffer_guard(&cdvd_lpar, &cdvd_ea, &cdvd_sz);
    if (!guard_ok) {
        S->step_failed = STEP_PREGUARD_FAILED;
        S->first_err_rc = -1;

        mp = msg;
        append_str(&mp, "grd reject: sanity failed (0 hc)");
        *mp = '\0';
        HDDLOG(TAG_GRD, cdvd_lpar, cdvd_ea, msg);

        mp = msg;
        append_str(&mp, "finish: ps2_netemu_p6_r1 failed step=1");
        *mp = '\0';
        HDDLOG(TAG_END, (u64)S->step_failed, (u64)S->total_hypercalls, msg);
        return; /* Abort cleanly without issuing any hypercalls */
    }
    arena->buf_lpar = cdvd_lpar;
    arena->buf_ea   = cdvd_ea;
    arena->buf_sz   = cdvd_sz;

    mp = msg;
    append_str(&mp, "grd ok: lpar & ea sanity pass");
    *mp = '\0';
    HDDLOG(TAG_GRD, cdvd_lpar, cdvd_ea, msg);

    /* Read Stock HDD driver buffer state from H = 0x241C850 */
    u64 hdd_lpar = 0, hdd_ea = 0;
    int hdd_valid = 0;
    const volatile u64 *h_ptr = (const volatile u64 *)0x241C850ULL;
    if (h_ptr[2] == 3ULL) { /* dev_id == 3 (H + 0x10) */
        hdd_lpar = h_ptr[4]; /* H + 0x20: physical LPAR */
        hdd_ea   = h_ptr[5]; /* H + 0x28: CPU EA */
        if (hdd_lpar >= 0x100000000ULL && (hdd_lpar & 0xFFFF00000000ULL) == 0x500000000000ULL && (hdd_lpar & 0xFFFFFULL) == 0) {
            hdd_valid = 1;
        }
    }

    /* 2. Execute Staged Optical Sequence */
    u64 dev_bus = opt_bus;
    u64 dev_id = opt_dev;
    u32 winning_cand = 0;

    /* Step 1: Open Device (LV1 170) */
    mp = msg;
    append_str(&mp, "pre open: bus=4 dev=2");
    *mp = '\0';
    HDDLOG(TAG_PRE, dev_bus, dev_id, msg);

    s64 orc = lv1_hcall(170, dev_bus, dev_id, 0, 0, 0, 0);
    S->total_hypercalls++;
    arena->open_rc = (s32)orc;

    mp = msg;
    append_str(&mp, "post open: rc=");
    format_dec(&mp, (u32)orc);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)orc, 0ULL, msg);

    if (orc != 0) {
        S->step_failed = STEP_OPEN;
        S->first_err_rc = (u32)orc;
        goto end_log;
    }

    /* Step 2: Systematically test candidates */
    u64 curr_dma_region = 0;
    u32 curr_alloc_size = 0;
    u8  curr_alloc_exp = 0;

    for (u32 i = 0; i < 7; i++) {
        const struct MapCandidate *cand = &candidates[i];
        arena->total_cand_tested = i + 1;

        /* Resolve target address to map */
        u64 lpar_to_map = 0;
        if (cand->source_type == 0) {
            lpar_to_map = cdvd_lpar;
        } else if (cand->source_type == 1) {
            lpar_to_map = hdd_valid ? hdd_lpar : 0;
        } else if (cand->source_type == 2) {
            lpar_to_map = hdd_valid ? hdd_ea : 0;
        } else if (cand->source_type == 3) {
            lpar_to_map = cdvd_ea;
        }

        if (lpar_to_map == 0) {
            continue; /* Source address not available */
        }

        /* If DMA region parameters differ, free old region and allocate new one */
        if (curr_dma_region == 0 || curr_alloc_size != cand->alloc_size || curr_alloc_exp != cand->alloc_exp) {
            if (curr_dma_region != 0) {
                mp = msg;
                append_str(&mp, "pre free: rgn=0x");
                format_hex64(&mp, curr_dma_region);
                *mp = '\0';
                HDDLOG(TAG_PRE, curr_dma_region, 0ULL, msg);

                s64 frc = lv1_hcall(175, dev_bus, dev_id, curr_dma_region, 0, 0, 0);
                S->total_hypercalls++;
                curr_dma_region = 0;

                mp = msg;
                append_str(&mp, "post free: rc=");
                format_dec(&mp, (u32)frc);
                *mp = '\0';
                HDDLOG(TAG_POST, (u64)frc, 0ULL, msg);
            }

            mp = msg;
            append_str(&mp, "pre dma_alloc: sz=0x");
            format_hex32(&mp, cand->alloc_size);
            append_str(&mp, " pexp=");
            format_dec(&mp, (u32)cand->alloc_exp);
            *mp = '\0';
            HDDLOG(TAG_PRE, (u64)cand->alloc_size, (u64)cand->alloc_exp, msg);

            s64 drc = lv1_hcall(174, dev_bus, dev_id, cand->alloc_size, cand->alloc_exp, 0, 0);
            S->total_hypercalls++;
            arena->dma_alloc_rc = (s32)drc;

            if (drc != 0) {
                mp = msg;
                append_str(&mp, "post dma_alloc: rc=");
                format_dec(&mp, (u32)drc);
                *mp = '\0';
                HDDLOG(TAG_POST, (u64)drc, 0ULL, msg);
                continue;
            }

            curr_dma_region = S->raw_val1;
            curr_alloc_size = cand->alloc_size;
            curr_alloc_exp = cand->alloc_exp;
            arena->dma_region = curr_dma_region;

            mp = msg;
            append_str(&mp, "post dma_alloc: rc=0 rgn=0x");
            format_hex64(&mp, curr_dma_region);
            *mp = '\0';
            HDDLOG(TAG_POST, 0ULL, curr_dma_region, msg);
        }

        /* Now issue Map Device DMA Region (LV1 176) */
        mp = msg;
        append_str(&mp, "pre map #");
        format_dec(&mp, (u32)cand->id);
        append_str(&mp, ": lpar=0x");
        format_hex64(&mp, lpar_to_map);
        append_str(&mp, " len=0x");
        format_hex32(&mp, cand->map_len);
        append_str(&mp, " flg=0x");
        format_hex64(&mp, cand->map_flags);
        *mp = '\0';
        HDDLOG(TAG_PRE, lpar_to_map, (u64)cand->map_len, msg);

        s64 mrc = lv1_hcall(176, dev_bus, dev_id, lpar_to_map, curr_dma_region, cand->map_len, cand->map_flags);
        S->total_hypercalls++;
        arena->map_rc = (s32)mrc;
        u64 bus_addr = S->raw_val1;

        mp = msg;
        append_str(&mp, "post map #");
        format_dec(&mp, (u32)cand->id);
        append_str(&mp, ": rc=");
        format_dec(&mp, (u32)mrc);
        append_str(&mp, " bus_addr=0x");
        format_hex64(&mp, bus_addr);
        *mp = '\0';
        HDDLOG(TAG_POST, (u64)mrc, bus_addr, msg);

        if (mrc == 0) {
            /* Success! Candidate accepted by hypervisor */
            winning_cand = cand->id;
            arena->winning_cand = cand->id;
            arena->dma_bus_addr = bus_addr;

            /* Unmap immediately (LV1 177) */
            mp = msg;
            append_str(&mp, "pre unmap: rgn=0x");
            format_hex64(&mp, curr_dma_region);
            append_str(&mp, " len=0x");
            format_hex32(&mp, cand->map_len);
            *mp = '\0';
            HDDLOG(TAG_PRE, curr_dma_region, (u64)cand->map_len, msg);

            s64 umrc = lv1_hcall(177, dev_bus, dev_id, curr_dma_region, cand->map_len, 0, 0);
            S->total_hypercalls++;
            arena->unmap_rc = (s32)umrc;

            mp = msg;
            append_str(&mp, "post unmap: rc=");
            format_dec(&mp, (u32)umrc);
            *mp = '\0';
            HDDLOG(TAG_POST, (u64)umrc, 0ULL, msg);

            break; /* Stop at the first successful candidate */
        }
    }

    /* Clean up DMA region if still allocated */
    if (curr_dma_region != 0) {
        mp = msg;
        append_str(&mp, "pre free: rgn=0x");
        format_hex64(&mp, curr_dma_region);
        *mp = '\0';
        HDDLOG(TAG_PRE, curr_dma_region, 0ULL, msg);

        s64 frc = lv1_hcall(175, dev_bus, dev_id, curr_dma_region, 0, 0, 0);
        S->total_hypercalls++;
        arena->free_rc = (s32)frc;

        mp = msg;
        append_str(&mp, "post free: rc=");
        format_dec(&mp, (u32)frc);
        *mp = '\0';
        HDDLOG(TAG_POST, (u64)frc, 0ULL, msg);
    }

    /* Close Device (LV1 171) */
    mp = msg;
    append_str(&mp, "pre close: bus=4 dev=2");
    *mp = '\0';
    HDDLOG(TAG_PRE, dev_bus, dev_id, msg);

    s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
    S->total_hypercalls++;
    arena->close_rc = (s32)crc;

    mp = msg;
    append_str(&mp, "post close: rc=");
    format_dec(&mp, (u32)crc);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)crc, 0ULL, msg);

end_log:
    mp = msg;
    append_str(&mp, "finish: ps2_netemu_p6_r1 ");
    if (winning_cand != 0) {
        append_str(&mp, "cand #");
        format_dec(&mp, winning_cand);
        append_str(&mp, " ok!");
        S->step_failed = 0;
        S->first_err_rc = 0;
    } else {
        append_str(&mp, "all map candidates failed (-17)");
        S->step_failed = STEP_MAP;
        S->first_err_rc = -17;
    }
    *mp = '\0';
    HDDLOG(TAG_END, (u64)winning_cand, (u64)S->total_hypercalls, msg);
}

/* 79.8 MHz timebase gap: 1.5 seconds = 119,700,000 cycles */
#define TB_GAP_TICKS 119700000ULL

/* Format on-screen menu rows for secondary channel / glance display */
static void format_row(char *dst, u32 r, volatile struct ProbeArena *arena) {
    char *p = dst;

    /* Primary Execution Status */
    if (r == 0) {
        append_str(&p, "P6-R1");
        if (S->step_failed == STEP_PREGUARD_FAILED) {
            append_str(&p, " SANITY REJECT (0 HC)");
        } else if (arena->winning_cand != 0) {
            append_str(&p, " DONE: CAND #");
            format_dec(&p, arena->winning_cand);
            append_str(&p, " MAP OK");
        } else {
            append_str(&p, " FAIL: ALL CANDIDATES REJECTED (-17)");
        }
        *p = '\0';
        return;
    }

    if (r == 1) {
        append_str(&p, "WIN=");
        format_dec(&p, arena->winning_cand);
        append_str(&p, " TESTED=");
        format_dec(&p, arena->total_cand_tested);
        append_str(&p, " HC=");
        format_dec(&p, S->total_hypercalls);
        append_str(&p, " LOG=");
        format_dec(&p, S->log_records_written);
        *p = '\0';
        return;
    }

    if (r == 2) {
        append_str(&p, "CDVD LPAR: 0x");
        format_hex64(&p, arena->buf_lpar);
        *p = '\0';
        return;
    }

    if (r == 3) {
        append_str(&p, "CDVD EA:   0x");
        format_hex64(&p, arena->buf_ea);
        append_str(&p, " SZ=");
        format_hex64(&p, arena->buf_sz);
        *p = '\0';
        return;
    }

    if (r == 4) {
        append_str(&p, "DMA RGN=0x");
        format_hex64(&p, arena->dma_region);
        append_str(&p, " BUS=0x");
        format_hex64(&p, arena->dma_bus_addr);
        *p = '\0';
        return;
    }

    if (r == 5) {
        append_str(&p, "RC: OP=");
        format_dec(&p, (u32)arena->open_rc);
        append_str(&p, " ALLOC=");
        format_dec(&p, (u32)arena->dma_alloc_rc);
        append_str(&p, " MAP=");
        format_dec(&p, (u32)arena->map_rc);
        append_str(&p, " CL=");
        format_dec(&p, (u32)arena->close_rc);
        *p = '\0';
        return;
    }

    if (r == 6) {
        append_str(&p, "SCAN: ROM=");
        format_dec(&p, S->rom_count);
        append_str(&p, " HDD=");
        format_dec(&p, S->hdd_found);
        append_str(&p, " TOT=");
        format_dec(&p, arena->total_devices);
        *p = '\0';
        return;
    }

    /* Fallback default row */
    append_str(&p, "P6-R1 RUNNING");
    *p = '\0';
}

/* Hook entry called from 0x270FFC: replaces menu-row string selector */
const char *s4_menu(u32 row_index) {
    if (row_index > 8) {
        row_index = 0;
    }

    /* Check if 4 KiB Arena exists */
    volatile struct ProbeArena *arena = get_arena();
    if (!arena) {
        if (!(S->status & STATUS_ALLOC_FAILED)) {
            S->status |= STATUS_STARTED;
            u64 alloc_res = (u64)native_alloc(ARENA_BYTES, 3, 0);
            if (arena_rw(alloc_res)) {
                S->arena_ptr = alloc_res;
                S->status |= STATUS_ALLOC_OK;
                arena = (volatile struct ProbeArena *)alloc_res;
                for (u32 i = 0; i < sizeof(struct ProbeArena); i++) {
                    ((volatile u8 *)alloc_res)[i] = 0;
                }
            } else {
                S->status |= STATUS_ALLOC_FAILED;
                return (const char *)STOCK_LABEL;
            }
        } else {
            return (const char *)STOCK_LABEL;
        }
    }

    /* Menu open cycle detector using hardware timebase */
    u64 now_tb = native_clock();
    u64 last_tb = S->last_eval_tb;
    S->last_eval_tb = now_tb;

    if (last_tb != 0 && (now_tb - last_tb) > TB_GAP_TICKS) {
        S->open_count++;
    }

    /* Run the diagnostic probe exactly once */
    if (!(S->status & STATUS_DONE)) {
        run_probe(arena);
        S->status |= STATUS_DONE;
    }

    /* Format on-screen string in arena row buffer */
    format_row((char *)arena->row_strings[row_index], row_index, arena);
    return (const char *)arena->row_strings[row_index];
}
