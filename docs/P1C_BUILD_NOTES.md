# P1c Build Notes: Optical vs HDD Repository Dumper

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1c ps2_netemu.self probe: dump all repository fields of optical node (type 5) and HDD node (bus 4 dev 3 type 0 port 2), validate on PC, do NOT install.
- **Rules**: Read-only repository calls (LV1 91) only. No open (170/171) or other hypercalls. Stores strictly in mailbox, allocator arena, or stack.

---

## 1. Goal & Requirements
- Read all repository fields for:
  - Optical node: Bus 4, Dev 2 (ROM, type 5, port 0, IDs 4/2)
  - HDD node: Bus 4, Dev 3 (DISK, type 0, port 2)
- Compare their repository properties to investigate why `open_device` on the optical node killed the partition in P1b.
- Only LV1 call 91 via stock helper `0x111eb8` / key encoder `0x111f6c`.
- Dynamic allocation: Native allocator `0xB9848` `(size, 3, 0)` with pool validation against `0x934980` / `0x24565b8`, allocating a 4 KiB arena. Pointer kept in mailbox.
- Label display: Compact format for TV readout via `Debug Information` menu row hook at `0x270FFC`. Multi-page pager stepping through optical & HDD fields.
- PC validation: pyghidra `EmulatorHelper`, store target audit, zero sc other than LV1 91, SELF round-trip byte-for-byte exact.
