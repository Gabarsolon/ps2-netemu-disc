/* SPDX-License-Identifier: MIT */
#include "probe.h"
#include "storage_abi.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <sys/file.h>
#include <sys/thread.h>
#include <sys/sys_time.h>
#include <sys/stat.h>

char probe_lines[PROBE_LOG_LINES][PROBE_LINE_LENGTH];
atomic_uint probe_line_count;
atomic_int probe_done, probe_stop, probe_log_failed, probe_timed_out;
atomic_uint_fast64_t probe_deadline;
atomic_uint_fast64_t probe_stage_deadline;
unsigned probe_selection;
static int log_handle = -1;
static uint8_t sector[65536] __attribute__((aligned(128)));
static uint8_t bounce[65536] __attribute__((aligned(65536)));
static uint8_t command_data[4096] __attribute__((aligned(128)));
static uint8_t sense_data[32] __attribute__((aligned(128)));
static uint32_t be32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) | ((uint32_t)p[2] << 8) | p[3];
}
static uint64_t be64(const uint8_t *p) { return ((uint64_t)be32(p) << 32) | be32(p + 4); }
static uint32_t be24(const uint8_t *p) { return ((uint32_t)p[0] << 16) | ((uint32_t)p[1] << 8) | p[2]; }
uint64_t probe_now(void) { return (uint64_t)sys_time_get_system_time(); }
/* Only this worker writes the log/screen queue. Published rows are immutable.
 * A stuck log operation is bounded by the independent guard, as drive I/O is. */
static void line(const char *fmt, ...) {
    char text[PROBE_LINE_LENGTH];
    int at = snprintf(text, sizeof(text), "%llu ", (unsigned long long)(probe_now() / 1000));
    va_list ap; va_start(ap, fmt);
    (void)vsnprintf(text + at, sizeof(text) - (size_t)at - 1, fmt, ap); va_end(ap);
    size_t n = strlen(text);
    unsigned index = atomic_load_explicit(&probe_line_count, memory_order_relaxed);
    if (index < PROBE_LOG_LINES) {
        memcpy(probe_lines[index], text, n + 1);
        atomic_store_explicit(&probe_line_count, index + 1, memory_order_release);
    }
    text[n++] = '\n';
    if (log_handle >= 0) {
        uint64_t wrote = 0;
        atomic_store(&probe_deadline, probe_now() + 5000000);
        int rc = sysLv2FsWrite(log_handle, text, n, &wrote);
        /* Attempt fsync after every line, including a short/failed write. */
        int sync_rc = sysLv2FsFsync(log_handle);
        atomic_store(&probe_deadline, 0);
        if (rc || wrote != n || sync_rc) atomic_store(&probe_log_failed, 1);
    }
}
static int begin(const char *what) {
    if (atomic_load(&probe_stop)) return 0;
    line("BEGIN %s; deadline=5s", what);
    atomic_store(&probe_deadline, probe_now() + 5000000);
    return !atomic_load(&probe_stop);
}
static void ended(void) { atomic_store(&probe_deadline, 0); }
static void cleanup_begin(const char *what) {
    line("BEGIN cleanup %s; deadline=5s", what);
    atomic_store(&probe_deadline, probe_now() + 5000000);
}
static void dump(const char *name, const uint8_t *p, unsigned length) {
    for (unsigned i = 0; i < length; i += 16) {
        char hex[49] = {0};
        unsigned take = length - i; if (take > 16) take = 16;
        for (unsigned j = 0; j < take; j++) (void)snprintf(hex + j * 3, 4, "%02X ", p[i + j]);
        line("%s +%02X %s", name, i, hex);
    }
}
static int atapi_raw(int fd, const char *name, const uint8_t *cdb, uint32_t length, uint8_t *data) {
    probe_atapi cmd __attribute__((aligned(128)));
    memset(&cmd, 0, sizeof(cmd)); memcpy(cmd.packet, cdb, 12);
    cmd.packet_length = 12; cmd.blocks = 1; cmd.block_size = length;
    cmd.protocol = length ? 1 : 0; cmd.direction = 1;
    uint64_t auxiliary = 0;
    if (length) memset(data, 0, length);
    if (!begin(name)) return -1;
    int rc = probe_storage_atapi(fd, &cmd, data, &auxiliary); ended();
    line("%s rc=%08X auxiliary_raw=%016llX (semantics unverified)", name, (unsigned)rc, (unsigned long long)auxiliary);
    return rc;
}
static int atapi(int fd, const char *name, const uint8_t *cdb, uint32_t length) {
    /* A closed opcode allow-list, all read/status commands; no caller-supplied CDB. */
    switch (cdb[0]) { case 0: case 0x12: case 0x25: case 0x46: case 0xad: break; default: return -1; }
    int rc = atapi_raw(fd, name, cdb, length, command_data);
    if (rc && !atomic_load(&probe_stop)) {
        uint8_t sense_cdb[12] = {3, 0, 0, 0, 18};
        int sr = atapi_raw(fd, "REQUEST SENSE", sense_cdb, 18, sense_data);
        if (!sr) {
            dump("sense", sense_data, 18);
            unsigned response = sense_data[0] & 0x7f;
            if (response == 0x70 || response == 0x71)
                line("sense fixed key=%02X ASC=%02X ASCQ=%02X", sense_data[2] & 15, sense_data[12], sense_data[13]);
            else if (response == 0x72 || response == 0x73)
                line("sense descriptor key=%02X ASC=%02X ASCQ=%02X", sense_data[1] & 15, sense_data[2], sense_data[3]);
            else line("sense response unrecognized: %02X", response);
        }
    }
    return rc;
}
static void read_sector(int fd, uint32_t lba, uint32_t sector_size) {
    char label[80]; snprintf(label, sizeof(label), "sys_storage_read lba=%u count=1", lba);
    memset(sector, 0xcc, sizeof(sector)); uint32_t count = 0;
    if (!begin(label)) return;
    int rc = probe_storage_read(fd, lba, sector, &count); ended();
    line("READ lba=%u rc=%08X sectors_read=%u expected=1 bytes_per_sector=%u bytes_reported=%llu flags=0", lba, (unsigned)rc, count, sector_size, (unsigned long long)count * sector_size);
    if (!rc && count == 1) {
        dump("sector", sector, 64);
        if (lba == 16)
            line("PVD lba16 signature_01_CD001=%s descriptor_version=%u", !memcmp(sector, "\x01" "CD001", 6) ? "MATCH" : "NO_MATCH", sector[6]);
    } else line("READ failed or short; buffer not interpreted");
}
static void read_file(const char *path) {
    int fd = -1; char label[160]; snprintf(label, sizeof(label), "open file %.130s", path);
    if (!begin(label)) return;
    int rc = sysLv2FsOpen(path, SYS_O_RDONLY, &fd, 0, NULL, 0); ended();
    line("file open rc=%08X fd=%d path=%s", (unsigned)rc, fd, path);
    if (rc) return;
    uint8_t bytes[64] __attribute__((aligned(128))) = {0}; uint64_t got = 0;
    if (begin("read file first 64 bytes")) {
        rc = sysLv2FsRead(fd, bytes, sizeof(bytes), &got); ended();
        line("file read rc=%08X bytes=%llu requested=64 path=%s", (unsigned)rc, (unsigned long long)got, path);
        if (!rc && got <= sizeof(bytes)) dump("file", bytes, (unsigned)got);
    }
    cleanup_begin("close file"); rc = sysLv2FsClose(fd); ended(); line("file close rc=%08X", (unsigned)rc);
}
/* Bounded breadth-first listing reaches PS3_GAME/PARAM.SFO if the root has no
 * files. This is a single 64-byte read, never a dump/copy of a game. */
static void filesystem_probe(void) {
    sysFSStat st = {0};
    if (!begin("stat /dev_bdvd")) return;
    int rc = sysLv2FsStat("/dev_bdvd", &st); ended();
    line("stat /dev_bdvd rc=%08X mode=%08X size=%llu", (unsigned)rc, st.st_mode, (unsigned long long)st.st_size);
    /* Log the result of trying to open the root itself, even though it is a directory. */
    int root_fd = -1;
    if (begin("open /dev_bdvd O_RDONLY")) {
        rc = sysLv2FsOpen("/dev_bdvd", SYS_O_RDONLY, &root_fd, 0, NULL, 0); ended();
        line("open /dev_bdvd rc=%08X fd=%d", (unsigned)rc, root_fd);
        if (!rc) { cleanup_begin("close /dev_bdvd"); rc = sysLv2FsClose(root_fd); ended(); line("close root rc=%08X", (unsigned)rc); }
    }
    char dirs[8][256] = {{"/dev_bdvd"}}; unsigned directories = 1, entries = 0; int sampled = 0;
    for (unsigned d = 0; d < directories && !atomic_load(&probe_stop); d++) {
        int dir = -1;
        if (!begin("open directory")) return;
        rc = sysLv2FsOpenDir(dirs[d], &dir); ended();
        line("opendir rc=%08X fd=%d path=%s", (unsigned)rc, dir, dirs[d]);
        if (rc) continue;
        for (unsigned entry = 0; entry < 24 && entries < 32 && !atomic_load(&probe_stop); entry++, entries++) {
            sysFSDirent de = {0}; uint64_t got = 0;
            if (!begin("readdir")) break;
            rc = sysLv2FsReadDir(dir, &de, &got); ended();
            if (rc || !got) { line("readdir rc=%08X count=%llu", (unsigned)rc, (unsigned long long)got); break; }
            de.d_name[sizeof(de.d_name) - 1] = 0;
            if (!strcmp(de.d_name, ".") || !strcmp(de.d_name, "..")) continue;
            char path[256]; int n = snprintf(path, sizeof(path), "%s/%s", dirs[d], de.d_name);
            if (n < 0 || (unsigned)n >= sizeof(path)) { line("entry path too long, skipped"); continue; }
            memset(&st, 0, sizeof(st));
            if (!begin("stat directory entry")) break;
            rc = sysLv2FsStat(path, &st); ended();
            line("entry rc=%08X mode=%08X size=%llu path=%s", (unsigned)rc, st.st_mode, (unsigned long long)st.st_size, path);
            if (!rc && S_ISDIR(st.st_mode) && directories < 8) {
                memcpy(dirs[directories++], path, (size_t)n + 1);
            } else if (!rc && S_ISREG(st.st_mode) && !sampled) { read_file(path); sampled = 1; }
        }
        cleanup_begin("close directory"); rc = sysLv2FsCloseDir(dir); ended(); line("closedir rc=%08X", (unsigned)rc);
        /* Root plus the first directory containing a readable sample suffices. */
        if (sampled) break;
    }
    if (!sampled) line("No regular file sampled within bounds (8 directories, 24 entries each, 32 total)");
}
static void baseline_probe(void) {
    int rc;
    line("UNKNOWN until owner runs: LV2 disc readability; this does not test the netemu LV1 partition");
    line("ABI: SDK constants + IRISMAN storage.h wrappers; config SKIPPED: typed SDK API absent / conflicting public signature");
    line("Device discovery: known-ID information queries only, not exhaustive enumeration; only BD is opened");
    uint32_t bd_sector_size = 2048;
    uint8_t info[256] __attribute__((aligned(128)));
    uint64_t ids[] = {PROBE_BD_DEVICE, UINT64_C(0x0101000000000007), UINT64_C(0x010300000000000a), UINT64_C(0x010300000000000b)};
    for (unsigned i = 0; i < sizeof(ids) / sizeof(ids[0]); i++) {
        memset(info, 0, sizeof(info));
        if (!begin("sys_storage_get_device_info")) return;
        rc = probe_storage_info(ids[i], info); ended();
        line("device id=%016llX info_rc=%08X", (unsigned long long)ids[i], (unsigned)rc);
        if (!rc) {
            line("info sectors=%llu sector_size=%u flags_raw_52_55=%02X%02X%02X%02X", (unsigned long long)be64(info + 40), be32(info + 48), info[52], info[53], info[54], info[55]);
            dump("device_info", info, 64);
            if (!i) bd_sector_size = be32(info + 48);
        }
    }
    int bd = -1;
    if (!begin("sys_storage_open BD mode=0 flags=0")) return;
    rc = probe_storage_open(PROBE_BD_DEVICE, &bd); ended();
    line("BD open rc=%08X fd=%d", (unsigned)rc, bd);
    if (!rc) {
        if (bd_sector_size == 2048) {
            read_sector(bd, 16, bd_sector_size); read_sector(bd, 0, bd_sector_size); read_sector(bd, 17, bd_sector_size);
        } else line("2048-byte raw reads skipped: device reported sector size %u", bd_sector_size);
        uint8_t cdb[12] = {0x12, 0, 0, 0, 36};
        if (!atapi(bd, "INQUIRY", cdb, 36)) { dump("inquiry", command_data, 36); line("inquiry vendor=%.8s product=%.16s revision=%.4s", command_data + 8, command_data + 16, command_data + 32); }
        memset(cdb, 0, sizeof(cdb)); (void)atapi(bd, "TEST UNIT READY", cdb, 0);
        memset(cdb, 0, sizeof(cdb)); cdb[0] = 0x46; cdb[8] = 32;
        if (!atapi(bd, "GET CONFIGURATION", cdb, 32)) {
            unsigned profile = ((unsigned)command_data[6] << 8) | command_data[7];
            dump("configuration", command_data, 32);
            line("current_profile=%04X name=%s", profile, profile == 8 ? "CD-ROM" : profile == 0x10 ? "DVD-ROM" : profile == 0x40 ? "BD-ROM" : "other/none (see raw)");
        }
        memset(cdb, 0, sizeof(cdb)); cdb[0] = 0x25;
        if (!atapi(bd, "READ CAPACITY(10)", cdb, 8)) {
            uint32_t last = be32(command_data), size = be32(command_data + 4);
            dump("capacity", command_data, 8);
            line("capacity last_lba=%u block_size=%u total_sectors=%llu", last, size, (unsigned long long)last + 1);
            if (last != UINT32_MAX && size == 2048 && bd_sector_size == 2048) read_sector(bd, last, size);
            else line("last-sector read skipped: capacity invalid/16-byte needed or block size not 2048");
        }
        memset(cdb, 0, sizeof(cdb)); cdb[0] = 0xad; cdb[9] = 32;
        if (!atapi(bd, "READ DISC STRUCTURE DVD physical layer0", cdb, 32)) {
            dump("dvd_structure", command_data, 32);
            unsigned payload = ((unsigned)command_data[0] << 8) | command_data[1];
            if (payload >= 19)
                line("DVD physical book=%X layers=%u track_path=%u start_psn=%u end_psn=%u layer0_end_psn=%u", command_data[4] >> 4, ((command_data[6] >> 5) & 3) + 1, (command_data[6] >> 4) & 1, be24(command_data + 9), be24(command_data + 13), be24(command_data + 17));
            else line("DVD physical response too short/invalid: length=%u", payload);
        }
        cleanup_begin("sys_storage_close BD"); rc = probe_storage_close(bd); ended(); line("BD close rc=%08X", (unsigned)rc);
    }
    filesystem_probe();
}
static void storage_variants(void) {
    uint8_t info[256] __attribute__((aligned(128))) = {0};
    if (!begin("v3 storage device info")) return;
    int rc = probe_storage_info(PROBE_BD_DEVICE, info); ended();
    uint32_t size = be32(info + 48); uint64_t capacity = be64(info + 40);
    line("v3 info rc=%08X sector_size=%u sectors=%llu", (unsigned)rc, size, (unsigned long long)capacity);
    if (rc || size != 2048 || capacity < 18) {
        line("v3 storage SKIP: require confirmed 2048-byte sectors and capacity >=18"); return;
    }
    /* Fresh ordinary open for each count. No retry loop, no flags sweep.
     * Buffer storage stays alive even if a worker call blocks. */
    for (uint32_t requested = 1; requested <= 2 && !atomic_load(&probe_stop); requested++) {
        int fd = -1; uint32_t got = 0;
        if (!begin("v3 fresh sys_storage_open id=0101000000000006 args=(id,0,&fd,0)")) return;
        rc = probe_storage_open(PROBE_BD_DEVICE, &fd); ended();
        line("v3 open rc=%08X handle=%d type=LV2-storage-u32 count=%u", (unsigned)rc, fd, requested);
        if (rc) continue;
        memset(bounce, 0xcc, sizeof(bounce));
        line("v3 READ args=(fd,0,16,%u,buf,&nread,0) buf=%08llX alignment=65536 capacity_bytes=65536", requested, (unsigned long long)(uintptr_t)bounce);
        if (begin("v3 sys_storage_read lba=16 flags=0 aligned=65536")) {
            uint64_t start = probe_now();
            rc = probe_storage_read_count(fd, 16, requested, bounce, &got); ended();
            line("v3 READ rc=%08X sectors_read=%u requested=%u bytes_reported=%llu elapsed_us=%llu",
                 (unsigned)rc, got, requested, (unsigned long long)got * size, (unsigned long long)(probe_now() - start));
            if (!rc && got == requested) {
                dump("v3 sector16", bounce, 64);
                line("v3 PVD signature_01_CD001=%s", !memcmp(bounce, "\x01" "CD001", 6) ? "MATCH" : "NO_MATCH");
            } else line("v3 failed/short/invalid count: buffer not interpreted");
        }
        cleanup_begin("v3 close storage"); rc = probe_storage_close(fd); ended();
        line("v3 close rc=%08X", (unsigned)rc);
    }
}
static int stage_begin(unsigned stage, const char *name) {
    if (atomic_load(&probe_stop)) return 0;
    atomic_store(&probe_stage_deadline, probe_now() + 15000000);
    line("=== STAGE %u BEGIN %s; stage_deadline=15s; operation_deadline=5s ===", stage, name);
    return !atomic_load(&probe_stop);
}
static void stage_end(unsigned stage) {
    line("=== STAGE %u END ===", stage);
    atomic_store(&probe_stage_deadline, 0);
}
void probe_worker(void *unused) {
    (void)unused;
    atomic_store(&probe_deadline, probe_now() + 5000000);
    int mkdir_rc = sysLv2FsMkdir("/dev_hdd0/tmp", 0777);
    ended();
    atomic_store(&probe_deadline, probe_now() + 5000000);
    /* v2 append behavior retained. No stage writes any disc or media file. */
    int rc = sysLv2FsOpen("/dev_hdd0/tmp/ps2disc_probe.log", SYS_O_WRONLY | SYS_O_CREAT | SYS_O_APPEND, &log_handle, 0666, NULL, 0);
    ended(); if (rc) { log_handle = -1; atomic_store(&probe_log_failed, 1); }
    line("=== RUN BEGIN PS2DISC P0C probe v3; selection=%u; log_open_rc=%08X; APPEND; READ ONLY ===", probe_selection, (unsigned)rc);
    line("mkdir tmp rc=%08X; no auth/vendor/control/patch/Cobra calls; flags=0 only", (unsigned)mkdir_rc);
    if ((!probe_selection || probe_selection == 1) && stage_begin(1, "named file reads")) {
        read_file("/dev_bdvd/SYSTEM.CNF");
        /* Existing mount only: never create, remap or mount this path. */
        read_file("/dev_ps2disc/SYSTEM.CNF");
        stage_end(1);
    }
    if ((!probe_selection || probe_selection == 2) && stage_begin(2, "fresh handle / aligned counts")) {
        storage_variants(); stage_end(2);
    }
    if ((!probe_selection || probe_selection == 3) && stage_begin(3, "v2 baseline")) {
        baseline_probe(); stage_end(3);
    }
    line("=== RUN END DONE; log_failed=%d; Triangle/Circle exits; absolute watchdog=60s ===", atomic_load(&probe_log_failed));
    if (log_handle >= 0) { cleanup_begin("close log"); rc = sysLv2FsClose(log_handle); ended(); log_handle = -1; (void)rc; }
    atomic_store_explicit(&probe_done, 1, memory_order_release);
    sysThreadExit(0);
}
