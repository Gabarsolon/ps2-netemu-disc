#include "disc.h"

static int check_cdvd_buffer_guard(u64 *p_lpar, u64 *p_ea, u64 *p_sz) {
    u64 raw_lpar = *(const volatile u64 *)0x2458438ULL;
    u64 raw_ea   = *(const volatile u64 *)0x2458428ULL;
    u64 raw_sz   = *(const volatile u64 *)0x2458430ULL;

    *p_lpar = raw_lpar;
    *p_ea   = raw_ea;
    *p_sz   = raw_sz;

    if (raw_lpar < 0x100000000ULL || (raw_lpar & 0xFFFF00000000ULL) != 0x500000000000ULL || (raw_lpar & 0xFFFFFULL) != 0) {
        return 0;
    }
    if (raw_ea >= 0x100000000ULL || raw_ea < 0x80000000ULL || (raw_ea & 0xFFFFFULL) != 0 || raw_ea == raw_lpar) {
        return 0;
    }
    if (raw_sz < 0x80000ULL) {
        return 0;
    }
    return 1;
}

static s32 poll_completion(u64 dev, u64 tag, volatile u64 *p_status, volatile u32 *p_polls, volatile u64 *p_ticks) {
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    u64 start_tb = native_clock();
    for (u32 iter = 0; iter < 1000000; iter++) {
        s64 rc = lv1_hcall(254, dev, tag, 0, 0, 0, 0);
        if (rc == 0) {
            *p_status = mb->raw_val1;
            *p_polls = iter + 1;
            *p_ticks = native_clock() - start_tb;
            return 0;
        }
        u64 now_tb = native_clock();
        if ((now_tb - start_tb) >= 400000000ULL) { /* ~5.0 seconds */
            break;
        }
    }
    *p_ticks = native_clock() - start_tb;
    return 1; /* timeout */
}

static int execute_non_read_cmd(
    u8 opcode, u32 alloc_len, u32 proto, u32 in_out,
    volatile u8 *cmnd_block_ea, u64 cmnd_block_lpar,
    volatile u8 *data_ea, u64 data_lpar)
{
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    for (u32 i = 0; i < 64; i++) cmnd_block_ea[i] = 0;

    cmnd_block_ea[0] = opcode;
    if (opcode == 0x12) {
        cmnd_block_ea[4] = (u8)alloc_len;
    }

    volatile u32 *b32 = (volatile u32 *)cmnd_block_ea;
    b32[8]  = 12;         /* pktlen = 12 */
    b32[9]  = alloc_len;  /* blocks / bytes */
    b32[10] = 1;          /* block_size = 1 */
    b32[11] = proto;      /* proto (0=NON_DATA, 1=PIO_IN) */
    b32[12] = in_out;     /* in_out (0=WRITE, 1=READ) */
    volatile u64 *b64 = (volatile u64 *)cmnd_block_ea;
    b64[7]  = data_lpar;

    if (alloc_len > 0) {
        u32 clr = alloc_len < 2048 ? alloc_len : 2048;
        for (u32 i = 0; i < clr; i++) data_ea[i] = 0;
    }

    s64 send_rc = lv1_hcall(248, 2, 1, cmnd_block_lpar, 0x40, (alloc_len > 0) ? data_lpar : 0, alloc_len);
    if (send_rc != 0) return -1;

    u64 tag = mb->raw_val1;
    u64 status = 0;
    u32 polls = 0;
    u64 ticks = 0;
    s32 poll_res = poll_completion(2, tag, &status, &polls, &ticks);
    if (poll_res != 0 || status != 0) return -2;

    return 0;
}

static int read_atapi_sectors(u32 lba, u32 n_sectors) {
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    if (!mb || !(mb->flags & 1)) return -1;

    volatile u8 *cmnd_block_ea = (volatile u8 *)mb->buf_ea;
    u64 cmnd_block_lpar = mb->buf_lpar;
    u64 data_lpar = mb->buf_lpar + 0x1000;

    for (u32 i = 0; i < 64; i++) cmnd_block_ea[i] = 0;

    cmnd_block_ea[0] = 0x28; /* READ(10) */
    cmnd_block_ea[2] = (u8)(lba >> 24);
    cmnd_block_ea[3] = (u8)(lba >> 16);
    cmnd_block_ea[4] = (u8)(lba >> 8);
    cmnd_block_ea[5] = (u8)lba;
    cmnd_block_ea[7] = (u8)(n_sectors >> 8);
    cmnd_block_ea[8] = (u8)n_sectors;

    volatile u32 *b32 = (volatile u32 *)cmnd_block_ea;
    b32[8]  = 12;            /* pktlen = 12 */
    b32[9]  = n_sectors;     /* blocks */
    b32[10] = 2048;          /* block_size = 2048 */
    b32[11] = 3;             /* proto = 3 (DMA protocol) */
    b32[12] = 1;             /* in_out = 1 (READ) */
    volatile u64 *b64 = (volatile u64 *)cmnd_block_ea;
    b64[7]  = data_lpar;

    u32 total_bytes = n_sectors * 2048;
    s64 send_rc = lv1_hcall(248, 2, 1, cmnd_block_lpar, 0x40, data_lpar, total_bytes);
    if (send_rc != 0) {
        mb->last_read_rc = (s32)send_rc;
        return -1;
    }

    u64 tag = mb->raw_val1;
    u64 status = 0;
    u32 polls = 0;
    u64 ticks = 0;
    s32 poll_res = poll_completion(2, tag, &status, &polls, &ticks);
    if (poll_res != 0 || status != 0) {
        mb->last_read_rc = (s32)(poll_res != 0 ? -100 : status);
        return -2;
    }

    mb->last_read_rc = 0;
    mb->sectors_read += n_sectors;
    return 0;
}

static inline void fast_memcpy(u8 *dst, const volatile u8 *src, u32 n) {
    if (!(((u64)dst | (u64)src) & 7)) {
        u64 *d64 = (u64 *)dst;
        const volatile u64 *s64 = (const volatile u64 *)src;
        u32 n64 = n / 8;
        for (u32 i = 0; i < n64; i++) {
            d64[i] = s64[i];
        }
        dst += n64 * 8;
        src += n64 * 8;
        n %= 8;
    }
    for (u32 i = 0; i < n; i++) {
        dst[i] = src[i];
    }
}

static int init_optical_disc(void) {
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    if (mb->flags & 1) {
        return 0;
    }
    mb->magic = 0x44495343; /* 'DISC' */

    u64 cdvd_lpar = 0, cdvd_ea = 0, cdvd_sz = 0;
    if (!check_cdvd_buffer_guard(&cdvd_lpar, &cdvd_ea, &cdvd_sz)) {
        mb->last_read_rc = -10;
        return -1;
    }

    /* LV1 170: Open optical drive (bus 4, dev 2) */
    s64 orc = lv1_hcall(170, 4, 2, 0, 0, 0, 0);
    if (orc != 0) {
        mb->last_read_rc = -20 - (s32)orc;
        return -2;
    }

    /* LV1 174: Allocate DMA region (1 MiB, pexp 20) */
    s64 drc = lv1_hcall(174, 4, 2, 0x100000, 20, 0, 0);
    if (drc != 0) {
        lv1_hcall(171, 4, 2, 0, 0, 0, 0);
        mb->last_read_rc = -30 - (s32)drc;
        return -3;
    }
    u64 dma_region = mb->raw_val1;

    /* LV1 176: Map DMA region */
    s64 mrc = lv1_hcall(176, 4, 2, cdvd_lpar, dma_region, 0x100000, 0xE000000000000800ULL);
    if (mrc != 0) {
        lv1_hcall(175, 4, 2, dma_region, 0, 0, 0);
        lv1_hcall(171, 4, 2, 0, 0, 0, 0);
        mb->last_read_rc = -40 - (s32)mrc;
        return -4;
    }

    mb->buf_ea = cdvd_ea;
    mb->buf_lpar = cdvd_lpar;
    mb->dma_region = dma_region;

    volatile u8 *cmnd_block_ea = (volatile u8 *)cdvd_ea;
    u64 cmnd_block_lpar = cdvd_lpar;
    volatile u8 *data_ea = (volatile u8 *)(cdvd_ea + 0x1000);
    u64 data_lpar = cdvd_lpar + 0x1000;

    /* TEST UNIT READY */
    int trc = execute_non_read_cmd(0x00, 0, 0, 0, cmnd_block_ea, cmnd_block_lpar, data_ea, data_lpar);
    if (trc != 0) {
        lv1_hcall(177, 4, 2, dma_region, 0x100000, 0, 0);
        lv1_hcall(175, 4, 2, dma_region, 0, 0, 0);
        lv1_hcall(171, 4, 2, 0, 0, 0, 0);
        mb->last_read_rc = -50 + trc;
        return -5;
    }

    /* READ CAPACITY(10) */
    execute_non_read_cmd(0x25, 8, 1, 1, cmnd_block_ea, cmnd_block_lpar, data_ea, data_lpar);
    u32 max_lba = ((u32)data_ea[0] << 24) | ((u32)data_ea[1] << 16) |
                  ((u32)data_ea[2] << 8)  | (u32)data_ea[3];
    u32 block_sz = ((u32)data_ea[4] << 24) | ((u32)data_ea[5] << 16) |
                   ((u32)data_ea[6] << 8)  | (u32)data_ea[7];
    if (block_sz != 2048) {
        block_sz = 2048;
    }

    mb->max_lba = max_lba;
    mb->block_size = block_sz;
    mb->disc_size = (u64)(max_lba + 1) * (u64)block_sz;

    /* OPTICAL DISC HARDWARE AUTHENTICATION (0x5005 over VUART Port 10) */
    /* Release drive temporarily so ss_server3 / isolated SPU can authenticate */
    lv1_hcall(177, 4, 2, dma_region, 0x100000, 0, 0);
    lv1_hcall(175, 4, 2, dma_region, 0, 0, 0);
    lv1_hcall(171, 4, 2, 0, 0, 0, 0);

    /* Format 0x70 request packet at data_ea + 0x800 */
    volatile u8 *req_ea = data_ea + 0x800;
    u64 req_lpar = data_lpar + 0x800;
    volatile u8 *reply_ea = data_ea + 0x900;
    u64 reply_lpar = data_lpar + 0x900;

    for (u32 i = 0; i < 0x70; i++) req_ea[i] = 0;
    volatile u32 *b32 = (volatile u32 *)req_ea;
    volatile u64 *b64 = (volatile u64 *)req_ea;
    b32[0] = 0x0000FACE;            /* magic */
    b32[1] = 0x00005000;            /* service */
    b32[2] = 0x00000060;            /* payload len */
    b32[3] = 0x00000060;            /* length echo */
    b64[2] = 0x0000000000005005ULL; /* opcode */
    b64[3] = 0x0000000000005000ULL; /* service echo */
    b64[6] = 0x1020000401000001ULL; /* caller LAID */
    req_ea[56] = 0x00;              /* byte A */
    req_ea[57] = 0x13;              /* byte B (DVD-5) */
    b32[16] = 0x0000004B;           /* retries = 75 */

    /* Send request via HV 163 */
    s64 w_rc = lv1_hcall(163, 10, req_lpar, 0x70, 0, 0, 0);
    if (w_rc == 0) {
        /* Bounded poll HV 162 for reply */
        for (u32 i = 0; i < 0x70; i++) reply_ea[i] = 0;
        u32 total_read = 0;
        u64 start_tb = native_clock();
        while (total_read < 0x70) {
            u64 current_buf_lpar = reply_lpar + total_read;
            u64 needed = 0x70ULL - (u64)total_read;
            s64 r_rc = lv1_hcall(162, 10, current_buf_lpar, needed, 0, 0, 0);
            if (r_rc == 0) {
                total_read += (u32)mb->raw_val1;
            }
            if ((native_clock() - start_tb) >= 160000000ULL) { /* ~2.0s */
                break;
            }
        }
    }

    /* Re-open drive and map DMA */
    lv1_hcall(170, 4, 2, 0, 0, 0, 0);
    lv1_hcall(174, 4, 2, 0x100000, 20, 0, 0);
    dma_region = mb->raw_val1;
    lv1_hcall(176, 4, 2, cdvd_lpar, dma_region, 0x100000, 0xE000000000000800ULL);

    mb->dma_region = dma_region;
    mb->fd = VIRTUAL_DISC_FD;
    mb->flags = 1;

    /* Set Cobra global disc flags in V */
    *(volatile u8 *)(0x3174478ULL + 4) = 1;      /* V[4] = 1 (disc mounted!) */
    *(volatile u8 *)(0x3174478ULL + 0x804) = 0;  /* V[0x804] = 0 (DVD) */
    *(volatile u8 *)(0x3174478ULL + 0x805) = 0;  /* V[0x805] = 0 */
    *(volatile u64 *)(0x3174478ULL + 0x810) = mb->disc_size;

    /* Read LBA 16 (PVD) to verify CD001 */
    if (read_atapi_sectors(16, 1) == 0) {
        if (data_ea[1] == 'C' && data_ea[2] == 'D' && data_ea[3] == '0' && data_ea[4] == '0' && data_ea[5] == '1') {
            mb->flags |= 2; /* PVD CD001 verified! */
        }
    }

    return 0;
}

int s1_open(int unk, const char *path) {
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    mb->open_calls++;

    /* 1. Optical disc path: if already opened/mounted, return virtual fd */
    if (mb->flags & 1) {
        return mb->fd; /* 0xBD00 */
    }

    /* 2. Try optical disc initialization FIRST! */
    int rc = init_optical_disc();
    if (rc == 0) {
        return mb->fd; /* 0xBD00 */
    }

    /* 3. Fail-open fallback: stock Cobra open (carrier ISO) */
    return cobra_open(unk, path);
}

int s1_stat(int fd, void *st) {
    if (fd != VIRTUAL_DISC_FD) {
        return cobra_stat(fd, st);
    }
    if (!st || (u64)st < 0x800000ULL) return -1;

    volatile struct DiscMailbox *mb = DISC_MAILBOX;

    u8 *p = (u8 *)st;
    /* Stock caller reserves 0x30 bytes at sp+0x78; sp+0xb0 holds r28.
     * Clearing 64 bytes here would overwrite that saved register. */
    for (u32 i = 0; i < 0x30; i++) p[i] = 0;

    *(u32 *)(p + 0x00) = 0100444; /* S_IFREG | 0444 */
    *(u64 *)(p + 0x28) = mb->disc_size;

    *(volatile u64 *)(0x3174478ULL + 0x810) = mb->disc_size;

    return 0;
}

int s1_read(int fd, u64 off, u8 *buf, u64 size) {
    if (fd != VIRTUAL_DISC_FD) {
        return (int)raw_read(fd, off, buf, size);
    }

    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    if (!(mb->flags & 1)) return -1;

    if ((u64)buf < 0x800000ULL) return -1; /* Protection guard */

    if (off >= mb->disc_size) return 0;
    if (off + size > mb->disc_size) {
        size = mb->disc_size - off;
    }
    if (size == 0) return 0;

    mb->read_calls++;
    mb->last_lba = (u32)(off / 2048);

    volatile u8 *data_ea = (volatile u8 *)(mb->buf_ea + 0x1000);

    u64 curr_off = off;
    u64 bytes_left = size;
    u8 *dst = buf;

    while (bytes_left > 0) {
        u32 lba = (u32)(curr_off / 2048);
        u32 in_sector = (u32)(curr_off % 2048);

        if (in_sector == 0 && bytes_left >= 2048) {
            u32 chunk_sectors = (u32)(bytes_left / 2048);
            if (chunk_sectors > 32) chunk_sectors = 32;

            if (read_atapi_sectors(lba, chunk_sectors) != 0) {
                break;
            }

            u32 chunk_bytes = chunk_sectors * 2048;
            fast_memcpy(dst, data_ea, chunk_bytes);

            curr_off += chunk_bytes;
            dst += chunk_bytes;
            bytes_left -= chunk_bytes;
        } else {
            if (read_atapi_sectors(lba, 1) != 0) {
                break;
            }

            u32 avail = 2048 - in_sector;
            u32 to_copy = (avail < bytes_left) ? avail : (u32)bytes_left;

            fast_memcpy(dst, data_ea + in_sector, to_copy);

            curr_off += to_copy;
            dst += to_copy;
            bytes_left -= to_copy;
        }
    }

    u32 total_read = (u32)(size - bytes_left);
    return (int)total_read;
}

int s1_mount(void *cdvd_struct) {
    if (!cdvd_struct || (u64)cdvd_struct < 0x800000ULL) {
        return -1;
    }

    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    int rc = init_optical_disc();
    if (rc != 0) {
        return stock_mount(cdvd_struct);
    }

    u8 *p = (u8 *)cdvd_struct;
    u32 total_sectors = mb->max_lba + 1;

    *(u32 *)(p + 0x18) = 0x14;          /* DVD format */
    *(u32 *)(p + 0x1c) = total_sectors; /* total sectors */
    *(u32 *)(p + 0x20) = total_sectors;
    *(u32 *)(p + 0x24) = 2048;          /* sector size */
    *(u32 *)(p + 0x28) = 0;
    *(u32 *)(p + 0x2c) = 2048;
    *(u64 *)(p + 0x38) = 0x8000;        /* sector 16 offset */
    *(u32 *)p |= 0x10;

    /* Synthesize LIMG header in Netemu buffer at 0x2458440 + 0x168 */
    volatile u8 *limg = (volatile u8 *)(0x2458440ULL + 0x168);
    *(volatile u32 *)(limg + 0x00) = 0x4C494D47; /* 'LIMG' */
    *(volatile u32 *)(limg + 0x04) = 1;          /* DVD */
    *(volatile u32 *)(limg + 0x08) = total_sectors;
    *(volatile u32 *)(limg + 0x0C) = 2048;

    /* Copy Sector 16 into 0x2458440 + 0x178 */
    volatile u8 *pvd_dst = (volatile u8 *)(0x2458440ULL + 0x178);
    volatile u8 *pvd_src = (volatile u8 *)(mb->buf_ea + 0x1000);
    fast_memcpy((u8 *)pvd_dst, pvd_src, 2048);

    return 0;
}

const u8 *s4_menu(u64 selected) {
    volatile struct DiscMailbox *mb = DISC_MAILBOX;
    u32 page = (u32)(selected & 3);

    if (!(mb->flags & 1)) {
        if (mb->last_read_rc == -10) {
            return (const u8 *)"DISC ERR: BUFFER GUARD FAIL";
        } else if (mb->last_read_rc <= -20 && mb->last_read_rc > -30) {
            return (const u8 *)"DISC ERR: OPEN FAILED (HV 170)";
        } else if (mb->last_read_rc <= -50) {
            return (const u8 *)"DISC ERR: TUR FAILED (NO DISC)";
        }
        return (const u8 *)"PS2 DISC: NOT MOUNTED";
    }

    if (page == 0) {
        if (mb->flags & 2) {
            return (const u8 *)"PS2 DISC: AUTH OK (CD001)";
        } else {
            return (const u8 *)"PS2 DISC: MOUNTED (NO PVD)";
        }
    } else if (page == 1) {
        return (const u8 *)"PS2 DISC: STREAMING DIRECT";
    } else if (page == 2) {
        return (const u8 *)"PS2 DISC: CECH-25XX SLIM";
    } else {
        return (const u8 *)"PS2 DISC: TDU SLES-54466";
    }
}
