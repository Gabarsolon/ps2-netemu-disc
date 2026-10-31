# P2b result (console, 2026-10-31; both runs with the PS2 disc inserted)

| Variant | Result (PROVEN, console) |
|---|---|
| H0 | `P2-H0 DONE ALL OK (STEPS COMPLETE)`: open, `lv1_allocate_device_dma_region(4,2,...)`, free, close all `rc=0`; DMA region id >= 8. No shutdown. |
| H1 | `P2-H1 FAIL ALLOC_SHIM rc=RESOURCE_SHORTAGE (-2)`, "data: alloc shim failed": the PRE-GUARD refused to call the stock allocator shim 0x19a5c for a 1 MiB buffer (the shim itself was not called: no hypercall was issued after the failure). No shutdown. |

## Reading
- **PROVEN:** from the netemu partition the optical device accepts open and a DMA region allocation; the guard-protected buffer step stopped cleanly.
- **PROVEN:** the pre-guard decided that the stock heap block (0x930F80) has less than 1 MiB left (cursor + 0x100000 > limit) or the guard misreads the block. The static estimate "about 9 MiB free" in docs\P2B_BUILD_NOTES.md was therefore wrong or the fields were misinterpreted: UNKNOWN which.
- **UNKNOWN:** the actual heap cursor/limit values. Next: a hypercall-free diagnostic that shows them (and the EA mapping cursor), then choose a buffer strategy (smaller block via the allocator, a different physically backed region, or sharing the HDD driver's buffer only with proof it is idle).
