/* Freestanding PPC64 BE, compiled for ISA 2.02 (970). No mutable globals.
 * P1d Hypercall Return Diagnostic Probe:
 * Compile-time switch PROBE_VARIANT:
 *   'A' => issues lv1_open_device(bus_id=9, dev_id=0, flags=0) [invalid bus, expect -17]
 *   'B' => issues lv1_close_device(bus_id=4, dev_id=2) [optical node without open, expect -11]
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef long long s64;
typedef int s32;

#ifndef PROBE_VARIANT
#define PROBE_VARIANT 'A'
#endif

/* Native helper trampoline in code slot: calls stock 0x111eb8 (LV1 91) */
extern s64 repo_read(u64 *out1, u64 *out2, u64 node1, u64 node2, u64 node3, u64 node4);

/* Leaf wrappers in code slot: issue sc 0 with r11=0x800000aa and 0x800000ab
 * Linked into code slot at 0x4820 / 0x4830 */
extern s64 lv1_open_device(u64 bus_id, u64 dev_id, u64 flags);
extern s64 lv1_close_device(u64 bus_id, u64 dev_id);

/* 96-byte Mailbox at 0x930F20 (struct ProbeState) */
struct ProbeState {
    u32 status;            /* 0..3: bit 0: started, bit 1: done, bit 2: open_att, bit 3: open_ok, bit 4: close_att, bit 5: close_ok */
    u32 total_devices;     /* 4..7: total devices discovered across all buses */
    u32 rom_count;         /* 8..11: count of type 5 (ROM) devices */
    u32 hdd_found;         /* 12..15: 1 if type 0 (DISK) device found on bus 4 port 2 */
    u32 flags;             /* 16..19: probe flags */
    u32 total_hypercalls;  /* 20..23: count of LV1 91, 170, 171 calls made */
    u32 first_err_rc;      /* 24..27: return code of first failed LV1 91 call */
    u32 reserved;          /* 28..31: padding / 0 */

    u8 rom_bus_idx;        /* 32: bus index (0..15) of first ROM device */
    u8 rom_dev_idx;        /* 33: dev index (0..15) of first ROM device */
    u8 rom_port;           /* 34: port value of first ROM device (or 0xFF) */
    u8 storage_bus_idx;    /* 35: bus index that has bus_type == 5 (or 0xFF) */

    u8 hdd_bus_idx;        /* 36: bus index where HDD control was found */
    u8 hdd_dev_idx;        /* 37: dev index */
    u8 hdd_port;           /* 38: port value */
    u8 phat_match;         /* 39: bit 0: emu (bus type 5), bit 1: gxemu (bus 4) */

    u32 open_rc_low;       /* 40..43: low 32 bits of open_rc */
    u32 close_rc_low;      /* 44..47: low 32 bits of close_rc */

    u64 hdd_bus_id;        /* 48..55: 64-bit bus_id from repository */
    u64 hdd_dev_id;        /* 56..63: 64-bit dev_id from repository */

    u64 rom_bus_id;        /* 64..71: 64-bit bus_id from repository (preserves P1a offset 64) */
    u64 rom_dev_id;        /* 72..79: 64-bit dev_id from repository (preserves P1a offset 72) */

    s64 open_rc;           /* 80..87: 64-bit raw open rc */
    s64 close_rc;          /* 88..95: 64-bit raw close rc */
};

_Static_assert(sizeof(struct ProbeState) == 96, "ProbeState must be exactly 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_bus_id) == 64, "rom_bus_id offset 64");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_dev_id) == 72, "rom_dev_id offset 72");
_Static_assert(__builtin_offsetof(struct ProbeState, open_rc) == 80, "open_rc offset 80");
_Static_assert(__builtin_offsetof(struct ProbeState, close_rc) == 88, "close_rc offset 88");

#define S ((volatile struct ProbeState *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED          (1U << 0)
#define STATUS_DONE             (1U << 1)
#define STATUS_OPEN_ATTEMPTED   (1U << 2)
#define STATUS_OPEN_OK          (1U << 3)
#define STATUS_CLOSE_ATTEMPTED  (1U << 4)
#define STATUS_CLOSE_OK         (1U << 5)

#define KEY_BUS(b)  (0x6275730000000000ULL | (u64)(b))
#define KEY_DEV(d)  (0x6465760000000000ULL | (u64)(d))
#define KEY_TYPE    0x7479706500000000ULL
#define KEY_ID      0x6964000000000000ULL
#define KEY_PORT    0x706f727400000000ULL

#define STR_STRIDE  64

/* Immutable label string tables linked into extended RO segment */
extern const u8 labels_page_a[];
extern const u8 labels_page_b[];
extern const u8 labels_page_c[];
extern const u8 labels_page_d[];

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

    for (u32 b = 0; b < 16; b++) {
        u64 bus_k = KEY_BUS(b);

        /* Read bus type: bus/b/type */
        val1 = 0; val2 = 0;
        rc = repo_read(&val1, &val2, bus_k, KEY_TYPE, 0, 0);
        S->total_hypercalls++;
        if (rc != 0) {
            if (S->first_err_rc == 0) S->first_err_rc = (u32)rc;
            continue; /* bus doesn't exist */
        }

        u64 b_type = val1;
        if (b_type == 5) {
            S->storage_bus_idx = (u8)b;
        }

        /* Read bus ID: bus/b/id */
        u64 b_id = 0;
        val1 = 0; val2 = 0;
        rc = repo_read(&val1, &val2, bus_k, KEY_ID, 0, 0);
        S->total_hypercalls++;
        if (rc == 0) {
            b_id = val1;
        }

        /* Scan devices 0..15 on this bus */
        for (u32 d = 0; d < 16; d++) {
            u64 dev_k = KEY_DEV(d);

            /* Read device type: bus/b/dev/d/type */
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_TYPE, 0);
            S->total_hypercalls++;
            if (rc != 0) {
                continue;
            }

            u64 d_type = val1;
            S->total_devices++;

            /* Read device ID: bus/b/dev/d/id */
            u64 d_id = 0;
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_ID, 0);
            S->total_hypercalls++;
            if (rc == 0) {
                d_id = val1;
            }

            /* Read device port: bus/b/dev/d/port */
            u32 d_port = 0xFF;
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_PORT, 0);
            S->total_hypercalls++;
            if (rc == 0) {
                d_port = (u32)val1;
            }

            if (d_type == 5) {
                /* ROM (Optical) device found */
                S->rom_count++;
                if (S->rom_count == 1) {
                    S->rom_bus_idx = (u8)b;
                    S->rom_dev_idx = (u8)d;
                    S->rom_port = (u8)d_port;
                    S->rom_bus_id = b_id;
                    S->rom_dev_id = d_id;
                }
                if (b_type == 5) {
                    S->phat_match |= 1;
                }
                if (b == 4) {
                    S->phat_match |= 2;
                }
            } else if (b == 4 && d_type == 0 && d_port == 2) {
                /* HDD control: exactly bus 4, type 0 (DISK), port 2 */
                if (!S->hdd_found) {
                    S->hdd_found = 1;
                    S->hdd_bus_idx = (u8)b;
                    S->hdd_dev_idx = (u8)d;
                    S->hdd_port = (u8)d_port;
                    S->hdd_bus_id = b_id;
                    S->hdd_dev_id = d_id;
                }
            }
        }
    }

#if PROBE_VARIANT == 'A'
    /* Variant A: exactly ONE lv1_open_device(bus_id=9, dev_id=0, flags=0) */
    S->status |= STATUS_OPEN_ATTEMPTED;
    s64 orc = lv1_open_device(9, 0, 0);
    S->total_hypercalls++;
    S->open_rc = orc;
    S->open_rc_low = (u32)orc;
    if (orc == 0) {
        S->status |= STATUS_OPEN_OK;
    }
    S->close_rc = 0;
    S->close_rc_low = 0;
#elif PROBE_VARIANT == 'B'
    /* Variant B: exactly ONE lv1_close_device(bus_id=4, dev_id=2) without opening */
    S->status |= STATUS_CLOSE_ATTEMPTED;
    s64 crc = lv1_close_device(4, 2);
    S->total_hypercalls++;
    S->close_rc = crc;
    S->close_rc_low = (u32)crc;
    if (crc == 0) {
        S->status |= STATUS_CLOSE_OK;
    }
    S->open_rc = 0;
    S->open_rc_low = 0;
#endif
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
    return 11;
}

__attribute__((always_inline)) static inline u32 map_page_b_idx(s64 rc, u32 attempted) {
    if (!attempted) return 528; /* not attempted */
    u32 u = (u32)rc;
    if ((u & 0xFFFFFF00) == 0xFFFFFF00) {
        return u & 0xFF; /* 0..255 */
    }
    if ((u & 0xFFFFFF00) == 0x00000000) {
        return 256 + (u & 0xFF); /* 256..511 */
    }
    u32 hi = (u >> 28) & 0xF;
    return 512 + hi; /* 512..527 */
}

__attribute__((always_inline)) static inline u32 map_page_c_idx(void) {
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

__attribute__((always_inline)) static inline u32 map_rc_idx(s64 rc, u32 attempted) {
    if (!attempted) return 0; /* SKIP or -- */
    s32 s = (s32)rc;
    if (s == 0) return 1;    /* 0(OK) */
    if (s == -2) return 2;   /* -2(SHORT) */
    if (s == -3) return 3;   /* -3(NO_PRIV) */
    if (s == -4) return 4;   /* -4(DENIED) */
    if (s == -5) return 5;   /* -5(ACC_VIOL) */
    if (s == -6) return 6;   /* -6(NO_ENT) */
    if (s == -9) return 7;   /* -9(BUSY) */
    if (s == -10) return 8;  /* -10(EMPTY) */
    if (s == -11) return 9;  /* -11(STATE) */
    if (s == -17) return 10; /* -17(PARAM) */
    return 11;                /* other */
}

__attribute__((always_inline)) static inline u32 map_repo_rc(u32 err) {
    if (err == 0) return 0;
    s64 serr = (s64)(int)err;
    if (serr == -1) return 1;
    if (serr == -6) return 2;
    if (serr == -2) return 3;
    if (serr == -3) return 4;
    if (serr == -4) return 5;
    if (serr == -5) return 6;
    return 7;
}

__attribute__((always_inline)) static inline u32 map_page_d_idx(void) {
    u32 open_att = (S->status & STATUS_OPEN_ATTEMPTED) ? 1 : 0;
    u32 close_att = (S->status & STATUS_CLOSE_ATTEMPTED) ? 1 : 0;
    u32 o_idx = map_rc_idx(S->open_rc, open_att);
    u32 c_idx = map_rc_idx(S->close_rc, close_att);
    u32 r_idx = map_repo_rc(S->first_err_rc);
    return (o_idx * 12 + c_idx) * 8 + r_idx;
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
        /* Page A: P1D-A DONE open(9,0,0) rc=<name> or P1D-B DONE close(4,2) rc=<name> */
#if PROBE_VARIANT == 'A'
        u32 att = (S->status & STATUS_OPEN_ATTEMPTED) ? 1 : 0;
        u32 idx = map_rc_name_idx(S->open_rc, att);
#elif PROBE_VARIANT == 'B'
        u32 att = (S->status & STATUS_CLOSE_ATTEMPTED) ? 1 : 0;
        u32 idx = map_rc_name_idx(S->close_rc, att);
#endif
        return labels_page_a + idx * STR_STRIDE;
    }
    case 1: {
        /* Page B: raw rc as hex (low 32 bits) plus common LV1 code name */
#if PROBE_VARIANT == 'A'
        u32 att = (S->status & STATUS_OPEN_ATTEMPTED) ? 1 : 0;
        u32 idx = map_page_b_idx(S->open_rc, att);
#elif PROBE_VARIANT == 'B'
        u32 att = (S->status & STATUS_CLOSE_ATTEMPTED) ? 1 : 0;
        u32 idx = map_page_b_idx(S->close_rc, att);
#endif
        return labels_page_b + idx * STR_STRIDE;
    }
    case 2: {
        /* Page C: optical node summary + HDD control (type/ids) */
        u32 idx = map_page_c_idx();
        return labels_page_c + idx * STR_STRIDE;
    }
    case 3: {
        /* Page D: scan summary (open rc, close rc, first repository error) */
        u32 idx = map_page_d_idx();
        return labels_page_d + idx * STR_STRIDE;
    }
    }
    return STOCK_LABEL;
}
