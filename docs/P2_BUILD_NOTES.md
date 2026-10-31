# P2 Build Notes: Netemu Optical Read Stages (H0..H3)

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P2 ps2_netemu optical read diagnostic probe build — staged label-only diagnostic variants (H0..H3) from "can open the optical drive" to "can read a sector". Validate on PC, do not install.

---

## 1. Verified Hypercall Numbers in Official 4.93 LV1

Verified against `local_only/fw493/lv1.elf` (SHA-256 `e8d0b532adf6ba6c6c1ea40a5c5b86407abe11ea7a3ab8624ca5b09d3e4c3d6b`):

| Number | Hex | Registration | Descriptor | Handler Entry | Official / Linux Name | Verified in 4.93 LV1 Table |
|---|---|---|---|---|---|---|
| **91** | `0x5b` | `0x3c26b0` | — | `0x111eb8` (stock) | `lv1_read_repository_node` | Yes |
| **170** | `0xaa` | `0x3c2910` | `0x34f6c8` | `0x305a38` | `lv1_open_device` | Yes |
| **171** | `0xab` | `0x3c2920` | `0x34f830` | `0x306eec` | `lv1_close_device` | Yes |
| **174** | `0xae` | `0x3c2950` | `0x34f7e8` | `0x306a6c` | `lv1_allocate_device_dma_region` | Yes |
| **175** | `0xaf` | `0x3c2960` | `0x34f7d0` | `0x306918` | `lv1_free_device_dma_region` | Yes |
| **176** | `0xb0` | `0x3c2970` | `0x34f7b8` | `0x306770` | `lv1_map_device_dma_region` | Yes |
| **177** | `0xb1` | `0x3c2980` | `0x34f7a0` | `0x30660c` | `lv1_unmap_device_dma_region` | Yes |
| **245** | `0xf5` | `0x3c2aa0` | `0x34fbc0` | `0x308b88` | `lv1_storage_read` | Yes |
| **248** | `0xf8` | `0x3c2ac0` | `0x34fc68` | `0x3094e4` | `lv1_storage_send_device_command` | Yes |
| **249** | `0xf9` | `0x3c2ad0` | `0x34fc50` | `0x3093ac` | `lv1_storage_get_async_status` | Yes |
| **254** | `0xfe` | `0x3c2ae0` | `0x34fc38` | `0x30926c` | `lv1_storage_check_async_status` | Yes |

---

## 2. Generic Wrapper Extension (`lv1_hcall`)

The generic safe wrapper at `0x4800` (180 bytes) preserves the stock helper (`0x111eb8`) prologue and epilogue discipline exactly:
- Stock helper has 45 instructions.
- 29 instructions remain byte-for-byte identical to stock.
- The wrapper argument setup maps C parameters `num, a1, a2, a3, a4, a5, a6` to hypercall registers `r11, r3, r4, r5, r6, r7, r8`:
  - `0x24: mr r11, r3` (num -> r11)
  - `0x28: mr r3, r4`  (a1 -> r3)
  - `0x38: mr r4, r5`  (a2 -> r4)
  - `0x3C: mr r5, r6`  (a3 -> r5)
  - `0x40: mr r6, r7`  (a4 -> r6)
  - `0x44: mr r7, r8`  (a5 -> r7)
  - `0x48: mr r8, r9`  (a6 -> r8, opcode `0x7D284B78` replacing unused stock nop slot)
  - `0x4C: nop`
  - `0x50: nop`
  - `0x54: oris r11, r11, 0x8000` (hypercall flag)
  - `0x58: sc 0`
- On return:
  - Stores `r4` into `raw_val1` (`0x930F70`)
  - Stores `r5` into `raw_val2` (`0x930F78`)
  - Restores all non-volatile registers `r14..r29, r30, r31`, `CR` fields `cr2..cr4`, and `LR`.
  - Returns `rc` in `r3`.

---

## 3. Buffer Allocation Design: Stock Allocator Shim `0x19a5c`

### Disassembly and Call Chain
The stock HDD driver initializes its DMA buffer at `0x12c010`:
```text
0x12bff8: ld r3, -0x6f20(r2)    ; ptr to "SB_HDD" (0x300c70)
0x12bffc: addi r5, r30, 0x20    ; &p_ea
0x12c000: addi r6, r1, 0x80     ; &p_lpar
0x12c004: li r0, 0
0x12c008: lis r4, 0x10          ; size = 0x100000 (1 MiB)
0x12c00c: std r0, 0x80(r1)
0x12c010: bl 0x00019a5c
0x12c014: nop
0x12c018: ld r0, 0x80(r1)       ; loads returned LPAR address
```
Chain:
1. `0x19a5c(name, size, &ea, &lpar)`: Checks max size (`size <= 0x800000`), sets page flags, branches to `0x19900`.
2. `0x19900`: Rounds size up to 1 MiB boundary (`0x100000`), calls `0x1622c(align=20, size, &lpar)`.
3. `0x1622c`: Reads global heap block at `-0x7e50(r2)`, aligns allocation cursor at `0x58(r31)`, checks limits, and returns real LPAR address in `r3`. No mutex or reentrancy issues on the main emulator thread.
4. `0x19984`: Obtains base EA, updates mapped EA cursor at `-0x7b30(r2)`, calls `0x16790` (page-table mapping helper) with `(name, ea, lpar, size, prot)`.
5. Returns `0` on success, with `*p_ea` holding CPU address and `*p_lpar` holding physical LPAR address.

### Design Choice
- We call `0x19a5c("SB_OPT", 0x100000, &ea, &lpar)` via trampoline `alloc_buffer` at `0x4910`.
- Trampoline sets stock TOC (`0x751280`).
- Because our probe runs strictly ONCE (`STATUS_STARTED` flag), it allocates one separate 1 MiB buffer once.
- Does not touch or map memory owned by the HDD driver.
- Command block (64 bytes) is placed at `ea + 0` (`lpar + 0`).
- Data buffer (up to 2048 bytes) is placed at `ea + 0x1000` (`lpar + 0x1000`).

---

## 4. ATAPI Command Block (`struct lv1_atapi_cmnd_block`, 64 bytes)

Matched with Linux `drivers/scsi/ps3rom.c` and 3.55 `ps2_softemu.elf` (`0x88c88..0x88d54`):
- `+0x00..0x1F`: 32-byte CDB (`pkt[32]`)
- `+0x20..0x23`: `pktlen` = 12
- `+0x24..0x27`: `blocks` (transfer count or blocks)
- `+0x28..0x2B`: `block_size` (1 for byte-counted PIO, 2048 for sector DMA)
- `+0x2C..0x2F`: `proto` (0=NON_DATA, 1=PIO_DATA_IN, 3=DMA_DATA_IN)
- `+0x30..0x33`: `in_out` (0=WRITE/NONE, 1=READ)
- `+0x34..0x3F`: Padding / zero (12 bytes)

Commands:
- **TEST UNIT READY (0x00)**: CDB 12 bytes 0, `pktlen=12, blocks=0, block_size=1, proto=0, in_out=0, data=0, size=0`.
- **INQUIRY (0x12)**: CDB `pkt[0]=0x12, pkt[4]=36`, `pktlen=12, blocks=36, block_size=1, proto=1, in_out=1, data=lpar+0x1000, size=36`.
- **READ CAPACITY (0x25)**: CDB `pkt[0]=0x25`, `pktlen=12, blocks=8, block_size=1, proto=1, in_out=1, data=lpar+0x1000, size=8`.

---

## 5. Polling Loop and Timebase Bound

- Hypercall 254 (`storage_check_async_status`) is polled in a loop.
- Bound 1: 200,000 loop iterations.
- Bound 2: 160,000,000 timebase ticks (~2.0 seconds at ~79.8 MHz timebase frequency), measured via `native_clock()` (`0xb9cd0`, `mftb r3`).
- If `rc == 0`, command is complete: `raw_val1` is recorded as `status`.
- If timeout: abort immediately without `unmap`, without `free`, without `close`.

---

## 6. Staged Diagnostic Variants

- **H0**: `open(4,2,0)` -> LV1 174 `allocate_device_dma_region(4,2, 0x80000, 12, 0)` -> LV1 175 `free_device_dma_region(4,2, dma_region)` -> `close(4,2)`.
- **H1**: H0 + `alloc_buffer("SB_OPT", 0x100000)` + LV1 176 `map_device_dma_region(4,2, lpar, dma_region, 0x80000, flags)` + LV1 177 `unmap_device_dma_region` before free.
- **H2**: H1 + TUR (opcode 0) + INQUIRY (opcode 0x12, 36 bytes) with bounded poll loop.
- **H3**: H2 + READ CAPACITY (opcode 0x25, 8 bytes) + LV1 245 `storage_read` for sector 16 (1 sector, region from repository/HDD default, lba 16) with bounded poll loop.

---

## 7. Mailbox Layout (192 bytes at `0x930F20..0x930FE0`)

All offsets verified in `stock.elf` (193 contiguous zero bytes at `0x930F20..0x930FE1`):
- `+0x00`: `status` (u32)
- `+0x04`: `total_devices` (u32)
- `+0x08`: `rom_count` (u32)
- `+0x0C`: `hdd_found` (u32)
- `+0x10`: `flags` (u32)
- `+0x14`: `total_hypercalls` (u32)
- `+0x18`: `first_err_rc` (u32)
- `+0x1C`: `step_failed` (u32)
- `+0x20`: `rom_bus_idx, rom_dev_idx, rom_port, storage_bus_idx` (4 bytes)
- `+0x24`: `hdd_bus_idx, hdd_dev_idx, hdd_port, phat_match` (4 bytes)
- `+0x28`: `stock_rc` (s32)
- `+0x2C`: `open_rc` (s32)
- `+0x30`: `dma_alloc_rc` (s32)
- `+0x34`: `map_rc` (s32)
- `+0x38`: `tur_send_rc` (s32)
- `+0x3C`: `tur_poll_rc` (s32)
- `+0x40`: `inq_send_rc` (s32)
- `+0x44`: `inq_poll_rc` (s32)
- `+0x48`: `cap_send_rc` (s32)
- `+0x4C`: `cap_poll_rc` (s32)
- `+0x50`: `read_send_rc` (s32)
- `+0x54`: `read_poll_rc` (s32)
- `+0x58`: `unmap_rc` (s32)
- `+0x5C`: `free_rc` (s32)
- `+0x60`: `close_rc` (s32)
- `+0x64`: `alloc_shim_rc` (s32)
- `+0x68`: `rom_bus_id` (u64, offset 64)
- `+0x70`: `raw_val1` (u64, offset 80 -> `0x930F70`)
- `+0x78`: `raw_val2` (u64, offset 88 -> `0x930F78`)
- `+0x80`: `buf_lpar` (u64)
- `+0x88`: `buf_ea` (u64)
- `+0x90`: `dma_region` (u64)
- `+0x98`: `dma_bus_addr` (u64)
- `+0xA0`: `tur_status` (u64)
- `+0xA8`: `inq_status` (u64)
- `+0xB0`: `cap_status` (u64)
- `+0xB8`: `read_status` (u64)

---

## 8. Build Artifacts & Cryptographic Verification

All four variants were built using `netemu_p2/build.py` and written to `local_only/p2/`. Each SELF was roundtrip-decrypted using `selfdec.py` and compared byte-for-byte against the input ELF. Every variant passed byte-for-byte verification.

| Variant | ELF SHA-256 | SELF SHA-256 | SELF Decrypt Match | Code Size / Limit |
|---|---|---|---|---|
| **H0** | `32ad3d91e7d9e977ec41e88686c8638983847898004f951da4cf0f0ce15e5ab6` | `16f23922a0e8d4ce91775bb648c6f1ea3362dc585f8c01e25c065915c5b1c95f` | **100% IDENTICAL** | 2,712 / 14,320 bytes (18.9%) |
| **H1** | `eba023050ff1bda7a36f190a17b7ef14b29a68e3f4fa15d00a7bf603e07af649` | `e7c8b6666754b9738f83ccf1b6957278b11265b156dc72f7e4b7fe6a87e3fe85` | **100% IDENTICAL** | 3,032 / 14,320 bytes (21.2%) |
| **H2** | `da637bd53c960aa6caff52985f39261742160cc1af97dce4f2aac50886489c48` | `13c3eeb2a62d478591fa3e39dd3f54abf3977b6461e2e4254307fd42aec08062` | **100% IDENTICAL** | 3,824 / 14,320 bytes (26.7%) |
| **H3** | `9b599ddadf19aa3c7cb2ffc6ba0fff7be0fc48ab64fdf975af28100066aad10e` | `45c4aef6585beb09592d9c30576be084cc3c1b2fa0110a00597ba104d9760088` | **100% IDENTICAL** | 4,200 / 14,320 bytes (29.3%) |

---

## 9. PC Validation Results (`netemu_p2/validate_pc.py`)

All tests in `netemu_p2/validate_pc.py` passed 100%:

1. **Instruction Discipline & Wrapper Integrity**:
   - Exactly 29 instructions in `lv1_hcall` match stock `0x111eb8`.
   - `sc 0` located strictly at `0x4858`.
   - `mr r8, r9` placed at `0x4848`.
2. **Register Preservation**:
   - Verified across wrapper execution: non-volatile registers `r14..r29`, `r30`, `r31`, condition fields `cr2..cr4`, `LR`, and parameter registers `r8` (6th argument) are 100% preserved.
3. **Exact Call Sequence Verification**:
   - H0: `[170, 174, 175, 171]`
   - H1: `[170, 174, 176, 177, 175, 171]`
   - H2: `[170, 174, 176, 248, 254, 248, 254, 177, 175, 171]`
   - H3: `[170, 174, 176, 248, 254, 248, 254, 248, 254, 245, 254, 177, 175, 171]`
4. **Bounded Polling**:
   - Successfully polled with simulated completion delays (e.g. 3 polls).
5. **Timeout Safety**:
   - On mock timeouts, verified immediate abort **WITHOUT** unmapping, freeing, or closing.
6. **Disc Absent & Authentication Handling**:
   - Disc absent status (`0x02023a00`) handled gracefully with clean shutdown of DMA regions.
   - Disc authentication error (`0x02052100` / `0x8001002F` / `ENXIO`) handled cleanly without crash.
7. **Error Propagation**:
   - Immediate halt on early open failure without running subsequent stages.
8. **Once-Only Lazy Execution**:
   - Subsequent menu calls made 0 new hypercalls.
9. **Memory Store Audit**:
   - Proved that our code strictly writes only to stack, mailbox `[0x930F20, 0x930FE0)`, and command block `[BUF, BUF + 68]`.
   - Verified that our code **NEVER** writes to the data buffer `[BUF + 0x1000, BUF + 0x80000]`.
10. **Label Bounds Fuzzing**:
    - Fuzzed all 137 Page A strings per variant; all within 64-byte bounds with zero-byte termination.
11. **Strict Store Audit (`tools/p1a_audit.py`)**:
    - Confirmed exactly one `sc` instruction in each ELF at `0x4858` (syscall 0).
12. **Installer Syntax**:
    - Parse-checked `tools/install_netemu.ps1` and `tools/restore_netemu.ps1` without execution.

---

## 10. Open Problems & UNKNOWNs

1. **Hardware Authentication Requirement on Live PS2 Media**:
   - LV2 tests under GameOS revealed that standard sector reads return `ENXIO` / `0x02052100` until authenticated.
   - It is unknown whether the drive firmware enforces this authentication inside the `ps2_netemu` partition, or if CFW/Cobra/GameOS leaves the drive in a state where sectors can be read directly. H3 Test 4B will definitively answer this.
2. **Stock Allocator Shim Reentrancy**:
   - While `0x19a5c` allocates memory cleanly on the main thread, netemu partition state at the moment the menu hook fires has not previously called `0x19a5c` after initialization. Because `STATUS_STARTED` guarantees exactly one allocation, heap exhaustion is not a factor.
3. **Drive Sleep / Power Down**:
   - If the drive spindle has spun down before the PS button menu is opened, the 2-second timeout bound could potentially expire before the drive spins up. For this reason, inserting the disc shortly before launching or testing is advised.

