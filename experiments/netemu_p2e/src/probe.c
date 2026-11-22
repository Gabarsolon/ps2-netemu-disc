/* Freestanding PPC64 BE, compiled for ISA 2.02 (970). No mutable globals.
 * P2E Optical Read Stages Diagnostic Probe (K0..K3) [Defect Fix for Buffer EA/LPAR Swap]:
 *
 * PROBE_VARIANT:
 *   0 => K0: open(4,2,0) -> 174 alloc DMA region (512 KiB) -> 175 free DMA region -> close(4,2).
 *            Reads & displays SB_CDVD buffer LPAR/EA as baseline.
 *   1 => K1: K0 + verified guard on SB_CDVD -> 176 map DMA region (512 KiB) -> 177 unmap -> 175 free -> close.
 *   2 => K2: K1 + TUR (opcode 0) + INQUIRY (opcode 0x12, 36 bytes) with bounded poll loop (200k iter / 2s tb);
 *            on timeout abort without unmap/free/close.
 *   3 => K3: K2 + READ CAPACITY (opcode 0x25, 8 bytes) + 245 storage_read for sector 16 with bounded poll loop;
 *            on timeout abort without unmap/free/close.
 *
 * SAFETY DISCIPLINE (P2E):
 *   - Mailbox strictly 96 bytes at [0x930F20, 0x930F80). Zero writes to 0x930F80 or above.
 *   - Arena 4096 bytes allocated via native_alloc(4096, 3, 0) and validated against pool descriptors.
 *   - Verified guard on SB_CDVD (LPAR at 0x2458428, EA at 0x2458438, SZ at 0x2458430). Zero reads of 0x930F80.
 *   - All menu string formatting occurs directly inside validated arena (arena->row_strings[9][64]).
 *   - Fail-open: returns STOCK_LABEL if allocator fails.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef long long s64;
typedef int s32;

#ifndef PROBE_VARIANT
#define PROBE_VARIANT 0
#endif

/* Native helper trampoline in code slot: calls stock 0x111eb8 (LV1 91) */
extern s64 repo_read(u64 *out1, u64 *out2, u64 node1, u64 node2, u64 node3, u64 node4);

/* Generic hypercall wrapper modeled on stock helper:
 * Linked into code slot at 0x4800 (sc 0 at 0x4858) */
extern s64 lv1_hcall(u64 num, u64 a1, u64 a2, u64 a3, u64 a4, u64 a5, u64 a6);

/* Native allocator trampoline in code slot: branches to stock 0x0b9848 */
extern u64 native_alloc(u64 size, u64 arg2, u64 arg3);

/* Native timebase reader trampoline: branches to stock 0xb9cd0 (mftb r3) */
extern u64 native_clock(void);

/* 96-byte Mailbox at 0x930F20 (struct ProbeMailbox) */
struct ProbeMailbox {
    u32 status;            /* 0..3: bit 0: started, bit 1: done, bit 2: alloc_ok, bit 3: alloc_failed */
    u32 total_hypercalls;  /* 4..7: count of hypercalls made */
    u32 timeouts;          /* 8..11: bit 0: TUR, bit 1: INQ, bit 2: CAP, bit 3: READ */
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
    u64 pad1;              /* 72..79: padding to offset 80 */

    u64 raw_val1;          /* 80..87: val1 from lv1_hcall epilogue (address 0x930F70) */
    u64 raw_val2;          /* 88..95: val2 from lv1_hcall epilogue (address 0x930F78) */
};

_Static_assert(sizeof(struct ProbeMailbox) == 96, "ProbeMailbox must be exactly 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, open_count) == 20, "open_count offset 20");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, arena_ptr) == 24, "arena_ptr offset 24");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, rom_bus_id) == 48, "rom_bus_id offset 48");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, rom_dev_id) == 56, "rom_dev_id offset 56");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, raw_val1) == 80, "raw_val1 offset 80");
_Static_assert(__builtin_offsetof(struct ProbeMailbox, raw_val2) == 88, "raw_val2 offset 88");

#define S ((volatile struct ProbeMailbox *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED          (1U << 0)
#define STATUS_DONE             (1U << 1)
#define STATUS_ALLOC_OK         (1U << 2)
#define STATUS_ALLOC_FAILED     (1U << 3)

#define TIMEOUT_TUR             (1U << 0)
#define TIMEOUT_INQ             (1U << 1)
#define TIMEOUT_CAP             (1U << 2)
#define TIMEOUT_READ            (1U << 3)

#define STEP_NONE               0
#define STEP_PREGUARD_FAILED    1
#define STEP_OPEN               2
#define STEP_DMA_ALLOC          3
#define STEP_MAP                4
#define STEP_TUR                5
#define STEP_INQ                6
#define STEP_CAP                7
#define STEP_READ               8
#define STEP_UNMAP              9
#define STEP_FREE               10
#define STEP_CLOSE              11

#define ARENA_BYTES 4096U

/* Allocator-backed 4 KiB Arena Structure */
struct ProbeArena {
    s32 stock_rc;          /* 0x000: stock helper rc or pre-guard status */
    s32 open_rc;           /* 0x004: LV1 170 open rc */
    s32 dma_alloc_rc;      /* 0x008: LV1 174 alloc DMA region rc */
    s32 map_rc;            /* 0x00C: LV1 176 map DMA region rc */
    s32 tur_send_rc;       /* 0x010: LV1 248 TUR send rc */
    s32 inq_send_rc;       /* 0x014: LV1 248 INQUIRY send rc */
    s32 cap_send_rc;       /* 0x018: LV1 248 READ CAPACITY send rc */
    s32 read_send_rc;      /* 0x01C: LV1 245 storage_read send rc */
    s32 unmap_rc;          /* 0x020: LV1 177 unmap DMA region rc */
    s32 free_rc;           /* 0x024: LV1 175 free DMA region rc */
    s32 close_rc;          /* 0x028: LV1 171 close rc */
    u32 rom_region_id;     /* 0x02C: region id for ROM device from repo or default */
    u32 total_devices;     /* 0x030: total devices discovered across all buses */
    u32 cap_max_lba;       /* 0x034: READ CAPACITY max LBA */
    u32 cap_block_size;    /* 0x038: READ CAPACITY block size */
    u32 pad0;              /* 0x03C: padding to 8-byte align */

    u64 dma_region;        /* 0x040: DMA region ID from 174 */
    u64 dma_bus_addr;      /* 0x048: DMA bus address from 176 */
    u64 buf_lpar;          /* 0x050: buffer LPAR address from SB_CDVD */
    u64 buf_ea;            /* 0x058: buffer CPU effective address from SB_CDVD */
    u64 buf_sz;            /* 0x060: buffer size from SB_CDVD */

    u64 tur_status;        /* 0x068: TUR async completion status */
    u64 inq_status;        /* 0x070: INQUIRY async completion status */
    u64 cap_status;        /* 0x078: READ CAPACITY async completion status */
    u64 read_status;       /* 0x080: READ(10) async completion status */

    u8 inq_data[64];       /* 0x088..0x0C7: copy of INQUIRY response bytes */
    u8 sector_data[64];    /* 0x0C8..0x107: copy of sector 16 first bytes */

    char row_strings[9][64]; /* 0x108..0x347: 576 bytes dedicated string buffers for rows 0..8 */
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

#define KEY_BUS(b)  (0x6275730000000000ULL | (u64)(b))
#define KEY_DEV(d)  (0x6465760000000000ULL | (u64)(d))
#define KEY_TYPE    0x7479706500000000ULL
#define KEY_ID      0x6964000000000000ULL
#define KEY_PORT    0x706f727400000000ULL
#define KEY_REG0    0x726567696f6e0000ULL

#if PROBE_VARIANT >= 1
/* Verified guard for SB_CDVD buffer source (P2E proven via 0x133cb0 and 0x19900):
 * - Physical LPAR address at 0x2458428 (0x2456fe0 + 0x1448)
 * - Buffer size at 0x2458430 (0x2456fe0 + 0x1450)
 * - CPU EA at 0x2458438 (0x2456fe0 + 0x1458)
 *
 * Runtime Sanity Requirements (symmetric and independent of naming):
 * 1. LPAR must be strictly 32-bit (< 0x1_0000_0000), >= 0x80000000, and 1 MiB aligned.
 * 2. EA must be strictly 64-bit (>= 0x1_0000_0000), match 0x5000_0000_0000 pattern, and != LPAR.
 * 3. Size must be at least 512 KiB (0x80000).
 */
static int check_cdvd_buffer_guard(u64 *p_lpar, u64 *p_ea, u64 *p_sz) {
    u64 raw_lpar = *(const volatile u64 *)0x2458428ULL;
    u64 raw_ea   = *(const volatile u64 *)0x2458438ULL;
    u64 raw_sz   = *(const volatile u64 *)0x2458430ULL;

    /* Always populate outputs with raw values so caller / labels show what was read */
    *p_lpar = raw_lpar;
    *p_ea   = raw_ea;
    *p_sz   = raw_sz;

    /* 1. LPAR must be 32-bit (< 0x1_0000_0000), >= 0x80000000, and 1 MiB aligned (0xFFFFF == 0) */
    if (raw_lpar >= 0x100000000ULL || raw_lpar < 0x80000000ULL || (raw_lpar & 0xFFFFFULL) != 0) {
        return 0;
    }

    /* 2. EA must be >= 0x1_0000_0000, match 0x5000_0000_0000 pattern, and != LPAR */
    if (raw_ea < 0x100000000ULL || (raw_ea & 0xFFFF00000000ULL) != 0x500000000000ULL || raw_ea == raw_lpar) {
        return 0;
    }

    /* 3. Size must be at least 512 KiB (0x80000) */
    if (raw_sz < 0x80000ULL) {
        return 0;
    }

    return 1;
}
#endif

#if PROBE_VARIANT >= 2
/* Bounded polling loop for LV1 254 (storage_check_async_status):
 * Bound 1: 200,000 iterations
 * Bound 2: 160,000,000 timebase ticks (~2.0 seconds at ~79.8 MHz timebase)
 * Returns 0 on completion (status saved in *p_status), 1 on timeout.
 */
static s32 poll_completion(u64 dev, u64 tag, volatile u64 *p_status) {
    u64 start_tb = native_clock();
    for (u32 iter = 0; iter < 200000; iter++) {
        s64 rc = lv1_hcall(254, dev, tag, 0, 0, 0, 0);
        S->total_hypercalls++;
        if (rc == 0) {
            *p_status = S->raw_val1;
            return 0; /* completed */
        }
        u64 now_tb = native_clock();
        if ((u32)(now_tb - start_tb) >= 160000000U) {
            break;
        }
    }
    return 1; /* timeout */
}

/* Helper to setup 64-byte ATAPI command block in buffer */
static void setup_atapi_block(volatile u8 *block, u8 opcode, u32 alloc_len, u32 proto, u32 in_out, u64 buf_lpar) {
    /* 1. Clear 64 bytes of command block */
    volatile u64 *b64 = (volatile u64 *)block;
    for (u32 i = 0; i < 8; i++) {
        b64[i] = 0;
    }

    /* 2. Setup CDB at pkt[0..11] */
    block[0] = opcode;
    if (opcode == 0x12) {
        block[4] = (u8)alloc_len; /* INQUIRY allocation length */
    }

    /* 3. Setup header fields at +0x20..+0x33 */
    volatile u32 *b32 = (volatile u32 *)block;
    b32[8]  = 12;         /* +0x20: pktlen = 12 */
    b32[9]  = alloc_len;  /* +0x24: blocks */
    b32[10] = 1;          /* +0x28: block_size = 1 */
    b32[11] = proto;      /* +0x2C: proto (0=NON_DATA, 1=PIO_IN) */
    b32[12] = in_out;     /* +0x30: in_out (0=WRITE, 1=READ) */

    /* 4. Setup buffer pointer at +0x38 */
    b64[7]  = buf_lpar;   /* +0x38: buffer LPAR */
}
#endif

static void run_probe(void) {
    /* 0. Allocate and validate 4 KiB Arena */
    u64 a = native_alloc(ARENA_BYTES, 3, 0);
    if (!arena_rw(a)) {
        S->status |= STATUS_ALLOC_FAILED;
        return; /* FAIL-OPEN: do nothing, do not issue any hypercalls! */
    }
    S->arena_ptr = a;
    S->status |= STATUS_ALLOC_OK;
    volatile struct ProbeArena *arena = (volatile struct ProbeArena *)a;

    /* Clear arena */
    volatile u64 *p64 = (volatile u64 *)a;
    for (u32 i = 0; i < sizeof(struct ProbeArena) / 8; i++) {
        p64[i] = 0;
    }

    u64 val1 = 0;
    u64 val2 = 0;
    s64 rc = 0;

    S->storage_bus_idx = 0xFF;
    S->rom_bus_idx = 0xFF;
    S->rom_dev_idx = 0xFF;
    S->rom_port = 0xFF;
    S->hdd_bus_idx = 0xFF;
    S->hdd_dev_idx = 0xFF;
    S->hdd_port = 0xFF;
    arena->rom_region_id = 0;

#if PROBE_VARIANT >= 1
    /* Read SB_CDVD buffer descriptors */
    u64 cdvd_lpar = 0;
    u64 cdvd_ea = 0;
    u64 cdvd_sz = 0;

    /* In K1..K3: verified guard check on SB_CDVD before any hypercalls */
    if (!check_cdvd_buffer_guard(&cdvd_lpar, &cdvd_ea, &cdvd_sz)) {
        arena->buf_lpar = cdvd_lpar;
        arena->buf_ea   = cdvd_ea;
        arena->buf_sz   = cdvd_sz;
        S->step_failed = STEP_PREGUARD_FAILED;
        S->first_err_rc = -2; /* RESOURCE_SHORTAGE */
        arena->stock_rc = -2;
        return; /* Abort cleanly without issuing any hypercalls */
    }
    arena->buf_lpar = cdvd_lpar;
    arena->buf_ea   = cdvd_ea;
    arena->buf_sz   = cdvd_sz;
#else
    /* In K0: read for display without guard check */
    arena->buf_lpar = *(const volatile u64 *)0x2458428ULL;
    arena->buf_ea   = *(const volatile u64 *)0x2458438ULL;
    arena->buf_sz   = *(const volatile u64 *)0x2458430ULL;
#endif

    /* 1. Repository scan via stock helper (repo_read -> 0x111eb8) */
    for (u32 b = 0; b < 16; b++) {
        u64 bus_k = KEY_BUS(b);

        val1 = 0; val2 = 0;
        rc = repo_read(&val1, &val2, bus_k, KEY_TYPE, 0, 0);
        S->total_hypercalls++;
        if (rc != 0) {
            if (S->first_err_rc == 0) S->first_err_rc = (u32)rc;
            continue;
        }

        u64 b_type = val1;
        if (b_type == 5) {
            S->storage_bus_idx = (u8)b;
        }

        u64 b_id = 0;
        val1 = 0; val2 = 0;
        rc = repo_read(&val1, &val2, bus_k, KEY_ID, 0, 0);
        S->total_hypercalls++;
        if (rc == 0) {
            b_id = val1;
        }

        for (u32 d = 0; d < 16; d++) {
            u64 dev_k = KEY_DEV(d);

            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_TYPE, 0);
            S->total_hypercalls++;

            if (b == 4 && d == 2) {
                arena->stock_rc = (s32)rc;
            }

            if (rc != 0) {
                continue;
            }

            u64 d_type = val1;
            arena->total_devices++;

            u64 d_id = 0;
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_ID, 0);
            S->total_hypercalls++;
            if (rc == 0) {
                d_id = val1;
            }

            u32 d_port = 0xFF;
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_PORT, 0);
            S->total_hypercalls++;
            if (rc == 0) {
                d_port = (u32)val1;
            }

            if (d_type == 5) {
                /* ROM device found */
                S->rom_count++;
                if (S->rom_count == 1) {
                    S->rom_bus_idx = (u8)b;
                    S->rom_dev_idx = (u8)d;
                    S->rom_port = (u8)d_port;
                    S->rom_bus_id = b_id;
                    S->rom_dev_id = d_id;

                    /* Query region 0 ID: bus/b/dev/d/region/0/id */
                    val1 = 0; val2 = 0;
                    s64 reg_rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_REG0, KEY_ID);
                    S->total_hypercalls++;
                    if (reg_rc == 0) {
                        arena->rom_region_id = (u32)val1;
                    }
                }
                if (b_type == 5) {
                    S->phat_match |= 1;
                }
                if (b == 4) {
                    S->phat_match |= 2;
                }
            } else if (b == 4 && d_type == 0 && d_port == 2) {
                /* HDD control */
                if (!S->hdd_found) {
                    S->hdd_found = 1;
                    S->hdd_bus_idx = (u8)b;
                    S->hdd_dev_idx = (u8)d;
                    S->hdd_port = (u8)d_port;
                }
            }
        }
    }

    /* 2. Execute Staged Optical Sequence */
    u64 dev_bus = 4;
    u64 dev_id = 2;

    /* Step 1: Open Device (LV1 170) */
    s64 orc = lv1_hcall(170, dev_bus, dev_id, 0, 0, 0, 0);
    S->total_hypercalls++;
    arena->open_rc = (s32)orc;
    if (orc != 0) {
        S->step_failed = STEP_OPEN;
        S->first_err_rc = (u32)orc;
        return;
    }

    /* Step 2: Allocate Device DMA Region (LV1 174) */
    /* Size 0x80000 (512 KiB), page_exp 12 (4 KiB), flags 0 */
    s64 drc = lv1_hcall(174, dev_bus, dev_id, 0x80000, 12, 0, 0);
    S->total_hypercalls++;
    arena->dma_alloc_rc = (s32)drc;
    u64 dma_region = S->raw_val1;
    arena->dma_region = dma_region;
    if (drc != 0) {
        S->step_failed = STEP_DMA_ALLOC;
        S->first_err_rc = (u32)drc;
        /* Close device before returning */
        s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
        S->total_hypercalls++;
        arena->close_rc = (s32)crc;
        return;
    }

#if PROBE_VARIANT >= 1
    /* Step 3: Map Device DMA Region (LV1 176) using SB_CDVD buffer */
    /* flags 0xe000000000000800ULL as in stock helper 0x160fc */
    s64 mrc = lv1_hcall(176, dev_bus, dev_id, cdvd_lpar, dma_region, 0x80000, 0xe000000000000800ULL);
    S->total_hypercalls++;
    arena->map_rc = (s32)mrc;
    arena->dma_bus_addr = S->raw_val1;
    if (mrc != 0) {
        S->step_failed = STEP_MAP;
        S->first_err_rc = (u32)mrc;
        /* Free DMA region and close */
        s64 frc = lv1_hcall(175, dev_bus, dev_id, dma_region, 0, 0, 0);
        S->total_hypercalls++;
        arena->free_rc = (s32)frc;
        s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
        S->total_hypercalls++;
        arena->close_rc = (s32)crc;
        return;
    }
#endif

#if PROBE_VARIANT >= 2
    /* Step 4: TEST UNIT READY (Opcode 0x00, LV1 248) */
    volatile u8 *cmnd_block_ea = (volatile u8 *)cdvd_ea;
    u64 cmnd_block_lpar = cdvd_lpar;
    u64 data_lpar = cdvd_lpar + 0x1000;
    volatile u8 *data_ea = (volatile u8 *)(cdvd_ea + 0x1000);

    setup_atapi_block(cmnd_block_ea, 0x00, 0, 0, 0, 0);
    s64 tur_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, 0, 0);
    S->total_hypercalls++;
    arena->tur_send_rc = (s32)tur_rc;
    if (tur_rc == 0) {
        u64 tur_tag = S->raw_val1;
        s32 tur_poll = poll_completion(dev_id, tur_tag, &arena->tur_status);
        if (tur_poll != 0) {
            /* TIMEOUT: Abort immediately WITHOUT unmap/free/close! */
            S->timeouts |= TIMEOUT_TUR;
            S->step_failed = STEP_TUR;
            return;
        }
    } else {
        S->step_failed = STEP_TUR;
        S->first_err_rc = (u32)tur_rc;
    }

    /* Step 5: INQUIRY (Opcode 0x12, 36 bytes inbound, LV1 248) */
    setup_atapi_block(cmnd_block_ea, 0x12, 36, 1, 1, data_lpar);
    s64 inq_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 36);
    S->total_hypercalls++;
    arena->inq_send_rc = (s32)inq_rc;
    if (inq_rc == 0) {
        u64 inq_tag = S->raw_val1;
        s32 inq_poll = poll_completion(dev_id, inq_tag, &arena->inq_status);
        if (inq_poll != 0) {
            /* TIMEOUT: Abort immediately WITHOUT unmap/free/close! */
            S->timeouts |= TIMEOUT_INQ;
            S->step_failed = STEP_INQ;
            return;
        }
        /* Copy INQUIRY response bytes into arena */
        for (u32 i = 0; i < 36; i++) {
            arena->inq_data[i] = data_ea[i];
        }
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_INQ;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)inq_rc;
    }
#endif

#if PROBE_VARIANT >= 3
    /* Step 6: READ CAPACITY(10) (Opcode 0x25, 8 bytes inbound, LV1 248) */
    setup_atapi_block(cmnd_block_ea, 0x25, 8, 1, 1, data_lpar);
    s64 cap_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 8);
    S->total_hypercalls++;
    arena->cap_send_rc = (s32)cap_rc;
    if (cap_rc == 0) {
        u64 cap_tag = S->raw_val1;
        s32 cap_poll = poll_completion(dev_id, cap_tag, &arena->cap_status);
        if (cap_poll != 0) {
            /* TIMEOUT: Abort immediately WITHOUT unmap/free/close! */
            S->timeouts |= TIMEOUT_CAP;
            S->step_failed = STEP_CAP;
            return;
        }
        /* Extract Max LBA and Block Size (Big Endian) */
        arena->cap_max_lba = ((u32)data_ea[0] << 24) | ((u32)data_ea[1] << 16) |
                             ((u32)data_ea[2] << 8)  | (u32)data_ea[3];
        arena->cap_block_size = ((u32)data_ea[4] << 24) | ((u32)data_ea[5] << 16) |
                               ((u32)data_ea[6] << 8)  | (u32)data_ea[7];
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_CAP;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)cap_rc;
    }

    /* Step 7: READ Sector 16 (LV1 245 storage_read, 1 sector = 2048 bytes) */
    u64 rom_reg = (u64)arena->rom_region_id;
    s64 rd_rc = lv1_hcall(245, dev_id, rom_reg, 16, 1, 0, data_lpar);
    S->total_hypercalls++;
    arena->read_send_rc = (s32)rd_rc;
    if (rd_rc == 0) {
        u64 rd_tag = S->raw_val1;
        s32 rd_poll = poll_completion(dev_id, rd_tag, &arena->read_status);
        if (rd_poll != 0) {
            /* TIMEOUT: Abort immediately WITHOUT unmap/free/close! */
            S->timeouts |= TIMEOUT_READ;
            S->step_failed = STEP_READ;
            return;
        }
        /* Copy sector 16 first bytes into arena */
        for (u32 i = 0; i < 32; i++) {
            arena->sector_data[i] = data_ea[i];
        }
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_READ;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)rd_rc;
    }
#endif

    /* Normal cleanup: ONLY reached when NO timeout occurred */
#if PROBE_VARIANT >= 1
    /* Step 8: Unmap Device DMA Region (LV1 177) */
    s64 umrc = lv1_hcall(177, dev_bus, dev_id, dma_region, 0x80000, 0, 0);
    S->total_hypercalls++;
    arena->unmap_rc = (s32)umrc;
    if (umrc != 0 && S->step_failed == 0) {
        S->step_failed = STEP_UNMAP;
        S->first_err_rc = (u32)umrc;
    }
#endif

    /* Step 9: Free Device DMA Region (LV1 175) */
    s64 frc = lv1_hcall(175, dev_bus, dev_id, dma_region, 0, 0, 0);
    S->total_hypercalls++;
    arena->free_rc = (s32)frc;
    if (frc != 0 && S->step_failed == 0) {
        S->step_failed = STEP_FREE;
        S->first_err_rc = (u32)frc;
    }

    /* Step 10: Close Device (LV1 171) */
    s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
    S->total_hypercalls++;
    arena->close_rc = (s32)crc;
    if (crc != 0 && S->step_failed == 0) {
        S->step_failed = STEP_CLOSE;
        S->first_err_rc = (u32)crc;
    }
}

/* Fast in-arena string formatting routines */
static __attribute__((always_inline)) inline char *fmt_str(char *p, const char *s) {
    while (*s) *p++ = *s++;
    return p;
}

static __attribute__((always_inline)) inline char *fmt_hex(char *p, u64 val, int nibbles) {
    const char hex[] = "0123456789abcdef";
    for (int i = (nibbles - 1) * 4; i >= 0; i -= 4) {
        *p++ = hex[(val >> i) & 0xF];
    }
    return p;
}

static __attribute__((always_inline)) inline char *fmt_dec(char *p, s32 val) {
    if (val < 0) {
        *p++ = '-';
        val = -val;
    }
    if (val == 0) {
        *p++ = '0';
        return p;
    }
    char buf[12];
    int pos = 0;
    while (val > 0) {
        buf[pos++] = '0' + (val % 10);
        val /= 10;
    }
    for (int i = pos - 1; i >= 0; i--) {
        *p++ = buf[i];
    }
    return p;
}

#define PUT_STR(s)    do { p = fmt_str(p, (s)); } while(0)
#define PUT_HEX(v, n) do { p = fmt_hex(p, (v), (n)); } while(0)
#define PUT_DEC(v)    do { p = fmt_dec(p, (v)); } while(0)

/* Format individual menu row (0..8) into destination buffer */
static void format_row(char *dst, u32 row, u32 open_count, volatile struct ProbeArena *arena) {
    char *p = dst;
    u32 page = open_count % 3;

    if (page == 0) {
        /* Primary Diagnostic Status Screen (9 rows visible at once) */
        switch (row) {
        case 0: {
            /* Row 0: Overall Summary */
            PUT_STR("P2E-K");
            PUT_DEC(PROBE_VARIANT);
            if (S->timeouts != 0) {
                PUT_STR(" TIMEOUT AT STEP=");
                PUT_DEC(S->step_failed);
                PUT_STR(" (ABORTED)");
            } else if (S->step_failed == STEP_PREGUARD_FAILED) {
                PUT_STR(" SANITY REJECT (0 HC)");
            } else if (S->step_failed == 0) {
                PUT_STR(" DONE: ALL STEPS OK");
            } else {
                PUT_STR(" FAIL: STEP=");
                PUT_DEC(S->step_failed);
                PUT_STR(" RC=");
                PUT_DEC(S->first_err_rc);
            }
            break;
        }
        case 1: {
            /* Row 1: Return Codes */
            PUT_STR("RC: OP=");
            PUT_DEC(arena->open_rc);
            PUT_STR(" DMA=");
            PUT_DEC(arena->dma_alloc_rc);
#if PROBE_VARIANT >= 1
            PUT_STR(" MAP=");
            PUT_DEC(arena->map_rc);
#endif
            PUT_STR(" CL=");
            PUT_DEC(arena->close_rc);
            PUT_STR(" HC=");
            PUT_DEC(S->total_hypercalls);
            break;
        }
        case 2: {
            /* Row 2: Buffer LPAR */
            PUT_STR("CDVD LPAR: 0x");
            PUT_HEX(arena->buf_lpar, 16);
            break;
        }
        case 3: {
            /* Row 3: Buffer EA */
            PUT_STR("CDVD EA:   0x");
            PUT_HEX(arena->buf_ea, 16);
            PUT_STR(" SZ=");
            PUT_HEX(arena->buf_sz, 6);
            break;
        }
        case 4: {
            /* Row 4: DMA Region & Bus Address */
            PUT_STR("DMA RGN=0x");
            PUT_HEX(arena->dma_region, 8);
#if PROBE_VARIANT >= 1
            PUT_STR(" BUS=0x");
            PUT_HEX(arena->dma_bus_addr, 8);
#endif
            break;
        }
        case 5: {
            /* Row 5: TUR Status */
#if PROBE_VARIANT < 2
            PUT_STR("TUR: NOT RUN IN K");
            PUT_DEC(PROBE_VARIANT);
#else
            PUT_STR("TUR RC=");
            PUT_DEC(arena->tur_send_rc);
            PUT_STR(" STAT=0x");
            PUT_HEX(arena->tur_status, 8);
            if (arena->tur_status == 0) PUT_STR(" (READY)");
            else if ((u32)arena->tur_status == 0x02023a00U) PUT_STR(" (NO DISC)");
            else PUT_STR(" (ERR)");
#endif
            break;
        }
        case 6: {
            /* Row 6: INQUIRY Data */
#if PROBE_VARIANT < 2
            PUT_STR("INQ: NOT RUN IN K");
            PUT_DEC(PROBE_VARIANT);
#else
            PUT_STR("INQ RC=");
            PUT_DEC(arena->inq_send_rc);
            PUT_STR(": \"");
            /* Print up to 24 printable chars of inquiry vendor/model */
            for (u32 i = 8; i < 32; i++) {
                char c = (char)arena->inq_data[i];
                if (c >= 32 && c <= 126) *p++ = c;
                else *p++ = ' ';
            }
            PUT_STR("\"");
#endif
            break;
        }
        case 7: {
            /* Row 7: READ CAPACITY */
#if PROBE_VARIANT < 3
            PUT_STR("CAP: NOT RUN IN K");
            PUT_DEC(PROBE_VARIANT);
#else
            PUT_STR("CAP RC=");
            PUT_DEC(arena->cap_send_rc);
            PUT_STR(" LBA=0x");
            PUT_HEX(arena->cap_max_lba, 8);
            PUT_STR(" BLK=");
            PUT_DEC(arena->cap_block_size);
#endif
            break;
        }
        case 8: {
            /* Row 8: READ Sector 16 / ISO PVD */
#if PROBE_VARIANT < 3
            PUT_STR("LBA16: NOT RUN IN K");
            PUT_DEC(PROBE_VARIANT);
#else
            PUT_STR("LBA16 RC=");
            PUT_DEC(arena->read_send_rc);
            if (arena->sector_data[1] == 'C' && arena->sector_data[2] == 'D' &&
                arena->sector_data[3] == '0' && arena->sector_data[4] == '0' && arena->sector_data[5] == '1') {
                PUT_STR(" ISO PVD \"CD001\" MATCH!");
            } else {
                PUT_STR(" [");
                PUT_HEX(arena->sector_data[0], 2);
                PUT_HEX(arena->sector_data[1], 2);
                PUT_HEX(arena->sector_data[2], 2);
                PUT_HEX(arena->sector_data[3], 2);
                PUT_STR("]");
            }
#endif
            break;
        }
        }
    } else if (page == 1) {
        /* Page 1: Async Status & Cleanup Counters */
        switch (row) {
        case 0: PUT_STR("P2E-K"); PUT_DEC(PROBE_VARIANT); PUT_STR(" - GROUP 1: ASYNC STATUS"); break;
        case 1: PUT_STR("TUR ASYNC STAT:  0x"); PUT_HEX(arena->tur_status, 16); break;
        case 2: PUT_STR("INQ ASYNC STAT:  0x"); PUT_HEX(arena->inq_status, 16); break;
        case 3: PUT_STR("CAP ASYNC STAT:  0x"); PUT_HEX(arena->cap_status, 16); break;
        case 4: PUT_STR("READ ASYNC STAT: 0x"); PUT_HEX(arena->read_status, 16); break;
        case 5: {
            PUT_STR("UNMAP="); PUT_DEC(arena->unmap_rc);
            PUT_STR(" REL="); PUT_DEC(arena->free_rc);
            PUT_STR(" CLS="); PUT_DEC(arena->close_rc);
            break;
        }
        case 6: {
            PUT_STR("TOTAL HC: "); PUT_DEC(S->total_hypercalls);
            PUT_STR(" TIMEOUTS: 0x"); PUT_HEX(S->timeouts, 2);
            break;
        }
        case 7: {
            PUT_STR("ROM BUS "); PUT_DEC(S->rom_bus_idx);
            PUT_STR(" DEV "); PUT_DEC(S->rom_dev_idx);
            PUT_STR(" REG "); PUT_DEC(arena->rom_region_id);
            break;
        }
        case 8: {
            PUT_STR("P2E DIAG OK HC="); PUT_DEC(S->total_hypercalls);
            PUT_STR(" OPENS="); PUT_HEX(open_count, 4);
            break;
        }
        }
    } else {
        /* Page 2: Raw Hex Bytes of Inquiry & Sector 16 */
        switch (row) {
        case 0: PUT_STR("P2E-K"); PUT_DEC(PROBE_VARIANT); PUT_STR(" - GROUP 2: RAW HEX DATA"); break;
        case 1: {
            PUT_STR("INQ[00..07]: ");
            for (int i = 0; i < 8; i++) { PUT_HEX(arena->inq_data[i], 2); *p++ = ' '; }
            break;
        }
        case 2: {
            PUT_STR("INQ[08..15]: ");
            for (int i = 8; i < 16; i++) { PUT_HEX(arena->inq_data[i], 2); *p++ = ' '; }
            break;
        }
        case 3: {
            PUT_STR("INQ[16..23]: ");
            for (int i = 16; i < 24; i++) { PUT_HEX(arena->inq_data[i], 2); *p++ = ' '; }
            break;
        }
        case 4: {
            PUT_STR("INQ[24..31]: ");
            for (int i = 24; i < 32; i++) { PUT_HEX(arena->inq_data[i], 2); *p++ = ' '; }
            break;
        }
        case 5: {
            PUT_STR("LBA16[00..07]: ");
            for (int i = 0; i < 8; i++) { PUT_HEX(arena->sector_data[i], 2); *p++ = ' '; }
            break;
        }
        case 6: {
            PUT_STR("LBA16[08..15]: ");
            for (int i = 8; i < 16; i++) { PUT_HEX(arena->sector_data[i], 2); *p++ = ' '; }
            break;
        }
        case 7: {
            PUT_STR("LBA16[16..23]: ");
            for (int i = 16; i < 24; i++) { PUT_HEX(arena->sector_data[i], 2); *p++ = ' '; }
            break;
        }
        case 8: {
            PUT_STR("LBA16[24..31]: ");
            for (int i = 24; i < 32; i++) { PUT_HEX(arena->sector_data[i], 2); *p++ = ' '; }
            break;
        }
        }
    }

    *p = '\0';
}

/* 79.8 MHz timebase gap: 1.5 seconds = 119,700,000 cycles */
#define TB_GAP_TICKS 119700000ULL

/* Menu hook called from 0x270FFC (trampoline at 0x4960) */
const u8* s4_menu(u64 selected) {
    if (!(S->status & STATUS_STARTED)) {
        S->status |= STATUS_STARTED;
        run_probe();
        S->status |= STATUS_DONE;
    }
    if (!(S->status & STATUS_DONE)) {
        return STOCK_LABEL;
    }

    volatile struct ProbeArena *arena = get_arena();
    if (!arena) {
        return STOCK_LABEL; /* Fail-open if arena is invalid */
    }

    /* Timebase gap detection for menu open cycles */
    u64 now = native_clock();
    u64 last = S->last_eval_tb;
    if (last != 0 && now > last && (now - last) > TB_GAP_TICKS) {
        S->open_count++;
    }
    S->last_eval_tb = now;

    /* Row index r clamped to 0..8 */
    u32 r = (u32)(selected > 8 ? 8 : selected);

    char *dst = (char *)arena->row_strings[r];
    format_row(dst, r, S->open_count, arena);

    return (const u8 *)dst;
}
