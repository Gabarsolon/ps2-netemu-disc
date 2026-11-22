/* Freestanding PPC64 BE, compiled for ISA 2.02 (970). No mutable globals.
 * P2 Optical Read Stages Diagnostic Probe (H0..H3):
 *
 * PROBE_VARIANT:
 *   0 => H0: open(4,2,0) -> 174 alloc DMA region -> 175 free DMA region -> close(4,2).
 *   1 => H1: H0 + alloc buffer (0x19a5c) -> 176 map DMA region -> 177 unmap DMA region -> 175 free -> close.
 *   2 => H2: H1 + TUR (opcode 0) + INQUIRY (opcode 0x12, 36 bytes) with bounded poll loop (200k iter / 2s tb);
 *            on timeout abort without unmap/free/close.
 *   3 => H3: H2 + READ CAPACITY (opcode 0x25, 8 bytes) + 245 storage_read for sector 16 with bounded poll loop;
 *            on timeout abort without unmap/free/close.
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

/* Stock buffer allocator shim trampoline: calls 0x19a5c with stock TOC (0x751280) */
extern s64 alloc_buffer(const char *name, u64 size, u64 *p_ea, u64 *p_lpar);

/* Native timebase reader trampoline: branches to stock 0xb9cd0 (mftb r3) */
extern u64 native_clock(void);

/* 192-byte Mailbox at 0x930F20 (struct ProbeState) */
struct ProbeState {
    u32 status;            /* 0..3: bit 0: started, bit 1: done */
    u32 total_devices;     /* 4..7: total devices discovered across all buses */
    u32 rom_count;         /* 8..11: count of type 5 (ROM) devices */
    u32 hdd_found;         /* 12..15: 1 if type 0 (DISK) device found on bus 4 port 2 */
    u32 flags;             /* 16..19: probe flags */
    u32 total_hypercalls;  /* 20..23: count of hypercalls made */
    u32 first_err_rc;      /* 24..27: return code of first failed call */
    u32 step_failed;       /* 28..31: step number that failed (0=none/success) */

    u8  rom_bus_idx;       /* 32: bus index of first ROM device */
    u8  rom_dev_idx;       /* 33: dev index of first ROM device */
    u8  rom_port;          /* 34: port value of first ROM device */
    u8  storage_bus_idx;   /* 35: bus index that has bus_type == 5 */

    u8  hdd_bus_idx;       /* 36: bus index where HDD control was found */
    u8  hdd_dev_idx;       /* 37: dev index */
    u8  hdd_port;          /* 38: port value */
    u8  phat_match;        /* 39: bit 0: emu, bit 1: gxemu */

    s32 stock_rc;          /* 40..43: signed 32-bit rc from stock helper for target node */
    s32 open_rc;           /* 44..47: LV1 170 open rc */
    s32 dma_alloc_rc;      /* 48..51: LV1 174 alloc DMA region rc */
    s32 map_rc;            /* 52..55: LV1 176 map DMA region rc */
    s32 tur_send_rc;       /* 56..59: LV1 248 TUR send rc */
    s32 inq_send_rc;       /* 60..63: LV1 248 INQUIRY send rc */

    u64 rom_bus_id;        /* 64..71: 64-bit bus_id from repository (preserves P1a offset 64) */
    u64 rom_dev_id;        /* 72..79: 64-bit dev_id from repository (preserves P1a offset 72) */

    u64 raw_val1;          /* 80..87: val1 from lv1_hcall epilogue (0x930F70) */
    u64 raw_val2;          /* 88..95: val2 from lv1_hcall epilogue (0x930F78) */

    s32 cap_send_rc;       /* 96..99: LV1 248 READ CAPACITY send rc */
    s32 read_send_rc;      /* 100..103: LV1 245 storage_read send rc */
    s32 unmap_rc;          /* 104..107: LV1 177 unmap DMA region rc */
    s32 free_rc;           /* 108..111: LV1 175 free DMA region rc */
    s32 close_rc;          /* 112..115: LV1 171 close rc */
    s32 alloc_shim_rc;     /* 116..119: 0x19a5c alloc_buffer rc */
    u32 timeouts;          /* 120..123: bit 0: TUR, bit 1: INQ, bit 2: CAP, bit 3: READ */
    u32 rom_region_id;     /* 124..127: region id for ROM device from repo or default */

    u64 buf_lpar;          /* 128..135: buffer LPAR address from 0x19a5c */
    u64 buf_ea;            /* 136..143: buffer CPU effective address from 0x19a5c */
    u64 dma_region;        /* 144..151: DMA region ID from 174 */
    u64 dma_bus_addr;      /* 152..159: DMA bus address from 176 */

    u64 tur_status;        /* 160..167: TUR async completion status */
    u64 inq_status;        /* 168..175: INQUIRY async completion status */
    u64 cap_status;        /* 176..183: READ CAPACITY async completion status */
    u64 read_status;       /* 184..191: READ(10) async completion status */
};

_Static_assert(sizeof(struct ProbeState) == 192, "ProbeState must be exactly 192 bytes");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_bus_id) == 64, "rom_bus_id offset 64");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_dev_id) == 72, "rom_dev_id offset 72");
_Static_assert(__builtin_offsetof(struct ProbeState, raw_val1) == 80, "raw_val1 offset 80");
_Static_assert(__builtin_offsetof(struct ProbeState, raw_val2) == 88, "raw_val2 offset 88");

#define S ((volatile struct ProbeState *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED          (1U << 0)
#define STATUS_DONE             (1U << 1)

#define TIMEOUT_TUR             (1U << 0)
#define TIMEOUT_INQ             (1U << 1)
#define TIMEOUT_CAP             (1U << 2)
#define TIMEOUT_READ            (1U << 3)

#define STEP_NONE               0
#define STEP_OPEN               1
#define STEP_ALLOC_SHIM         2
#define STEP_DMA_ALLOC          3
#define STEP_MAP                4
#define STEP_TUR                5
#define STEP_INQ                6
#define STEP_CAP                7
#define STEP_READ               8
#define STEP_UNMAP              9
#define STEP_FREE               10
#define STEP_CLOSE              11

#define KEY_BUS(b)  (0x6275730000000000ULL | (u64)(b))
#define KEY_DEV(d)  (0x6465760000000000ULL | (u64)(d))
#define KEY_TYPE    0x7479706500000000ULL
#define KEY_ID      0x6964000000000000ULL
#define KEY_PORT    0x706f727400000000ULL
#define KEY_REG0    0x726567696f6e0000ULL

#define STR_STRIDE  64

#if PROBE_VARIANT >= 1
/* Constant string for stock buffer allocator */
static const char str_sb_opt[] = "SB_OPT";
#endif

/* Immutable label string tables linked into extended RO segment */
extern const u8 labels_page_a[];
extern const u8 labels_page_b[];
extern const u8 labels_page_c[];
extern const u8 labels_page_d[];

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
static void setup_atapi_block(volatile u8 *block, u8 opcode, u32 alloc_len, u32 proto, u32 in_out, u64 buf_lpar, u32 buf_len) {
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

    /* 4. Setup buffer pointer at +0x38 and length at +0x40 */
    b64[7]  = buf_lpar;   /* +0x38: buffer LPAR */
    b32[16] = buf_len;    /* +0x40: arglen */
}
#endif

static void run_probe(void) {
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
    S->rom_region_id = 0;

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
                S->stock_rc = (s32)rc;
            }

            if (rc != 0) {
                continue;
            }

            u64 d_type = val1;
            S->total_devices++;

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
                        S->rom_region_id = (u32)val1;
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
    S->open_rc = (s32)orc;
    if (orc != 0) {
        S->step_failed = STEP_OPEN;
        S->first_err_rc = (u32)orc;
        return;
    }

#if PROBE_VARIANT >= 1
    /* Step 2: Allocate Driver Buffer via stock shim 0x19a5c */
    u64 ea = 0;
    u64 lpar = 0;
    s64 arc = alloc_buffer(str_sb_opt, 0x100000, &ea, &lpar);
    S->alloc_shim_rc = (s32)arc;
    S->buf_ea = ea;
    S->buf_lpar = lpar;
    if (arc != 0 || lpar == 0 || ea == 0) {
        S->step_failed = STEP_ALLOC_SHIM;
        S->first_err_rc = (u32)arc;
        /* Close device before returning */
        s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
        S->total_hypercalls++;
        S->close_rc = (s32)crc;
        return;
    }
#endif

    /* Step 3: Allocate Device DMA Region (LV1 174) */
    /* Size 0x80000 (512 KiB), page_exp 12 (4 KiB), flags 0 */
    s64 drc = lv1_hcall(174, dev_bus, dev_id, 0x80000, 12, 0, 0);
    S->total_hypercalls++;
    S->dma_alloc_rc = (s32)drc;
    u64 dma_region = S->raw_val1;
    S->dma_region = dma_region;
    if (drc != 0) {
        S->step_failed = STEP_DMA_ALLOC;
        S->first_err_rc = (u32)drc;
        /* Close device before returning */
        s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
        S->total_hypercalls++;
        S->close_rc = (s32)crc;
        return;
    }

#if PROBE_VARIANT >= 1
    /* Step 4: Map Device DMA Region (LV1 176) */
    /* flags 0xe000000000000800ULL as in stock helper 0x160fc */
    s64 mrc = lv1_hcall(176, dev_bus, dev_id, lpar, dma_region, 0x80000, 0xe000000000000800ULL);
    S->total_hypercalls++;
    S->map_rc = (s32)mrc;
    S->dma_bus_addr = S->raw_val1;
    if (mrc != 0) {
        S->step_failed = STEP_MAP;
        S->first_err_rc = (u32)mrc;
        /* Free DMA region and close */
        s64 frc = lv1_hcall(175, dev_bus, dev_id, dma_region, 0, 0, 0);
        S->total_hypercalls++;
        S->free_rc = (s32)frc;
        s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
        S->total_hypercalls++;
        S->close_rc = (s32)crc;
        return;
    }
#endif

#if PROBE_VARIANT >= 2
    /* Step 5: TEST UNIT READY (Opcode 0x00, LV1 248) */
    volatile u8 *cmnd_block_ea = (volatile u8 *)ea;
    u64 cmnd_block_lpar = lpar;
    u64 data_lpar = lpar + 0x1000;

    setup_atapi_block(cmnd_block_ea, 0x00, 0, 0, 0, 0, 0);
    s64 tur_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, 0, 0);
    S->total_hypercalls++;
    S->tur_send_rc = (s32)tur_rc;
    if (tur_rc == 0) {
        u64 tur_tag = S->raw_val1;
        s32 tur_poll = poll_completion(dev_id, tur_tag, &S->tur_status);
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

    /* Step 6: INQUIRY (Opcode 0x12, 36 bytes inbound, LV1 248) */
    setup_atapi_block(cmnd_block_ea, 0x12, 36, 1, 1, data_lpar, 36);
    s64 inq_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 36);
    S->total_hypercalls++;
    S->inq_send_rc = (s32)inq_rc;
    if (inq_rc == 0) {
        u64 inq_tag = S->raw_val1;
        s32 inq_poll = poll_completion(dev_id, inq_tag, &S->inq_status);
        if (inq_poll != 0) {
            /* TIMEOUT: Abort immediately WITHOUT unmap/free/close! */
            S->timeouts |= TIMEOUT_INQ;
            S->step_failed = STEP_INQ;
            return;
        }
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_INQ;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)inq_rc;
    }
#endif

#if PROBE_VARIANT >= 3
    /* Step 7: READ CAPACITY(10) (Opcode 0x25, 8 bytes inbound, LV1 248) */
    setup_atapi_block(cmnd_block_ea, 0x25, 8, 1, 1, data_lpar, 8);
    s64 cap_rc = lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 8);
    S->total_hypercalls++;
    S->cap_send_rc = (s32)cap_rc;
    if (cap_rc == 0) {
        u64 cap_tag = S->raw_val1;
        s32 cap_poll = poll_completion(dev_id, cap_tag, &S->cap_status);
        if (cap_poll != 0) {
            /* TIMEOUT: Abort immediately WITHOUT unmap/free/close! */
            S->timeouts |= TIMEOUT_CAP;
            S->step_failed = STEP_CAP;
            return;
        }
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_CAP;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)cap_rc;
    }

    /* Step 8: READ Sector 16 (LV1 245 storage_read, 1 sector = 2048 bytes) */
    u64 rom_reg = (u64)S->rom_region_id;
    s64 rd_rc = lv1_hcall(245, dev_id, rom_reg, 16, 1, 0, data_lpar);
    S->total_hypercalls++;
    S->read_send_rc = (s32)rd_rc;
    if (rd_rc == 0) {
        u64 rd_tag = S->raw_val1;
        s32 rd_poll = poll_completion(dev_id, rd_tag, &S->read_status);
        if (rd_poll != 0) {
            /* TIMEOUT: Abort immediately WITHOUT unmap/free/close! */
            S->timeouts |= TIMEOUT_READ;
            S->step_failed = STEP_READ;
            return;
        }
    } else {
        if (S->step_failed == 0) S->step_failed = STEP_READ;
        if (S->first_err_rc == 0) S->first_err_rc = (u32)rd_rc;
    }
#endif

    /* Normal cleanup: ONLY reached when NO timeout occurred */
#if PROBE_VARIANT >= 1
    /* Step 9: Unmap Device DMA Region (LV1 177) */
    s64 umrc = lv1_hcall(177, dev_bus, dev_id, dma_region, 0x80000, 0, 0);
    S->total_hypercalls++;
    S->unmap_rc = (s32)umrc;
    if (umrc != 0 && S->step_failed == 0) {
        S->step_failed = STEP_UNMAP;
        S->first_err_rc = (u32)umrc;
    }
#endif

    /* Step 10: Free Device DMA Region (LV1 175) */
    s64 frc = lv1_hcall(175, dev_bus, dev_id, dma_region, 0, 0, 0);
    S->total_hypercalls++;
    S->free_rc = (s32)frc;
    if (frc != 0 && S->step_failed == 0) {
        S->step_failed = STEP_FREE;
        S->first_err_rc = (u32)frc;
    }

    /* Step 11: Close Device (LV1 171) */
    s64 crc = lv1_hcall(171, dev_bus, dev_id, 0, 0, 0, 0);
    S->total_hypercalls++;
    S->close_rc = (s32)crc;
    if (crc != 0 && S->step_failed == 0) {
        S->step_failed = STEP_CLOSE;
        S->first_err_rc = (u32)crc;
    }
}

__attribute__((always_inline)) static inline u32 map_rc_name_idx(s64 rc, u32 attempted) {
    if (!attempted) return 0;
    s32 s = (s32)rc;
    if (s == 0) return 1;
    if (s == -2) return 2;
    if (s == -3) return 3;
    if (s == -4) return 4;
    if (s == -5) return 5;
    if (s == -6) return 6;
    if (s == -9) return 7;
    if (s == -10) return 8;
    if (s == -11) return 9;
    if (s == -17) return 10;
    return 11; /* HEX */
}

__attribute__((always_inline)) static inline u32 map_page_b_idx(s32 s, u32 attempted) {
    if (!attempted) return 528; /* not attempted */
    u32 u = (u32)s;
    if ((u & 0xFFFFFF00) == 0xFFFFFF00) {
        return u & 0xFF; /* 0..255 (-256..-1) */
    }
    if ((u & 0xFFFFFF00) == 0x00000000) {
        return 256 + (u & 0xFF); /* 256..511 (0..255) */
    }
    u32 hi = (u >> 28) & 0xF;
    return 512 + hi; /* 512..527 */
}

__attribute__((always_inline)) static inline u32 map_page_d_idx(void) {
    u32 r = 0; /* NO ROM */
    if (S->rom_count > 0) {
        if (S->rom_bus_idx == 4 && S->rom_dev_idx == 2 && S->rom_port == 0) r = 1;
        else if (S->rom_bus_idx == 5 && S->rom_dev_idx == 0) r = 2;
        else if (S->rom_bus_idx == 4 && S->rom_dev_idx == 2) r = 3;
        else r = 4;
    }
    u32 h_idx = 0; /* NO HDD */
    if (S->hdd_found) {
        u32 b = S->hdd_bus_idx < 8 ? S->hdd_bus_idx : 8;
        u32 d = S->hdd_dev_idx < 4 ? S->hdd_dev_idx : 4;
        u32 p = S->hdd_port < 4 ? S->hdd_port : 4;
        u32 ph = S->phat_match & 3;
        h_idx = 1 + ((b * 5 + d) * 5 + p) * 4 + ph;
    }
    return r * 901 + h_idx;
}

const u8* s4_menu(u64 selected) {
    if (!(S->status & STATUS_STARTED)) {
        S->status |= STATUS_STARTED;
        run_probe();
        S->status |= STATUS_DONE;
    }
    if (!(S->status & STATUS_DONE)) {
        return STOCK_LABEL;
    }

    u32 page = (u32)(selected & 3);
    switch (page) {
    case 0: {
        /* Page A: P2-H<n> DONE <summary> or P2-H<n> FAIL <step> rc=<name> */
        if (S->timeouts != 0) {
            /* Timeout occurred */
            if (S->timeouts & TIMEOUT_TUR) return labels_page_a + 1 * STR_STRIDE;
            if (S->timeouts & TIMEOUT_INQ) return labels_page_a + 2 * STR_STRIDE;
            if (S->timeouts & TIMEOUT_CAP) return labels_page_a + 3 * STR_STRIDE;
            if (S->timeouts & TIMEOUT_READ) return labels_page_a + 4 * STR_STRIDE;
        }
        if (S->step_failed == 0) {
            return labels_page_a + 0 * STR_STRIDE; /* ALL OK */
        }
        u32 step = S->step_failed;
        if (step > 11) step = 11;
        u32 rc_idx = map_rc_name_idx((s64)(s32)S->first_err_rc, 1);
        u32 idx = 5 + (step - 1) * 12 + rc_idx;
        return labels_page_a + idx * STR_STRIDE;
    }
    case 1: {
        /* Page B: compact hex return codes / failing step RC */
        if (S->step_failed == 0 && S->timeouts == 0) {
            return labels_page_b + 0 * STR_STRIDE; /* ALL SUCCESS */
        }
        u32 idx = map_page_b_idx((s32)S->first_err_rc, 1);
        return labels_page_b + (1 + idx) * STR_STRIDE;
    }
    case 2: {
        /* Page C: Data (INQUIRY text / capacity / sector first bytes / async statuses) */
#if PROBE_VARIANT == 0
        /* H0: DMA region handle */
        u32 rgn = (u32)S->dma_region;
        if (S->dma_alloc_rc != 0) return labels_page_c + 0 * STR_STRIDE; /* ALLOC FAILED */
        if (rgn < 8) return labels_page_c + (1 + rgn) * STR_STRIDE;
        return labels_page_c + 9 * STR_STRIDE; /* RGN >= 8 */

#elif PROBE_VARIANT == 1
        /* H1: Buffer allocation & mapping status */
        if (S->alloc_shim_rc != 0) return labels_page_c + 0 * STR_STRIDE; /* SHIM FAIL */
        if (S->map_rc != 0) return labels_page_c + 1 * STR_STRIDE;        /* MAP FAIL */
        if (S->unmap_rc != 0) return labels_page_c + 2 * STR_STRIDE;      /* UNMAP FAIL */
        return labels_page_c + 3 * STR_STRIDE;                            /* MAP & UNMAP OK */

#elif PROBE_VARIANT == 2
        /* H2: INQUIRY string / TUR & INQ statuses */
        if (S->timeouts & TIMEOUT_TUR) return labels_page_c + 0 * STR_STRIDE;
        if (S->timeouts & TIMEOUT_INQ) return labels_page_c + 1 * STR_STRIDE;
        if (S->tur_status != 0) {
            if ((u32)S->tur_status == 0x02023a00U) return labels_page_c + 2 * STR_STRIDE; /* NOT READY / NO DISC */
            return labels_page_c + 3 * STR_STRIDE; /* TUR ERROR */
        }
        if (S->inq_status != 0) {
            return labels_page_c + 4 * STR_STRIDE; /* INQ STATUS ERROR */
        }
        /* Check INQUIRY string at ea + 0x1000 */
        volatile const u8 *inq = (volatile const u8 *)(S->buf_ea + 0x1000);
        if (inq[8] == 'S' && inq[9] == 'O' && inq[10] == 'N' && inq[11] == 'Y') {
            return labels_page_c + 5 * STR_STRIDE; /* MATCH "SONY PS-SYSTEM 308R" */
        }
        return labels_page_c + 6 * STR_STRIDE; /* OTHER INQ STRING */

#elif PROBE_VARIANT == 3
        /* H3: READ CAPACITY & Sector 16 data */
        if (S->timeouts & TIMEOUT_READ) return labels_page_c + 0 * STR_STRIDE;
        if (S->read_send_rc != 0) return labels_page_c + 1 * STR_STRIDE;
        if (S->read_status != 0) {
            u32 st = (u32)S->read_status;
            if (st == 0x02023a00U) return labels_page_c + 2 * STR_STRIDE; /* NO DISC */
            if (st == 0x02052100U || (st & 0xFFFF) == 0x002FU) return labels_page_c + 3 * STR_STRIDE; /* AUTH REQ / ENXIO */
            return labels_page_c + 4 * STR_STRIDE; /* READ OTHER STATUS */
        }
        /* Check sector 16 first bytes at ea + 0x1000 */
        volatile const u8 *sec = (volatile const u8 *)(S->buf_ea + 0x1000);
        if (sec[0] == 0x01 && sec[1] == 'C' && sec[2] == 'D' && sec[3] == '0' &&
            sec[4] == '0' && sec[5] == '1' && sec[6] == 0x01 && sec[7] == 0x00) {
            return labels_page_c + 5 * STR_STRIDE; /* ISO9660 PVD MATCH! */
        }
        return labels_page_c + 6 * STR_STRIDE; /* READ OK BUT NON-PVD */
#endif
    }
    case 3: {
        /* Page D: scan summary (optical ids, HDD ids) */
        u32 idx = map_page_d_idx();
        return labels_page_d + idx * STR_STRIDE;
    }
    }
    return STOCK_LABEL;
}
