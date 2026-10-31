# P1c Build Notes: Optical vs HDD Repository Dumper

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1c ps2_netemu.self probe: dump all repository fields of optical node (type 5, bus 4 dev 2) and HDD node (bus 4 dev 3 type 0 port 2), validate on PC, do NOT install.
- **Rules**: Read-only repository calls (LV1 91) only. No open (170/171) or other hypercalls. Stores strictly in mailbox, allocator arena, or stack.

---

## 1. Step 1 Static Verification (PROVEN via pyghidra on stock.elf)
- Stock ELF SHA256: `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`.
- Stock SELF SHA256: `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`.
- Verified TOC entries used by enumerator `0x114ea4`:
  - `TOC -0x7af0 (0x749790)`: `0x300960` -> `'bus'`
  - `TOC -0x7ae8 (0x749798)`: `0x3009f0` -> `'dev'`
  - `TOC -0x7ae0 (0x7497a0)`: `0x300388` -> `'id'`
  - `TOC -0x7ad8 (0x7497a8)`: `0x3009f8` -> `'type'`
  - `TOC -0x7ad0 (0x7497b0)`: `0x300a00` -> `'port'`
  - `TOC -0x7ac8 (0x7497b8)`: `0x300a08` -> `'pci_bus'`
  - `TOC -0x7ac0 (0x7497c0)`: `0x300a10` -> `'pci_dev'`
  - `TOC -0x7ab8 (0x7497c8)`: `0x300a18` -> `'pci_fun'`
  - `TOC -0x7ab0 (0x7497d0)`: `0x300a20` -> `'intr'`
  - `TOC -0x7aa8 (0x7497d8)`: `0x300a28` -> `'reg'`
  - `TOC -0x7aa0 (0x7497e0)`: `0x300628` -> `'data'`
  - `TOC -0x7a98 (0x7497e8)`: `0x300a30` -> `'meddling'`
  - `TOC -0x7a90 (0x7497f0)`: `0x300a40` -> `'blk_size'`
  - `TOC -0x7a88 (0x7497f8)`: `0x300a50` -> `'n_blocks'`
  - `TOC -0x7a80 (0x749800)`: `0x300a60` -> `'n_regs'`
  - Bus-level string: `0x300a68` -> `'num_dev'`
- Region keys check:
  - No `region` or `access_right` string exists in `stock.elf` (confirmed via whole-ELF byte searches; prompt rule respected: do not invent key names).
- HDD init at `0x12be04`:
  - Verified it reads `bus/4/id`, enumerates bus 4, dev 0, type 0, port 2.
- Native allocator `0xB9848`:
  - Calling convention: `native_alloc(size, 3, 0)`.
  - Lazy pool check verified:
    - Base address pointer at `0x934980`.
    - Descriptor checks: `*(u64*)0x24565b8 == base`, `*(u64*)0x2446588 == base + 0x20000`.
    - Returned address must be 64-byte aligned and within `[base + 0x20000, base + 0x20000 + 0x40000)`.
- Mailbox `0x930F20..0x930F80`:
  - Verified 100% zero in `stock.elf` (96 bytes).
- Hook site `0x270FFC`:
  - Expected word verified: `0xe882cea8` (`ld r4, -0x3158(r2)`).
- Marker string `0x304EC0`:
  - Verified string: `"Debug Information\0"`.

---

## 2. P1c Architecture & Design
- **Mailbox Layout (96 bytes at `0x930F20`)**:
  - `0x00`: `u32 status` (STARTED, DONE, ALLOC_OK, ALLOC_FAIL)
  - `0x04`: `u32 total_hypercalls`
  - `0x08`: `u32 rom_count`
  - `0x0c`: `u32 hdd_found`
  - `0x10`: `u32 first_err_rc`
  - `0x14`: `u32 bank` (0..5)
  - `0x18`: `u32 last_selected` (0..3, or 0xFF)
  - `0x1c`: `u32 pad1`
  - `0x20`: `u64 arena_ptr` (allocated 4 KiB buffer)
  - `0x28`: `u8 rom_bus_idx, rom_dev_idx, rom_port, hdd_bus_idx, hdd_dev_idx, hdd_port, pad2[2]`
  - `0x30`: `u64 rom_bus_id`
  - `0x38`: `u64 rom_dev_id`
  - `0x40`: `u64 hdd_bus_id`
  - `0x48`: `u64 hdd_dev_id`
  - `0x50..0x5f`: `u64 reserved[2]`
- **Arena Layout (4 KiB allocated at `0xB9848`)**:
  - Contains array of `struct FieldRecord { s64 rc; u64 v1; u64 v2; }` (24 bytes each).
  - Holds 20 records for Optical node (bus 4, dev 2), 20 records for HDD node (bus 4, dev 3), and 3 records for Bus 4.
  - Total: 43 records x 24 bytes = 1,032 bytes (fits in 4 KiB).
- **Pager (24 Pages across 6 Banks)**:
  - Rows 0..3 within each menu view select subpages 0..3.
  - Scrolling through rows 0 -> 1 -> 2 -> 3 -> 0 advances the bank (0..5).
  - Reverse scrolling (0 -> 3) decrements the bank.
  - Page 0: Summary (`P00 P1C DONE rom=1 hdd=1 ids 4/2`)
  - Pages 1..22: Pairwise comparison of Optical and HDD fields.
  - Page 23: Bus 4 bus-level keys (`type`, `id`, `num_dev`).
- **Immutable String Tables**:
  - Padded to 32 bytes per string.
  - Exhaustively bounded indices (mathematically impossible to go out of bounds).
  - Total extended RO data size: ~205 KB (well below 445 KB of P1b and 726 KB of Buzz).
