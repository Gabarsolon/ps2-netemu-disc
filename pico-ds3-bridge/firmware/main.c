#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "pico/bootrom.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "tusb.h"
#include "ds3.h"

#define UART_ID         uart0
#define BAUD_RATE       115200
#define UART_TX_PIN     0
#define UART_RX_PIN     1
#define LED_PIN         25

// DS3 Digital Button Masks
#define BTN_SELECT      (1u << 0)
#define BTN_L3          (1u << 1)
#define BTN_R3          (1u << 2)
#define BTN_START       (1u << 3)
#define BTN_UP          (1u << 4)
#define BTN_RIGHT       (1u << 5)
#define BTN_DOWN        (1u << 6)
#define BTN_LEFT        (1u << 7)
#define BTN_L2          (1u << 8)
#define BTN_R2          (1u << 9)
#define BTN_L1          (1u << 10)
#define BTN_R1          (1u << 11)
#define BTN_TRIANGLE    (1u << 12)
#define BTN_CIRCLE      (1u << 13)
#define BTN_CROSS       (1u << 14)
#define BTN_SQUARE      (1u << 15)

#define TOTAL_BUTTONS   16

static uint16_t current_buttons = 0;
static bool current_ps = false;
static uint8_t stick_lx = 128;
static uint8_t stick_ly = 128;
static uint8_t stick_rx = 128;
static uint8_t stick_ry = 128;

// Auto-release timers (ms)
static uint32_t btn_release_time[TOTAL_BUTTONS] = {0};
static uint32_t ps_release_time = 0;

static uint32_t now_ms(void) {
    return (uint32_t)(time_us_64() / 1000);
}

static void build_ds3_report(uint8_t report[48], uint32_t now) {
    memset(report, 0, 48);

    // Digital buttons (wire byte 2 and 3)
    report[1] = (uint8_t)current_buttons;
    report[2] = (uint8_t)(current_buttons >> 8);

    // PS Button (wire byte 4, bit 0)
    if (current_ps || ds3_ps_value(now)) {
        report[3] |= 0x01;
    }

    // Analog Sticks (128 = center)
    report[5] = stick_lx;
    report[6] = stick_ly;
    report[7] = stick_rx;
    report[8] = stick_ry;

    // Pressure analog bytes (13..24):
    // D-pad Up, Right, Down, Left, L2, R2, L1, R1, Triangle, Circle, Cross, Square
    for (int i = 0; i < 12; i++) {
        if (current_buttons & (1u << (4 + i))) {
            report[13 + i] = 0xFF;
        }
    }

    // Battery and connection status
    report[28] = 2; // cable plugged in
    report[29] = 5; // battery full
    report[30] = 0x10;
    for (int i = 40; i < 48; i += 2) {
        report[i] = 2; report[i + 1] = 0;
    }
}

// Map button string to bitmask
static int parse_button(const char *name) {
    if (!name) return -1;
    char upper[32];
    size_t len = strlen(name);
    if (len >= sizeof(upper)) len = sizeof(upper) - 1;
    for (size_t i = 0; i < len; i++) upper[i] = (char)toupper((unsigned char)name[i]);
    upper[len] = '\0';

    if (!strcmp(upper, "CROSS") || !strcmp(upper, "X")) return 14;
    if (!strcmp(upper, "CIRCLE") || !strcmp(upper, "O")) return 13;
    if (!strcmp(upper, "TRIANGLE") || !strcmp(upper, "TRI")) return 12;
    if (!strcmp(upper, "SQUARE") || !strcmp(upper, "SQ")) return 15;
    if (!strcmp(upper, "UP")) return 4;
    if (!strcmp(upper, "DOWN")) return 6;
    if (!strcmp(upper, "LEFT")) return 7;
    if (!strcmp(upper, "RIGHT")) return 5;
    if (!strcmp(upper, "START")) return 3;
    if (!strcmp(upper, "SELECT")) return 0;
    if (!strcmp(upper, "L1")) return 10;
    if (!strcmp(upper, "R1")) return 11;
    if (!strcmp(upper, "L2")) return 8;
    if (!strcmp(upper, "R2")) return 9;
    if (!strcmp(upper, "L3")) return 1;
    if (!strcmp(upper, "R3")) return 2;
    if (!strcmp(upper, "PS")) return 99; // Special code for PS button

    return -1;
}

static void release_all(void) {
    current_buttons = 0;
    current_ps = false;
    stick_lx = 128;
    stick_ly = 128;
    stick_rx = 128;
    stick_ry = 128;
    for (int i = 0; i < TOTAL_BUTTONS; i++) btn_release_time[i] = 0;
    ps_release_time = 0;
}

// Process serial command line
static void process_command(char *cmd) {
    while (*cmd == ' ' || *cmd == '\t') cmd++;
    if (*cmd == '\0') return;

    char *saveptr = NULL;
    char *action = strtok_r(cmd, " \r\n", &saveptr);
    if (!action) return;

    char upper_action[32];
    size_t alen = strlen(action);
    if (alen >= sizeof(upper_action)) alen = sizeof(upper_action) - 1;
    for (size_t i = 0; i < alen; i++) upper_action[i] = (char)toupper((unsigned char)action[i]);
    upper_action[alen] = '\0';

    uint32_t now = now_ms();

    if (!strcmp(upper_action, "PRESS")) {
        char *btn_name = strtok_r(NULL, " \r\n", &saveptr);
        char *dur_str = strtok_r(NULL, " \r\n", &saveptr);
        int dur = dur_str ? atoi(dur_str) : 120;
        if (dur < 20) dur = 20;

        int b = parse_button(btn_name);
        if (b == 99) {
            current_ps = true;
            ps_release_time = now + dur;
            char out[64];
            snprintf(out, sizeof(out), "OK PRESS PS %dms\r\n", dur);
            uart_puts(UART_ID, out);
        } else if (b >= 0 && b < TOTAL_BUTTONS) {
            current_buttons |= (1u << b);
            btn_release_time[b] = now + dur;
            char out[64];
            snprintf(out, sizeof(out), "OK PRESS %s %dms\r\n", btn_name, dur);
            uart_puts(UART_ID, out);
        } else {
            uart_puts(UART_ID, "ERR UNKNOWN_BUTTON\r\n");
        }
    } else if (!strcmp(upper_action, "DOWN")) {
        char *btn_name = strtok_r(NULL, " \r\n", &saveptr);
        int b = parse_button(btn_name);
        if (b == 99) {
            current_ps = true;
            ps_release_time = 0;
            uart_puts(UART_ID, "OK DOWN PS\r\n");
        } else if (b >= 0 && b < TOTAL_BUTTONS) {
            current_buttons |= (1u << b);
            btn_release_time[b] = 0;
            char out[64];
            snprintf(out, sizeof(out), "OK DOWN %s\r\n", btn_name);
            uart_puts(UART_ID, out);
        } else {
            uart_puts(UART_ID, "ERR UNKNOWN_BUTTON\r\n");
        }
    } else if (!strcmp(upper_action, "UP")) {
        char *btn_name = strtok_r(NULL, " \r\n", &saveptr);
        int b = parse_button(btn_name);
        if (b == 99) {
            current_ps = false;
            ps_release_time = 0;
            uart_puts(UART_ID, "OK UP PS\r\n");
        } else if (b >= 0 && b < TOTAL_BUTTONS) {
            current_buttons &= ~(1u << b);
            btn_release_time[b] = 0;
            char out[64];
            snprintf(out, sizeof(out), "OK UP %s\r\n", btn_name);
            uart_puts(UART_ID, out);
        } else {
            uart_puts(UART_ID, "ERR UNKNOWN_BUTTON\r\n");
        }
    } else if (!strcmp(upper_action, "STICK")) {
        char *which = strtok_r(NULL, " \r\n", &saveptr);
        char *x_str = strtok_r(NULL, " \r\n", &saveptr);
        char *y_str = strtok_r(NULL, " \r\n", &saveptr);
        if (which && x_str && y_str) {
            int x = atoi(x_str);
            int y = atoi(y_str);
            if (x < 0) x = 0;
            if (x > 255) x = 255;
            if (y < 0) y = 0;
            if (y > 255) y = 255;

            if (toupper((unsigned char)which[0]) == 'L') {
                stick_lx = (uint8_t)x;
                stick_ly = (uint8_t)y;
            } else {
                stick_rx = (uint8_t)x;
                stick_ry = (uint8_t)y;
            }
            uart_puts(UART_ID, "OK STICK\r\n");
        } else {
            uart_puts(UART_ID, "ERR USAGE: STICK <L|R> <X> <Y>\r\n");
        }
    } else if (!strcmp(upper_action, "PS")) {
        current_ps = true;
        ps_release_time = now + 300;
        uart_puts(UART_ID, "OK PS 300ms\r\n");
    } else if (!strcmp(upper_action, "RELEASE") || !strcmp(upper_action, "RESET")) {
        release_all();
        uart_puts(UART_ID, "OK RELEASE\r\n");
    } else if (!strcmp(upper_action, "BOOTSEL")) {
        uart_puts(UART_ID, "OK REBOOTING_TO_BOOTSEL\r\n");
        sleep_ms(50);
        reset_usb_boot(0, 0);
    } else if (!strcmp(upper_action, "AUTO_PS")) {
        char *val = strtok_r(NULL, " \r\n", &saveptr);
        if (val && atoi(val) == 1) {
            ds3_set_auto_ps(true);
            uart_puts(UART_ID, "OK AUTO_PS 1\r\n");
        } else {
            ds3_set_auto_ps(false);
            uart_puts(UART_ID, "OK AUTO_PS 0\r\n");
        }
    } else if (!strcmp(upper_action, "STATUS")) {
        char out[128];
        bool ps_active = current_ps || ds3_ps_value(now);
        snprintf(out, sizeof(out), "STATUS mounted=%d streaming=%d btns=0x%04X ps=%d sticks=[%d,%d,%d,%d]\r\n",
                 tud_mounted(), ds3_streaming(), current_buttons, ps_active ? 1 : 0, stick_lx, stick_ly, stick_rx, stick_ry);
        uart_puts(UART_ID, out);
    } else {
        uart_puts(UART_ID, "ERR UNKNOWN_COMMAND\r\n");
    }
}

// HID Callbacks
void tud_hid_report_complete_cb(uint8_t instance, uint8_t const* report, uint16_t len) {
    (void) instance;
    if (len == 49 && report[0] == 1) {
        ds3_input_acked((report[4] & 1) != 0);
    }
}

uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t* buffer, uint16_t reqlen) {
    (void) instance;
    if (report_type == HID_REPORT_TYPE_FEATURE) {
        uint16_t n = ds3_feature_get(report_id, buffer, reqlen);
        char msg[64];
        snprintf(msg, sizeof(msg), "[DS3] GET_FEATURE 0x%02X (%u bytes)\r\n", report_id, n);
        uart_puts(UART_ID, msg);
        return n;
    }
    if (report_type == HID_REPORT_TYPE_INPUT && report_id == 1) {
        uint8_t rep[48];
        build_ds3_report(rep, now_ms());
        uint16_t n = reqlen < 48 ? reqlen : 48;
        memcpy(buffer, rep, n);
        return n;
    }
    return 0;
}

void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t const* buffer, uint16_t bufsize) {
    (void) instance;
    if (report_type == HID_REPORT_TYPE_FEATURE) {
        bool ok = ds3_feature_set(report_id, buffer, bufsize);
        char msg[64];
        snprintf(msg, sizeof(msg), "[DS3] SET_FEATURE 0x%02X (%u bytes) ok=%d\r\n", report_id, bufsize, ok);
        uart_puts(UART_ID, msg);
        if (ds3_streaming()) {
            uart_puts(UART_ID, "[DS3] PS3 Handshake Complete! Streaming ACTIVE\r\n");
        }
    } else if (report_type == HID_REPORT_TYPE_OUTPUT) {
        uint8_t small = 0, large = 0;
        if (ds3_output(report_id, buffer, bufsize, now_ms(), &small, &large)) {
            if (small || large) {
                char msg[64];
                snprintf(msg, sizeof(msg), "[DS3] RUMBLE small=%u large=%u\r\n", small, large);
                uart_puts(UART_ID, msg);
            }
        }
    }
}

void tud_mount_cb(void) {
    ds3_session_configured(now_ms());
    uart_puts(UART_ID, "[DS3] USB MOUNTED on Host!\r\n");
}

void tud_umount_cb(void) {
    ds3_session_reset(now_ms(), false);
    uart_puts(UART_ID, "[DS3] USB UNMOUNTED\r\n");
}

int main(void) {
    stdio_init_all();

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 0);

    // Initialize UART0 (GP0 = TX, GP1 = RX) at 115200 baud
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    // Set genuine MAC from board ID
    pico_unique_board_id_t board_id;
    pico_get_unique_board_id(&board_id);
    uint8_t mac[6] = {0x02, board_id.id[2], board_id.id[3], board_id.id[4], board_id.id[5], board_id.id[6]};
    ds3_identity(mac);
    ds3_session_reset(0, false);

    // Initialize TinyUSB Device stack on native USB
    tusb_rhport_init_t dev_init = {
        .role = TUSB_ROLE_DEVICE,
        .speed = TUSB_SPEED_AUTO
    };
    tusb_init(0, &dev_init);

    sleep_ms(100);
    uart_puts(UART_ID, "\r\n=======================================================\r\n");
    uart_puts(UART_ID, "[Pico 2] DualShock 3 Serial Bridge Active!\r\n");
    uart_puts(UART_ID, "Commands: PRESS <btn> [ms] | DOWN <btn> | UP <btn> | PS\r\n");
    uart_puts(UART_ID, "Buttons: CROSS, CIRCLE, SQUARE, TRIANGLE, UP, DOWN, LEFT, RIGHT\r\n");
    uart_puts(UART_ID, "         L1, R1, L2, R2, L3, R3, START, SELECT, PS\r\n");
    uart_puts(UART_ID, "=======================================================\r\n");

    char cmd_buf[128];
    uint8_t cmd_idx = 0;
    uint32_t last_report_time = 0;
    uint32_t last_blink_time = 0;
    bool led_state = false;

    while (1) {
        tud_task();
        uint32_t now = now_ms();

        // 1. Process UART Serial Input
        while (uart_is_readable(UART_ID)) {
            char c = (char)uart_getc(UART_ID);
            if (c == '\r' || c == '\n') {
                if (cmd_idx > 0) {
                    cmd_buf[cmd_idx] = '\0';
                    process_command(cmd_buf);
                    cmd_idx = 0;
                }
            } else if (cmd_idx < sizeof(cmd_buf) - 1) {
                cmd_buf[cmd_idx++] = c;
            }
        }

        // 2. Check Auto-Release Timers
        for (int i = 0; i < TOTAL_BUTTONS; i++) {
            if (btn_release_time[i] && (int32_t)(now - btn_release_time[i]) >= 0) {
                current_buttons &= ~(1u << i);
                btn_release_time[i] = 0;
            }
        }
        if (ps_release_time && (int32_t)(now - ps_release_time) >= 0) {
            current_ps = false;
            ps_release_time = 0;
        }

        // 3. Periodic DS3 activation tick (for PS3 auto-assignment)
        ds3_activation_tick(now);

        // Monitor PS button transitions and log to UART
        static bool last_logged_ps = false;
        bool ps_now = current_ps || ds3_ps_value(now);
        if (ps_now != last_logged_ps) {
            last_logged_ps = ps_now;
            uart_puts(UART_ID, ps_now ? "[DS3] PS BUTTON PRESSED\r\n" : "[DS3] PS BUTTON RELEASED\r\n");
        }

        // 4. Send DS3 HID Report at 100 Hz (every 10ms) whenever USB is mounted
        if (now - last_report_time >= 10) {
            last_report_time = now;

            if (tud_mounted() && tud_hid_ready()) {
                uint8_t report[48];
                build_ds3_report(report, now);
                tud_hid_report(1, report, 48);
            }
        }

        // 5. LED Status Indicator
        uint32_t blink_rate = ds3_streaming() ? 1000 : (tud_mounted() ? 500 : 150);
        if (now - last_blink_time >= blink_rate) {
            last_blink_time = now;
            led_state = !led_state;
            gpio_put(LED_PIN, led_state);
        }
    }

    return 0;
}
