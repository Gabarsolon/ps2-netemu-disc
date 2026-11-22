#include "hddlog.h"

static void safe_strcpy(char *dst, const char *src, u32 max_len) {
    u32 i = 0;
    if (!dst || !max_len) return;
    if (src) {
        while (src[i] && i + 1 < max_len) {
            dst[i] = src[i];
            i++;
        }
    }
    dst[i] = 0;
}

static u32 hddlog_busy_mask(volatile struct LogArena *arena) {
    const volatile u8 *H = (const volatile u8 *)0x241C850ULL;
    if (!H) return 1;
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
    const volatile u32 *ufs_lock = *(const volatile u32 * const *)0x3055180ULL;
    if (ufs_lock && *ufs_lock != 0) mask |= 64;

    if (arena) {
        arena->log_busy_last = mask;
        arena->log_busy_seen |= mask;
        arena->log_tagstat = tag;
        arena->log_expected_tag = expected;
        arena->log_status40 = status;
        arena->log_hdd_state = *(const volatile u32 *)H;
        arena->log_command_type = *(const volatile u32 *)(H + 0x58);
    }
    return mask;
}

static int is_hdd_log_safe(volatile struct LogArena *arena) {
    return hddlog_busy_mask(arena) == 0;
}

int hddlog_init(void) {
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    volatile struct LogArena *arena = 0;

    if (!mb->arena_ptr) {
        u64 alloc_res = native_alloc(sizeof(struct LogArena), 3, 0);
        if (!alloc_res || alloc_res < 0x80000000ULL) return -1;
        mb->arena_ptr = alloc_res;
        arena = (volatile struct LogArena *)alloc_res;
        for (u32 i = 0; i < sizeof(struct LogArena); i++) {
            ((volatile u8 *)arena)[i] = 0;
        }
    } else {
        arena = (volatile struct LogArena *)mb->arena_ptr;
    }

    if (arena->is_log_initialized) return 0;

    if (!arena->log_session_started) {
        arena->log_session_started = 1;
        arena->boot_tb = native_clock();
        arena->log_cursor = 1;
        arena->log_seq = 0;
    }

    if (!is_hdd_log_safe(arena)) return -1;

    s32 fd = stock_ufs_open(0, "/tmp/netemu_log.bin");
    if (fd < 0 || fd > 7) return -1;

    volatile u64 *words = (volatile u64 *)arena->sec0_buf;
    for (u32 i = 0; i < 64; i++) words[i] = 0;
    words[0] = 0x4E4554454D554C47ULL; /* "NETEMULG" */
    volatile u32 *header = (volatile u32 *)arena->sec0_buf;
    header[2] = 0x00010000;
    header[3] = 512;
    header[4] = 65536;
    header[5] = 512;
    header[6] = 127;
    header[7] = 1;
    words[4] = arena->boot_tb;

    s64 wrote = stock_raw_write(fd, 0, (const void *)arena->sec0_buf, 512);
    s32 closed = stock_ufs_close(fd);
    if (wrote != 512 || closed != 0) return -1;

    if (!is_hdd_log_safe(arena) || stock_hdd_cache_flush() != 0) return -1;

    arena->is_log_initialized = 1;
    return 0;
}

int hddlog_write(u32 tag, u64 a, u64 b, const char *text) {
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    volatile struct LogArena *arena = (volatile struct LogArena *)mb->arena_ptr;

    if (!arena || !arena->is_log_initialized) {
        if (hddlog_init() != 0) return -1;
        arena = (volatile struct LogArena *)mb->arena_ptr;
        if (!arena || !arena->is_log_initialized) return -1;
    }

    if (arena->log_cursor > 127) return -1;
    if (!is_hdd_log_safe(arena)) return -1;

    s32 fd = stock_ufs_open(0, "/tmp/netemu_log.bin");
    if (fd < 0 || fd > 7) return -1;

    volatile u64 *words = (volatile u64 *)arena->rec_buf;
    for (u32 i = 0; i < 64; i++) words[i] = 0;
    volatile u32 *record = (volatile u32 *)arena->rec_buf;
    record[0] = 0x4C4F4752; /* "LOGR" */
    record[1] = arena->log_seq + 1;
    record[2] = tag;
    record[3] = ((arena->log_hdd_state & 65535) << 16) | (arena->log_command_type & 65535);
    words[2] = native_clock();
    words[3] = a;
    words[4] = b;
    words[5] = arena->boot_tb;

    safe_strcpy((char *)arena->rec_buf + 72, text, 440);

    u64 file_off = (u64)arena->log_cursor * 512;
    s64 wrote = stock_raw_write(fd, file_off, (const void *)arena->rec_buf, 512);
    s32 closed = stock_ufs_close(fd);
    if (wrote != 512 || closed != 0) return -1;

    if (!is_hdd_log_safe(arena) || stock_hdd_cache_flush() != 0) return -1;

    arena->log_cursor++;
    arena->log_seq++;

    /* Update header record count */
    if (is_hdd_log_safe(arena)) {
        s32 hfd = stock_ufs_open(0, "/tmp/netemu_log.bin");
        if (hfd >= 0 && hfd <= 7) {
            volatile u32 *hdr32 = (volatile u32 *)arena->sec0_buf;
            hdr32[7] = arena->log_cursor;
            hdr32[11] = arena->log_seq;
            stock_raw_write(hfd, 0, (const void *)arena->sec0_buf, 512);
            stock_ufs_close(hfd);
            stock_hdd_cache_flush();
        }
    }
    return 0;
}
