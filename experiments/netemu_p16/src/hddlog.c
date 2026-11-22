#include "hddlog.h"

static void safe_strcpy(char *dst, const char *src, u32 max_len) {
    u32 i = 0;
    if (!dst || !max_len) return;
    if (src) while (src[i] && i + 1 < max_len) { dst[i] = src[i]; i++; }
    dst[i] = 0;
}

/* Exact existing predicate; volatile reads prevent stale values on callbacks.
 * Bit 0 disabled, 1 error, 2 wrong device, 3 tag, 4 status40,
 * 5 expected-tag/status48, 6 UFS lock. No predicate is weakened. */
static u32 hddlog_busy_mask(void) {
    const volatile u8 *H = (const volatile u8 *)0x241C850ULL;
    u32 mask = 0;
    if (H[0x85] != 1) mask |= 1;
    if (H[0x78] != 0) mask |= 2;
    if (*(const volatile u64 *)(H + 0x10) != 3) mask |= 4;
    u64 tag = *(const volatile u64 *)(H + 0x38);
    u64 status = *(const volatile u64 *)(H + 0x40);
    u64 expected = *(const volatile u64 *)(H + 0x48);
    if (tag != 0) mask |= 8;
    if (status != 0) mask |= 16;
    if (expected != 0) mask |= 32;
    if (*(const volatile u32 *)0x3055180ULL != 0) mask |= 64;
    volatile struct ProbeArena *arena = (volatile struct ProbeArena *)S->arena_ptr;
    if (arena) {
        arena->log_busy_last = mask; arena->log_busy_seen |= mask;
        arena->log_tagstat = tag; arena->log_expected_tag = expected;
        arena->log_status40 = status;
        arena->log_hdd_state = *(const volatile u32 *)H;
        arena->log_command_type = *(const volatile u32 *)(H + 0x58);
    }
    return mask;
}

static int is_hdd_log_safe(void) { return hddlog_busy_mask() == 0; }

/* No busy-wait: a later bounded menu callback retries the compact summary. */
int hddlog_init(void) {
    if (!S->arena_ptr) return -1;
    volatile struct ProbeArena *arena = (volatile struct ProbeArena *)S->arena_ptr;
    if (arena->is_log_initialized) return 0;
    if (!arena->log_session_started) {
        arena->log_session_started = 1;
        arena->boot_tb = native_clock();
        arena->log_cursor = 1;
        arena->log_seq = 0;
    }
    if (!is_hdd_log_safe()) {
        S->log_fail_reason = REASON_NOT_IDLE;
        S->log_records_skipped++;
        return -1;
    }
    s32 fd = stock_ufs_open(0, "/tmp/netemu_log.bin");
    if (fd < 0 || fd > 7) {
        S->log_fail_reason = fd == -2 ? REASON_NO_FILE : REASON_WRITE_FAILED;
        return -1;
    }
    volatile u64 *words = (volatile u64 *)arena->sec0_buf;
    for (u32 i = 0; i < 64; i++) words[i] = 0;
    words[0] = 0x4E4554454D554C47ULL;
    volatile u32 *header = (volatile u32 *)arena->sec0_buf;
    header[2] = 0x00010000; header[3] = 512; header[4] = 65536;
    header[5] = 512; header[6] = 127; header[7] = 1;
    words[4] = arena->boot_tb;
    s64 wrote = stock_raw_write(fd, 0, (const void *)arena->sec0_buf, 512);
    s32 closed = stock_ufs_close(fd);
    if (wrote != 512 || closed != 0) {
        S->log_fail_reason = REASON_WRITE_FAILED;
        return -1;
    }
    if (!is_hdd_log_safe() || stock_hdd_cache_flush() != 0) {
        S->log_fail_reason = REASON_FLUSH_FAILED;
        return -1;
    }
    arena->is_log_initialized = 1;
    return 0;
}

int hddlog_write(u32 tag, u64 a, u64 b, const char *text) {
    if (!S->arena_ptr) return -1;
    volatile struct ProbeArena *arena = (volatile struct ProbeArena *)S->arena_ptr;
    if (!arena->is_log_initialized) { S->log_records_skipped++; return -1; }
    if (arena->log_cursor > 127) { S->log_fail_reason = REASON_FULL; return -1; }
    if (!is_hdd_log_safe()) {
        S->log_fail_reason = REASON_NOT_IDLE; S->log_records_skipped++; return -1;
    }
    s32 fd = stock_ufs_open(0, "/tmp/netemu_log.bin");
    if (fd < 0 || fd > 7) {
        S->log_fail_reason = fd == -2 ? REASON_NO_FILE : REASON_WRITE_FAILED;
        return -1;
    }
    volatile u64 *words = (volatile u64 *)arena->rec_buf;
    for (u32 i = 0; i < 64; i++) words[i] = 0;
    volatile u32 *record = (volatile u32 *)arena->rec_buf;
    record[0] = 0x4C4F4752; record[1] = arena->log_seq + 1;
    record[2] = tag; words[2] = native_clock(); words[3] = a;
    record[3] = ((arena->log_hdd_state & 65535) << 16) | (arena->log_command_type & 65535);
    words[4] = b; words[5] = arena->boot_tb;
    words[6] = arena->log_tagstat; words[7] = arena->log_expected_tag;
    words[8] = arena->log_status40;
    safe_strcpy((char *)arena->rec_buf + 72, text, 440);

    volatile u32 *header = (volatile u32 *)arena->sec0_buf;
    u32 old_clean = header[10];
    header[7] = arena->log_cursor + 1;
    header[10] = tag == TAG_END ? 1 : 0;
    header[11] = S->log_records_written + 1;
    s64 wrote = stock_raw_write(fd, (u64)arena->log_cursor * 512,
                                (const void *)arena->rec_buf, 512);
    s64 hdr = wrote == 512 ? stock_raw_write(fd, 0, (const void *)arena->sec0_buf, 512) : -1;
    s32 closed = stock_ufs_close(fd);
    int complete = wrote == 512 && hdr == 512 && closed == 0;
    if (!complete) S->log_fail_reason = REASON_WRITE_FAILED;
    else if (!is_hdd_log_safe() || stock_hdd_cache_flush() != 0) {
        complete = 0; S->log_fail_reason = REASON_FLUSH_FAILED;
    }
    if (!complete) {
        /* Retrying overwrites the same sector/sequence; no false in-memory ACK. */
        header[7] = arena->log_cursor; header[10] = old_clean;
        header[11] = S->log_records_written;
        return -1;
    }
    arena->log_cursor++; arena->log_seq++; S->log_records_written++;
    if (tag == TAG_END) S->log_clean_shutdown = 1;
    return 0;
}
