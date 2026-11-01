#include "hddlog.h"

/* Validation of arena memory range against native allocator pool descriptors */
static __attribute__((noinline)) int arena_rw(u64 a) {
    u64 base = *(const volatile u64*)0x934980ULL;
    return (base & ~0xf800000ULL) == 0x80000000ULL &&
           *(const volatile u64*)0x24565b8ULL == base &&
           *(const volatile u64*)0x2446588ULL == base + 0x20000ULL &&
           !(a & 63) && a >= (base + 0x20000ULL) &&
           (a + ARENA_BYTES) <= (base + 0x60000ULL);
}

/* String copy helper for freestanding environment */
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
    /* Read singleton pointer H */
    const u8 *H = (const u8 *)0x241C850ULL;
    if (!H) return 0;
    M->hdd_state_h = (u64)H;

    /* Read fields */
    u8  enabled  = H[0x85];
    u8  err_flag = H[0x78];
    u64 dev_id   = *(const volatile u64 *)(H + 0x10);
    u64 tagstat  = *(const volatile u64 *)(H + 0x38);
    u64 status40 = *(const volatile u64 *)(H + 0x40);
    u64 status48 = *(const volatile u64 *)(H + 0x48);

    /* Record in mailbox for telemetry */
    M->driver_enabled = enabled;
    M->driver_error   = err_flag;
    M->idle_tagstat   = tagstat;
    M->idle_status40  = status40;
    M->idle_status48  = status48;

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
    if (M->status & STATUS_INIT_OK) {
        return 0;
    }

    /* 1. Allocate 4 KiB arena via native_alloc in RAM */
    u64 arena_raw = native_alloc(ARENA_BYTES, 3, 0);
    if (!arena_rw(arena_raw)) {
        M->status |= (STATUS_ALLOC_FAILED | STATUS_INIT_FAILED);
        M->fail_reason = REASON_ALLOC_FAILED;
        return -1;
    }

    M->arena_ptr = arena_raw;
    M->status |= STATUS_ALLOC_OK;
    M->boot_tb = native_clock();

    /* Zero out arena structure */
    volatile u64 *p = (volatile u64 *)arena_raw;
    for (u32 i = 0; i < (ARENA_BYTES / 8); i++) {
        p[i] = 0;
    }

    volatile struct HddLogArena *arena = (volatile struct HddLogArena *)arena_raw;
    arena->log_cursor = 1;
    arena->log_seq = 0;
    arena->is_initialized = 0;

    /* 2. Verify everything by READS ONLY: H must be idle */
    if (!is_hdd_log_safe()) {
        M->status |= STATUS_INIT_FAILED;
        M->fail_reason = REASON_NOT_IDLE;
        return -1;
    }

    M->status |= STATUS_INIT_OK;
    return 0;
}

int hddlog_write(u32 tag, u64 a, u64 b, const char *text) {
    /* Fail-open: if not initialized or already failed/full, do nothing */
    if (!(M->status & STATUS_INIT_OK)) {
        return -1;
    }
    if (M->status & (STATUS_INIT_FAILED | STATUS_LOG_FAILED | STATUS_LOG_FULL)) {
        return -1;
    }

    u64 arena_addr = M->arena_ptr;
    if (!arena_rw(arena_addr)) {
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_ALLOC_FAILED;
        return -1;
    }

    volatile struct HddLogArena *arena = (volatile struct HddLogArena *)arena_addr;

    /* Verify idle precondition prior to opening file */
    if (!is_hdd_log_safe()) {
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_NOT_IDLE;
        return -1;
    }

    /* Step 1: Open placeholder file: ufs_open(0, "/tmp/netemu_log.bin") */
    static const char path[] = "/tmp/netemu_log.bin";
    s32 fd = stock_ufs_open(0, path);
    M->last_ufs_rc = fd;
    if (fd < 0 || fd > 7) {
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = (fd == -2) ? REASON_NO_FILE : REASON_WRITE_FAILED;
        return -1;
    }

    /* Step 2: First call only: read Sector 0 header via raw_read */
    if (arena->is_initialized == 0) {
        s64 rd = stock_raw_read(fd, 0, (void *)arena->sec0_buf, 512);
        M->last_ufs_rc = (s32)rd;
        if (rd != 512) {
            stock_ufs_close(fd);
            M->status |= STATUS_LOG_FAILED;
            M->fail_reason = REASON_READ_FAILED;
            return -1;
        }

        /* Check if magic is 'NETEMULG' */
        volatile u64 *sec0_words = (volatile u64 *)arena->sec0_buf;
        if (sec0_words[0] == 0x4E4554454D554C47ULL) {
            /* Existing valid header: load next_record_idx */
            volatile u32 *sec0_u32 = (volatile u32 *)arena->sec0_buf;
            u32 cur = sec0_u32[28 / 4];
            if (cur >= 1 && cur <= 127) {
                arena->log_cursor = cur;
            } else if (cur > 127) {
                /* Log is full (stop-when-full) */
                stock_ufs_close(fd);
                M->status |= STATUS_LOG_FULL;
                M->fail_reason = REASON_FULL;
                return -1;
            } else {
                arena->log_cursor = 1;
            }
        } else {
            /* Check if all-zeros */
            int all_zeros = 1;
            for (u32 i = 0; i < 64; i++) {
                if (sec0_words[i] != 0) {
                    all_zeros = 0;
                    break;
                }
            }

            if (all_zeros) {
                /* Fresh placeholder: initialize Sector 0 Header */
                sec0_words[0] = 0x4E4554454D554C47ULL; /* 'NETEMULG' */
                volatile u32 *sec0_u32 = (volatile u32 *)arena->sec0_buf;
                sec0_u32[8 / 4]  = 0x00010000; /* Version 1.0 */
                sec0_u32[12 / 4] = 512;        /* Header Size */
                sec0_u32[16 / 4] = 65536;      /* File Size */
                sec0_u32[20 / 4] = 512;        /* Sector Size */
                sec0_u32[24 / 4] = 127;        /* Max Records */
                sec0_u32[28 / 4] = 1;          /* Next Record Idx */
                sec0_words[32 / 8] = M->boot_tb;/* Boot TB */
                sec0_u32[40 / 4] = 0;          /* Clean shutdown */
                sec0_u32[44 / 4] = 0;          /* Record count */

                arena->log_cursor = 1;
            } else {
                /* Corrupt / unrecognized file header */
                stock_ufs_close(fd);
                M->status |= STATUS_LOG_FAILED;
                M->fail_reason = REASON_BAD_HEADER;
                return -1;
            }
        }
        arena->is_initialized = 1;
    }

    u32 rec_idx = arena->log_cursor;
    if (rec_idx < 1) rec_idx = 1;
    if (rec_idx > 127) {
        stock_ufs_close(fd);
        M->status |= STATUS_LOG_FULL;
        M->fail_reason = REASON_FULL;
        return -1;
    }

    /* Step 3: Build 512-byte aligned record in ARENA */
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

    /* Copy message text at offset 72 (max 440 bytes) */
    char *rec_text = (char *)(arena->rec_buf + 72);
    safe_strcpy(rec_text, text, 440);

    /* Step 4: Write record at offset = rec_idx * 512 */
    u64 offset = (u64)rec_idx * 512ULL;
    if (offset + 512ULL > 65536ULL) {
        stock_ufs_close(fd);
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_FULL;
        return -1;
    }

    s64 wr = stock_raw_write(fd, offset, (const void *)arena->rec_buf, 512);
    M->last_ufs_rc = (s32)wr;
    if (wr != 512) {
        stock_ufs_close(fd);
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    /* Step 5: Advance cursor and update Sector 0 Header */
    u32 next_rec = rec_idx + 1;
    arena->log_cursor = next_rec;
    M->cursor = next_rec;
    M->records_written++;
    M->bytes_written += 512;

    volatile u32 *sec0_u32 = (volatile u32 *)arena->sec0_buf;
    sec0_u32[28 / 4] = next_rec;
    sec0_u32[44 / 4] = M->records_written;

    s64 wr_hdr = stock_raw_write(fd, 0, (const void *)arena->sec0_buf, 512);
    M->last_ufs_rc = (s32)wr_hdr;
    if (wr_hdr != 512) {
        stock_ufs_close(fd);
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    /* Step 6: ALWAYS close fd (frees slot on physical disk) */
    s32 cl_rc = stock_ufs_close(fd);
    M->last_ufs_rc = cl_rc;
    if (cl_rc != 0) {
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_WRITE_FAILED;
        return -1;
    }

    /* Step 7: Check idle before flush */
    if (!is_hdd_log_safe()) {
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_NOT_IDLE;
        return -1;
    }

    /* Step 8: Write-through cache flush to physical HDD */
    s32 flush_rc = stock_hdd_cache_flush();
    M->last_flush_rc = flush_rc;
    if (flush_rc == 0) {
        M->flush_completed = 1;
    } else {
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_FLUSH_FAILED;
        return -1;
    }

    /* Step 9: Verify H tag/status idle again */
    if (!is_hdd_log_safe()) {
        M->status |= STATUS_LOG_FAILED;
        M->fail_reason = REASON_NOT_IDLE;
        return -1;
    }

    return 0;
}
