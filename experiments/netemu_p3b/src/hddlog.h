#ifndef HDDLOG_H
#define HDDLOG_H

/* Freestanding PPC64 BE, compiled for ISA 2.02 (970).
 * Reusable Durable HDD Logger for patched ps2_netemu.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef long long s64;
typedef int s32;

/* External stock trampolines residing in the code slot */
extern u64 native_alloc(u64 size, u64 arg2, u64 arg3);
extern u64 native_clock(void);
extern u64 get_r2(void);
extern s32 stock_ufs_open(u64 dev_unused, const char *path);
extern s32 stock_ufs_close(s32 fd);
extern s64 stock_raw_read(s32 fd, u64 offset, void *buf, u64 count);
extern s64 stock_raw_write(s32 fd, u64 offset, const void *buf, u64 count);
extern s32 stock_hdd_cache_flush(void);

/* Sector 0: Log Header (exactly 512 bytes) */
struct NetemuLogHeader {
    u64 magic;           /* 0x00: 0x4E4554454D554C47 ("NETEMULG") */
    u32 version;         /* 0x08: 0x00010000 (v1.0) */
    u32 header_size;     /* 0x0C: 512 */
    u32 file_size;       /* 0x10: 65536 */
    u32 sector_size;     /* 0x14: 512 */
    u32 max_records;     /* 0x18: 127 */
    u32 next_record_idx; /* 0x1C: 1..127 (write cursor) */
    u64 boot_tb;         /* 0x20: Timebase at netemu startup (Boot ID) */
    u32 clean_shutdown;  /* 0x28: 0 = uncommitted/crash, 1 = clean exit */
    u32 record_count;    /* 0x2C: total records written in current session */
    u8  reserved[464];   /* 0x30..0x1FF: pad to exactly 512 bytes */
};

_Static_assert(sizeof(struct NetemuLogHeader) == 512, "NetemuLogHeader must be exactly 512 bytes");
_Static_assert(__builtin_offsetof(struct NetemuLogHeader, next_record_idx) == 28, "next_record_idx at 28");
_Static_assert(__builtin_offsetof(struct NetemuLogHeader, boot_tb) == 32, "boot_tb at 32");

/* Sectors 1..127: Log Record (exactly 512 bytes) */
struct NetemuLogRecord {
    u32 magic;           /* 0x00: 0x4C4F4752 ("LOGR") */
    u32 sequence;        /* 0x04: Monotonic sequence counter */
    u32 tag;             /* 0x08: Component / phase tag */
    u32 flags;           /* 0x0C: Status flags */
    u64 timestamp_tb;    /* 0x10: Timebase ticks from native_clock */
    u64 a;               /* 0x18: Parameter A */
    u64 b;               /* 0x20: Parameter B */
    u64 reserved[4];     /* 0x28: 32 bytes reserved telemetry */
    char text[440];      /* 0x48: NUL-terminated message string (440 bytes) */
};

_Static_assert(sizeof(struct NetemuLogRecord) == 512, "NetemuLogRecord must be exactly 512 bytes");
_Static_assert(__builtin_offsetof(struct NetemuLogRecord, text) == 72, "text at 72");

/* Mailbox at 0x930F20 (strictly 96 bytes, [0x930F20, 0x930F80)) */
#define MAILBOX_ADDR 0x930F20ULL
#define STOCK_LABEL  ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED          (1U << 0)
#define STATUS_DONE             (1U << 1)
#define STATUS_ALLOC_OK         (1U << 2)
#define STATUS_ALLOC_FAILED     (1U << 3)
#define STATUS_INIT_OK          (1U << 4)
#define STATUS_INIT_FAILED      (1U << 5)
#define STATUS_LOG_FAILED       (1U << 6)
#define STATUS_LOG_FULL         (1U << 7)

#define REASON_OK               0
#define REASON_NOT_IDLE         1
#define REASON_NO_FILE          2
#define REASON_ALLOC_FAILED     3
#define REASON_READ_FAILED      4
#define REASON_BAD_HEADER       5
#define REASON_WRITE_FAILED     6
#define REASON_FLUSH_FAILED     7
#define REASON_FULL             8

struct HddLogMailbox {
    u32 status;            /* 0x00: bitmask */
    u32 records_written;   /* 0x04: count of records successfully written & flushed */
    u32 bytes_written;     /* 0x08: total bytes written */
    s32 last_ufs_rc;       /* 0x0C: return code from last UFS call */
    s32 last_flush_rc;     /* 0x10: return code from last hdd_cache_flush */
    u32 open_count;        /* 0x14: menu open cycles detected by TB gap */
    u64 arena_ptr;         /* 0x18: pointer to 4 KiB arena from native_alloc */
    u64 boot_tb;           /* 0x20: boot timebase ticks from native_clock */
    u64 last_eval_tb;      /* 0x28: timebase of last hook evaluation */
    u32 cursor;            /* 0x30: current next_record_idx */
    u32 fail_reason;       /* 0x34: reason code if logging stopped */
    u64 hdd_state_h;       /* 0x38: pointer H (0x241c850) */
    u64 idle_tagstat;      /* 0x40: H+0x38 read during idle check */
    u64 idle_status40;     /* 0x48: H+0x40 read during idle check */
    u64 idle_status48;     /* 0x50: H+0x48 read during idle check */
    u8  driver_enabled;    /* 0x58: H+0x85 read during idle check */
    u8  driver_error;      /* 0x59: H+0x78 read during idle check */
    u8  flush_completed;   /* 0x5A: 1 if cache flush completed */
    u8  pad[5];            /* 0x5B: pad to exactly 96 bytes */
};

_Static_assert(sizeof(struct HddLogMailbox) == 96, "HddLogMailbox must be exactly 96 bytes");

#define M ((volatile struct HddLogMailbox *)MAILBOX_ADDR)

/* Allocator-backed 4 KiB Arena Structure */
#define ARENA_BYTES 4096U

struct HddLogArena {
    u8   sec0_buf[512];          /* 0x000..0x1FF: 512-byte aligned buffer for Sector 0 */
    u8   rec_buf[512];           /* 0x200..0x3FF: 512-byte aligned buffer for log records */
    char row_strings[9][64];     /* 0x400..0x63F: 576 bytes for menu rows 0..8 */
    u64  hdd_words[10];          /* 0x640..0x68F: 80 bytes from H */
    u32  log_seq;                /* 0x690..0x693: monotonic sequence */
    u32  log_cursor;             /* 0x694..0x697: cursor (next_record_idx) */
    u32  is_initialized;         /* 0x698..0x69B: 1 after first call init */
    u32  pad;                    /* 0x69C..0x69F */
};

_Static_assert(sizeof(struct HddLogArena) <= ARENA_BYTES, "HddLogArena must fit in 4 KiB arena");

/* Small API macros for one-line logging */
#define HDDLOG_TAG(c0, c1, c2, c3) \
    (((u32)(c0) << 24) | ((u32)(c1) << 16) | ((u32)(c2) << 8) | ((u32)(c3)))

#define TAG_BOOT HDDLOG_TAG('B', 'O', 'O', 'T')
#define TAG_T1   HDDLOG_TAG('T', '1', ' ', ' ')
#define TAG_T2   HDDLOG_TAG('T', '2', ' ', ' ')
#define TAG_END  HDDLOG_TAG('E', 'N', 'D', ' ')

#define HDDLOG(tag, a, b, text) hddlog_write((tag), (a), (b), (text))

/* Module public functions */
int hddlog_init(void);
int hddlog_write(u32 tag, u64 a, u64 b, const char *text);

#endif /* HDDLOG_H */
