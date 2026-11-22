#ifndef HDDLOG_H
#define HDDLOG_H

#include "disc.h"

/* Durable Write-Ahead HDD Logger for patched ps2_netemu */

struct NetemuLogHeader {
    u64 magic;           /* 0x00: 0x4E4554454D554C47 ("NETEMULG") */
    u32 version;         /* 0x08: 0x00010000 (v1.0) */
    u32 header_size;     /* 0x0C: 512 */
    u32 file_size;       /* 0x10: 65536 */
    u32 sector_size;     /* 0x14: 512 */
    u32 max_records;     /* 0x18: 127 */
    u32 next_record_idx; /* 0x1C: 1..127 */
    u64 boot_tb;         /* 0x20: Timebase */
    u32 clean_shutdown;  /* 0x28 */
    u32 record_count;    /* 0x2C */
    u8  reserved[464];   /* 0x30..0x1FF */
};

_Static_assert(sizeof(struct NetemuLogHeader) == 512, "NetemuLogHeader 512 bytes");

struct NetemuLogRecord {
    u32 magic;           /* 0x00: 0x4C4F4752 ("LOGR") */
    u32 sequence;        /* 0x04 */
    u32 tag;             /* 0x08 */
    u32 flags;           /* 0x0C */
    u64 timestamp_tb;    /* 0x10 */
    u64 a;               /* 0x18 */
    u64 b;               /* 0x20 */
    u64 boot_id;         /* 0x28 */
    u64 reserved[3];     /* 0x30..0x47 */
    char text[440];      /* 0x48 */
};

_Static_assert(sizeof(struct NetemuLogRecord) == 512, "NetemuLogRecord 512 bytes");

struct LogArena {
    u64 boot_tb;
    u32 log_cursor;
    u32 log_seq;
    u32 is_log_initialized;
    u32 log_session_started;
    u32 log_busy_last;
    u32 log_busy_seen;
    u64 log_tagstat;
    u64 log_expected_tag;
    u64 log_status40;
    u32 log_hdd_state;
    u32 log_command_type;
    u8  pvd_sample[16];
    u8  sec0_buf[512];
    u8  rec_buf[512];
};

int hddlog_init(void);
int hddlog_write(u32 tag, u64 a, u64 b, const char *text);

#endif
