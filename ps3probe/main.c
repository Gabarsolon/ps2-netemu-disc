/* SPDX-License-Identifier: MIT. GCM/pad/guard flow adapted from owner Buzz app.
 * CPU paints pixels, then copies to RSX display buffers. All GPU waits bounded. */
#include "probe.h"
#include "ui_layout.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <sys/process.h>
#include <sys/thread.h>
#include <sys/timer.h>
#include <sysutil/video.h>
#include <cell/gcm.h>
#include <cell/sysutil.h>
#include <io/pad.h>

SYS_PROCESS_PARAM(1100, 0x100000);
PS3TC_HEAP_SIZE(UINT64_C(80) * 1024 * 1024);
static uint64_t absolute_deadline;
static atomic_int process_exit_request, menu_open;
static unsigned width, height, pitch, current, pending, label_value;
static uint32_t *buffers[2], *software, offsets[2];
static int pad_owned, registered;
static ui_layout layout;
static uint64_t exit_requested_at;
static void event(uint64_t status, uint64_t parameter, void *unused) {
    (void)parameter; (void)unused;
    if (status == CELL_SYSUTIL_REQUEST_EXITGAME) atomic_store(&process_exit_request, 1);
    if (status == CELL_SYSUTIL_SYSTEM_MENU_OPEN) atomic_store(&menu_open, 1);
    if (status == CELL_SYSUTIL_SYSTEM_MENU_CLOSE) atomic_store(&menu_open, 0);
}
static int pump(void) {
    if (registered && cellSysutilCheckCallback()) atomic_store(&process_exit_request, 1);
    return !atomic_load(&process_exit_request);
}
/* Never logs or acquires libc/file/RSX locks. Kernel-wide hangs cannot be cured
 * by a userspace watchdog; a blocked storage worker is never joined. */
static void guard(void *unused) {
    (void)unused;
    for (;;) {
        sys_timer_usleep(50000);
        uint64_t now = probe_now(), operation = atomic_load(&probe_deadline);
        uint64_t stage = atomic_load(&probe_stage_deadline);
        if (now >= absolute_deadline || (operation && now >= operation) || (stage && now >= stage)) {
            atomic_store(&probe_timed_out, 1); atomic_store(&probe_stop, 1);
            atomic_store(&process_exit_request, 1);
            sys_timer_usleep(250000);
            sysProcessExit(2);
        }
        if (atomic_load(&process_exit_request)) {
            /* main normally performs pad/callback cleanup first. */
            if (!exit_requested_at) exit_requested_at = now;
            if (now - exit_requested_at > 1500000) sysProcessExit(0);
        }
    }
}
static int wait_flip(void) {
    if (!pending) return 0;
    uint64_t until = probe_now() + 2000000;
    while (cellGcmGetFlipStatus()) {
        if (!pump() || probe_now() >= until) return -1;
        sys_timer_usleep(1000);
    }
    cellGcmResetFlipStatus(); pending = 0; return 0;
}
static int drain(void) {
    CellGcmContextData *ctx = CELL_GCM_CURRENT;
    uint32_t expected = ++label_value;
    cellGcmSetWriteBackEndLabel(ctx, 255, expected); cellGcmFlush(ctx);
    volatile uint32_t *label = (volatile uint32_t *)cellGcmGetLabelAddress(255);
    if (!label) return -1;
    uint64_t until = probe_now() + 2000000;
    while (*label != expected) {
        if (!pump() || probe_now() >= until) return -1;
        sys_timer_usleep(1000);
    }
    return 0;
}
static int video_init(void) {
    void *host = memalign(1024 * 1024, 32u * 1024 * 1024);
    if (!host || cellGcmInit(0x100000, 32u * 1024 * 1024, host)) return -1;
    for (unsigned i = 0; i < 2; i++) {
        buffers[i] = rsxMemalign(64, 1920u * 1080 * 4);
        if (!buffers[i] || cellGcmAddressToOffset(buffers[i], &offsets[i])) return -1;
    }
    software = malloc(1920u * 1080 * 4); if (!software) return -1;
    videoState state = {0}; videoResolution resolution = {0}; videoConfiguration cfg = {0};
    if (videoGetState(0, 0, &state) || videoGetResolution(state.displayMode.resolution, &resolution) ||
        resolution.width < 640 || resolution.width > 1920 || resolution.height < 480 || resolution.height > 1080) return -1;
    width = resolution.width; height = resolution.height; pitch = width * 4;
    cfg.resolution = state.displayMode.resolution; cfg.format = VIDEO_BUFFER_FORMAT_XRGB;
    cfg.pitch = pitch; cfg.aspect = state.displayMode.aspect;
    if (videoConfigure(0, &cfg, NULL, 0)) return -1;
    uint64_t until = probe_now() + 2000000;
    do {
        if (videoGetState(0, 0, &state) || !pump() || probe_now() >= until) return -1;
        if (state.state != VIDEO_STATE_BUSY) break;
        sys_timer_usleep(1000);
    } while (1);
    cellGcmSetFlipMode(GCM_FLIP_VSYNC); cellGcmResetFlipStatus();
    for (unsigned i = 0; i < 2; i++)
        if (cellGcmSetDisplayBuffer(i, offsets[i], pitch, width, height)) return -1;
    ui_layout_init(&layout, width, height, cfg.aspect == VIDEO_ASPECT_16_9, state.displayMode.scanMode == VIDEO_SCANMODE_INTERLACE);
    return 0;
}
static int frame(const char *text, const char *status) {
    if (!pump()) return -1;
    if (atomic_load(&menu_open)) return 0;
    if (wait_flip() || drain()) return -1;
    ui_view view = {0}; ui_result result;
    view.title = status; view.text = text; view.page = -1;
    ui_canvas canvas = {software, (int)width, NULL, NULL};
    if (ui_render(&layout, &view, &canvas, &result)) return -1;
    memcpy(buffers[current], software, (size_t)pitch * height);
    atomic_thread_fence(memory_order_seq_cst);
    CellGcmContextData *ctx = CELL_GCM_CURRENT;
    cellGcmResetFlipStatus();
    if (cellGcmSetFlip(ctx, current)) return -1;
    cellGcmSetWaitFlip(ctx); cellGcmFlush(ctx);
    current ^= 1; pending = 1; return 0;
}
int main(void) {
    absolute_deadline = probe_now() + 60000000;
    sys_ppu_thread_t thread;
    if (sysThreadCreate(&thread, guard, NULL, 900, 0x10000, 0, "ps2disc_guard")) sysProcessExit(1);
    if (cellSysutilRegisterCallback(0, event, NULL)) sysProcessExit(1);
    registered = 1;
    if (video_init()) sysProcessExit(1);
    pad_owned = !ioPadInit(7);
    /* Cheap launch selector, no settings files. No choice within 10s runs all.
     * Selection time is included in the original absolute 60s guard. */
    uint64_t select_until = probe_now() + 10000000;
    unsigned select_previous[7] = {0};
    static const char *choices[] = {"ALL: files, storage, v2 baseline", "1: named file reads only",
                                    "2: fresh handle / aligned reads only", "3: v2 baseline only"};
    int selected = 0;
    while (probe_now() < select_until && !atomic_load(&process_exit_request) && !selected) {
        if (pad_owned && !atomic_load(&menu_open)) for (int p = 0; p < 7; p++) {
            padData data = {0}; if (ioPadGetData(p, &data) || data.len <= 0) continue;
            unsigned buttons = (data.BTN_LEFT ? 1u : 0u) | (data.BTN_RIGHT ? 2u : 0u) |
                               (data.BTN_CROSS ? 4u : 0u) | ((data.BTN_CIRCLE || data.BTN_TRIANGLE) ? 8u : 0u);
            unsigned pressed = buttons & ~select_previous[p]; select_previous[p] = buttons;
            if (pressed & 1) probe_selection = (probe_selection + 3) % 4;
            if (pressed & 2) probe_selection = (probe_selection + 1) % 4;
            if (pressed & 4) selected = 1;
            if (pressed & 8) atomic_store(&process_exit_request, 1);
        }
        char menu[512];
        snprintf(menu, sizeof(menu), "Left/Right: select stage\nCross: start; Circle/Triangle: exit\n\n%s\n\nStarts selected choice in %llus.\nRead-only; five-second call guard.", choices[probe_selection],
                 (unsigned long long)(probe_now() < select_until ? (select_until - probe_now() + 999999) / 1000000 : 0));
        if (frame(menu, "PS2 Disc Probe v3 - stage selection")) atomic_store(&process_exit_request, 1);
        sys_timer_usleep(50000);
    }
    if (atomic_load(&process_exit_request)) sysProcessExit(0);
    if (sysThreadCreate(&thread, probe_worker, NULL, 1200, 0x20000, 0, "ps2disc_worker")) sysProcessExit(1);
    unsigned previous[7] = {0}; int scroll = 0;
    while (!atomic_load(&process_exit_request)) {
        unsigned count = atomic_load_explicit(&probe_line_count, memory_order_acquire);
        if (pad_owned && !atomic_load(&menu_open)) for (int p = 0; p < 7; p++) {
            padData data = {0}; if (ioPadGetData(p, &data) || data.len <= 0) continue;
            unsigned buttons = (data.BTN_CIRCLE || data.BTN_TRIANGLE ? 1u : 0u) |
                               (data.BTN_UP ? 2u : 0u) | (data.BTN_DOWN ? 4u : 0u);
            unsigned pressed = buttons & ~previous[p]; previous[p] = buttons;
            if (pressed & 1) { atomic_store(&probe_stop, 1); atomic_store(&process_exit_request, 1); }
            if ((pressed & 2) && scroll < (int)count - 1) scroll++;
            if ((pressed & 4) && scroll) scroll--;
        }
        char text[6000] = "Starting read-only drive checks...", status[192];
        unsigned rows = (unsigned)(layout.lines > 4 ? layout.lines - 4 : 1);
        unsigned end = count > (unsigned)scroll ? count - (unsigned)scroll : 0;
        unsigned start = end > rows ? end - rows : 0;
        if (count) {
            size_t used = 0; text[0] = 0;
            for (unsigned i = start; i < end && used + PROBE_LINE_LENGTH < sizeof(text); i++) {
                int n = snprintf(text + used, sizeof(text) - used, "%.*s\n", layout.columns, probe_lines[i]);
                if (n > 0) used += (size_t)n;
            }
        }
        uint64_t now = probe_now();
        snprintf(status, sizeof(status), "%s | %s | auto-exit %llus",
                 atomic_load(&probe_done) ? "Finished: log ready" : "Reading inserted disc",
                 atomic_load(&probe_log_failed) ? "LOG FAILED; screen continues" : "/dev_hdd0/tmp/ps2disc_probe.log",
                 (unsigned long long)(now < absolute_deadline ? (absolute_deadline - now + 999999) / 1000000 : 0));
        if (frame(text, status)) break;
        sys_timer_usleep(50000);
    }
    atomic_store(&probe_stop, 1); atomic_store(&process_exit_request, 1);
    /* Allow cooperative close on normal user exit; never join a blocked syscall. */
    uint64_t until = probe_now() + 500000;
    while (!atomic_load(&probe_done) && probe_now() < until) sys_timer_usleep(10000);
    if (pad_owned) ioPadEnd();
    if (registered) cellSysutilUnregisterCallback(0);
    sysProcessExit(atomic_load(&probe_timed_out) ? 2 : 0);
    return 0;
}
