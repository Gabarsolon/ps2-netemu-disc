#pragma once
#include "tusb.h"

#define DS3_T_SETUP   0x01
#define DS3_T_DATA    0x02
#define DS3_T_ACK     0x04
#define DS3_T_STALL   0x08
#define DS3_T_ERROR   0x10
#define DS3_T_SKIPPED 0x20
#define DS3_T_BUS_RST 0x40

void modec_usb_setup(const tusb_control_request_t *request);
void modec_usb_data(const uint8_t *data, uint16_t len, uint16_t offset);
void modec_usb_flags(uint8_t flags);
void modec_usb_reset(void);
bool modec_hid_feature_request(const tusb_control_request_t *request);
bool modec_hid_feature_control(uint8_t rhport, uint8_t stage, const tusb_control_request_t *request);
void bridge_ds3_bus_reset(void);
