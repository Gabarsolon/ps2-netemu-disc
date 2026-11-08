#include <string.h>
#include "tusb.h"
#include "ds3.h"

#define USB_VID   0x054C
#define USB_PID   0x0268

tusb_desc_device_t const desc_device =
{
    .bLength            = sizeof(tusb_desc_device_t),
    .bDescriptorType    = TUSB_DESC_DEVICE,
    .bcdUSB             = 0x0200,
    .bDeviceClass       = 0x00,
    .bDeviceSubClass    = 0x00,
    .bDeviceProtocol    = 0x00,
    .bMaxPacketSize0    = 64,

    .idVendor           = USB_VID,
    .idProduct          = USB_PID,
    .bcdDevice          = 0x0100,

    .iManufacturer      = 0x01,
    .iProduct           = 0x02,
    .iSerialNumber      = 0x00,

    .bNumConfigurations = 0x01
};

uint8_t const * tud_descriptor_device_cb(void) {
  return (uint8_t const *) &desc_device;
}

// 41-byte DS3 Clean Configuration Descriptor
// 1 HID interface, Interrupt OUT 0x02 (64 bytes, 1ms), Interrupt IN 0x81 (64 bytes, 1ms)
static const uint8_t ds3_configuration[] = {
  // Configuration descriptor: 9 bytes
  0x09, TUSB_DESC_CONFIGURATION, 41, 0x00, 1, 1, 0, 0x80, 250, // 500mA
  // Interface descriptor: 9 bytes
  0x09, TUSB_DESC_INTERFACE, 0, 0, 2, TUSB_CLASS_HID, 0, 0, 0,
  // HID descriptor: 9 bytes
  0x09, HID_DESC_TYPE_HID, 0x11, 0x01, 0, 1, HID_DESC_TYPE_REPORT, 148, 0x00,
  // Endpoint In: 7 bytes
  0x07, TUSB_DESC_ENDPOINT, 0x81, TUSB_XFER_INTERRUPT, 64, 0x00, 1,
  // Endpoint Out: 7 bytes
  0x07, TUSB_DESC_ENDPOINT, 0x02, TUSB_XFER_INTERRUPT, 64, 0x00, 1
};

uint8_t const * tud_descriptor_configuration_cb(uint8_t index) {
  (void) index;
  return ds3_configuration;
}

uint8_t const * tud_hid_descriptor_report_cb(uint8_t instance) {
  (void) instance;
  return ds3_report_descriptor;
}

// String Descriptors
static char const *string_desc_arr[] = {
  (const char[]) { 0x09, 0x04 }, // English (0x0409)
  "Sony",                        // 1: Manufacturer
  "PLAYSTATION(R)3 Controller",  // 2: Product
};

static uint16_t _desc_str[40];

uint16_t const* tud_descriptor_string_cb(uint8_t index, uint16_t langid) {
  (void) langid;
  uint8_t chr_count;

  if (index == 0) {
    memcpy(&_desc_str[1], string_desc_arr[0], 2);
    chr_count = 1;
  } else {
    if (index >= sizeof(string_desc_arr)/sizeof(string_desc_arr[0])) return NULL;
    const char* str = string_desc_arr[index];
    chr_count = (uint8_t) strlen(str);
    if (chr_count > 39) chr_count = 39;
    for (uint8_t i = 0; i < chr_count; i++) {
      _desc_str[1 + i] = str[i];
    }
  }

  _desc_str[0] = (uint16_t)((TUSB_DESC_STRING << 8) | (2 * chr_count + 2));
  return _desc_str;
}

// Callbacks implemented in main.c
uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t* buffer, uint16_t reqlen);
void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type, uint8_t const* buffer, uint16_t bufsize);

void tud_hid_set_protocol_cb(uint8_t instance, uint8_t protocol) {
  (void) instance; (void) protocol;
}
