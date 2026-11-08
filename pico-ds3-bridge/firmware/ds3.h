#pragma once
#include <stdbool.h>
#include <stdint.h>

extern const uint8_t ds3_report_descriptor[148];

void ds3_identity(const uint8_t address[6]);
void ds3_session_reset(uint32_t now, bool auto_ps);
void ds3_session_configured(uint32_t now);
void ds3_activation_tick(uint32_t now);
void ds3_request_ps(uint32_t now);
void ds3_set_auto_ps(bool enable);
bool ds3_streaming(void);
bool ds3_send_allowed(uint32_t now);
bool ds3_ps_value(uint32_t now);
void ds3_input_acked(bool ps);

uint16_t ds3_feature_get(uint8_t id, uint8_t *out, uint16_t capacity);
bool ds3_feature_set(uint8_t id, const uint8_t *data, uint16_t len);
bool ds3_output(uint8_t id, const uint8_t *data, uint16_t len, uint32_t now,
                uint8_t *small, uint8_t *large);
