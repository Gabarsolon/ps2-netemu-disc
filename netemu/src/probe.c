/* Freestanding PPC64 BE, compiled for ISA 2.02 (970). No mutable globals.
 * P1a Repository Probe: enumerates LV1 repository storage nodes using LV1 call 91.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef long long s64;

/* Native helper trampoline in code slot: calls stock 0x111eb8 */
extern s64 repo_read(u64 *out1, u64 *out2, u64 node1, u64 node2, u64 node3, u64 node4);

/* 96-byte Mailbox at 0x930F20 (struct State) */
struct ProbeState {
    u32 status;            /* bit 0: started, bit 1: done */
    u32 total_devices;     /* total devices discovered across all buses */
    u32 rom_count;         /* count of type 5 (ROM) devices */
    u32 hdd_found;         /* 1 if type 0 (DISK) device found, else 0 */
    u32 flash_count;       /* count of type 14 (FLASH) devices */
    u32 total_hypercalls;  /* count of LV1 91 calls made */
    u32 last_lv1_rc;       /* return code of last failed (or 0) LV1 91 call */
    u32 first_err_rc;      /* return code of first failed LV1 91 call */

    u32 rom_bus_idx;       /* bus index (0..15) of first ROM device */
    u32 rom_dev_idx;       /* dev index (0..15) of first ROM device */
    u32 rom_port;          /* port value of first ROM device (or 0xFF) */
    u32 storage_bus_idx;   /* bus index that has bus_type == 5 (or 0xFF) */

    u32 hdd_bus_idx;       /* bus index where HDD was found */
    u32 hdd_dev_idx;       /* dev index */
    u32 hdd_port;          /* port value */
    u32 phat_match;        /* bit 0: emu (bus type 5), bit 1: gxemu (bus 4) */

    u64 rom_bus_id;        /* 64-bit bus_id from repository */
    u64 rom_dev_id;        /* 64-bit dev_id from repository */

    u64 hdd_bus_id;        /* 64-bit bus_id from repository */
    u64 hdd_dev_id;        /* 64-bit dev_id from repository */
};

_Static_assert(sizeof(struct ProbeState) == 96, "ProbeState must be exactly 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_bus_id) == 64, "rom_bus_id offset");

#define S ((volatile struct ProbeState *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define KEY_BUS(b)  (0x6275730000000000ULL | (u64)(b))
#define KEY_DEV(d)  (0x6465760000000000ULL | (u64)(d))
#define KEY_TYPE    0x7479706500000000ULL
#define KEY_ID      0x6964000000000000ULL
#define KEY_PORT    0x706f727400000000ULL

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
            S->last_lv1_rc = (u32)rc;
            continue; /* bus doesn't exist */
        }

        u64 b_type = val1;
        if (b_type == 5) {
            S->storage_bus_idx = b;
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
                /* ROM (Optical) device found! */
                S->rom_count++;
                if (S->rom_count == 1) {
                    S->rom_bus_idx = b;
                    S->rom_dev_idx = d;
                    S->rom_port = d_port;
                    S->rom_bus_id = b_id;
                    S->rom_dev_id = d_id;
                }
                if (b_type == 5) {
                    S->phat_match |= 1;
                }
                if (b == 4) {
                    S->phat_match |= 2;
                }
            } else if (d_type == 0) {
                /* DISK (HDD) device found */
                if (!S->hdd_found) {
                    S->hdd_found = 1;
                    S->hdd_bus_idx = b;
                    S->hdd_dev_idx = d;
                    S->hdd_port = d_port;
                    S->hdd_bus_id = b_id;
                    S->hdd_dev_id = d_id;
                }
            } else if (d_type == 14) {
                /* FLASH device found */
                S->flash_count++;
            }
        }
    }
}

const u8* s4_menu(u64 selected) {
    if (!(S->status & 1)) {
        S->status |= 1;
        run_probe();
        S->status |= 2;
    }
    if (!(S->status & 2)) {
        return STOCK_LABEL;
    }

    u32 page = (u32)(selected & 3);
    switch (page) {
    case 0: {
        u32 d = S->total_devices > 16 ? 16 : S->total_devices;
        u32 r = S->rom_count > 4 ? 4 : S->rom_count;
        u32 h = S->hdd_found ? 1 : 0;
        u32 idx = (d * 5 + r) * 2 + h;
        return labels_page_a + idx * 32;
    }
    case 1: {
        if (S->rom_count == 0) {
            return labels_page_b;
        }
        u32 b = S->rom_bus_idx > 15 ? 15 : S->rom_bus_idx;
        u32 d = S->rom_dev_idx > 15 ? 15 : S->rom_dev_idx;
        u32 p = S->rom_port < 8 ? S->rom_port : 8;
        u32 idx = 1 + (b * 16 + d) * 9 + p;
        return labels_page_b + idx * 32;
    }
    case 2: {
        if (!S->hdd_found) {
            return labels_page_c;
        }
        u32 b = S->hdd_bus_idx < 8 ? S->hdd_bus_idx : 8;
        u32 d = S->hdd_dev_idx < 4 ? S->hdd_dev_idx : 4;
        u32 p = S->hdd_port < 4 ? S->hdd_port : 4;
        u32 ph = S->phat_match & 3;
        u32 idx = 1 + ((b * 5 + d) * 5 + p) * 4 + ph;
        return labels_page_c + idx * 32;
    }
    case 3: {
        u32 err = S->first_err_rc;
        u32 rc_idx = 0;
        if (err != 0) {
            s64 serr = (s64)(int)err;
            if (serr >= -9 && serr <= -1) {
                rc_idx = (u32)(-serr);
            } else if (serr >= -15 && serr < -9) {
                rc_idx = 10;
            } else {
                rc_idx = 11;
            }
        }
        u32 sb = S->storage_bus_idx;
        u32 sb_idx = (sb < 8) ? sb : (sb <= 15 ? 8 : 9);
        u32 n = S->total_hypercalls;
        u32 n_idx = (n < 32) ? 0 : (n < 64 ? 1 : (n < 128 ? 2 : (n < 256 ? 3 : 4)));
        u32 idx = (rc_idx * 10 + sb_idx) * 5 + n_idx;
        return labels_page_d + idx * 32;
    }
    }
    return STOCK_LABEL;
}
