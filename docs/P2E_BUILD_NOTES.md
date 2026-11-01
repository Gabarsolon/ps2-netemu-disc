# P2E Build Notes: Defect Fix for Buffer EA vs LPAR Swap & Pointer Kind Audit

## Status
- **Date**: 2026-11-01
- **Task**: P2E Defect Fix in P2D build.
- **Trigger**:
  - Console test of K0 on PS3 (`docs/P2D_K0_RESULT.md`):
    - K0 executed cleanly (`P2D-K0 DONE: ALL STEPS OK`, `RC: OP=0 DMA=0 CL=0 HC=130`).
    - Printed values:
      - At `0x2458438`: `0x0000500002c00000`
      - At `0x2458428`: `0x0000000084000000`
      - At `0x2458430`: `0x0000000000100000` (1 MiB)
    - Comparison with measured HDD state (`docs/P2C_RESULT.md`):
      - `H+0x20`: `0x0000500002d00000`
      - `H+0x28`: `0x0000000084800000`
  - **Defect Identified**:
    - The two fields at `0x2458438` and `0x2458428` are SWAPPED relative to P2D's naming!
    - `0x0000500002c00000` is the CPU Effective Address (EA).
    - `0x0000000084000000` is the physical LPAR address.
    - In P2D `probe.c`, `lpar` was loaded from `0x2458438` and `ea` from `0x2458428`. If K1..K3 ran, it would pass an EA to `lv1_map_device_dma_region` (LV1 176) and attempt to write ATAPI command blocks through `0x84000000`, causing a fatal crash/fault!
    - K0 was unaffected because K0 does not use or map the buffer.

---

## 1. Static Reverse Engineering: Root Cause of Address Inversion

(In progress: re-verifying `0x19a5c`, `0x19900`, `0x1622c`, `0x133c80`, `0x12c010` via PyGhidra).
