/* Numeric ABI adapters, independently written from public ABI facts.
 * Sources and SDK limitations: README.md. No write/control adapters exist here. */
#ifndef PS2DISC_STORAGE_ABI_H
#define PS2DISC_STORAGE_ABI_H
#include <stdint.h>
#include <stddef.h>
#include <sys/lv2_syscall.h>
#include <lv2/syscalls.h>
#define PROBE_BD_DEVICE UINT64_C(0x0101000000000006)
typedef struct __attribute__((packed)) {
    uint8_t packet[32];
    uint32_t packet_length, blocks, block_size, protocol, direction, reserved;
} probe_atapi;
_Static_assert(sizeof(probe_atapi) == 56, "public LV2 ATAPI ABI size");
_Static_assert(offsetof(probe_atapi, packet_length) == 32, "ATAPI ABI offset");
static inline int probe_storage_info(uint64_t id, void *info) {
    lv2syscall2(SYSCALL_STORAGE_GET_DEVICE_INFO, id, (uint64_t)(uintptr_t)info);
    return_to_user_prog(int);
}
static inline int probe_storage_open(uint64_t id, int *handle) {
    lv2syscall4(SYSCALL_STORAGE_OPEN, id, 0, (uint64_t)(uintptr_t)handle, 0);
    return_to_user_prog(int);
}
static inline int probe_storage_close(int handle) {
    lv2syscall1(SYSCALL_STORAGE_CLOSE, handle);
    return_to_user_prog(int);
}
/* IRISMAN storage.h: count is variable, mode and final flags are both zero.
 * LV1's region/flag parameters are a different ABI; do not substitute them. */
static inline int probe_storage_read_count(int handle, uint32_t lba, uint32_t sectors,
                                           void *buffer, uint32_t *count) {
    lv2syscall7(SYSCALL_STORAGE_READ, handle, 0, lba, sectors,
               (uint64_t)(uintptr_t)buffer, (uint64_t)(uintptr_t)count, 0);
    return_to_user_prog(int);
}
static inline int probe_storage_read(int handle, uint32_t lba, void *buffer, uint32_t *count) {
    return probe_storage_read_count(handle, lba, 1, buffer, count);
}
static inline int probe_storage_atapi(int handle, probe_atapi *command, void *data, uint64_t *aux) {
    lv2syscall7(SYSCALL_STORAGE_EXECUTE_DEVICE_COMMAND, handle, 1,
               (uint64_t)(uintptr_t)command, sizeof(*command),
               (uint64_t)(uintptr_t)data, command->block_size, (uint64_t)(uintptr_t)aux);
    return_to_user_prog(int);
}
#endif
