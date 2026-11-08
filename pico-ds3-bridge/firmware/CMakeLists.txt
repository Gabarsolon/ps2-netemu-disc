set(target_name pico_ds3_serial)

get_target_property(device_sources tinyusb_device_base INTERFACE_SOURCES)
list(FILTER device_sources EXCLUDE REGEX "/device/usbd(_control)?\\.c$")
list(FILTER device_sources EXCLUDE REGEX "/class/hid/hid_device\\.c$")
list(APPEND device_sources 
  "${CMAKE_CURRENT_LIST_DIR}/../../buzz-pico-adapter/firmware_source/tinyusb_runtime/usbd.c"
  "${CMAKE_CURRENT_LIST_DIR}/../../buzz-pico-adapter/firmware_source/tinyusb_runtime/usbd_control.c"
  "${CMAKE_CURRENT_LIST_DIR}/../../buzz-pico-adapter/firmware_source/tinyusb_runtime/hid_device.c"
)
set_property(TARGET tinyusb_device_base PROPERTY INTERFACE_SOURCES "${device_sources}")

include_directories(${CMAKE_CURRENT_LIST_DIR} ${PICO_TINYUSB_PATH}/src/device)

add_executable(${target_name})

target_sources(${target_name} PRIVATE
  main.c
  usb_descriptors.c
  ds3.c
  usb_hooks.c
)

target_link_options(${target_name} PRIVATE -Xlinker --print-memory-usage)
target_compile_options(${target_name} PRIVATE -Wall -Wextra)
target_include_directories(${target_name} PRIVATE 
  ${CMAKE_CURRENT_LIST_DIR}
  ${PICO_TINYUSB_PATH}/src/device
)
target_link_libraries(${target_name} PRIVATE pico_stdlib pico_unique_id hardware_uart tinyusb_device)
pico_add_extra_outputs(${target_name})
