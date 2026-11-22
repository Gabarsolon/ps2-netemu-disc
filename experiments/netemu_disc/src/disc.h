#ifndef DISC_H
#define DISC_H

typedef unsigned char      u8;
typedef unsigned short     u16;
typedef unsigned int       u32;
typedef unsigned long long u64;
typedef signed int         s32;
typedef signed long long   s64;

/* Trampolines in code slot */
extern s64 lv1_hcall(u64 num, u64 a1, u64 a2, u64 a3, u64 a4, u64 a5, u64 a6);
extern u64 native_alloc(u64 size, u64 arg2, u64 arg3);
extern u64 native_clock(void);
extern s32 cobra_open(s32 unk, const char *path);
extern s32 cobra_stat(s32 fd, void *st);
extern s64 raw_read(s32 fd, u64 offset, void *buf, u64 count);
extern s32 stock_mount(void *cdvd_struct);
extern s32 stock_ufs_open(u64 dev_unused, const char *path);
extern s32 stock_ufs_close(s32 fd);
extern s64 stock_raw_write(s32 fd, u64 offset, const void *buf, u64 count);
extern s32 stock_hdd_cache_flush(void);

/* Disc Backend State in mailbox [0x930F20, 0x930F80) */
struct DiscMailbox {
    u32 magic;             /* 0x00: 0x44495343 ('DISC') */
    u32 flags;             /* 0x04: bit 0: opened, bit 1: verified PVD */
    s32 fd;                /* 0x08: virtual fd: 0xBD00 */
    u32 block_size;        /* 0x0C: 2048 */
    u64 disc_size;         /* 0x10: (max_lba + 1) * block_size */
    u32 max_lba;           /* 0x18: from READ CAPACITY */
    u32 open_calls;        /* 0x1C: count of s1_open calls */
    u64 dma_region;        /* 0x20: from lv1_storage_allocate_dma_region */
    u64 arena_ptr;         /* 0x28: pointer to LogArena from native_alloc */
    u64 buf_ea;            /* 0x30: CPU EA of CDVD buffer */
    u64 buf_lpar;          /* 0x38: LPAR of CDVD buffer */
    u32 read_calls;        /* 0x40: count of s1_read calls */
    u32 last_lba;          /* 0x44: last LBA requested */
    s32 last_read_rc;      /* 0x48: last read return code */
    u32 sectors_read;      /* 0x4C: total sectors read */
    u64 raw_val1;          /* 0x50..0x57: address 0x930F70 (raw_val1 from lv1_hcall epilogue) */
    u64 raw_val2;          /* 0x58..0x5F: address 0x930F78 (raw_val2 from lv1_hcall epilogue) */
};

_Static_assert(sizeof(struct DiscMailbox) == 96, "DiscMailbox must be exactly 96 bytes");
_Static_assert(__builtin_offsetof(struct DiscMailbox, arena_ptr) == 0x28, "arena_ptr at 0x28");
_Static_assert(__builtin_offsetof(struct DiscMailbox, buf_ea) == 0x30, "buf_ea at 0x30");
_Static_assert(__builtin_offsetof(struct DiscMailbox, buf_lpar) == 0x38, "buf_lpar at 0x38");
_Static_assert(__builtin_offsetof(struct DiscMailbox, raw_val1) == 0x50, "raw_val1 at 0x50 (0x930F70)");
_Static_assert(__builtin_offsetof(struct DiscMailbox, raw_val2) == 0x58, "raw_val2 at 0x58 (0x930F78)");

#define DISC_MAILBOX ((volatile struct DiscMailbox *)0x930F20ULL)

#define VIRTUAL_DISC_FD 0xBD00

int s1_open(int unk, const char *path);
int s1_stat(int fd, void *st);
int s1_read(int fd, u64 off, u8 *buf, u64 size);
int s1_mount(void *cdvd_struct);
const u8 *s4_menu(u64 selected);

#endif
