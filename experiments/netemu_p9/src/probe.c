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
    u32 timeouts;          /* 8..11: timeout bitfield */
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

    /* Durable logging telemetry */
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
#define STEP_TUR                5
#define STEP_INQ                6
#define STEP_CAP                7
#define STEP_PIO_16             8
#define STEP_PIO_0              9
#define STEP_PIO_17             10
#define STEP_DMA_16             11
#define STEP_SENSE              12
#define STEP_UNMAP              13
#define STEP_FREE               14
#define STEP_CLOSE              15

#define TIMEOUT_TUR             (1U << 0)
#define TIMEOUT_INQ             (1U << 1)
#define TIMEOUT_CAP             (1U << 2)
#define TIMEOUT_PIO_16          (1U << 3)
#define TIMEOUT_PIO_0           (1U << 4)
#define TIMEOUT_PIO_17          (1U << 5)
#define TIMEOUT_DMA_16          (1U << 6)
#define TIMEOUT_SENSE           (1U << 7)

#define CLASS_UNCHANGED         0
#define CLASS_ZEROS             1
#define CLASS_DATA_OK           2
#define CLASS_OTHER             3

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

    s32 tur_send_rc;       /* 0x65C: LV1 248 TUR send rc */
    s32 inq_send_rc;       /* 0x660: LV1 248 INQUIRY send rc */
    s32 cap_send_rc;       /* 0x664: LV1 248 READ CAPACITY send rc */
    s32 pio_16_send_rc;    /* 0x668: LV1 248 READ(10) PIO LBA 16 send rc */
    s32 pio_0_send_rc;     /* 0x66C: LV1 248 READ(10) PIO LBA 0 send rc */
    s32 pio_17_send_rc;    /* 0x670: LV1 248 READ(10) PIO LBA 17 send rc */
    s32 dma_16_send_rc;    /* 0x674: LV1 248 READ(10) DMA LBA 16 send rc */
    s32 sense_send_rc;     /* 0x678: LV1 248 REQUEST SENSE send rc */

    u32 rom_region_id;     /* 0x67C: region id for ROM device from repo */
    u32 total_devices;     /* 0x680: total devices discovered across all buses */
    u32 is_log_initialized;/* 0x684: 1 if hddlog_init succeeded */
    u32 log_cursor;        /* 0x688: next record index */
    u32 log_seq;           /* 0x68C: monotonic log record sequence */

    u32 tur_polls;         /* 0x690: async poll iterations for TUR */
    u32 inq_polls;         /* 0x694: async poll iterations for INQUIRY */
    u32 cap_polls;         /* 0x698: async poll iterations for READ CAPACITY */
    u32 pio_16_polls;      /* 0x69C: async poll iterations for PIO LBA 16 */
    u32 pio_0_polls;       /* 0x6A0: async poll iterations for PIO LBA 0 */
    u32 pio_17_polls;      /* 0x6A4: async poll iterations for PIO LBA 17 */
    u32 dma_16_polls;      /* 0x6A8: async poll iterations for DMA LBA 16 */
    u32 sense_polls;       /* 0x6AC: async poll iterations for REQUEST SENSE */

    u32 cap_max_lba;       /* 0x6B0: Max LBA from READ CAPACITY(10) */
    u32 cap_block_size;    /* 0x6B4: Block size from READ CAPACITY(10) */

    u32 pio_16_a5_cnt;     /* 0x6B8: count of remaining 0xA5 in buffer after PIO LBA 16 */
    u32 pio_0_a5_cnt;      /* 0x6BC: count of remaining 0xA5 in buffer after PIO LBA 0 */
    u32 pio_17_a5_cnt;     /* 0x6C0: count of remaining 0xA5 in buffer after PIO LBA 17 */
    u32 dma_16_a5_cnt;     /* 0x6C4: count of remaining 0xA5 in buffer after DMA LBA 16 */

    u8  pio_16_class;      /* 0x6C8: buffer classification for PIO LBA 16 */
    u8  pio_0_class;       /* 0x6C9: buffer classification for PIO LBA 0 */
    u8  pio_17_class;      /* 0x6CA: buffer classification for PIO LBA 17 */
    u8  dma_16_class;      /* 0x6CB: buffer classification for DMA LBA 16 */

    u64 dma_region;        /* 0x6D0: DMA region ID from 174 */
    u64 dma_bus_addr;      /* 0x6D8: DMA bus address from 176 */
    u64 buf_lpar;          /* 0x6E0: buffer physical LPAR address from SB_CDVD */
    u64 buf_ea;            /* 0x6E8: buffer CPU effective address from SB_CDVD */
    u64 buf_sz;            /* 0x6F0: buffer size from SB_CDVD */
    u64 boot_tb;           /* 0x6F8: boot session timebase ID */

    u64 tur_status;        /* 0x700: async status word from TUR */
    u64 inq_status;        /* 0x708: async status word from INQUIRY */
    u64 cap_status;        /* 0x710: async status word from READ CAPACITY */
    u64 pio_16_status;     /* 0x718: async status word from PIO LBA 16 */
    u64 pio_0_status;      /* 0x720: async status word from PIO LBA 0 */
    u64 pio_17_status;     /* 0x728: async status word from PIO LBA 17 */
    u64 dma_16_status;     /* 0x730: async status word from DMA LBA 16 */
    u64 sense_status;      /* 0x738: async status word from REQUEST SENSE */

    u64 tur_tb_ticks;      /* 0x740: elapsed timebase ticks for TUR */
    u64 inq_tb_ticks;      /* 0x748: elapsed timebase ticks for INQUIRY */
    u64 cap_tb_ticks;      /* 0x750: elapsed timebase ticks for READ CAPACITY */
    u64 pio_16_tb_ticks;   /* 0x758: elapsed timebase ticks for PIO LBA 16 */
    u64 pio_0_tb_ticks;    /* 0x760: elapsed timebase ticks for PIO LBA 0 */
    u64 pio_17_tb_ticks;   /* 0x768: elapsed timebase ticks for PIO LBA 17 */
    u64 dma_16_tb_ticks;   /* 0x770: elapsed timebase ticks for DMA LBA 16 */
    u64 sense_tb_ticks;    /* 0x778: elapsed timebase ticks for REQUEST SENSE */

    u8  inq_data[36];      /* 0x780: 36 bytes INQUIRY response */
    u8  sense_data[18];    /* 0x7A4: 18 bytes sense data */
    u8  pio_16_sample[32]; /* 0x7B6: sample of sector 16 (PVD) */
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

static void format_bytes_hex(char **dst, const volatile u8 *data, u32 count) {
    const char hex[] = "0123456789abcdef";
    for (u32 i = 0; i < count; i++) {
        *(*dst)++ = hex[(data[i] >> 4) & 0xF];
        *(*dst)++ = hex[data[i] & 0xF];
    }
}

static void format_ascii(char **dst, const volatile u8 *data, u32 count) {
    for (u32 i = 0; i < count; i++) {
        u8 c = data[i];
        if (c >= 32 && c <= 126) {
            *(*dst)++ = (char)c;
        } else {
            *(*dst)++ = '.';
        }
    }
}

/* Verified guard for SB_CDVD buffer source (P6 R1 console proven):
 * - Physical LPAR address at 0x2458438 (0x2456fe0 + 0x1458)
 * - Buffer size at 0x2458430 (0x2456fe0 + 0x1450)
 * - CPU EA at 0x2458428 (0x2456fe0 + 0x1448)
 *
 * Runtime Sanity Requirements:
 * 1. Physical LPAR must be strictly 64-bit (>= 0x1_0000_0000), match 0x5000_0000_0000 pattern, and 1 MiB aligned.
 * 2. CPU EA must be strictly 32-bit (< 0x1_0000_0000), >= 0x80000000, match 1 MiB alignment, and != LPAR.
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

/* Helper to setup 64-byte ATAPI non-read or short inquiry/sense command block in buffer */
static __attribute__((noinline)) void setup_atapi_block(volatile u8 *block, u8 opcode, u32 alloc_len, u32 proto, u32 in_out, u64 buf_lpar) {
    volatile u64 *b64 = (volatile u64 *)block;
    for (u32 i = 0; i < 8; i++) {
        b64[i] = 0;
    }

    block[0] = opcode;
    if (opcode == 0x12) {
        block[4] = (u8)alloc_len; /* INQUIRY allocation length */
    } else if (opcode == 0x03) {
        block[4] = (u8)alloc_len; /* REQUEST SENSE allocation length */
    }

    volatile u32 *b32 = (volatile u32 *)block;
    b32[8]  = 12;         /* +0x20: pktlen = 12 */
    b32[9]  = alloc_len;  /* +0x24: blocks */
    b32[10] = 1;          /* +0x28: block_size = 1 */
    b32[11] = proto;      /* +0x2C: proto (0=NON_DATA, 1=PIO_IN) */
    b32[12] = in_out;     /* +0x30: in_out (0=WRITE, 1=READ) */

    b64[7]  = buf_lpar;   /* +0x38: buffer LPAR */
}

/* Pre-fill CPU data buffer area with known test pattern */
static __attribute__((noinline)) void prefill_buffer(volatile u8 *buf, u32 len, u8 val) {
    for (u32 i = 0; i < len; i++) {
        buf[i] = val;
    }
}

/* Count remaining instances of pattern byte in data buffer */
static u32 count_a5(const volatile u8 *buf, u32 len) {
    u32 cnt = 0;
    for (u32 i = 0; i < len; i++) {
        if (buf[i] == 0xA5) {
            cnt++;
        }
    }
    return cnt;
}

/* Classify 2048-byte sector buffer */
static u8 classify_sector(const volatile u8 *buf, u32 a5_cnt) {
    if (a5_cnt == 2048) {
        return CLASS_UNCHANGED;
    }
    if (buf[1] == 'C' && buf[2] == 'D' && buf[3] == '0' && buf[4] == '0' && buf[5] == '1') {
        return CLASS_DATA_OK;
    }
    /* Check for all zeros */
    u32 zero_cnt = 0;
    for (u32 i = 0; i < 2048; i++) {
        if (buf[i] == 0x00) zero_cnt++;
    }
    if (zero_cnt == 2048) {
        return CLASS_ZEROS;
    }
    return CLASS_OTHER;
}

static const char *class_to_str(u8 c) {
    switch (c) {
        case CLASS_UNCHANGED: return "UNCHANGED";
        case CLASS_ZEROS:     return "ZEROS";
        case CLASS_DATA_OK:   return "DATA_OK";
        default:              return "OTHER";
    }
}

/* Bounded polling loop for LV1 254 (storage_check_async_status):
 * Bound 1: 200,000 iterations
 * Bound 2: 160,000,000 timebase ticks (~2.0 seconds at ~79.8 MHz timebase)
 * Returns 0 on completion (status saved in *p_status), 1 on timeout.
 */
static s32 poll_completion(u64 dev, u64 tag, volatile u64 *p_status, volatile u32 *p_polls, volatile u64 *p_ticks) {
    u64 start_tb = native_clock();
    for (u32 iter = 0; iter < 200000; iter++) {
        s64 rc = lv1_hcall(254, dev, tag, 0, 0, 0, 0);
        S->total_hypercalls++;
        if (rc == 0) {
            *p_status = S->raw_val1;
            *p_polls = iter + 1;
            *p_ticks = native_clock() - start_tb;
            return 0; /* completed */
        }
        u64 now_tb = native_clock();
        if ((now_tb - start_tb) >= 160000000ULL) {
            break;
        }
    }
    *p_ticks = native_clock() - start_tb;
    return 1; /* timeout */
}

/* Request sense execution helper */
static __attribute__((noinline)) void do_request_sense(u64 dev_id, volatile u8 *cmnd_block_ea, u64 cmnd_block_lpar, volatile u8 *data_ea, u64 data_lpar, volatile struct ProbeArena *arena) {
    setup_atapi_block(cmnd_block_ea, 0x03, 18, 1, 1, data_lpar);
    prefill_buffer(data_ea, 18, 0x00);

    char msg[128];
    char *mp = msg;
    append_str(&mp, "pre sense: cmd_lpar=0x");
    format_hex64(&mp, cmnd_block_lpar);
    append_str(&mp, " buf_lpar=0x");
    format_hex64(&mp, data_lpar);
    *mp = '\0';
    HDDLOG(TAG_PRE, cmnd_block_lpar, data_lpar, msg);

    s64 sns_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 18);
    S->total_hypercalls++;
    arena->sense_send_rc = (s32)sns_rc;
    if (sns_rc == 0) {
        u64 sns_tag = S->raw_val1;
        s32 sns_poll = poll_completion(dev_id, sns_tag, &arena->sense_status, &arena->sense_polls, &arena->sense_tb_ticks);
        if (sns_poll != 0) {
            S->timeouts |= TIMEOUT_SENSE;
            mp = msg;
            append_str(&mp, "timeout: sense timed out");
            *mp = '\0';
            HDDLOG(TAG_TMO, (u64)arena->sense_polls, arena->sense_tb_ticks, msg);
            return;
        }
        for (u32 i = 0; i < 18; i++) {
            arena->sense_data[i] = data_ea[i];
        }
    }
    mp = msg;
    append_str(&mp, "post sense: rc=");
    format_dec(&mp, (u32)sns_rc);
    append_str(&mp, " async=0x");
    format_hex64(&mp, arena->sense_status);
    append_str(&mp, " skey=0x");
    format_hex32(&mp, (u32)(arena->sense_data[2] & 0x0F));
    append_str(&mp, " asc=0x");
    format_hex32(&mp, (u32)arena->sense_data[12]);
    append_str(&mp, " ascq=0x");
    format_hex32(&mp, (u32)arena->sense_data[13]);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)sns_rc, arena->sense_status, msg);
}

/* Modular Read Test Executor:
 * Configures ATAPI command block, pre-fills buffer with 0xA5, executes HV 248,
 * polls completion, classifies buffer, logs windows, and runs request sense on error.
 * Returns 0 on success, 1 on timeout, -1 on command error.
 */
static __attribute__((noinline)) int execute_read_test(
    u64 dev_id, u32 lba, u32 blocks, u32 block_size, u32 proto, u32 step_id, u32 timeout_bit,
    const char *test_name,
    volatile u8 *cmnd_block_ea, u64 cmnd_block_lpar,
    volatile u8 *data_ea, u64 data_lpar,
    volatile struct ProbeArena *arena,
    volatile s32 *p_send_rc, volatile u64 *p_status, volatile u32 *p_polls, volatile u64 *p_ticks,
    volatile u32 *p_a5_cnt, volatile u8 *p_class)
{
    char msg[256];
    char *mp;

    /* 1. Pre-fill CPU data buffer with 0xA5 */
    prefill_buffer(data_ea, 2048, 0xA5);

    /* 2. Format 64-byte ATAPI command block */
    volatile u64 *b64 = (volatile u64 *)cmnd_block_ea;
    for (u32 i = 0; i < 8; i++) {
        b64[i] = 0;
    }

    /* CDB: READ(10) (0x28) */
    cmnd_block_ea[0] = 0x28;
    cmnd_block_ea[1] = 0x00;
    cmnd_block_ea[2] = (u8)(lba >> 24);
    cmnd_block_ea[3] = (u8)(lba >> 16);
    cmnd_block_ea[4] = (u8)(lba >> 8);
    cmnd_block_ea[5] = (u8)lba;
    cmnd_block_ea[6] = 0x00;
    cmnd_block_ea[7] = 0x00;
    cmnd_block_ea[8] = 0x01; /* 1 logical sector requested */
    cmnd_block_ea[9] = 0x00;
    cmnd_block_ea[10] = 0x00;
    cmnd_block_ea[11] = 0x00;

    volatile u32 *b32 = (volatile u32 *)cmnd_block_ea;
    b32[8]  = 12;         /* +0x20: pktlen = 12 */
    b32[9]  = blocks;     /* +0x24: blocks (2048 for PIO, 1 for DMA) */
    b32[10] = block_size; /* +0x28: block_size (1 for PIO, 2048 for DMA) */
    b32[11] = proto;      /* +0x2C: proto (1=PIO_IN, 3=DMA) */
    b32[12] = 1;          /* +0x30: in_out = 1 (READ) */

    b64[7]  = data_lpar;  /* +0x38: buffer LPAR */

    /* 3. Log PRE record */
    mp = msg;
    append_str(&mp, "pre ");
    append_str(&mp, test_name);
    append_str(&mp, ": lba=");
    format_dec(&mp, lba);
    append_str(&mp, " proto=");
    format_dec(&mp, proto);
    append_str(&mp, " blks=");
    format_dec(&mp, blocks);
    append_str(&mp, " bsz=");
    format_dec(&mp, block_size);
    *mp = '\0';
    HDDLOG(TAG_PRE, cmnd_block_lpar, data_lpar, msg);

    /* 4. Issue HV 248 */
    s64 send_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 2048);
    S->total_hypercalls++;
    *p_send_rc = (s32)send_rc;

    if (send_rc == 0) {
        u64 tag = S->raw_val1;
        s32 poll_res = poll_completion(dev_id, tag, p_status, p_polls, p_ticks);
        if (poll_res != 0) {
            S->timeouts |= timeout_bit;
            S->step_failed = step_id;
            mp = msg;
            append_str(&mp, "timeout: ");
            append_str(&mp, test_name);
            append_str(&mp, " timed out; halting hypercalls");
            *mp = '\0';
            HDDLOG(TAG_TMO, (u64)*p_polls, *p_ticks, msg);
            return 1; /* Timeout */
        }
    } else {
        if (S->step_failed == 0) S->step_failed = step_id;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)send_rc;
    }

    /* 5. Classification and Window Analysis */
    u32 a5 = count_a5(data_ea, 2048);
    *p_a5_cnt = a5;
    u8 cls = classify_sector(data_ea, a5);
    *p_class = cls;

    /* 6. Log POST record */
    mp = msg;
    append_str(&mp, "post ");
    append_str(&mp, test_name);
    append_str(&mp, ": rc=");
    format_dec(&mp, (u32)send_rc);
    append_str(&mp, " async=0x");
    format_hex64(&mp, *p_status);
    append_str(&mp, " cls=");
    append_str(&mp, class_to_str(cls));
    append_str(&mp, " a5=");
    format_dec(&mp, a5);
    append_str(&mp, " polls=");
    format_dec(&mp, *p_polls);
    append_str(&mp, " w0=");
    format_bytes_hex(&mp, data_ea, 16);
    append_str(&mp, " w16=");
    format_bytes_hex(&mp, data_ea + 16, 16);
    append_str(&mp, " vol='");
    format_ascii(&mp, data_ea + 40, 8);
    append_str(&mp, "' wend=");
    format_bytes_hex(&mp, data_ea + 2032, 16);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)send_rc, *p_status, msg);

    /* 7. Request Sense on Error or Check Condition */
    if (send_rc != 0 || (*p_status & 0xFF) == 0x02) {
        do_request_sense(dev_id, cmnd_block_ea, cmnd_block_lpar, data_ea, data_lpar, arena);
        return -1;
    }

    return 0;
}

/* Core probe sequence */
static void run_probe(volatile struct ProbeArena *arena) {
    char msg[256];
    char *mp;

    /* Initialize durable write-ahead HDD logger */
    hddlog_init();

    /* 1. Log Session BOOT Record */
    mp = msg;
    append_str(&mp, "boot: ps2_netemu_p9_U1");
    *mp = '\0';
    HDDLOG(TAG_BOOT, (u64)sizeof(struct ProbeArena), 1ULL, msg);

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
        append_str(&mp, "finish: ps2_netemu_p9_U1 failed step=1");
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

    /* 2. Execute Staged Optical Sequence */
    u64 dev_bus = opt_bus;
    u64 dev_id = opt_dev;

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

    /* Step 2: Allocate DMA Region (LV1 174: size 0x100000, page exponent 20) */
    mp = msg;
    append_str(&mp, "pre dma_alloc: sz=0x100000 pexp=20");
    *mp = '\0';
    HDDLOG(TAG_PRE, 0x100000ULL, 20ULL, msg);

    s64 drc = lv1_hcall(174, dev_bus, dev_id, 0x100000, 20, 0, 0);
    S->total_hypercalls++;
    arena->dma_alloc_rc = (s32)drc;

    if (drc != 0) {
        mp = msg;
        append_str(&mp, "post dma_alloc: rc=");
        format_dec(&mp, (u32)drc);
        *mp = '\0';
        HDDLOG(TAG_POST, (u64)drc, 0ULL, msg);
        S->step_failed = STEP_DMA_ALLOC;
        S->first_err_rc = (u32)drc;
        goto do_close;
    }

    u64 curr_dma_region = S->raw_val1;
    arena->dma_region = curr_dma_region;

    mp = msg;
    append_str(&mp, "post dma_alloc: rc=0 rgn=0x");
    format_hex64(&mp, curr_dma_region);
    *mp = '\0';
    HDDLOG(TAG_POST, 0ULL, curr_dma_region, msg);

    /* Step 3: Map Device DMA Region (LV1 176: lpar, bus, len 0x100000, flags 0xe000000000000800) */
    mp = msg;
    append_str(&mp, "pre map: lpar=0x");
    format_hex64(&mp, cdvd_lpar);
    append_str(&mp, " rgn=0x");
    format_hex64(&mp, curr_dma_region);
    *mp = '\0';
    HDDLOG(TAG_PRE, cdvd_lpar, curr_dma_region, msg);

    s64 mrc = lv1_hcall(176, dev_bus, dev_id, cdvd_lpar, curr_dma_region, 0x100000, 0xe000000000000800ULL);
    S->total_hypercalls++;
    arena->map_rc = (s32)mrc;
    u64 bus_addr = S->raw_val1;
    arena->dma_bus_addr = bus_addr;

    mp = msg;
    append_str(&mp, "post map: rc=");
    format_dec(&mp, (u32)mrc);
    append_str(&mp, " bus_addr=0x");
    format_hex64(&mp, bus_addr);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)mrc, bus_addr, msg);

    if (mrc != 0) {
        S->step_failed = STEP_MAP;
        S->first_err_rc = (u32)mrc;
        goto do_free;
    }

    /* Buffer layout:
     * Command block at offset 0: CPU ea = cdvd_ea, physical LPAR = cdvd_lpar
     * Data buffer at offset 0x1000: CPU ea = cdvd_ea + 0x1000, physical LPAR = cdvd_lpar + 0x1000
     */
    volatile u8 *cmnd_block_ea = (volatile u8 *)cdvd_ea;
    u64 cmnd_block_lpar = cdvd_lpar;
    volatile u8 *data_ea = (volatile u8 *)(cdvd_ea + 0x1000);
    u64 data_lpar = cdvd_lpar + 0x1000;

    /* Step 4: TEST UNIT READY (Opcode 0x00, LV1 248) */
    setup_atapi_block(cmnd_block_ea, 0x00, 0, 0, 0, 0);

    mp = msg;
    append_str(&mp, "pre tur: cmd_lpar=0x");
    format_hex64(&mp, cmnd_block_lpar);
    *mp = '\0';
    HDDLOG(TAG_PRE, cmnd_block_lpar, 0ULL, msg);

    s64 tur_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, 0, 0);
    S->total_hypercalls++;
    arena->tur_send_rc = (s32)tur_rc;
    if (tur_rc == 0) {
        u64 tur_tag = S->raw_val1;
        s32 tur_poll = poll_completion(dev_id, tur_tag, &arena->tur_status, &arena->tur_polls, &arena->tur_tb_ticks);
        if (tur_poll != 0) {
            S->timeouts |= TIMEOUT_TUR;
            S->step_failed = STEP_TUR;
            mp = msg;
            append_str(&mp, "timeout: tur timed out; halting hypercalls");
            *mp = '\0';
            HDDLOG(TAG_TMO, (u64)arena->tur_polls, arena->tur_tb_ticks, msg);
            goto end_log; /* HALT IMMEDIATELY ON TIMEOUT */
        }
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_TUR;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)tur_rc;
    }

    mp = msg;
    append_str(&mp, "post tur: rc=");
    format_dec(&mp, (u32)tur_rc);
    append_str(&mp, " async=0x");
    format_hex64(&mp, arena->tur_status);
    append_str(&mp, " polls=");
    format_dec(&mp, arena->tur_polls);
    append_str(&mp, " ticks=");
    format_hex64(&mp, arena->tur_tb_ticks);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)tur_rc, arena->tur_status, msg);

    /* Step 5: INQUIRY (Opcode 0x12, 36 bytes PIO inbound) */
    setup_atapi_block(cmnd_block_ea, 0x12, 36, 1, 1, data_lpar);
    prefill_buffer(data_ea, 36, 0x00);

    mp = msg;
    append_str(&mp, "pre inq: cmd_lpar=0x");
    format_hex64(&mp, cmnd_block_lpar);
    append_str(&mp, " buf_lpar=0x");
    format_hex64(&mp, data_lpar);
    *mp = '\0';
    HDDLOG(TAG_PRE, cmnd_block_lpar, data_lpar, msg);

    s64 inq_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 36);
    S->total_hypercalls++;
    arena->inq_send_rc = (s32)inq_rc;
    if (inq_rc == 0) {
        u64 inq_tag = S->raw_val1;
        s32 inq_poll = poll_completion(dev_id, inq_tag, &arena->inq_status, &arena->inq_polls, &arena->inq_tb_ticks);
        if (inq_poll != 0) {
            S->timeouts |= TIMEOUT_INQ;
            S->step_failed = STEP_INQ;
            mp = msg;
            append_str(&mp, "timeout: inq timed out; halting hypercalls");
            *mp = '\0';
            HDDLOG(TAG_TMO, (u64)arena->inq_polls, arena->inq_tb_ticks, msg);
            goto end_log; /* HALT IMMEDIATELY ON TIMEOUT */
        }
        for (u32 i = 0; i < 36; i++) {
            arena->inq_data[i] = data_ea[i];
        }
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_INQ;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)inq_rc;
    }

    mp = msg;
    append_str(&mp, "post inq: rc=");
    format_dec(&mp, (u32)inq_rc);
    append_str(&mp, " async=0x");
    format_hex64(&mp, arena->inq_status);
    append_str(&mp, " resp='");
    format_ascii(&mp, data_ea + 8, 16);
    append_str(&mp, "'");
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)inq_rc, arena->inq_status, msg);

    /* Step 6: READ CAPACITY(10) (Opcode 0x25, 8 bytes PIO inbound) */
    setup_atapi_block(cmnd_block_ea, 0x25, 8, 1, 1, data_lpar);
    prefill_buffer(data_ea, 8, 0x00);

    mp = msg;
    append_str(&mp, "pre cap: cmd_lpar=0x");
    format_hex64(&mp, cmnd_block_lpar);
    append_str(&mp, " buf_lpar=0x");
    format_hex64(&mp, data_lpar);
    *mp = '\0';
    HDDLOG(TAG_PRE, cmnd_block_lpar, data_lpar, msg);

    s64 cap_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 8);
    S->total_hypercalls++;
    arena->cap_send_rc = (s32)cap_rc;
    if (cap_rc == 0) {
        u64 cap_tag = S->raw_val1;
        s32 cap_poll = poll_completion(dev_id, cap_tag, &arena->cap_status, &arena->cap_polls, &arena->cap_tb_ticks);
        if (cap_poll != 0) {
            S->timeouts |= TIMEOUT_CAP;
            S->step_failed = STEP_CAP;
            mp = msg;
            append_str(&mp, "timeout: cap timed out; halting hypercalls");
            *mp = '\0';
            HDDLOG(TAG_TMO, (u64)arena->cap_polls, arena->cap_tb_ticks, msg);
            goto end_log; /* HALT IMMEDIATELY ON TIMEOUT */
        }
        arena->cap_max_lba = ((u32)data_ea[0] << 24) | ((u32)data_ea[1] << 16) |
                             ((u32)data_ea[2] << 8)  | (u32)data_ea[3];
        arena->cap_block_size = ((u32)data_ea[4] << 24) | ((u32)data_ea[5] << 16) |
                                ((u32)data_ea[6] << 8)  | (u32)data_ea[7];
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_CAP;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)cap_rc;
    }

    mp = msg;
    append_str(&mp, "post cap: rc=");
    format_dec(&mp, (u32)cap_rc);
    append_str(&mp, " async=0x");
    format_hex64(&mp, arena->cap_status);
    append_str(&mp, " lba=0x");
    format_hex32(&mp, arena->cap_max_lba);
    append_str(&mp, " blk=");
    format_dec(&mp, arena->cap_block_size);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)cap_rc, arena->cap_status, msg);

    /* =========================================================================
     * PART 2: VARIANT U1 PIO SECTOR READ INVESTIGATION
     * ========================================================================= */

    /* Step 7: ATAPI READ(10) of LBA 16 (PVD Sector) - PIO DATA-IN Protocol (proto=1, blocks=2048, bsz=1) */
    int t_r16 = execute_read_test(
        dev_id, 16, 2048, 1, 1, STEP_PIO_16, TIMEOUT_PIO_16, "pio_16",
        cmnd_block_ea, cmnd_block_lpar, data_ea, data_lpar, arena,
        &arena->pio_16_send_rc, &arena->pio_16_status, &arena->pio_16_polls, &arena->pio_16_tb_ticks,
        &arena->pio_16_a5_cnt, &arena->pio_16_class
    );
    if (t_r16 == 1) goto end_log; /* Halt immediately on timeout */

    for (u32 i = 0; i < 32; i++) {
        arena->pio_16_sample[i] = data_ea[i];
    }

    /* Step 8: ATAPI READ(10) of LBA 0 (Lead-in Sector) - PIO DATA-IN Protocol */
    int t_r0 = execute_read_test(
        dev_id, 0, 2048, 1, 1, STEP_PIO_0, TIMEOUT_PIO_0, "pio_0",
        cmnd_block_ea, cmnd_block_lpar, data_ea, data_lpar, arena,
        &arena->pio_0_send_rc, &arena->pio_0_status, &arena->pio_0_polls, &arena->pio_0_tb_ticks,
        &arena->pio_0_a5_cnt, &arena->pio_0_class
    );
    if (t_r0 == 1) goto end_log; /* Halt immediately on timeout */

    /* Step 9: ATAPI READ(10) of LBA 17 (Volume Descriptor Terminator) - PIO DATA-IN Protocol */
    int t_r17 = execute_read_test(
        dev_id, 17, 2048, 1, 1, STEP_PIO_17, TIMEOUT_PIO_17, "pio_17",
        cmnd_block_ea, cmnd_block_lpar, data_ea, data_lpar, arena,
        &arena->pio_17_send_rc, &arena->pio_17_status, &arena->pio_17_polls, &arena->pio_17_tb_ticks,
        &arena->pio_17_a5_cnt, &arena->pio_17_class
    );
    if (t_r17 == 1) goto end_log; /* Halt immediately on timeout */

    /* Step 10: Repeat T1 DMA READ(10) of LBA 16 (proto=3, blocks=1, bsz=2048) for comparison baseline */
    int t_d16 = execute_read_test(
        dev_id, 16, 1, 2048, 3, STEP_DMA_16, TIMEOUT_DMA_16, "dma_16",
        cmnd_block_ea, cmnd_block_lpar, data_ea, data_lpar, arena,
        &arena->dma_16_send_rc, &arena->dma_16_status, &arena->dma_16_polls, &arena->dma_16_tb_ticks,
        &arena->dma_16_a5_cnt, &arena->dma_16_class
    );
    if (t_d16 == 1) goto end_log; /* Halt immediately on timeout */

    /* Step: Unmap Device DMA Region (LV1 177) */
    mp = msg;
    append_str(&mp, "pre unmap: rgn=0x");
    format_hex64(&mp, curr_dma_region);
    append_str(&mp, " len=0x100000");
    *mp = '\0';
    HDDLOG(TAG_PRE, curr_dma_region, 0x100000ULL, msg);

    s64 umrc = lv1_hcall(177, dev_bus, dev_id, curr_dma_region, 0x100000, 0, 0);
    S->total_hypercalls++;
    arena->unmap_rc = (s32)umrc;

    mp = msg;
    append_str(&mp, "post unmap: rc=");
    format_dec(&mp, (u32)umrc);
    *mp = '\0';
    HDDLOG(TAG_POST, (u64)umrc, 0ULL, msg);

do_free:
    /* Step: Free DMA Region (LV1 175) */
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

do_close:
    /* Step: Close Device (LV1 171) */
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
    /* 3. Log Session END Record */
    mp = msg;
    append_str(&mp, "finish: ps2_netemu_p9_U1 ");
    if (S->step_failed == 0) {
        append_str(&mp, "clean success");
        S->first_err_rc = 0;
    } else {
        append_str(&mp, "step failed=");
        format_dec(&mp, S->step_failed);
    }
    *mp = '\0';
    HDDLOG(TAG_END, (u64)S->step_failed, (u64)S->total_hypercalls, msg);
}

/* 79.8 MHz timebase gap: 1.5 seconds = 119,700,000 cycles */
#define TB_GAP_TICKS 119700000ULL

/* Format on-screen menu rows for secondary channel / glance display */
static void format_row(char *dst, u32 r, volatile struct ProbeArena *arena) {
    char *p = dst;

    /* Primary Execution Status */
    if (r == 0) {
        append_str(&p, "P9-U1");
        if (S->step_failed == STEP_PREGUARD_FAILED) {
            append_str(&p, " SANITY REJECT (0 HC)");
        } else if (S->step_failed == 0) {
            append_str(&p, " PIO16: ");
            append_str(&p, class_to_str(arena->pio_16_class));
            if (arena->pio_16_class == CLASS_DATA_OK) {
                append_str(&p, " PVD: ");
                for (u32 i = 1; i <= 5; i++) {
                    char c = (char)arena->pio_16_sample[i];
                    *p++ = (c >= 32 && c <= 126) ? c : '.';
                }
            }
        } else {
            append_str(&p, " FAIL STEP=");
            format_dec(&p, S->step_failed);
            append_str(&p, " RC=");
            format_dec(&p, (u32)S->first_err_rc);
        }
        *p = '\0';
        return;
    }

    if (r == 1) {
        append_str(&p, "HC=");
        format_dec(&p, S->total_hypercalls);
        append_str(&p, " LOG=");
        format_dec(&p, S->log_records_written);
        append_str(&p, " SKIP=");
        format_dec(&p, (u32)S->log_records_skipped);
        append_str(&p, " TMO=0x");
        format_hex32(&p, S->timeouts);
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
        append_str(&p, "PIO: 16_A5=");
        format_dec(&p, arena->pio_16_a5_cnt);
        append_str(&p, " 0_A5=");
        format_dec(&p, arena->pio_0_a5_cnt);
        append_str(&p, " 17_A5=");
        format_dec(&p, arena->pio_17_a5_cnt);
        *p = '\0';
        return;
    }

    if (r == 6) {
        append_str(&p, "DMA16: A5=");
        format_dec(&p, arena->dma_16_a5_cnt);
        append_str(&p, " CLS=");
        append_str(&p, class_to_str(arena->dma_16_class));
        *p = '\0';
        return;
    }

    if (r == 7) {
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
    append_str(&p, "P9-U1 RUNNING");
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
