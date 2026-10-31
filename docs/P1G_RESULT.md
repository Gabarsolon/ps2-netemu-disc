# P1g result (console, 2026-10-31): the netemu partition CAN open and close the optical drive

Builds `local_only/p1g/ps2_netemu_p1g_G0..G3.self` (generic hypercall wrapper that keeps the stock helper's exact prologue/epilogue; one `sc` at 0x4858). Labels as reported by the owner, one run each, no disc inserted, no console shutdown in any run:

| Variant | Call | Result (PROVEN, console) |
|---|---|---|
| G0 | repository read of bus 4 / dev 2 type through the generic wrapper | `rc=0`, `v=5 (ROM)`, MATCH with the stock helper |
| G1 | `lv1_open_device(9, 0, 0)` (invalid bus) | `rc=0xffffffef (-17) INVALID_PARAMETER` |
| G2 | `lv1_close_device(4, 2)` without an open | `rc=0xfffffff5 (-11) NOT_OWNER` |
| G3 | `lv1_open_device(4, 2, 0)` on the optical node, then `lv1_close_device(4, 2)` | open `rc=0 SUCCESS`, close `rc=0 SUCCESS` |

## Reading
- **PROVEN:** the ps2_netemu partition may open and close the BD drive device (bus 4, dev 2) from its own code, with the drive empty. The hypervisor accepted both calls, and the partition did not die. The earlier crashes (P1b, P1d-A, P1e) were caused by our hand-written wrapper, not by LV1 or the drive. Return codes match the 4.93 LV1 static analysis (-17 for an invalid bus, -11 for a close by a non-holder).
- **UNKNOWN:** behaviour with a PS2 disc inserted; whether DMA setup, device commands and sector reads work from this partition (the P0I finding that `PS2_NE_LPAR` leaves the physical bus unpowered is still untested: opening was fine, a data transfer may not be); whether PS2 media data reads need the secure-service authentication (virtual UART 10, service 0x5000 op 0x5005, as softemu does).
- Next: run G3 once with the PS2 DVD inserted; then P2 stages (DMA region, device queries, one sector read), see docs\P2_PLAN.md.
