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

---

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
