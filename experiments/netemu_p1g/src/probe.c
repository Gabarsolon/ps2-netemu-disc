/* Freestanding PPC64 BE, compiled for ISA 2.02 (970). No mutable globals.
 * P1g Generic Hypercall Wrapper Diagnostic Probe:
 *
 * PROBE_VARIANT:
 *   0 => G0: lv1_hcall(0x5b, 1, 0x62757304, KEY_DEV(2), KEY_TYPE, 0)
 *            (optical node repository read through new wrapper; validates wrapper vs stock helper)
 *   1 => G1: lv1_hcall(170, 9, 0, 0, 0, 0)
 *            (open_device with invalid bus 9; expect -17 INVALID_PARAMETER)
 *   2 => G2: lv1_hcall(171, 4, 2, 0, 0, 0)
 *            (close_device on optical node without opening; expect -11 NOT_OWNER)
 *   3 => G3: lv1_hcall(170, 4, 2, 0, 0, 0)
 *            (REAL open of optical node, flags 0; if rc==0 close immediately with 171)
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
extern s64 lv1_hcall(u64 num, u64 a1, u64 a2, u64 a3, u64 a4, u64 a5);

/* 96-byte Mailbox at 0x930F20 (struct ProbeState) */
struct ProbeState {
    u32 status;            /* 0..3: bit 0: started, bit 1: done, bit 2: raw_att, bit 3: raw_ok, bit 4: close_att, bit 5: close_ok */
    u32 total_devices;     /* 4..7: total devices discovered across all buses */
    u32 rom_count;         /* 8..11: count of type 5 (ROM) devices */
    u32 hdd_found;         /* 12..15: 1 if type 0 (DISK) device found on bus 4 port 2 */
    u32 flags;             /* 16..19: probe flags */
    u32 total_hypercalls;  /* 20..23: count of hypercalls made */
    u32 first_err_rc;      /* 24..27: return code of first failed LV1 91 call */
    u32 match_status;      /* 28..31: 0: not run, 1: MATCH, 2: DIFF (used in G0) */

    u8 rom_bus_idx;        /* 32: bus index (0..15) of first ROM device */
    u8 rom_dev_idx;        /* 33: dev index (0..15) of first ROM device */
    u8 rom_port;           /* 34: port value of first ROM device (or 0xFF) */
    u8 storage_bus_idx;    /* 35: bus index that has bus_type == 5 (or 0xFF) */

    u8 hdd_bus_idx;        /* 36: bus index where HDD control was found */
    u8 hdd_dev_idx;        /* 37: dev index */
    u8 hdd_port;           /* 38: port value */
    u8 phat_match;         /* 39: bit 0: emu (bus type 5), bit 1: gxemu (bus 4) */

    s32 stock_rc;          /* 40..43: signed 32-bit rc from stock helper for target node */
    s32 raw_rc;            /* 44..47: primary hypercall return code (G0 clone rc, G1/G3 open rc, G2 close rc) */
    s32 close_rc;          /* 48..51: secondary close hypercall return code (used in G3) */
    u32 reserved;          /* 52..55: padding / reserved */

    u64 stock_val1;        /* 56..63: val1 from stock helper (expected: 5) */
    u64 rom_bus_id;        /* 64..71: 64-bit bus_id from repository (preserves P1a offset 64) */
    u64 rom_dev_id;        /* 72..79: 64-bit dev_id from repository (preserves P1a offset 72) */

    u64 raw_val1;          /* 80..87: val1 from lv1_hcall epilogue (0x930F70) */
    u64 raw_val2;          /* 88..95: val2 from lv1_hcall epilogue (0x930F78) */
};

_Static_assert(sizeof(struct ProbeState) == 96, "ProbeState must be exactly 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_bus_id) == 64, "rom_bus_id offset 64");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_dev_id) == 72, "rom_dev_id offset 72");
_Static_assert(__builtin_offsetof(struct ProbeState, raw_val1) == 80, "raw_val1 offset 80");
_Static_assert(__builtin_offsetof(struct ProbeState, raw_val2) == 88, "raw_val2 offset 88");

#define S ((volatile struct ProbeState *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED          (1U << 0)
#define STATUS_DONE             (1U << 1)
#define STATUS_RAW_ATTEMPTED    (1U << 2)
#define STATUS_RAW_OK           (1U << 3)
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

    /* 1. Repository scan via stock helper (repo_read -> 0x111eb8) */
    for (u32 b = 0; b < 16; b++) {
        u64 bus_k = KEY_BUS(b);

        /* Read bus type: bus/b/type */
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

            /* Record stock helper result for the target test node (bus 4 dev 2 type) */
            if (b == 4 && d == 2) {
                S->stock_rc = (s32)rc;
                S->stock_val1 = val1;
            }

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
                }
            }
        }
    }

    /* 2. Execute variant hypercall(s) through generic wrapper lv1_hcall */
#if PROBE_VARIANT == 0
    /* G0: LV1 91 (repository read) through NEW generic wrapper lv1_hcall.
     * Arguments: num=0x5b, a1=1 (lpar id), a2=0x62757304 (folded bus 4),
     *            a3=KEY_DEV(2), a4=KEY_TYPE, a5=0.
     * Returns rc in r3; stores returned r4 and r5 into raw_val1/raw_val2.
     */
    S->status |= STATUS_RAW_ATTEMPTED;
    s64 rrc = lv1_hcall(0x5b, 1, 0x62757304ULL, KEY_DEV(2), KEY_TYPE, 0);
    S->total_hypercalls++;
    S->raw_rc = (s32)rrc;
    if (rrc == 0) {
        S->status |= STATUS_RAW_OK;
    }
    if (S->stock_rc == S->raw_rc && S->stock_val1 == S->raw_val1) {
        S->match_status = 1; /* MATCH */
    } else {
        S->match_status = 2; /* DIFF */
    }

#elif PROBE_VARIANT == 1
    /* G1: lv1_open_device(bus_id=9, dev_id=0, flags=0) [invalid bus, expect -17] */
    S->status |= STATUS_RAW_ATTEMPTED;
    s64 orc = lv1_hcall(170, 9, 0, 0, 0, 0);
    S->total_hypercalls++;
    S->raw_rc = (s32)orc;
    if (orc == 0) {
        S->status |= STATUS_RAW_OK;
    }
    S->close_rc = 0;

#elif PROBE_VARIANT == 2
    /* G2: lv1_close_device(bus_id=4, dev_id=2) [optical node without open, expect -11] */
    S->status |= STATUS_RAW_ATTEMPTED;
    s64 crc = lv1_hcall(171, 4, 2, 0, 0, 0);
    S->total_hypercalls++;
    S->raw_rc = (s32)crc;
    if (crc == 0) {
        S->status |= STATUS_RAW_OK;
    }
    S->close_rc = 0;

#elif PROBE_VARIANT == 3
    /* G3: REAL open lv1_open_device(bus_id=4, dev_id=2, flags=0);
     * ONLY if rc == 0, close immediately with lv1_close_device(4, 2).
     */
    S->status |= STATUS_RAW_ATTEMPTED;
    s64 orc = lv1_hcall(170, 4, 2, 0, 0, 0);
    S->total_hypercalls++;
    S->raw_rc = (s32)orc;
    if (orc == 0) {
        S->status |= STATUS_RAW_OK;
        S->status |= STATUS_CLOSE_ATTEMPTED;
        s64 crc = lv1_hcall(171, 4, 2, 0, 0, 0);
        S->total_hypercalls++;
        S->close_rc = (s32)crc;
        if (crc == 0) {
            S->status |= STATUS_CLOSE_OK;
        }
    } else {
        S->close_rc = 0; /* not attempted */
    }
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

__attribute__((always_inline)) static inline u32 map_v_idx(u64 val, u32 attempted) {
    if (!attempted) return 0;
    if (val == 0) return 0;
    if (val == 1) return 1;
    if (val == 2) return 2;
    if (val == 3) return 3;
    if (val == 4) return 4;
    if (val == 5) return 5;
    if (val == 6) return 6;
    return 7;
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

#if PROBE_VARIANT == 0
__attribute__((always_inline)) static inline u32 map_page_c_g0_idx(void) {
    if (S->match_status == 1) {
        /* MATCH */
        if (S->raw_rc == 0 && S->raw_val1 == 5) {
            return 0; /* P1G-G0 MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM) */
        }
        if (S->raw_rc == 0) {
            u32 v = map_v_idx(S->raw_val1, 1);
            return 1 + v; /* 1..8 */
        }
        u32 r = map_rc_name_idx(S->raw_rc, 1);
        return 9 + r; /* 9..20 */
    } else if (S->match_status == 2) {
        /* DIFF */
        if (S->raw_rc != S->stock_rc) {
            u32 r_rc = map_rc_name_idx(S->raw_rc, 1);
            u32 s_rc = map_rc_name_idx(S->stock_rc, 1);
            return 21 + (r_rc * 12 + s_rc); /* 21..164 */
        }
        u32 r_v = map_v_idx(S->raw_val1, 1);
        u32 s_v = map_v_idx(S->stock_val1, 1);
        return 165 + (r_v * 8 + s_v); /* 165..228 */
    }
    return 229; /* NOT RUN */
}
#endif

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
        /* Page A: P1G-<variant> DONE <call>(<args>) rc=<name> */
        u32 att = (S->status & STATUS_RAW_ATTEMPTED) ? 1 : 0;
#if PROBE_VARIANT == 0
        u32 r_idx = map_rc_name_idx(S->raw_rc, att);
        u32 v_idx = map_v_idx(S->raw_val1, att);
        u32 idx = r_idx * 8 + v_idx;
#else
        u32 idx = map_rc_name_idx(S->raw_rc, att);
#endif
        return labels_page_a + idx * STR_STRIDE;
    }
    case 1: {
        /* Page B: raw rc hex + names */
        u32 att = (S->status & STATUS_RAW_ATTEMPTED) ? 1 : 0;
        u32 idx = map_page_b_idx(S->raw_rc, att);
        return labels_page_b + idx * STR_STRIDE;
    }
    case 2: {
        /* Page C: G0 = MATCH/DIFF; G1/G2 = status; G3 = both rcs (open and close) */
#if PROBE_VARIANT == 0
        u32 idx = map_page_c_g0_idx();
#elif PROBE_VARIANT == 1
        u32 att = (S->status & STATUS_RAW_ATTEMPTED) ? 1 : 0;
        u32 idx = map_rc_name_idx(S->raw_rc, att);
#elif PROBE_VARIANT == 2
        u32 att = (S->status & STATUS_RAW_ATTEMPTED) ? 1 : 0;
        u32 idx = map_rc_name_idx(S->raw_rc, att);
#elif PROBE_VARIANT == 3
        u32 o_att = (S->status & STATUS_RAW_ATTEMPTED) ? 1 : 0;
        u32 c_att = (S->status & STATUS_CLOSE_ATTEMPTED) ? 1 : 0;
        u32 o_idx = map_rc_name_idx(S->raw_rc, o_att);
        u32 c_idx = map_rc_name_idx(S->close_rc, c_att);
        u32 idx = o_idx * 12 + c_idx;
#endif
        return labels_page_c + idx * STR_STRIDE;
    }
    case 3: {
        /* Page D: scan summary (optical ids, HDD ids) */
        u32 idx = map_page_d_idx();
        return labels_page_d + idx * STR_STRIDE;
    }
    }
    return STOCK_LABEL;
}
