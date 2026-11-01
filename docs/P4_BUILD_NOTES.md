# P4 Build Notes: Durable Write-Ahead HDD Logger Integration into K0..K3

## Status
- **Date**: 2026-11-01
- **Task**: P4 - Merge the durable in-place HDD logger from P3B into optical read probe variants K0..K3.
- **Core Objective**: Implement durable write-ahead logging (WAL) directly to `/dev_hdd0/tmp/netemu_log.bin` so that test execution results are captured durably on disk without requiring photos or video capture.
- **Base Components**:
  - Proven HDD logging engine from `netemu_p3b` (`src/hddlog.c`, `src/hddlog.h`), confirmed functional on console (`docs/P3B_RESULT.md`).
  - Defect-fixed optical probe logic from `netemu_p2e` (correct EA/LPAR mapping, symmetric sanity guard, bounded polling, single `sc` instruction).

---

## 1. Architecture & Write-Ahead Protocol

### 1.1 Pre-allocated In-Place File Structure
- **Target File**: `/dev_hdd0/tmp/netemu_log.bin` (opened via stock UFS as `"/tmp/netemu_log.bin"`).
- **Size**: Exactly 65,536 bytes (128 sectors of 512 bytes).
- **Sector 0: Log Header (512 bytes)**:
  - Magic: `0x4E4554454D554C47` (`NETEMULG`).
  - Version: `0x00010000` (1.0).
  - Next Record Index: `1..127` (write cursor). Reset to `1` at `hddlog_init` to start a new, clean log session per boot/test.
  - Boot TB (`boot_tb`): 64-bit hardware timebase captured at initialization, serving as a unique session/boot ID.
  - Shutdown Status: `0` (active / uncommitted / crash marker), set to `1` upon clean completion (`TAG_END`).
  - Record Count: count of records written during the current session.
- **Sectors 1..127: Log Records (512 bytes each)**:
  - Magic: `0x4C4F4752` (`LOGR`).
  - Sequence: Monotonically increasing counter (`1, 2, ...`).
  - Tag: 32-bit ASCII tag (`BOOT`, `SCAN`, `GRD `, `PRE `, `POST`, `TMO `, `END `).
  - Flags: 32-bit status flags.
  - Timestamp TB: 64-bit timebase tick from `native_clock()`.
  - Param A (`a`): 64-bit primary argument or result.
  - Param B (`b`): 64-bit secondary argument or telemetry.
  - Boot ID (`boot_id`): 64-bit boot timebase matching Sector 0 header. Used by decoder to filter out stale records from earlier runs.
  - Text: 440 bytes NUL-terminated human-readable diagnostic message.

### 1.2 Write-Ahead Logging (WAL) Sequence
To detect the exact instruction or hypercall causing a fault, netemu logs BEFORE every risky operation:
1. `BOOT`: Variant identifier (`K0`, `K1`, `K2`, `K3`), code size, compile variant.
2. `SCAN`: Repository scan results (`rom_count`, `hdd_found`, `dev_bus`, `dev_id`).
3. `GRD `: Symmetric sanity guard check results (`LPAR`, `EA`, `SZ`).
4. For every hypercall step (`OPEN`, `DMA_ALLOC`, `MAP`, `TUR`, `INQ`, `CAP`, `READ`, `UNMAP`, `FREE`, `CLOSE`):
   - **`PRE `**: Logged **BEFORE** issuing the hypercall. Records step name, target device/bus, and memory pointers. Flushed to disk.
   - *Hypercall executes*
   - **`POST`**: Logged **AFTER** the hypercall returns. Records return code `rc`, async completion status, elapsed ticks, and returned data payload (e.g. INQUIRY vendor string, capacity LBA/block size, or sector bytes).
5. `END `: Logged upon completion of the probe sequence with overall summary.
6. **Crash Detection**: If a hypercall hangs the CPU or triggers a machine check / partition termination, the log file retains the `PRE ` record on physical disk. The reader flags any `PRE ` without a matching `POST` as the **Crash Site**.

### 1.3 Concurrency & Drive Idle Safety Preconditions
The logger re-checks the stock HDD singleton `H` (`0x241c850`) before every file access:
- `H[0x85] == 1` (driver ready / enabled)
- `H[0x78] == 0` (no driver fault)
- `*(u64*)(H + 0x10) == 3` (device id is HDD)
- `*(u64*)(H + 0x48) == 0` (no active command / expected tag is 0)
- `*(u64*)(H + 0x38) == 0` (completed tag is 0)
- `*(u64*)(H + 0x40) == 0` (status is 0)
- `*(u32*)0x3055180 == 0` (global UFS mutex is free)
- **Fail-Open Policy**: If the HDD is busy or an optical command is in-flight, logging is skipped (`records_skipped` incremented in mailbox) and execution continues without stalling. Logging is **never** executed inside optical polling loops.
- **Strict Slot Discipline**: File is opened, written/read, closed, and flushed within a single contiguous block. File descriptors are never held open across hypercalls.

---

## 2. Trampoline & Memory Layout

### 2.1 Code Slot Trampolines (`0x4800..0x4B00`)
Capacity of code slot: `0x4800` to `0x7FF0` (14,320 bytes). Trampolines occupy `0x4800..0x4B00` (768 bytes), leaving 13,552 bytes for C payload.

| Symbol | Address | Target | TOC Handling | Description |
|---|---|---|---|---|
| `lv1_hcall` | `0x4800` | Stock helper at `0x111eb8` | N/A | Generic safe hypercall wrapper (180 bytes, `sc 0` at `0x4858`) |
| `repo_read` | `0x48C0` | Stock `0x111eb8` | Stock `0x751280` | Hypervisor repository query helper |
| `native_clock` | `0x4900` | Stock `0x0b9cd0` | Jump | Hardware timebase reader (`mftb`) |
| `native_alloc` | `0x4920` | Stock `0x0b9848` | Stock `0x751280` | Stock memory allocator |
| `stock_ufs_open` | `0x4960` | Stock `0x1ecc5c` | Stock `0x751280` | UFS file open helper |
| `stock_ufs_close` | `0x49A0` | Stock `0x1ecb10` | Stock `0x751280` | UFS file close helper |
| `stock_raw_read` | `0x49E0` | Stock `0x1ed5cc` | Stock `0x751280` | UFS sector read helper |
| `stock_raw_write` | `0x4A20` | Stock `0x1ed458` | Stock `0x751280` | UFS sector write helper |
| `stock_hdd_cache_flush` | `0x4A60` | Stock `0x12cc98` | Stock `0x751280` | Standalone write-through cache flush |
| `get_r2` | `0x4AA0` | Inline | N/A | `mr r3, r2; blr` |
| `entry_menu` | `0x4AC0` | `s4_menu` | Payload TOC | Hook entry called from `0x270FFC` |

C payload begins at `0x4B00`.

### 2.2 Mailbox Specification (`0x930F20`, 96 bytes)
- Range: `[0x930F20, 0x930F80)`
- Offsets:
  - `0x00`: `status` (`u32`): bit 0: started, bit 1: done, bit 2: alloc_ok, bit 3: alloc_failed
  - `0x04`: `total_hypercalls` (`u32`): count of hypercalls issued
  - `0x08`: `timeouts` (`u32`): bitmask of timeouts (TUR, INQ, CAP, READ)
  - `0x0C`: `step_failed` (`u32`): step ID where error occurred
  - `0x10`: `first_err_rc` (`s32`): return code of first failing call
  - `0x14`: `open_count` (`u32`): count of PS menu open cycles
  - `0x18`: `arena_ptr` (`u64`): pointer to 4 KiB arena from `native_alloc`
  - `0x20`: `rom_bus_idx` (`u8`), `rom_dev_idx` (`u8`), `rom_port` (`u8`), `storage_bus_idx` (`u8`)
  - `0x24`: `hdd_bus_idx` (`u8`), `hdd_dev_idx` (`u8`), `hdd_port` (`u8`), `phat_match` (`u8`)
  - `0x28`: `rom_count` (`u32`), `hdd_found` (`u32`)
  - `0x30`: `rom_bus_id` (`u64`): repository 64-bit bus ID
  - `0x38`: `rom_dev_id` (`u64`): repository 64-bit device ID
  - `0x40`: `last_eval_tb` (`u64`): timebase tick of last menu open evaluation
  - `0x48`: `log_records_written` (`u32`): records flushed to HDD log file
  - `0x4C`: `log_records_skipped` (`u16`): records skipped due to busy HDD
  - `0x4E`: `log_fail_reason` (`u8`): reason code if logging halted
  - `0x4F`: `log_clean_shutdown` (`u8`): 1 if END record cleanly written
  - `0x50`: `raw_val1` (`u64`): scratch val1 from hypercall wrapper epilogue
  - `0x58`: `raw_val2` (`u64`): scratch val2 from hypercall wrapper epilogue
- Strict boundary rule: **Zero stores at or above `0x930F80`**.

---

## 3. PowerPC Opcode 17 (`sc`) String Hazard & Mitigation

### 3.1 Root Cause of False `sc` Hits in `.rodata`
During P1A audit analysis (`tools/p1a_audit.py`), any 4-byte sequence matching `(word & 0xFC000003) == 0x44000002` is flagged as a system call (`sc`).
In PowerPC big-endian byte order:
- Opcode 17 mask requires byte 0 to have top 6 bits = `17` (`0x44`).
- ASCII characters with top 6 bits matching 17 are:
  - `'D'` (`0x44`), `'E'` (`0x45`), `'F'` (`0x46`), `'G'` (`0x47`).
- When a string literal has `'D'`, `'E'`, `'F'`, or `'G'` aligned at a 4-byte boundary, and the fourth byte has bits `[1:0] == 2` (e.g. `0x02`, `0x06`, `0x0A`, `0x0E`, `0x12`, `0x16`, `0x1A`, `0x1E`, `0x22`, `0x26`, `0x2A`, `0x2E`, `0x32`, `0x36`, `0x3A`, `0x3E`), the string literal constitutes an exact binary match for the PowerPC `sc` opcode!

### 3.2 Specific Collision in P4 Logging
The string literals:
- `"POST FREE: rc="` -> contains `"FREE"` where `'F'` (`0x46`) + `'R'` (`0x52`) + `'E'` (`0x45`) + `'E'` (`0x45`, `0x45 & 3 == 1`... offset-shifted into `"EE: "` where `'E'` + `'E'` + `':'` (`0x3A` -> `0x3A & 3 == 2`!)) matched opcode 17.
- `"PRE FREE: rgn=0x"` -> similarly contained byte sequences triggering false positive `sc` detections.

### 3.3 Mitigation Applied
All log message prefixes and format strings were normalized to lowercase:
- `"pre open:"`, `"post open:"`
- `"pre dma_alloc:"`, `"post dma_alloc:"`
- `"pre map:"`, `"post map:"`
- `"pre tur:"`, `"post tur:"`
- `"pre inq:"`, `"post inq:"`
- `"pre cap:"`, `"post cap:"`
- `"pre read:"`, `"post read:"`
- `"pre unmap:"`, `"post unmap:"`
- `"pre free:"`, `"post free:"`
- `"pre close:"`, `"post close:"`

After this change, `p1a_audit.py` confirmed **EXACTLY ONE `sc` instruction in changed executable ranges: `[(18520, 0)]` at `0x4858`** for all four variants K0..K3.

---

## 4. Binary Artifacts & Cryptographic Hashes

All binaries are located in `local_only/p4/`:

| Artifact | Variant | Size (bytes) | SHA-256 Checksum |
|---|---|---|---|
| `ps2_netemu_p4_K0.elf` | K0 (Open/Alloc/Free/Close) | 10,901,288 | `f9fdf2a1b7d4122a4d28f707a4382743fc6e030fa6204f2b4c0c64485697ebab` |
| `ps2_netemu_p4_K0.self` | K0 Signed SELF | 2,528,000 | `0db3d223888cb27ed06a6daadbbfd394ccd06b057847474d61ce6c5e0ce9bab7` |
| `ps2_netemu_p4_K1.elf` | K1 (+ Map/Unmap CDVD) | 10,901,288 | `16c3a73f54e4b525ed1bdea28b20ee83bb235e76979c18c88cebb6598fa8bc7d` |
| `ps2_netemu_p4_K1.self` | K1 Signed SELF | 2,528,336 | `ee75288565010e8df1e35ba7da762158835f2d1e61d151e1400c0376dd02f69e` |
| `ps2_netemu_p4_K2.elf` | K2 (+ TUR & INQUIRY) | 10,901,288 | `53994530f3608656b09bce85b07185a5110249d0781a0a38270d86e1097aced1` |
| `ps2_netemu_p4_K2.self` | K2 Signed SELF | 2,528,848 | `1d334290f2d4c62d90a69178c45aa13700ade600b6d7962f915b8b99fb659059` |
| `ps2_netemu_p4_K3.elf` | K3 (+ READ CAPACITY & LBA 16) | 10,901,288 | `58376c8ed820b6c56007736fab5a2a614710444b901402506cbd9e7989b091e5` |
| `ps2_netemu_p4_K3.self` | K3 Signed SELF | 2,529,104 | `7df36f07224292d9f49ab095f2c5813955de591cbca2d871a8c25b239ab878e9` |

### Round-Trip SELF Decryption Verification
Every signed SELF was decrypted back using `tools/selfdec.py` and compared byte-for-byte against the patched ELF. All 4 round-trip decrypted ELFs matched 100% byte-for-byte.

---

## 5. Comprehensive PC Emulation Validation Matrix

Validation was executed in PyGhidra `EmulatorHelper` across all 4 variants:

| Test # | Description | K0 | K1 | K2 | K3 | Details / Behavior Observed |
|---|---|:---:|:---:|:---:|:---:|---|
| **Reg Pres.** | Register Preservation | PASS | PASS | PASS | PASS | `r8`, `cr2..cr4`, `LR`, `r30`, `r31`, `r14..r29` 100% preserved |
| **Test 1** | Normal Execution & WAL | PASS | PASS | PASS | PASS | K0: 12 recs, K1: 16 recs, K2: 20 recs, K3: 24 recs; clean `END` |
| **Test 2** | Crash Point Detection | PASS | PASS | PASS | PASS | Interrupted at Sector 4 `pre open`; decoder flagged `[CRASH POINT]` |
| **Test 3** | Concurrency Safety (H busy) | PASS | PASS | PASS | PASS | 0 disk writes when H busy; skipped count in mailbox (13, 17, 21, 25) |
| **Test 4** | UFS Open Fail-Open | PASS | PASS | PASS | PASS | Probe executes to completion; 0 fd leaks; fail code recorded |
| **Test 5** | Timeout Safety (TAG_TMO) | N/A | N/A | PASS | PASS | Polling timeout logged `TMO `; halted without cleanup hypercalls |
| **Test 6** | Guard Refusal Negative Test | N/A | PASS | PASS | PASS | Wrong EA/LPAR logged `GUARD_REFUSAL`; 0 hypercalls issued |
| **Test 6b** | Swapped Fields Negative Test | N/A | PASS | PASS | PASS | Swapped EA/LPAR rejected; 0 hypercalls issued |
| **Test 7** | Memory Write Provenance | PASS | PASS | PASS | PASS | Stores strictly inside stack, mailbox, arena; unmapped EA untouched |

---

## 6. Tooling Updates

- `tools/decode_netemu_log.py`:
  - Added extraction of `boot_id` from offset 40 of each record.
  - Matches `boot_id` against Sector 0 header `boot_tb`.
  - Flags records as `[CURRENT SESSION]` vs `[STALE - PREVIOUS BOOT]`.
  - Tracks PRE steps without a matching POST step, tagging the last unresolved PRE as `[CRASH POINT]`.
  - Formats parameter `a` and `b` as hex or decimal depending on step context.
- `tools/read_netemu_log.ps1`:
  - Updated PowerShell parser to display boot ID, session matching, and `[CRASH POINT]` alerts directly in the console.
  - Validated syntax with `[System.Management.Automation.Language.Parser]` (0 syntax errors).
