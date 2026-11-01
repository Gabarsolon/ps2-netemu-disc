#ifndef HDDLOG_H
#define HDDLOG_H

/* Freestanding PPC64 BE, compiled for ISA 2.02 (970).
 * Durable Write-Ahead HDD Logger for patched ps2_netemu (P4).
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
    u64 boot_tb;         /* 0x20: Timebase at netemu startup (Boot ID / Session ID) */
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
    u64 a;               /* 0x18: Parameter A / primary telemetry */
    u64 b;               /* 0x20: Parameter B / secondary telemetry */
    u64 boot_id;         /* 0x28: Boot ID matching header.boot_tb */
    u64 reserved[3];     /* 0x30..0x47: 24 bytes reserved telemetry */
    char text[440];      /* 0x48: NUL-terminated message string (440 bytes) */
};

_Static_assert(sizeof(struct NetemuLogRecord) == 512, "NetemuLogRecord must be exactly 512 bytes");
_Static_assert(__builtin_offsetof(struct NetemuLogRecord, boot_id) == 40, "boot_id at 40");
_Static_assert(__builtin_offsetof(struct NetemuLogRecord, text) == 72, "text at 72");

#define REASON_OK               0
#define REASON_NOT_IDLE         1
#define REASON_NO_FILE          2
#define REASON_ALLOC_FAILED     3
#define REASON_READ_FAILED      4
#define REASON_BAD_HEADER       5
#define REASON_WRITE_FAILED     6
#define REASON_FLUSH_FAILED     7
#define REASON_FULL             8

/* Small API macros for one-line logging */
#define HDDLOG_TAG(c0, c1, c2, c3) \
    (((u32)(c0) << 24) | ((u32)(c1) << 16) | ((u32)(c2) << 8) | ((u32)(c3)))

#define TAG_BOOT HDDLOG_TAG('B', 'O', 'O', 'T')
#define TAG_SCAN HDDLOG_TAG('S', 'C', 'A', 'N')
#define TAG_GRD  HDDLOG_TAG('G', 'R', 'D', ' ')
#define TAG_PRE  HDDLOG_TAG('P', 'R', 'E', ' ')
#define TAG_POST HDDLOG_TAG('P', 'O', 'S', 'T')
#define TAG_TMO  HDDLOG_TAG('T', 'M', 'O', ' ')
#define TAG_END  HDDLOG_TAG('E', 'N', 'D', ' ')

#define HDDLOG(tag, a, b, text) hddlog_write((tag), (a), (b), (text))

/* Module public functions */
int hddlog_init(void);
int hddlog_write(u32 tag, u64 a, u64 b, const char *text);

#endif /* HDDLOG_H */
