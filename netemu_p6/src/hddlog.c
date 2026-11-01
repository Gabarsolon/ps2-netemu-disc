#include "hddlog.h"

/* Freestanding string and formatting helpers */
static void safe_strcpy(char *dst, const char *src, u32 max_len) {
    if (!dst || max_len == 0) return;
    u32 i = 0;
    if (src) {
        while (src[i] != '\0' && i + 1 < max_len) {
            dst[i] = src[i];
            i++;
        }
    }
    dst[i] = '\0';
}

/* Re-derived & Verified HDD Idle Predicate
 * Reads stock HDD singleton H at 0x241c850 (TOC - 0x6f58).
 * Precondition for issuing UFS writes and standalone cache flush.
 */
static int is_hdd_log_safe(void) {
    const u8 *H = (const u8 *)0x241C850ULL;
    if (!H) return 0;

    u8  enabled  = H[0x85];
    u8  err_flag = H[0x78];
    u64 dev_id   = *(const volatile u64 *)(H + 0x10);
    u64 tagstat  = *(const volatile u64 *)(H + 0x38);
    u64 status40 = *(const volatile u64 *)(H + 0x40);
    u64 status48 = *(const volatile u64 *)(H + 0x48);

    /* Verify driver ready / enabled (1) */
    if (enabled != 1) return 0;

    /* Verify no driver error (0) */
    if (err_flag != 0) return 0;

    /* Verify device id is HDD (3) */
    if (dev_id != 3) return 0;

    /* Verify driver is completely idle (no commands in-flight) */
    if (status48 != 0) return 0; /* Expected tag must be 0 */
    if (tagstat  != 0) return 0; /* Completed tag must be 0 */
    if (status40 != 0) return 0; /* Status must be 0 */

    /* Check global UFS lock mutex (0x3055180, TOC - 0x42f8) */
    const u32 *ufs_lock = (const u32 *)0x3055180ULL;
    if (ufs_lock && *ufs_lock != 0) return 0;

    return 1;
}

int hddlog_init(void) {
    if (!S || !S->arena_ptr) return -1;
    volatile struct ProbeArena *arena = (volatile struct ProbeArena *)S->arena_ptr;
    if (arena->is_log_initialized) return 0;

    arena->boot_tb = native_clock();
    arena->log_cursor = 1;
    arena->log_seq = 0;

    /* Verify HDD is idle before opening file */
    if (!is_hdd_log_safe()) {
        S->log_fail_reason = REASON_NOT_IDLE;
        S->log_records_skipped++;
        arena->is_log_initialized = 1;
        return -1;
    }

    static const char path[] = "/tmp/netemu_log.bin";
    s32 fd = stock_ufs_open(0, path);
    if (fd < 0 || fd > 7) {
        S->log_fail_reason = (fd == -2) ? REASON_NO_FILE : REASON_WRITE_FAILED;
        return -1;
    }

    /* Initialize Sector 0 Header (512 bytes): resets cursor to 1 for new test run */
    volatile u64 *sec0_words = (volatile u64 *)arena->sec0_buf;
    for (u32 i = 0; i < 64; i++) {
        sec0_words[i] = 0;
    }
    sec0_words[0] = 0x4E4554454D554C47ULL; /* 'NETEMULG' */
    volatile u32 *sec0_u32 = (volatile u32 *)arena->sec0_buf;
    sec0_u32[8 / 4]  = 0x00010000; /* Version 1.0 */
    sec0_u32[12 / 4] = 512;        /* Header Size */
    sec0_u32[16 / 4] = 65536;      /* File Size */
    sec0_u32[20 / 4] = 512;        /* Sector Size */
    sec0_u32[24 / 4] = 127;        /* Max Records */
    sec0_u32[28 / 4] = 1;          /* Next Record Idx = 1 (reset cursor!) */
    sec0_words[32 / 8] = arena->boot_tb; /* Boot TB (session/boot ID) */
    sec0_u32[40 / 4] = 0;          /* Clean shutdown (0 = uncommitted/crash) */
    sec0_u32[44 / 4] = 0;          /* Record count = 0 */

    s64 wr = stock_raw_write(fd, 0, (const void *)arena->sec0_buf, 512);
    if (wr != 512) {
        stock_ufs_close(fd);
        S->log_fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    s32 cl_rc = stock_ufs_close(fd);
    if (cl_rc != 0) {
        S->log_fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    if (is_hdd_log_safe()) {
        s32 flush_rc = stock_hdd_cache_flush();
        if (flush_rc != 0) {
            S->log_fail_reason = REASON_FLUSH_FAILED;
            return -1;
        }
    }

    arena->is_log_initialized = 1;
    return 0;
}

int hddlog_write(u32 tag, u64 a, u64 b, const char *text) {
    if (!S || !S->arena_ptr) return -1;
    volatile struct ProbeArena *arena = (volatile struct ProbeArena *)S->arena_ptr;
    if (!arena->is_log_initialized) return -1;

    /* Stop-when-full: capacity is 127 records */
    if (arena->log_cursor > 127) {
        S->log_fail_reason = REASON_FULL;
        return -1;
    }

    /* Concurrency check: if HDD driver is busy, fail-open by skipping THIS record */
    if (!is_hdd_log_safe()) {
        S->log_records_skipped++;
        return 0;
    }

    static const char path[] = "/tmp/netemu_log.bin";
    s32 fd = stock_ufs_open(0, path);
    if (fd < 0 || fd > 7) {
        S->log_fail_reason = (fd == -2) ? REASON_NO_FILE : REASON_WRITE_FAILED;
        return -1;
    }

    /* Build 512-byte record in arena->rec_buf */
    volatile u64 *rec_words = (volatile u64 *)arena->rec_buf;
    for (u32 i = 0; i < 64; i++) {
        rec_words[i] = 0;
    }

    arena->log_seq++;
    volatile u32 *rec_u32 = (volatile u32 *)arena->rec_buf;
    rec_u32[0] = 0x4C4F4752;       /* Magic 'LOGR' */
    rec_u32[1] = arena->log_seq;   /* Sequence */
    rec_u32[2] = tag;              /* Tag */
    rec_u32[3] = 0;                /* Flags */
    rec_words[2] = native_clock(); /* Timestamp TB (offset 16) */
    rec_words[3] = a;              /* Parameter A (offset 24) */
    rec_words[4] = b;              /* Parameter B (offset 32) */
    rec_words[5] = arena->boot_tb; /* Boot ID (offset 40) */

    /* Copy message text at offset 72 (max 440 bytes) */
    char *rec_text = (char *)(arena->rec_buf + 72);
    safe_strcpy(rec_text, text, 440);

    /* Write record at offset = arena->log_cursor * 512 */
    u64 offset = (u64)arena->log_cursor * 512ULL;
    s64 wr = stock_raw_write(fd, offset, (const void *)arena->rec_buf, 512);
    if (wr != 512) {
        stock_ufs_close(fd);
        S->log_fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    /* Update Sector 0 Header */
    u32 next_rec = arena->log_cursor + 1;
    volatile u32 *sec0_u32 = (volatile u32 *)arena->sec0_buf;
    sec0_u32[28 / 4] = next_rec;
    sec0_u32[44 / 4] = S->log_records_written + 1;
    if (tag == TAG_END) {
        sec0_u32[40 / 4] = 1; /* Clean shutdown */
        S->log_clean_shutdown = 1;
    }

    s64 wr_hdr = stock_raw_write(fd, 0, (const void *)arena->sec0_buf, 512);
    if (wr_hdr != 512) {
        stock_ufs_close(fd);
        S->log_fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    /* ALWAYS close fd */
    s32 cl_rc = stock_ufs_close(fd);
    if (cl_rc != 0) {
        S->log_fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    /* Check idle before flush */
    if (!is_hdd_log_safe()) {
        S->log_records_skipped++;
        return 0;
    }

    /* Standalone write-through cache flush */
    s32 flush_rc = stock_hdd_cache_flush();
    if (flush_rc != 0) {
        S->log_fail_reason = REASON_FLUSH_FAILED;
        return -1;
    }

    arena->log_cursor = next_rec;
    S->log_records_written++;
    return 0;
}
