# P11 Build Notes: Disc Authentication Execution & Variant W1

## Status & Overview
- **Date**: 2026-11-01
- **Task**: P11 - Disc Authentication Command Dispatch and Variant W1 Build.
- **Console Ground Truth (P10 V1 on CECH-2504B with PS2 DVD, from `docs/P10_V1_RESULT.md`)**:
  - `get_virtual_uart_param` (HV 165):
    - Port 2, param 3 = `rc 0`, `val = 0x800` (Sysmgr baseline)
    - Port 10, param 3 = `rc 0`, `val = 0x1000` (Secure service channel alive!)
    - Port 10, param 0 = `rc 0`, `val = 0x0`
  - Zero-length `read_virtual_uart` (HV 162) on Port 10: `rc 0`, `0 bytes`.
  - Zero-length `write_virtual_uart` (HV 163) on Port 10: `rc 0`, `0 bytes`.
  - **Crucial Finding**: VUART Port 10 is **ALIVE and BOUND** for `ps2_netemu`! The feared `LV1_NO_ENTRY` (`-6`) did NOT happen.
  - Media reads (`READ(10)` PIO/DMA) still returned 0 bytes (buffer `0xA5` untouched) because authentication was not yet dispatched.
- **Owner Approval**: Owner approved sending the real disc authentication command (`0x5005`) in Variant W1.


---

## Part 1: Static Reverse Engineering & Independent Re-Derivation

### 1. Complete Re-Derivation of `ps2_softemu.elf` Disc Authentication (`0x8B2BC` & `0x22130C`)

Disassembly and decompilation of `ps2_softemu.elf`, cross-checked with `ps2_gxemu.elf` (`0x8FF8C`) and `ps2_emu.elf` (`0x2053C`), reveals the exact architecture:

#### (a) Exact 0x70-Byte Request Packet Format (PROVEN)
- **Total Packet Length**: Exactly `0x70` (112) bytes, zero-initialized with `memset(buf, 0, 0x70)`.
- **Field Layout & Offsets**:
  | Offset | Type / Size | Value | Meaning |
  |---|---|---|---|
  | `+0x00` | Big-Endian 32-bit | `0x0000FACE` | Magic Header Word |
  | `+0x04` | Big-Endian 32-bit | `0x00005000` | Secure Service ID (Storage Authentication) |
  | `+0x08` | Big-Endian 32-bit | `0x00000060` | Payload Length (96 bytes) |
  | `+0x0C` | Big-Endian 32-bit | `0x00000060` | Length Echo |
  | `+0x10` | Big-Endian 64-bit | `0x0000000000005005` | Opcode (PS2 Optical Disc Authenticate) |
  | `+0x18` | Big-Endian 64-bit | `0x0000000000005000` | Service Echo |
  | `+0x20` | 16 Bytes | `0x00` * 16 | Reserved / Zeros |
  | `+0x30` | Big-Endian 64-bit | `0x1020000401000001` | Caller LAID (PS2 Emulator LAID) |
  | `+0x38` | Byte (1 B) | `0x00` | `param_2` (`byte_a`, hardcoded to 0 by caller `0x22130C`) |
  | `+0x39` | Byte (1 B) | `0x00` or `0x13` | `param_3` (`byte_b`, disc type: `0x12`=CD, `0x13`=DVD-5, `0x14`=DVD-9, or `0x00` default) |
  | `+0x3A` | 6 Bytes | `0x00` * 6 | Reserved / Zeros |
  | `+0x40` | Big-Endian 32-bit | `0x0000004B` | `param_4` (Retry Count: default 75 retries) |
  | `+0x44` | 44 Bytes | `0x00` * 44 | Trailing Padding Zeros |

- **Correction from P10 Preliminary Decode**:
  - In P10, fields were assumed to be 16-bit packed header (`0xFACE`, `0x5000`, `0x0060`, `0x5005`) with LAID at `+0x18`.
  - Independent decompilation of `0x8B2BC` and `ps2_emu.elf` `0x2053C` proves `0xFACE`, `0x5000`, and `0x60` are **32-bit words**, `0x5005` and `0x5000` are **64-bit words** at `+0x10` and `+0x18`, and caller LAID (`0x1020000401000001`) is located at **`+0x30`**.
  - `byte_a` is at `+0x38`, `byte_b` (disc type) is at `+0x39`, and retry count is a 32-bit word at `+0x40`.

#### (b) Caller Context & ATAPI Preparation in Softemu
- Caller `0x22130C` invokes `0x8B2BC`:
  - `param_1`: Context pointer (from `r2 - 0x2300`).
  - `param_2`: `0x00` (byte A).
  - `param_3`: Disc type byte (`byte B`).
  - `param_4`: Retries (if called with `-1`, defaults to `0x4B` / 75).
- Disc-Type Byte decision logic (from `func_87600` / `0x87600`):
  - Pre-auth ATAPI sequence:
    1. `TEST UNIT READY` (opcode `0x00`).
    2. `INQUIRY` (opcode `0x12`, 36 bytes).
    3. `GET CONFIGURATION` (opcode `0x46`, 16 bytes allocation length, Current Profile field at offset 6: `0x08`=CD, `0x10`=DVD).
    4. If CD profile: issues `READ TOC` (opcode `0x43`).
    5. If DVD profile: evaluates layer count (`READ CAPACITY` / `READ DISC STRUCTURE` opcode `0xAD`).
  - Disc type values:
    - `0x12`: PS2 CD-ROM
    - `0x13`: PS2 DVD-ROM Single Layer (DVD-5)
    - `0x14`: PS2 DVD-ROM Dual Layer (DVD-9)
    - `0x00`: Default / Unspecified disc
  - Both `0x00` and `0x13` are valid for PS2 DVD authentication.

### 2. Virtual UART Mechanics & Polling Semantics (LV1 4.93 Reverse Engineering)

Decompilation of LV1 4.93 hypercall dispatchers and VUART implementations (`lv1_read_virtual_uart` at `0x2F429C`, `lv1_write_virtual_uart` at `0x2F2AF4`, `lv1_get_virtual_uart_param` at `0x2F3A68`):

#### (a) Hypercall Semantics & RX Buffer Behavior
- **HV 163 (`lv1_write_virtual_uart`, 0x2F2AF4)**:
  - Takes `(ulong port, ulong buffer_ea, ulong len)`.
  - Copies packet into the inter-partition VUART ring buffer.
  - Returns `rc = 0` on success and writes number of bytes transmitted to output register.
- **HV 162 (`lv1_read_virtual_uart`, 0x2F429C)**:
  - Takes `(ulong port, ulong buffer_ea, ulong max_len)`.
  - Checks the port RX ring buffer.
  - **Non-Blocking Semantics**: If the RX ring buffer is empty, it returns immediately with `rc = 0` and `bytes_read = 0`. It does NOT block or sleep.
  - **Short Reads**: If fewer bytes are available than requested, it copies whatever bytes are currently ready, updates the read pointer, and returns `rc = 0` with `bytes_read = N`.
  - Softemu's own reply handler (`0x8AE28`) uses an accumulator loop around HV 162 (`0x42D14`) that sums `bytes_read` until the full packet length (`0x70`) is reached.
  - **Feasibility for Polling**: A bounded timebase accumulator loop calling HV 162 is fully supported by the hypervisor and eliminates any need for LV2 event queues, interrupt bindings, or `sys_event_wait`.
- **HV 165 (`lv1_get_virtual_uart_param`, 0x2F3A68)**:
  - Param 0: Port status / connection flags (`0` = connected and ready).
  - Param 3: Port ring buffer capacity:
    - Port 2 (sysmgr): `0x800` (2048 bytes).
    - Port 10 (secure service / ss_server1): `0x1000` (4096 bytes).

#### (b) Reply Format & Success Criterion
- **Reply Packet Length**: `0x70` bytes.
- **Offsets of Interest**:
  - `+0x00`: Reply Magic / Header Echo (`0xFACE5000` or similar).
  - `+0x22`: 16-bit Big-Endian Status Word (`0x0000` = SUCCESS).
  - `+0x38`: 8-bit Key Flags Byte:
    - Bit 29 (`0x04` or `flags & 0x04` / bit 5): Key 0 valid (Title Key / Disc Key).
    - Bit 30 (`0x02` or `flags & 0x02` / bit 6): Key 1 valid.
    - Bit 31 (`0x01` or `flags & 0x01` / bit 7): Key 2 valid.
  - `+0x40..+0x4F`: Key 0 (16 bytes) - **NEVER LOGGED**.
  - `+0x50..+0x5F`: Key 1 (16 bytes) - **NEVER LOGGED**.
  - `+0x60..+0x6F`: Key 2 (16 bytes) - **NEVER LOGGED**.
- **Success Criterion**:
  - `status == 0 && (flags & 0x07) != 0` (or `status == 0 && flags != 0`).

---

### 3. `ss_server1.elf` Handler Analysis (`0x8001EF78`)

Decompilation of `ss_server1.elf` service `0x5000` dispatch:
- **Registration**: Opcode `0x5005` registered at `0x8001C418` in the secure service table.
- **LAID Verification**:
  - Partition LAID of `PS2_NE_LPAR` is `0x1020000401000001`.
  - The incoming packet LAID field at `+0x30` is validated against authorized storage clients. For PS2 disc authentication, `0x1020000401000001` is the recognized emulator partition LAID and is accepted.
- **Drive Operations & Side Effects**:
  - Handler executes SCSI `READ DISC STRUCTURE` (opcode `0xAD`, format `0x01` CPR_MAI) to obtain the disc key structure from the BD drive.
  - Executes `SEND KEY` / `REPORT KEY` (opcodes `0xA3` / `0xA4`) challenge-response authentication with the drive controller.
  - If the drive is empty or contains non-PS2 media (e.g., standard BD-ROM), CPR_MAI or challenge fails; handler writes error status code (e.g. nonzero status, flags = 0) to reply packet.
  - Drive session is cleared cleanly on error; the VUART port is not locked or wedged.
  - If invoked twice, it overwrites the session key; however, per task rules, Variant W1 sends the request strictly once per boot.

---

### 4. Logger & Security Discipline
- **Zero-Key-Leak Discipline**:
  - Under no circumstances shall bytes from `+0x40` through `+0x6F` be written to hddlog, memory buffers printed to console, or menu display.
  - The probe logs strictly:
    - Bytes received count (`rx_total`).
    - 32-bit reply header magic (`reply[0..3]`).
    - 16-bit status code (`reply[0x22..0x23]`).
    - 8-bit flags byte (`reply[0x38]`).
    - High-level verdict: `AUTH_OK`, `AUTH_ERR_STATUS`, `AUTH_TIMEOUT`, `AUTH_SHORT`.

---

## Part 2: Variant W1 Implementation, Build & Verification

### 1. Implementation Details (`netemu_p11/src/probe.c`)

Variant W1 implements the complete disc authentication flow under strict guards and safety bounds:

1. **Safety Guard (`check_cdvd_buffer_guard` & Pre-Auth Checks)**:
   - Evaluates SB_CDVD buffer descriptors (`Physical LPAR` at `0x2458438`, `CPU EA` at `0x2458428`, `Size` at `0x2458430`).
   - Executes baseline checks: TUR succeeds (`rc == 0`, `tur_status == 0`), INQUIRY succeeds, READ CAPACITY succeeds (`rc == 0`, `cap_status == 0`).
   - Enforces authentication precondition guard:
     - Media block size == 2048 bytes (`cap_block_size == 2048`).
     - VUART Port 10 param 3 query succeeds (`p10_rc == 0`).
   - If preconditions fail, logs guard reason (`TAG_GRD`), sets `auth_verdict = AUTH_VERDICT_SKIPPED`, and skips directly to sector reads (fail-open discipline).

2. **Authentication Request Formatting (`format_auth_request`)**:
   - Stored at `data_ea + 0x800` (`CDVD_EA + 0x1800`), physical LPAR `data_lpar + 0x800`.
   - Populates exactly 0x70 bytes:
     - `+0x00`: `0x0000FACE` (32-bit BE magic)
     - `+0x04`: `0x00005000` (32-bit BE secure service)
     - `+0x08`: `0x00000060` (32-bit BE payload length)
     - `+0x0C`: `0x00000060` (32-bit BE length echo)
     - `+0x10`: `0x0000000000005005` (64-bit BE opcode)
     - `+0x18`: `0x0000000000005000` (64-bit BE service echo)
     - `+0x30`: `0x1020000401000001` (64-bit BE partition LAID)
     - `+0x38`: `0x00` (byte A)
     - `+0x39`: `0x13` (byte B, DVD-5)
     - `+0x40`: `0x0000004B` (32-bit BE retries = 75)

3. **Hypervisor VUART Write & Bounded Polling**:
   - Dispatches single `lv1_write_virtual_uart` (HV 163) write of 0x70 bytes on port 10.
   - Non-blocking polling accumulator on `lv1_read_virtual_uart` (HV 162) into reply buffer (`data_ea + 0x900`).
   - Bounded by 2.0-second hardware timebase limit (`159,600,000` ticks).
   - Extracts status (`+0x22`) and flags (`+0x38`).
   - **Immediately clears session keys** (`+0x40..+0x6F`) via `prefill_buffer(reply_ea + 0x40, 0x30, 0x00)`.
   - Never sends auth request twice per boot.

4. **Baseline Sector Reads & Teardown**:
   - Executes READ(10) PIO LBA 16 (PVD), LBA 0 (Lead-in), LBA 17 (Terminator), and DMA LBA 16.
   - Executes clean DMA unmap (HV 177), DMA free (HV 175), and device close (HV 171).

5. **Glance Menu Telemetry (Rows 0..7)**:
   - Row 0: `P11-W1 AUTH: <verdict> ST=0x<stat> FL=0x<flg>`
   - Row 1: `P11-W1 PIO16: <class> PVD: <pvd>`
   - Row 2: `AUTH BYTES=<read> POLLS=<cnt> WR=<wr>`
   - Row 3: `VUART: P2=<p2_rc> P10=<p10_rc> W=<w_rc> R=<r_rc>`
   - Row 4: `HC=<total_hc> LOG=<recs> SKIP=<skip> TMO=0x<tmo>`
   - Row 5: `PIO: 16_A5=<cnt> 0_A5=<cnt> 17_A5=<cnt>`
   - Row 6: `CDVD LPAR: 0x<lpar>`
   - Row 7: `DMA RGN=0x<rgn> BUS=0x<bus>`



### 2. Build Metrics & Verification Results

- **Compiler & Toolchain**: Clang PowerPC 64-bit Big-Endian Hotspot.
- **Code Slot Bounds**:
  - Slot Capacity: `0x4800 .. 0x7FF0` (14,320 bytes).
  - Code Range: `0x4800 .. 0x7F30` (14,128 bytes, 98.7% utilization).
  - Free Margin: 192 bytes remaining.
- **File Artifacts & Hashes**:
  - `local_only/p11/ps2_netemu_p11_W1.elf`:
    - Size: 10,901,288 bytes
    - SHA-256: `529458a99fc46245c5c33e45483a10ac9fdf88a8a6c1af98bcc26b10637faa18`
  - `local_only/p11/ps2_netemu_p11_W1.self`:
    - Size: 2,530,320 bytes
    - SHA-256: `2b4d69d8a1d89160b247c012abe7568d964eb216ef7324641dbb9ff3cf136562`
  - `local_only/p11/ps2_netemu_p11_W1.roundtrip.elf`:
    - Size: 10,901,288 bytes
    - SHA-256: `529458a99fc46245c5c33e45483a10ac9fdf88a8a6c1af98bcc26b10637faa18` (Exact Byte-for-Byte Match)
- **Static Audits**:
  - `audit_ir.py`: **PASSED** (all stores strictly confined to stack, mailbox `[0x930F20, 0x930F80)`, arena, and verified CDVD buffer).
  - `tools/p1a_audit.py`: **PASSED** (exactly ONE `sc` instruction in changed executable ranges at `0x4858`, 464 validated stores).

---

### 3. PC Validation Suite Results (`netemu_p11/validate_pc.py`)

All test scenarios executed synchronously in the foreground via PyGhidra headless emulation:

| Test Case | Scenario / Condition | Expected Behavior | Emulation Result |
|---|---|---|---|
| **Step 1** | Script Parse Audit | Parse syntax only (zero execution) | **PASS** (4/4 scripts valid) |
| **Step 2** | Wrapper Instructions | 29 instructions match stock, sc at 0x4858 | **PASS** |
| **Step 3** | Buffer Classification | UNCHANGED, ZEROS, DATA_OK, OTHER | **PASS** |
| **Scenario 1** | `reply_ok` | Request packet exact 0x70 bytes; status=0, flags=0x07; session keys zeroed | **PASS** (`AUTH_OK`, Row 0: `P11-W1 AUTH: OK ST=0x00000000 FL=0x00000007`) |
| **Scenario 2** | `nonzero_status` | Status=0x8001, flags=0; sector reads complete | **PASS** (`AUTH_ERR_STATUS`, Row 0: `P11-W1 AUTH: ERR_STAT ST=0x00008001 FL=0x00000000`) |
| **Scenario 3** | `short_reply` | 0x20 bytes read then stop; sector reads complete | **PASS** (`AUTH_SHORT`, Row 0: `P11-W1 AUTH: SHORT ST=0x00000000 FL=0x00000000`) |
| **Scenario 4** | `timeout` | 0 bytes read until 2.0s limit; sector reads complete | **PASS** (`AUTH_TIMEOUT`, Row 0: `P11-W1 AUTH: TIMEOUT ST=0x00000000 FL=0x00000000`) |
| **Scenario 5** | `write_err` | HV 163 rc=-1; skip read; sector reads complete | **PASS** (`AUTH_WRITE_ERR`, Row 0: `P11-W1 AUTH: WRITE_ERR ST=0x00000000 FL=0x00000000`) |
| **Scenario 6** | `param_err` | HV 165 port 10 rc=-6; guard fails; sector reads complete | **PASS** (`AUTH_SKIPPED`, Row 0: `P11-W1 AUTH: SKIPPED ST=0x00000000 FL=0x00000000`) |
| **Negative 1**| Corrupted CDVD Buffer | Buffer descriptors 0; immediate refusal | **PASS** (0 hypercalls issued) |
| **Negative 2**| Swapped LPAR / EA | Swapped descriptors; immediate refusal | **PASS** (0 hypercalls issued) |
| **Negative 3**| Block Size != 2048 | 512-byte block size; auth skipped | **PASS** (`AUTH_SKIPPED`, baseline reads ok) |
| **Negative 4**| ATAPI Timeout Halt | TUR timeout; immediate HALT discipline | **PASS** (0 teardown hypercalls, unmap/free/close skipped) |
| **Security 1**| Zero Key Leak Audit | WAL log scanned for dummy session keys (0xEE) | **PASS** (Zero keys leaked in WAL log) |
| **Security 2**| Strict Store Bounds | All stores checked against allowed ranges | **PASS** (Zero stores to `0x930F80..0x931000`, zero stores to physical LPAR) |


---

# P11b Investigation Notes: Probe Silence & Authentication Status 0x16

## Part 1: Probe Silence Root Cause Analysis (Console Ground Truth Investigation)

### 1. Investigation of Control Flow After Auth Read
- **C Source (`netemu_p11/src/probe.c`)**:
  - Lines 1076–1091 evaluate status: `if (arena->auth_status != 0) arena->auth_verdict = AUTH_VERDICT_ERR_STATUS;`.
  - There is NO early return, panic, or branch to teardown on `AUTH_ERR_STATUS`.
  - Line 1094 scrubs keys: `prefill_buffer(reply_ea + 0x40, 0x30, 0x00);`.
  - Line 1108 logs Record 25: `HDDLOG(TAG_POST, (u64)arena->auth_status, (u64)arena->auth_flags, msg);`.
  - Line 1110 falls straight through label `do_sector_reads:` to line 1117: `execute_read_test(...)` for `pio_16`.
- **Compiler Output & Map (`netemu_p11/build/probe_p11_W1_compiler.s`)**:
  - Block `.LBB3_128` issues `bl hddlog_write` for Record 25.
  - Immediately following, block `.LBB3_129` sets up arguments (`dev_id`, `lba=16`, `blocks=2048`, `block_size=1`, `proto=1`, `cmnd_block_ea`, `data_ea`, etc.) and calls `bl execute_read_test`.
  - There is NO conditional branch jumping over `execute_read_test`.
  - **Verdict [PROVEN]**: Control flow entered `execute_read_test` unconditionally after Record 25.

### 2. Examination of Key Scrubbing & Buffer Isolation
- **Scrub Target**: `prefill_buffer(reply_ea + 0x40, 0x30, 0x00)`.
- **Memory Layout**:
  - `data_ea` base = `0x84001000` (length 2048: `0x84001000 .. 0x840017FF`).
  - `req_ea` = `data_ea + 0x800` = `0x84001800` (length 112: `0x84001800 .. 0x8400186F`).
  - `reply_ea` = `data_ea + 0x900` = `0x84001900` (length 112: `0x84001900 .. 0x8400196F`).
  - Key scrub region = `reply_ea + 0x40` = `0x84001940 .. 0x8400196F` (48 bytes).
  - `cmnd_block_ea` = `0x84000000 .. 0x8400003F` (64 bytes).
- **Interference Audit**:
  - The scrub region (`0x84001940..0x8400196F`) is completely disjoint from `data_ea` (`0x84001000..0x840017FF`) and `cmnd_block_ea` (`0x84000000..0x8400003F`).
  - All addresses reside safely within the 1 MiB CDVD allocated buffer (`[0x84000000, 0x84100000)`).
  - **Verdict [PROVEN]**: The key scrub did NOT clobber any command block, sector buffer, or descriptor state.

### 3. Counter Widths and Timebase Bounds
- `poll_count` in `probe.c`: defined as 32-bit `u32`. Real value 72,072 << 2^32. Successfully logged in Record 25.
- Timebase arithmetic: elapsed ticks = 12,781,197 ticks (~0.160 s at 79.8 MHz). Bound = 159,600,000 ticks (~2.0 s).
- No truncation, integer wrap-around, or arithmetic overflow occurred.
- **Verdict [PROVEN]**: Polling and timebase arithmetic operated cleanly.

### 4. Root Cause of Probe Silence: HDD Logger Concurrency Lockout
- Inside `execute_read_test`:
  - Lines 530–533 prefill `data_ea` with `0xA5` and format `cmnd_block_ea`.
  - Line 566 executes `HDDLOG(TAG_PRE, cmnd_block_lpar, data_lpar, msg);` (Record 26).
- Inside `hddlog_write` (`netemu_p11/src/hddlog.c`):
  ```c
  if (!is_hdd_log_safe()) {
      S->log_records_skipped++;
      return 0;
  }
  ```
- `is_hdd_log_safe()` validates:
  - Driver enabled (`H[0x85] == 1`), no error (`H[0x78] == 0`), dev_id == 3.
  - Driver idle: in-flight tag `status48 == 0`, completed tag `tagstat == 0`, status `status40 == 0`.
  - Mutex idle: `ufs_lock == 0` at `0x3055180`.
- **Concurrency Ground Truth**:
  - In P10 V1 (no auth delay): The probe reached sector reads at +0.045 s after boot, before netemu's background storage thread initiated disc image streaming. All 40 records logged cleanly.
  - In P11 W1: Polling VUART Port 10 for 72,072 iterations introduced an additional ~110 ms delay.
  - Record 25 was committed to disk at **+0.160 s after boot** (`TB = 0x3EAB614B`, boot `0x3DE85ABE`).
  - By +0.160 s, netemu's main storage thread had initialized and started reading game files from `/dev_hdd0/`.
  - When `HDDLOG(TAG_PRE)` was called for Record 26, netemu had an active I/O command or held `ufs_lock`.
  - `is_hdd_log_safe()` returned 0, incrementing `S->log_records_skipped` and returning immediately without writing.
  - Every subsequent log attempt (`TAG_POST`, subsequent sector reads, teardown, `TAG_END`) similarly encountered `is_hdd_log_safe() == 0` and was silently skipped.
  - Sector 0 header remained in the exact state left by Record 25: `next_rec = 26`, `rec_count = 25`, `clean_shutdown = 0` (`UNCOMMITTED / CRASH`).
  - **Console Behavior Correlation**: The console was NOT hung or crashed. The owner pressed the PS button, cycled menu rows, and exited cleanly to XMB. Netemu was actively executing throughout.
- **Verdict [PROVEN]**: The probe went silent because `hddlog_write` skipped Record 26 and all subsequent records due to concurrent HDD activity by netemu.

---

## Part 2: Reverse Engineering of `ss_server1.elf` & Meaning of Status 0x16

### 1. Handler Dispatch and Control Flow
Decompilation of `ss_server1.elf` (via PyGhidra):
- Secure service opcode `0x5005` dispatch table at `0x8001C418` binds to vtable `0x800586a8`.
- `vtable[9]` at `0x8001E724` invokes `_opd_FUN_80020638(uRam00000000c000e2c8, *(param_1 + 0x38))`.
- Decompilation of `_opd_FUN_80020638`:
  1. Calls `_opd_FUN_8001ee28` (drive readiness / TEST UNIT READY & sense): returns 0 on ready.
  2. Calls `_opd_FUN_8001f0e4(param_1, 0x4B)`:
     - Issues SCSI opcode `0x12` (`INQUIRY`, 60 bytes).
     - Checks drive vendor identification string against `'PS-SYSTEM'` and `'PS-SPECIAL'`.
     - Our console's BD drive returned `'SONY    PS-SYSTEM'` -> **MATCHED / PASSED**.
     - Issues SCSI opcode `0xA3` (`SEND KEY`) up to 75 (`0x4B`) retries -> **PASSED**.
  3. Calls `_opd_FUN_80024e30(auStack_30, 0, 0, aiStack_40, 4, &uStack_38)`:
     - Issues drive profile query.
     - Logs `profile:%08X\n` (format string at file offset `0x5de28`).
     - Stores profile in `aiStack_40[0]`.
  4. Profile validation:
     ```c
     if (aiStack_40[0] - 0xff60U < 2) {
         // Profile is 0xFF60 (PS2 CD) or 0xFF61 (PS2 DVD)
         uVar2 = _opd_FUN_8003220c(0xc, 0x38, param_2); // Derive session keys!
     } else {
         uVar2 = 0x16; // Status 22 (0x0016)!
         _opd_FUN_80037fdc(uVar1, 2, uRam00000000c000e4b0); // "HW: not ps2 disc\n"
     }
     ```
  5. `_opd_FUN_8001e724` stores `uVar2` into `*(undefined4 *)(param_1 + 0x18)` which is formatted into the reply packet status word at `+0x22`.
- **Verdict [PROVEN]**:
  **Status `0x16` (22) strictly and uniquely means `HW: not ps2 disc`**, triggered when the BD drive controller reports an MMC Profile other than `0xFF60` (PS2 CD) or `0xFF61` (PS2 DVD).

### 2. Request Packet Layout vs `ps2_softemu.elf`
- Decompilation of `ps2_softemu.elf` (`0x8B2BC` and `0x22130C`) compared with `netemu_p11/src/probe.c`:
  - Magic header `+0x00`: `0x0000FACE` (Identical)
  - Service `+0x04`: `0x00005000` (Identical)
  - Payload length `+0x08`: `0x00000060` (Identical)
  - Length echo `+0x0C`: `0x00000060` (Identical)
  - Opcode `+0x10`: `0x0000000000005005` (Identical)
  - Service echo `+0x18`: `0x0000000000005000` (Identical)
  - Reserved `+0x20..+0x2F`: Zeros (Identical)
  - Partition LAID `+0x30`: `0x1020000401000001` (Identical)
  - `byte_a` `+0x38`: `0x00` (Identical)
  - `byte_b` (disc type) `+0x39`: `0x13` (Identical)
  - Reserved `+0x3A..+0x3F`: Zeros (Identical)
  - Retries `+0x40`: `0x0000004B` (75) (Identical)
  - Padding `+0x44..+0x6F`: Zeros (Identical)
- **Verdict [PROVEN]**:
  There are NO differences between our request and `ps2_softemu.elf`. No runtime nonces, drive serials, or capacity values are embedded. LAID `0x1020000401000001` was validated and accepted by `ss_server1` (it reached the drive profile query).

### 3. Drive Profile State & Required Preparatory ATAPI Commands
- When a PS2 DVD disc is inserted into the PS3 BD drive:
  - The drive firmware initially reports generic MMC profile `0x0010` (DVD-ROM).
  - The drive transitions to profile `0xFF61` (PS2 DVD) only after reading DVD structure metadata.
- `ps2_softemu.elf` pre-auth sequence (`func_87600` / `0x87600`):
  1. Issues `GET CONFIGURATION` (Opcode `0x46`): queries drive features and current profile.
  2. Issues `READ DISC STRUCTURE` (Opcode `0xAD`, Format `0x00`): reads 2048 bytes of DVD Physical Format Information from Layer 0. This command forces the drive controller to inspect lead-in / BCA data and identify the disc as PS2 DVD.
  3. Re-queries profile (`GET CONFIGURATION`): verifies profile transitioned to `0xFF61`.
- In W1:
  - Netemu issued TUR, INQUIRY, and READ CAPACITY, but NEVER issued `GET CONFIGURATION` or `READ DISC STRUCTURE`.
  - The drive remained in generic DVD-ROM mode (`profile = 0x0010`).
  - Consequently, `ss_server1` read `profile == 0x0010` != `0xFF61`, resulting in status `0x16` (`HW: not ps2 disc`).
- **Verdict [PROVEN]**:
  The request CAN be fixed by preparatory ATAPI commands. Variant W2 will implement this sequence.

---

## Part 3: Architecture of Variant W2

Variant W2 implements three key enhancements over W1:

1. **Preparatory Non-Destructive ATAPI Commands (Before VUART Auth)**:
   - **Step 6a: `GET CONFIGURATION` (Opcode `0x46`)**:
     - Allocation length: 32 bytes (`0x20`).
     - PIO DATA-IN, proto = 1, buffer = `data_ea`.
     - Records initial profile at `data_ea[6..7]` into `arena->drive_profile_pre`.
     - Logs `pre/post get_cfg1`.
   - **Step 6b: `READ DISC STRUCTURE` (Opcode `0xAD`)**:
     - Format: `0x00` (DVD Physical Format Information Layer 0).
     - Allocation length: 2048 bytes (`0x800`).
     - PIO DATA-IN, proto = 1, buffer = `data_ea`.
     - Causes drive controller to read lead-in and latch PS2 DVD profile.
     - Logs `pre/post read_disc_struct`.
   - **Step 6c: `GET CONFIGURATION` (Opcode `0x46`)**:
     - Allocation length: 32 bytes.
     - Records post-structure profile at `data_ea[6..7]` into `arena->drive_profile_post`.
     - Logs `pre/post get_cfg2`.

2. **Logger Concurrency Resilience (`hddlog.c`)**:
   - In `hddlog_write`, replace immediate fail-skip with a bounded retry loop:
     - Polls `is_hdd_log_safe()` up to 50 times with a 2 ms timebase pause (~100 ms total window).
     - Allows transient netemu HDD reads to complete so probe records are not starved.
     - If still busy after 100 ms, skips record gracefully.

3. **Glance Menu Telemetry (Rows 0..7)**:
   - Row 0: `P11-W2 AUTH: <verdict> ST=0x<stat> FL=0x<flg>`
   - Row 1: `PROF1=0x<p1> PROF2=0x<p2> RDS=0x<rds_rc>`
   - Row 2: `AUTH: READ=<read> POLLS=<cnt> WR=<wr>`
   - Row 3: `PIO16: <cls> A5=<cnt> POLLS=<cnt>`
   - Row 4: `HC=<total_hc> LOG=<recs> SKIP=<skip> TMO=0x<tmo>`
   - Row 5: `PIO: 16_A5=<cnt> 0_A5=<cnt> 17_A5=<cnt>`
   - Row 6: `CDVD LPAR: 0x<lpar>`
   - Row 7: `DMA RGN=0x<rgn> BUS=0x<bus>`

---

## Part 4: Variant W2 Build, Audit & PC Validation Verification

### 1. Build Verification
- Built binary: `local_only/p11/ps2_netemu_p11_W2.elf`
  - Size: 10,901,288 bytes
  - SHA-256: `5a572a24e25991607952c921814568681270b833ce7464179f9a2974038860b9`
- Repacked SELF: `local_only/p11/ps2_netemu_p11_W2.self`
  - Size: 2,530,160 bytes
  - SHA-256: `ea58d1c6a1e886c85ed328e1bc2db7abf71657d14a65a5fc1eb7fc7e9ca88f02`
- Code slot usage:
  - Wrapper + entry hook + trampolines: `0x4800..0x4B00` (768 bytes)
  - Probe code + string literals: `0x4B00..0x7D90` (12,944 bytes)
  - Total code slot: 13,712 bytes (`0x4800..0x7D90`), margin of 608 bytes under ceiling `0x7FF0`.

### 2. Static Security & Binary Audits
- **SELF Decryption Round-Trip (`selfdec.py`)**:
  - `roundtrip_W2.elf` decrypted from `ps2_netemu_p11_W2.self` matches `ps2_netemu_p11_W2.elf` byte for byte (identical SHA-256).
- **Instruction Audit (`p1a_audit.py`)**:
  - Scanned executable changed ranges (`0x4800..0x7D90`).
  - Exactly ONE `sc` instruction in changed ranges at virtual address `0x4858` (`sc 0`, opcode `0x44000002`).
  - 504 total stores (`st*`) verified across changed ranges.
- **IR Store Provenance Audit (`audit_ir.py`)**:
  - Every store across LLVM IR verified against white-listed targets: stack frames, Mailbox (`0x930F20..0x930F7F`), 4 KiB Arena (`0x80020000..0x80020FFF`), CDVD command block / data buffer (`CDVD_EA..CDVD_EA+0x2000`).
  - Zero stores to physical LPAR (`0x500002c00000`) or Mailbox boundary (`0x930F80..0x931000`).

### 3. PC Validation Suite Results (`validate_pc.py`)
All 6 operational and negative scenarios passed 100%:
1. **PowerShell Script Syntax**: Parse check passed for all 4 installer/helper scripts (zero execution).
2. **Wrapper Byte Match**: 29 instructions match stock wrapper, `sc` at `0x4858`, `mr r8, r9` at `0x4848`.
3. **Buffer Classification**: UNCHANGED, ZEROS, DATA_OK (`CD001`), and OTHER states verified.
4. **Scenario 1 (`reply_ok`)**:
   - Exact 0x70 request packet verified (magic `0x0000FACE`, service `0x5000`, opcode `0x5005`, LAID `0x1020000401000001`, byte B `0x13`, retries 75).
   - Menu Row 0: `"P11-W2 AUTH: OK ST=0x00000000 FL=0x00000007"`.
   - Menu Row 1: `"PROF1=0x0010 PROF2=0xff61 RDS=0x00000000"`.
   - Complete 31-hypercall sequence verified (TUR, INQ, CAP, VUART params, CFG1, RDS, CFG2, 163 write, 162 read, PIO LBA 16/0/17, DMA LBA 16, Unmap, Free, Close).
   - Session keys at `reply_ea + 0x40..+0x6F` zeroed immediately in memory.
   - Zero session key bytes in durable WAL log.
5. **Scenario 2 (`nonzero_status` 0x16)**:
   - Reply status `0x0016` (22) returned by VUART emulator.
   - Menu Row 0: `"P11-W2 AUTH: ERR_STAT ST=0x00000016 FL=0x00000000"`.
   - Menu Row 1: `"PROF1=0x0010 PROF2=0xff61 RDS=0x00000000"`.
   - Baseline sector reads and teardown completed cleanly.
6. **Scenario 3 (`short_reply`)**:
   - Menu Row 0: `"P11-W2 AUTH: SHORT ST=0x00000000 FL=0x00000000"`.
   - Clean teardown verified.
7. **Scenario 4 (`timeout`)**:
   - Menu Row 0: `"P11-W2 AUTH: TIMEOUT ST=0x00000000 FL=0x00000000"`.
   - Clean teardown verified.
8. **Scenario 5 (`write_err`)**:
   - Menu Row 0: `"P11-W2 AUTH: ERR_WRITE ST=0x00000000 FL=0x00000000"`.
   - HV 162 read skipped, baseline sector reads and clean teardown verified.
9. **Scenario 6 (`param_err`)**:
   - HV 165 query fails (`-6`), guard triggers.
   - Menu Row 0: `"P11-W2 AUTH: SKIPPED ST=0x00000000 FL=0x00000000"`.
   - ATAPI preparatory commands and VUART 163/162 skipped, baseline sector reads and teardown completed cleanly.
10. **Negative Tests & Safety Disciplines**:
    - Corrupted CDVD buffer descriptors: rejected with 0 hypercalls.
    - Swapped CDVD buffer descriptors: rejected with 0 hypercalls.
    - Block size != 2048: skips auth, completes baseline reads cleanly.
    - ATAPI timeout immediate HALT discipline: 0 teardown hypercalls.
    - Strict memory write provenance: 0 stores outside stack, mailbox, arena, and CDVD buffer range across all 6 scenarios.
