/* Freestanding PPC64 BE, compiled for ISA 2.02 (970). No mutable globals.
 * P1c Optical vs HDD Repository Dumper:
 * Dumps all repository fields of Optical node (type 5, bus 4 dev 2) and
 * HDD node (bus 4 dev 3 type 0 port 2) into an allocator-owned 4 KiB arena.
 * Displays results across 24 pages via in-game menu Debug Information hook.
 * Read-only LV1 91 hypercalls only. Zero open/close or other hypercalls.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef long long s64;
typedef int s32;

/* Native helper trampolines in code slot */
extern s64 repo_read(u64 *out1, u64 *out2, u64 node1, u64 node2, u64 node3, u64 node4);
extern u64 native_alloc(u64 size, u64 arg2, u64 arg3);
extern u64 native_clock(void);

/* 96-byte Mailbox at 0x930F20 */
struct ProbeState {
    u32 status;            /* offset 0: status bits */
    u32 total_hypercalls;  /* offset 4: count of LV1 91 calls made */
    u32 rom_count;         /* offset 8: count of type 5 (ROM) devices */
    u32 hdd_found;         /* offset 12: 1 if HDD control found on bus 4 */
    u32 first_err_rc;      /* offset 16: first failed LV1 91 rc */
    u32 open_count;        /* offset 20: count of menu open cycles */
    u32 pad1[2];           /* offset 24..31: padding */

    u64 arena_ptr;         /* offset 32: pointer to 4 KiB arena from native_alloc */

    u8 rom_bus_idx;        /* offset 40: bus index of optical node (4) */
    u8 rom_dev_idx;        /* offset 41: dev index of optical node (2) */
    u8 rom_port;           /* offset 42: port of optical node (0) */
    u8 hdd_bus_idx;        /* offset 43: bus index of HDD node (4) */
    u8 hdd_dev_idx;        /* offset 44: dev index of HDD node (3) */
    u8 hdd_port;           /* offset 45: port of HDD node (2) */
    u8 pad2[2];            /* offset 46..47 */

    u64 rom_bus_id;        /* offset 48..55 */
    u64 rom_dev_id;        /* offset 56..63 */
    u64 hdd_bus_id;        /* offset 64..71 */
    u64 hdd_dev_id;        /* offset 72..79 */

    u64 last_eval_tb;      /* offset 80..87: timebase of last hook evaluation */
    u64 reserved;          /* offset 88..95: padding to exactly 96 bytes */
};

_Static_assert(sizeof(struct ProbeState) == 96, "ProbeState must be 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeState, open_count) == 20, "open_count offset 20");
_Static_assert(__builtin_offsetof(struct ProbeState, arena_ptr) == 32, "arena_ptr offset 32");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_bus_id) == 48, "rom_bus_id offset 48");
_Static_assert(__builtin_offsetof(struct ProbeState, rom_dev_id) == 56, "rom_dev_id offset 56");
_Static_assert(__builtin_offsetof(struct ProbeState, hdd_bus_id) == 64, "hdd_bus_id offset 64");
_Static_assert(__builtin_offsetof(struct ProbeState, hdd_dev_id) == 72, "hdd_dev_id offset 72");
_Static_assert(__builtin_offsetof(struct ProbeState, last_eval_tb) == 80, "last_eval_tb offset 80");

#define S ((volatile struct ProbeState *)0x930F20ULL)
#define STOCK_LABEL ((const u8 *)0x304EC0ULL)

#define STATUS_STARTED       (1U << 0)
#define STATUS_DONE          (1U << 1)
#define STATUS_ALLOC_OK      (1U << 2)
#define STATUS_ALLOC_FAILED  (1U << 3)

#define ARENA_BYTES 4096U

/* Field record stored in arena (24 bytes) */
struct FieldRecord {
    s64 rc;
    u64 v1;
    u64 v2;
};

_Static_assert(sizeof(struct FieldRecord) == 24, "FieldRecord must be 24 bytes");

/* Total fields: 20 for Optical node, 20 for HDD node, 3 for Bus 4 = 43 records (1,032 bytes) */
#define NUM_NODE_FIELDS 20
#define NUM_BUS_FIELDS   3
#define TOTAL_RECORDS   (NUM_NODE_FIELDS * 2 + NUM_BUS_FIELDS)
_Static_assert(TOTAL_RECORDS * sizeof(struct FieldRecord) <= ARENA_BYTES, "Records must fit in 4 KiB arena");

/* Key definitions matching stock encoder 0x111f6c */
#define KEY_BUS(b)   (0x6275730000000000ULL | (u64)(b))
#define KEY_DEV(d)   (0x6465760000000000ULL | (u64)(d))
#define KEY_TYPE     0x7479706500000000ULL
#define KEY_ID       0x6964000000000000ULL
#define KEY_PORT     0x706f727400000000ULL
#define KEY_BLK_SZ   0x626c6b5f73697a65ULL
#define KEY_N_BLKS   0x6e5f626c6f636b73ULL
#define KEY_N_REGS   0x6e5f726567730000ULL
#define KEY_MEDDL    0x6d6564646c696e67ULL
#define KEY_PCI_B    0x7063695f62757300ULL
#define KEY_PCI_D    0x7063695f64657600ULL
#define KEY_PCI_F    0x7063695f66756e00ULL
#define KEY_INTR(i)  (0x696e747200000000ULL | (u64)(i))
#define KEY_REG(i)   (0x7265670000000000ULL | (u64)(i))
#define KEY_DATA     0x6461746100000000ULL
#define KEY_NUM_DEV  0x6e756d5f64657600ULL

/* Native pool verification: checks 0x934980, 0x24565b8, 0x2446588 */
static __attribute__((noinline)) int arena_rw(u64 a) {
    u64 base = *(const volatile u64*)0x934980ULL;
    return (base & ~0xf800000ULL) == 0x80000000ULL &&
           *(const volatile u64*)0x24565b8ULL == base &&
           *(const volatile u64*)0x2446588ULL == base + 0x20000ULL &&
           !(a & 63) && a >= (base + 0x20000ULL) &&
           (a + ARENA_BYTES) <= (base + 0x60000ULL);
}

/* Helper to get pointer to arena */
static __attribute__((noinline)) volatile struct FieldRecord* get_arena(void) {
    u64 a = S->arena_ptr;
    if (!arena_rw(a)) return 0;
    return (volatile struct FieldRecord*)a;
}

/* Read one field and store into arena */
static void read_one_field(volatile struct FieldRecord *rec, u64 k1, u64 k2, u64 k3, u64 k4) {
    u64 v1 = 0, v2 = 0;
    s64 rc = repo_read(&v1, &v2, k1, k2, k3, k4);
    S->total_hypercalls++;
    if (rc != 0 && S->first_err_rc == 0) {
        S->first_err_rc = (u32)rc;
    }
    rec->rc = rc;
    rec->v1 = v1;
    rec->v2 = v2;
}

/* Dump all 20 fields for a given storage node */
static void dump_node(volatile struct FieldRecord *records, u32 b, u32 d) {
    u64 bus_k = KEY_BUS(b);
    u64 dev_k = KEY_DEV(d);

    /* Fixed keys (0..9) */
    read_one_field(&records[0], bus_k, dev_k, KEY_TYPE, 0);
    read_one_field(&records[1], bus_k, dev_k, KEY_ID, 0);
    read_one_field(&records[2], bus_k, dev_k, KEY_PORT, 0);
    read_one_field(&records[3], bus_k, dev_k, KEY_BLK_SZ, 0);
    read_one_field(&records[4], bus_k, dev_k, KEY_N_BLKS, 0);
    read_one_field(&records[5], bus_k, dev_k, KEY_N_REGS, 0);
    read_one_field(&records[6], bus_k, dev_k, KEY_MEDDL, 0);
    read_one_field(&records[7], bus_k, dev_k, KEY_PCI_B, 0);
    read_one_field(&records[8], bus_k, dev_k, KEY_PCI_D, 0);
    read_one_field(&records[9], bus_k, dev_k, KEY_PCI_F, 0);

    /* Interrupt keys (10..13): intr/0..intr/3 */
    read_one_field(&records[10], bus_k, dev_k, KEY_INTR(0), 0);
    read_one_field(&records[11], bus_k, dev_k, KEY_INTR(1), 0);
    read_one_field(&records[12], bus_k, dev_k, KEY_INTR(2), 0);
    read_one_field(&records[13], bus_k, dev_k, KEY_INTR(3), 0);

    /* MMIO Register keys (14..19): reg/0..reg/2 (type and data) */
    read_one_field(&records[14], bus_k, dev_k, KEY_REG(0), KEY_TYPE);
    read_one_field(&records[15], bus_k, dev_k, KEY_REG(0), KEY_DATA);
    read_one_field(&records[16], bus_k, dev_k, KEY_REG(1), KEY_TYPE);
    read_one_field(&records[17], bus_k, dev_k, KEY_REG(1), KEY_DATA);
    read_one_field(&records[18], bus_k, dev_k, KEY_REG(2), KEY_TYPE);
    read_one_field(&records[19], bus_k, dev_k, KEY_REG(2), KEY_DATA);
}

/* Execute probe once */
static void run_probe(void) {
    u64 val1 = 0, val2 = 0;
    s64 rc = 0;

    S->rom_bus_idx = 0xFF;
    S->rom_dev_idx = 0xFF;
    S->rom_port = 0xFF;
    S->hdd_bus_idx = 0xFF;
    S->hdd_dev_idx = 0xFF;
    S->hdd_port = 0xFF;
    S->open_count = 0;
    S->last_eval_tb = 0;

    /* 1. Allocate 4 KiB arena from native allocator 0xB9848 */
    u64 a = native_alloc(ARENA_BYTES, 3, 0);
    if (!arena_rw(a)) {
        S->status |= STATUS_ALLOC_FAILED;
        return;
    }
    volatile u8 *p = (volatile u8 *)a;
    for (u32 i = 0; i < ARENA_BYTES; i++) {
        p[i] = 0;
    }
    S->arena_ptr = a;
    S->status |= STATUS_ALLOC_OK;

    volatile struct FieldRecord *records = (volatile struct FieldRecord *)a;

    /* 2. Enumerate bus 4 to find Optical and HDD nodes */
    for (u32 b = 0; b < 16; b++) {
        u64 bus_k = KEY_BUS(b);
        val1 = 0; val2 = 0;
        rc = repo_read(&val1, &val2, bus_k, KEY_TYPE, 0, 0);
        S->total_hypercalls++;
        if (rc != 0) {
            if (S->first_err_rc == 0) S->first_err_rc = (u32)rc;
            continue;
        }

        u64 b_id = 0;
        val1 = 0; val2 = 0;
        rc = repo_read(&val1, &val2, bus_k, KEY_ID, 0, 0);
        S->total_hypercalls++;
        if (rc == 0) b_id = val1;

        for (u32 d = 0; d < 16; d++) {
            u64 dev_k = KEY_DEV(d);
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_TYPE, 0);
            S->total_hypercalls++;
            if (rc != 0) continue;

            u64 d_type = val1;
            u64 d_id = 0;
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_ID, 0);
            S->total_hypercalls++;
            if (rc == 0) d_id = val1;

            u32 d_port = 0xFF;
            val1 = 0; val2 = 0;
            rc = repo_read(&val1, &val2, bus_k, dev_k, KEY_PORT, 0);
            S->total_hypercalls++;
            if (rc == 0) d_port = (u32)val1;

            if (d_type == 5) {
                S->rom_count++;
                if (S->rom_count == 1) {
                    S->rom_bus_idx = (u8)b;
                    S->rom_dev_idx = (u8)d;
                    S->rom_port = (u8)d_port;
                    S->rom_bus_id = b_id;
                    S->rom_dev_id = d_id;
                }
            } else if (b == 4 && d_type == 0 && d_port == 2) {
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

    /* 3. Dump Optical node (bus 4 dev 2) into records 0..19 */
    u32 opt_b = S->rom_bus_idx != 0xFF ? S->rom_bus_idx : 4;
    u32 opt_d = S->rom_dev_idx != 0xFF ? S->rom_dev_idx : 2;
    dump_node(&records[0], opt_b, opt_d);

    /* 4. Dump HDD node (bus 4 dev 3) into records 20..39 */
    u32 hdd_b = S->hdd_bus_idx != 0xFF ? S->hdd_bus_idx : 4;
    u32 hdd_d = S->hdd_dev_idx != 0xFF ? S->hdd_dev_idx : 3;
    dump_node(&records[NUM_NODE_FIELDS], hdd_b, hdd_d);

    /* 5. Dump Bus 4 keys into records 40..42 */
    u64 bus4_k = KEY_BUS(4);
    read_one_field(&records[NUM_NODE_FIELDS * 2 + 0], bus4_k, KEY_TYPE, 0, 0);
    read_one_field(&records[NUM_NODE_FIELDS * 2 + 1], bus4_k, KEY_ID, 0, 0);
    read_one_field(&records[NUM_NODE_FIELDS * 2 + 2], bus4_k, KEY_NUM_DEV, 0, 0);
}

/* Immutable label string tables linked into extended RO segment */
extern const u8 labels_page_00[];
extern const u8 labels_page_01[];
extern const u8 labels_page_02[];
extern const u8 labels_page_03[];
extern const u8 labels_page_04[];
extern const u8 labels_page_05[];
extern const u8 labels_page_06[];
extern const u8 labels_page_07[];
extern const u8 labels_page_08[];
extern const u8 labels_page_09[];
extern const u8 labels_page_10[];
extern const u8 labels_page_11[];
extern const u8 labels_page_12[];
extern const u8 labels_page_13[];
extern const u8 labels_page_14[];
extern const u8 labels_page_15[];
extern const u8 labels_page_16[];
extern const u8 labels_page_17[];
extern const u8 labels_page_18[];
extern const u8 labels_page_19[];
extern const u8 labels_page_20[];
extern const u8 labels_page_21[];
extern const u8 labels_page_22[];
extern const u8 labels_page_23[];

/* Map rc and value into index [0..262] for standard 263-string field tables */
static u32 map_field_idx(s64 rc, u64 val) {
    if (rc != 0) {
        if (rc == -6) return 0; /* rc=-6 NO_ENT */
        if (rc == -4) return 1; /* rc=-4 DENIED */
        if (rc == -3) return 2; /* rc=-3 NO_PRIV */
        if (rc == -5) return 3; /* rc=-5 ACC_VIOL */
        if (rc == -1) return 4; /* rc=-1 SHORT */
        if (rc == -2) return 5; /* rc=-2 NOTSUP */
        return 6;               /* rc=ERR */
    }
    return 7 + (u32)(val & 0xFF);
}

/* Map blk_size value (e.g. 512, 2048) */
static u32 map_blk_idx(s64 rc, u64 val) {
    if (rc != 0) {
        if (rc == -6) return 0;
        if (rc == -4) return 1;
        if (rc == -3) return 2;
        if (rc == -5) return 3;
        return 4; /* other err */
    }
    if (val == 0) return 5;
    if (val == 512) return 6;
    if (val == 1024) return 7;
    if (val == 2048) return 8;
    if (val == 4096) return 9;
    if (val == 2352) return 10;
    if (val == 2064) return 11;
    return 12 + (u32)((val >> 8) & 0xFF);
}

/* 79.8 MHz timebase gap: 1.5 seconds = 119,700,000 cycles */
#define TB_GAP_TICKS 119700000ULL

/* Menu hook called from 0x270FFC */
const u8* s4_menu(u64 selected) {
    if (!(S->status & STATUS_STARTED)) {
        S->status |= STATUS_STARTED;
        run_probe();
        S->status |= STATUS_DONE;
    }

    /* If allocator failed or probe not complete, return stock label */
    if ((S->status & STATUS_ALLOC_FAILED) || !(S->status & STATUS_DONE)) {
        return STOCK_LABEL;
    }

    volatile struct FieldRecord *records = get_arena();
    if (!records) {
        return STOCK_LABEL;
    }

    /* Timebase gap detection for menu open */
    u64 now = native_clock();
    u64 last = S->last_eval_tb;

    if (last != 0 && now > last && (now - last) > TB_GAP_TICKS) {
        S->open_count++;
    }
    S->last_eval_tb = now;

    /* Row index r clamped to 0..8 */
    u32 r = (u32)(selected > 8 ? 8 : selected);

    /* Pager: 24 pages across menu opens: page = (OPEN_COUNT * 9 + r) mod 24 */
    u32 page = (S->open_count * 9 + r) % 24;
    if (page >= 24) page = 0;

    switch (page) {
    case 0: {
        /* Page 00: Summary (P1C DONE rom=<n> hdd=<0/1> ids 4/2) */
        u32 r = S->rom_count > 4 ? 4 : S->rom_count;
        u32 h = S->hdd_found ? 1 : 0;
        u32 b = S->rom_bus_idx > 15 ? 15 : S->rom_bus_idx;
        u32 d = S->rom_dev_idx > 15 ? 15 : S->rom_dev_idx;
        u32 p = S->rom_port < 3 ? S->rom_port : 3;
        u32 mode = 0;
        if (S->rom_bus_id == 4 && S->rom_dev_id == 2) mode = 0;
        else if (S->rom_bus_id == b && S->rom_dev_id == d) mode = 1;
        else if (S->rom_bus_id == 0x500 && S->rom_dev_id == 0x501) mode = 2;
        else mode = 3;
        u32 idx = ((r * 2 + h) * 4 + mode) * 4 + p;
        if (idx >= 160) idx = 159;
        return labels_page_00 + idx * 32;
    }
    case 1: {
        /* Page 01: Optical type */
        u32 idx = map_field_idx(records[0].rc, records[0].v1);
        return labels_page_01 + idx * 32;
    }
    case 2: {
        /* Page 02: HDD type */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 0].rc, records[NUM_NODE_FIELDS + 0].v1);
        return labels_page_02 + idx * 32;
    }
    case 3: {
        /* Page 03: Optical id */
        u32 idx = map_field_idx(records[1].rc, records[1].v1);
        return labels_page_03 + idx * 32;
    }
    case 4: {
        /* Page 04: HDD id */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 1].rc, records[NUM_NODE_FIELDS + 1].v1);
        return labels_page_04 + idx * 32;
    }
    case 5: {
        /* Page 05: Optical port */
        u32 idx = map_field_idx(records[2].rc, records[2].v1);
        return labels_page_05 + idx * 32;
    }
    case 6: {
        /* Page 06: HDD port */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 2].rc, records[NUM_NODE_FIELDS + 2].v1);
        return labels_page_06 + idx * 32;
    }
    case 7: {
        /* Page 07: Optical blk_size */
        u32 idx = map_blk_idx(records[3].rc, records[3].v1);
        if (idx >= 268) idx = 267;
        return labels_page_07 + idx * 32;
    }
    case 8: {
        /* Page 08: HDD blk_size */
        u32 idx = map_blk_idx(records[NUM_NODE_FIELDS + 3].rc, records[NUM_NODE_FIELDS + 3].v1);
        if (idx >= 268) idx = 267;
        return labels_page_08 + idx * 32;
    }
    case 9: {
        /* Page 09: Optical n_blocks */
        u32 idx = map_field_idx(records[4].rc, records[4].v1);
        return labels_page_09 + idx * 32;
    }
    case 10: {
        /* Page 10: HDD n_blocks */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 4].rc, records[NUM_NODE_FIELDS + 4].v1);
        return labels_page_10 + idx * 32;
    }
    case 11: {
        /* Page 11: Optical n_regs */
        u32 idx = map_field_idx(records[5].rc, records[5].v1);
        return labels_page_11 + idx * 32;
    }
    case 12: {
        /* Page 12: HDD n_regs */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 5].rc, records[NUM_NODE_FIELDS + 5].v1);
        return labels_page_12 + idx * 32;
    }
    case 13: {
        /* Page 13: Optical meddling */
        u32 idx = map_field_idx(records[6].rc, records[6].v1);
        return labels_page_13 + idx * 32;
    }
    case 14: {
        /* Page 14: HDD meddling */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 6].rc, records[NUM_NODE_FIELDS + 6].v1);
        return labels_page_14 + idx * 32;
    }
    case 15: {
        /* Page 15: Optical PCI (pci_bus/dev/fun) */
        u32 idx = map_field_idx(records[7].rc, records[7].v1);
        return labels_page_15 + idx * 32;
    }
    case 16: {
        /* Page 16: HDD PCI (pci_bus/dev/fun) */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 7].rc, records[NUM_NODE_FIELDS + 7].v1);
        return labels_page_16 + idx * 32;
    }
    case 17: {
        /* Page 17: Optical intr/0 */
        u32 idx = map_field_idx(records[10].rc, records[10].v1);
        return labels_page_17 + idx * 32;
    }
    case 18: {
        /* Page 18: HDD intr/0 */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 10].rc, records[NUM_NODE_FIELDS + 10].v1);
        return labels_page_18 + idx * 32;
    }
    case 19: {
        /* Page 19: Optical reg/0 type & data */
        u32 idx = map_field_idx(records[14].rc, records[14].v1);
        return labels_page_19 + idx * 32;
    }
    case 20: {
        /* Page 20: HDD reg/0 type & data */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 14].rc, records[NUM_NODE_FIELDS + 14].v1);
        return labels_page_20 + idx * 32;
    }
    case 21: {
        /* Page 21: Optical intr/1 & reg/1 */
        u32 idx = map_field_idx(records[11].rc, records[11].v1);
        return labels_page_21 + idx * 32;
    }
    case 22: {
        /* Page 22: HDD intr/1 & reg/1 */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS + 11].rc, records[NUM_NODE_FIELDS + 11].v1);
        return labels_page_22 + idx * 32;
    }
    case 23: {
        /* Page 23: Bus 4 keys (type, id, num_dev) */
        u32 idx = map_field_idx(records[NUM_NODE_FIELDS * 2 + 2].rc, records[NUM_NODE_FIELDS * 2 + 2].v1);
        return labels_page_23 + idx * 32;
    }
    }

    return STOCK_LABEL;
}
