#include <string.h>
#include "ds3.h"

const uint8_t ds3_report_descriptor[148] = {
  0x05, 0x01, 0x09, 0x04, 0xa1, 0x01, 0xa1, 0x02, 0x85, 0x01, 0x75, 0x08, 0x95, 0x01,
  0x15, 0x00, 0x26, 0xff, 0x00, 0x81, 0x03, 0x75, 0x01, 0x95, 0x13, 0x15, 0x00, 0x25,
  0x01, 0x35, 0x00, 0x45, 0x01, 0x05, 0x09, 0x19, 0x01, 0x29, 0x13, 0x81, 0x02, 0x75,
  0x01, 0x95, 0x0d, 0x06, 0x00, 0xff, 0x81, 0x03, 0x15, 0x00, 0x26, 0xff, 0x00, 0x05,
  0x01, 0x09, 0x01, 0xa1, 0x00, 0x75, 0x08, 0x95, 0x04, 0x35, 0x00, 0x46, 0xff, 0x00,
  0x09, 0x30, 0x09, 0x31, 0x09, 0x32, 0x09, 0x35, 0x81, 0x02, 0xc0, 0x05, 0x01, 0x75,
  0x08, 0x95, 0x27, 0x09, 0x01, 0x81, 0x02, 0x75, 0x08, 0x95, 0x30, 0x09, 0x01, 0x91,
  0x02, 0x75, 0x08, 0x95, 0x30, 0x09, 0x01, 0xb1, 0x02, 0xc0, 0xa1, 0x02, 0x85, 0x02,
  0x75, 0x08, 0x95, 0x30, 0x09, 0x01, 0xb1, 0x02, 0xc0, 0xa1, 0x02, 0x85, 0xee, 0x75,
  0x08, 0x95, 0x30, 0x09, 0x01, 0xb1, 0x02, 0xc0, 0xa1, 0x02, 0x85, 0xef, 0x75, 0x08,
  0x95, 0x30, 0x09, 0x01, 0xb1, 0x02, 0xc0, 0xc0
};

static uint8_t host_mac[6];
static uint8_t device_mac[6] = {0x02, 0x50, 0x49, 0x43, 0x4f, 0x32};
static uint8_t ef_byte = 0xa0;

static bool streaming = false;
static bool automatic_ps = false;
static bool configured = false;
static bool auto_done = false;
static bool ps_pending = false;
static uint32_t auto_at = 0;
static uint32_t ps_until = 0;

void ds3_identity(const uint8_t address[6]) {
  memcpy(device_mac, address, 6);
}

void ds3_set_auto_ps(bool enable) {
  automatic_ps = enable;
}

void ds3_session_reset(uint32_t now, bool auto_ps) {
  (void)now;
  streaming = false;
  automatic_ps = auto_ps;
  configured = false;
  auto_done = false;
  ps_pending = false;
  ps_until = 0;
}

void ds3_session_configured(uint32_t now) {
  configured = true;
  auto_at = now + 1500;
  auto_done = false;
  streaming = false;
  ps_pending = false;
}

static void ps_pulse(uint32_t now) {
  ps_pending = true;
  ps_until = now + 250;
  auto_done = true;
}

void ds3_request_ps(uint32_t now) {
  ps_pulse(now);
}

void ds3_activation_tick(uint32_t now) {
  if (configured && automatic_ps && !auto_done && (int32_t)(now - auto_at) >= 0) {
    ps_pulse(now);
  }
}

bool ds3_streaming(void) {
  return streaming;
}

bool ds3_send_allowed(uint32_t now) {
  (void)now;
  return streaming || ps_pending;
}

bool ds3_ps_value(uint32_t now) {
  if (ps_pending && (int32_t)(now - ps_until) >= 0) {
    ps_pending = false;
  }
  return ps_pending || (streaming && (int32_t)(now - ps_until) < 0);
}

void ds3_input_acked(bool ps) {
  if (ps) ps_pending = false;
}

uint16_t ds3_feature_get(uint8_t id, uint8_t *out, uint16_t cap) {
  uint8_t b[64] = {0};
  uint16_t n = 64;

  switch (id) {
    case 0x01: {
      const uint8_t prefix[] = {
        1, 4, 0, 0x0b, 0x0c, 1, 2, 0x18, 0x18, 0x18, 0x18, 9, 0x0a, 0x10, 0x11, 0x12,
        0x13, 0, 0, 0, 0, 4, 0, 2, 2, 2, 2, 0, 0, 0, 4, 4, 4, 4, 0, 0, 4, 0, 1, 2, 7, 0, 0x17
      };
      memcpy(b + 1, prefix, sizeof(prefix));
      break;
    }
    case 0xf2: {
      const uint8_t firmware[] = {0, 3, 0x55, 0x43, 0xc3, 1, 0x8a, 0};
      b[0] = 0xf2;
      b[1] = 255;
      b[2] = 255;
      memcpy(b + 4, device_mac, 6);
      memcpy(b + 10, firmware, sizeof(firmware));
      break;
    }
    case 0xf5:
      b[0] = 1;
      memcpy(b + 2, host_mac, 6);
      break;
    case 0xef:
      b[1] = 0xef; b[2] = 4; b[4] = 0x0b; b[5] = 3; b[6] = 1; b[7] = ef_byte;
      if (ef_byte == 0xa0) {
        for (unsigned i = 17; i < 33; i += 4) {
          b[i] = 2; b[i+1] = 0; b[i+2] = 1; b[i+3] = 0x8f;
        }
        b[31] = 0; b[32] = 0x7f;
      } else if (ef_byte == 0xb0) {
        b[17] = 2; b[18] = 0x6c; b[19] = 2; b[20] = 0x6e;
      }
      b[48] = 6;
      break;
    case 0xf7: {
      const uint8_t prefix[] = {1, 0, 8, 2, 0xdc, 1, 0xee, 255, 0, 0, 0};
      memcpy(b, prefix, sizeof(prefix));
      break;
    }
    case 0xf8:
      ds3_feature_get(0xef, b, sizeof(b));
      b[0] = 0; b[1] = 1; b[2] = 0; b[3] = 0;
      break;
    default:
      return 0;
  }

  if (n > cap) n = cap;
  memcpy(out, b, n);
  return n;
}

bool ds3_feature_set(uint8_t id, const uint8_t *p, uint16_t n) {
  if (n > 1 && p[0] == id) { p++; n--; }
  if (id == 0xf5 && n >= 8) { memcpy(host_mac, p + 2, 6); return true; }
  if (id == 0xef && n >= 7 && p[4] == 3 && p[5] == 1) { ef_byte = p[6]; return true; }
  if (id == 0xf4 && n >= 4 && p[0] == 0x42 && p[2] == 0 && p[3] == 0) {
    if (p[1] == 0x0c) { streaming = true; return true; }
    if (p[1] == 0x0b) { streaming = false; ps_pending = false; return true; }
  }
  return false;
}

bool ds3_output(uint8_t id, const uint8_t *p, uint16_t n, uint32_t now,
                uint8_t *small, uint8_t *large) {
  (void)now;
  if (id == 0) {
    if (!n || p[0] != 1) return false;
    p++; n--;
  }
  if (n < 5) return false;
  *small = p[2];
  *large = p[4];
  return true;
}
