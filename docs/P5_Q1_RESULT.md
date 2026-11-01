# P5 Q1 result (console, 2026-11-01): all 12 map candidates refused (-17)

Build `local_only/p5/ps2_netemu_p5_Q1.self`; log read over FTP and decoded (`local_only/netemu_log_Q1.bin`, 48 records, clean shutdown, ends `all map candidates failed (-17)`).

PROVEN (console): after `open(4,2)` rc 0, every DMA-region allocation was accepted (rc 0, bus address always `0xC0000000`) for (size, page exponent) = (0x100000, 20), (0x100000, 12), (0x80000, 12), (0x100000, 16); every `lv1_map_device_dma_region(4, 2, lpar 0x84000000, bus 0xC0000000, len, flags)` returned `-17` for len 0x100000 / 0x80000 / 0x1000 and flags 0xe000000000000800, 0xe000000000000000, 0xf800000000000000, 0x6000000000000800. All frees and the close returned 0.

Reading: the refusal does not depend on the length, the flags (incl. the official emulators' 0xe000000000000800) or the region's page size. So the refused argument is most likely the LPAR address 0x84000000 itself (the SB_CDVD buffer is not acceptable to LV1 as a DMA target for this device), the device/bus combination, or a state condition (e.g., something the optical device needs before mapping). The stock HDD map (dev 3, LPAR 0x84800000, region 0xd0000000, 0x80000, 0xe000000000000800) works, so the HDD driver's buffer is acceptable for device 3.
Next: decode the 4.93 LV1 handler of HV call 176 to find which check returns -17 (static, local_only/fw493/lv1.elf), and a safe no-DMA experiment (map the HDD driver's buffer LPAR for the optical device, then unmap) to separate "LPAR address" from "device/state".


## CORRECTION (2026-11-01, after P6)

The "swapped fields" diagnosis in this document chain was WRONG. The stock code (P0 static reading: H+0x20 = physical/LPAR address, H+0x28 = CPU address) and the guest address map agree with the ORIGINAL P2D assignment: the value `0x0000500002c00000` read at 0x2458438 (SB_CDVD) is the partition-physical (LPAR) address and `0x84000000` read at 0x2458428 is the CPU effective address (the 0x80000000+ window is where the guest maps its pool/heap: pool descriptors 0x80000000, arena EA 0x8003e140). Passing 0x84000000 as the LPAR address, as the P2E/P4/P5 builds did, is what made lv1_map_device_dma_region return -17 (the LV1 map handler validates the LPAR address; see docs/P6_BUILD_NOTES.md). The labels "BUF_EA / LPARBUF" in the P2C diagnostic simply followed the wrong assumption. The P2D K0 labels (`CDVD LPAR: 0x0000500002c00000`, `CDVD EA: 0x0000000084000000`) were right.
