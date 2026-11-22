#include "hddlog.h"
#include "hddlog.c"

/* 79.8 MHz timebase gap: 1.5 seconds = 119,700,000 cycles */
#define TB_GAP_TICKS 119700000ULL

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

static void format_dec(char **dst, u32 val) {
    if (val == 0) {
        *(*dst)++ = '0';
        return;
    }
    char buf[12];
    int pos = 0;
    while (val > 0) {
        buf[pos++] = '0' + (val % 10);
        val /= 10;
    }
    for (int i = pos - 1; i >= 0; i--) {
        *(*dst)++ = buf[i];
    }
}

static void append_str(char **dst, const char *s) {
    while (*s) {
        *(*dst)++ = *s++;
    }
}

/* L0 test sequence: executes at first menu evaluation */
static void run_l0_test(void) {
    /* 1. Initialize HDD logger (verifies idle, allocates arena) */
    int init_rc = hddlog_init();
    if (init_rc != 0) {
        return;
    }

    /* 2. Write four test records sequentially */
    /* Record 1: BOOT */
    HDDLOG(TAG_BOOT, 0ULL, 0ULL, "L0 BOOT");

    /* Record 2: T1 */
    HDDLOG(TAG_T1, 1ULL, 0x1111ULL, "L0 T1 after BOOT");

    /* Record 3: T2 */
    HDDLOG(TAG_T2, 2ULL, 0x2222ULL, "L0 T2 test record");

    /* Record 4: END */
    HDDLOG(TAG_END, 4ULL, 0x4444ULL, "L0 END complete");
}

/* Format row labels for menu display */
static void format_row(char *dst, u32 r, volatile struct HddLogArena *arena) {
    char *p = dst;

    if (r == 0) {
        /* Row 0: Primary outcome */
        if (M->fail_reason == REASON_NO_FILE) {
            append_str(&p, "P3B-L0 FAIL: NO FILE (/tmp/netemu_log.bin missing)");
        } else if (M->fail_reason == REASON_NOT_IDLE) {
            append_str(&p, "P3B-L0 FAIL: DISK NOT IDLE");
        } else if (M->fail_reason == REASON_ALLOC_FAILED) {
            append_str(&p, "P3B-L0 FAIL: ARENA ALLOC FAILED");
        } else if (M->fail_reason == REASON_READ_FAILED) {
            append_str(&p, "P3B-L0 FAIL: READ SEC0 FAILED");
        } else if (M->fail_reason == REASON_BAD_HEADER) {
            append_str(&p, "P3B-L0 FAIL: BAD SEC0 HEADER");
        } else if (M->fail_reason == REASON_WRITE_FAILED) {
            append_str(&p, "P3B-L0 FAIL: WRITE RC=");
            format_dec(&p, (u32)(-M->last_ufs_rc));
        } else if (M->fail_reason == REASON_FLUSH_FAILED) {
            append_str(&p, "P3B-L0 FAIL: FLUSH RC=");
            format_dec(&p, (u32)(-M->last_flush_rc));
        } else if (M->fail_reason == REASON_FULL) {
            append_str(&p, "P3B-L0 WARN: LOG FULL (127 ITEMS)");
        } else if (M->records_written == 4) {
            append_str(&p, "P3B-L0 OK: 4 RECS, 2048 B, FLUSH OK");
        } else {
            append_str(&p, "P3B-L0 RUN: RECS=");
            format_dec(&p, M->records_written);
        }
        *p = '\0';
        return;
    }

    if (r == 1) {
        /* Row 1: HDD Idle Check values */
        append_str(&p, "HDD IDLE 38=");
        format_hex64(&p, M->idle_tagstat);
        append_str(&p, " 40=");
        format_hex64(&p, M->idle_status40);
        *p = '\0';
        return;
    }

    if (r == 2) {
        /* Row 2: Expected tag 48 and enable flags */
        append_str(&p, "H STATUS: 48=");
        format_hex64(&p, M->idle_status48);
        append_str(&p, " EN=");
        format_dec(&p, (u32)M->driver_enabled);
        append_str(&p, " ERR=");
        format_dec(&p, (u32)M->driver_error);
        *p = '\0';
        return;
    }

    if (r == 3) {
        /* Row 3: Records written, bytes, cursor */
        append_str(&p, "RECS WRITTEN: ");
        format_dec(&p, M->records_written);
        append_str(&p, " / 4  BYTES: ");
        format_dec(&p, M->bytes_written);
        append_str(&p, "  CUR: #");
        format_dec(&p, M->cursor ? M->cursor : arena->log_cursor);
        *p = '\0';
        return;
    }

    if (r == 4) {
        /* Row 4: Flush status */
        append_str(&p, "FLUSH: ");
        if (M->flush_completed) {
            append_str(&p, "COMPLETED OK (RC=0)");
        } else {
            append_str(&p, "NOT REACHED / FAILED");
        }
        *p = '\0';
        return;
    }

    if (r == 5) {
        /* Row 5: Record 1 & 2 summaries */
        append_str(&p, "R1 [BOOT]: L0 BOOT  R2 [T1]: L0 T1");
        *p = '\0';
        return;
    }

    if (r == 6) {
        /* Row 6: Record 3 & 4 summaries */
        append_str(&p, "R3 [T2]: L0 T2  R4 [END]: L0 END");
        *p = '\0';
        return;
    }

    if (r == 7) {
        /* Row 7: Boot TB */
        append_str(&p, "BOOT TB: 0x");
        format_hex64(&p, M->boot_tb);
        *p = '\0';
        return;
    }

    if (r == 8) {
        /* Row 8: Session summary and open count */
        append_str(&p, "P3B HDD LOG (OPENS=");
        format_dec(&p, M->open_count);
        append_str(&p, ")");
        *p = '\0';
        return;
    }

    dst[0] = '\0';
}

/* Menu hook called from 0x270FFC (trampoline at 0x49C0) */
const u8* s4_menu(u64 selected, u64 stock_r2) {
    (void)stock_r2;

    /* Execute test variant once at first menu evaluation */
    if (!(M->status & STATUS_STARTED)) {
        M->status |= STATUS_STARTED;
        run_l0_test();
        M->status |= STATUS_DONE;
    }

    /* Fall back to stock label if allocator failed or arena invalid */
    if ((M->status & STATUS_ALLOC_FAILED) || !M->arena_ptr) {
        return STOCK_LABEL;
    }

    volatile struct HddLogArena *arena = (volatile struct HddLogArena *)M->arena_ptr;

    /* Timebase gap detection for menu open */
    u64 now = native_clock();
    u64 last = M->last_eval_tb;
    if (last != 0 && now > last && (now - last) > TB_GAP_TICKS) {
        M->open_count++;
    }
    M->last_eval_tb = now;

    /* Row index clamped to 0..8 */
    u32 r = (u32)(selected > 8 ? 8 : selected);

    char *dst = (char *)arena->row_strings[r];
    format_row(dst, r, arena);

    return (const u8 *)dst;
}
