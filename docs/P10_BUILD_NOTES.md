# P10 Build Notes: Disc Authentication, Secure Service 0x5005, and Variant V1

## Status
- **Date**: 2026-11-01
- **Task**: P10 - Optical Disc Authentication Investigation and Variant V1 Implementation.
- **Console Ground Truth (P9 U1 Result on PS3 CECH-2504B with PS2 DVD & PS3 BD Control)**:
  - `docs/P9_U1_RESULT.md`: ATAPI `READ(10)` with BOTH PIO (`proto = 1`, 2048 x 1 B) and DMA (`proto = 3`, 1 x 2048 B) protocols, and on BOTH media (Test Drive Unlimited PAL DVD-5 and GTA IV PS3 BD), return `rc = 0, async = 0, no sense`, but ZERO data (`0xA5` pre-fill stays 100% untouched).
  - Inbound non-media commands (`INQUIRY` 36 B proto 1, `READ CAPACITY` 8 B proto 1) DO deliver data into the same buffer.
  - **Deduction**: The drive/LV1 withholds media data from any partition that has not completed disc authentication. GameOS authenticates every disc at mount via `sys_ss_disc_auth` (`0x5007` for BD, `0x5004`/`0x29` for DVD/CD). Legacy emulators (`ps2_softemu.elf` `0x8B2BC`) invoke secure service `0x5000` op `0x5005` over virtual UART 10 before reading media sectors.

---

## Part 1: Static Reverse Engineering Findings

### 1. LV1 4.93 Storage Device Layer & Data Gating (PROVEN)
- **ATAPI Submission Path**: Disassembly of `local_only/fw493/lv1.elf` at HV 248 entry `0x3094E4` (`pmi_storage_send_device_command` at `0x251BE0` / `0x254920`):
  - LV1 indexes the device table at `[TOC - 0x5b70] + 0xEE8 + dev_id * 8`.
  - Storage command submission verifies the device handle, maps the LPAR data and command buffers, and passes the 12-byte SCSI command descriptor block directly to the Southbridge SATA/ATAPI controller.
  - **Crucial Finding**: The LV1 hypervisor storage layer does **NOT** maintain or check any software "disc authenticated" boolean flag before dispatching `READ(10)` packets. There is no software filter in LV1 that zeroes or suppresses data transfer.
  - **Drive Controller Enforcement**: The withholding of user data sectors is enforced directly by the **optical drive firmware / hardware controller**. When unauthenticated media is inserted, the drive accepts non-media SCSI commands (`INQUIRY` 0x12, `READ CAPACITY` 0x25, `TEST UNIT READY` 0x00) and returns valid controller parameters. However, for `READ(10)` (0x28) requests targeting media sectors, the drive controller completes the command with success status (`rc = 0, async = 0, sense = 0`) but withholds sector delivery until the drive has successfully executed the cryptographic challenge-response authentication handshake (`SEND KEY` SCSI opcode `0xA3`, class `0xE0`).
  - **Cross-LPAR Persistence**: The drive security state is maintained in drive controller hardware/firmware registers. When GameOS boots a PS2 LPAR, the Southbridge/drive subsystem undergoes a drive reset/re-initialization sequence (`sysmgr_ss.elf` `setup bd drive` at `0x8001DD00`), clearing any previous GameOS session authentication state. Thus, pre-authentication in GameOS before launching netemu does not survive into the PS2 LPAR.

---

### 2. Complete Layout of `ps2_softemu.elf` `ps2_disc_auth` (0x8B2BC) and Official Emulators (PROVEN)
- **Call Hierarchy**:
  - `0x22130C`: Top-level emulator disc mount / auth initiator.
  - `0x8B2BC`: `ps2_disc_auth(r3=context, r4=byte_a, r5=byte_b, r6=retries)`
  - `0x42C74`: `write_all_vuart(port=10, buf, len=0x70)`
  - `0x8AE28`: VUART reply reader via HV 162 (`lv1_read_virtual_uart`).
- **Exact 0x70-Byte Request Packet Format**:
  | Offset | Size | Field Name | Value / Meaning |
  |---|---|---|---|
  | `+0x00` | 2 B | Magic | `0xFACE` |
  | `+0x02` | 2 B | Service ID | `0x5000` (Secure Services / Storage Authentication) |
  | `+0x04` | 2 B | Payload Length | `0x0060` (96 bytes) |
  | `+0x06` | 2 B | Opcode | `0x5005` (PS2 Optical Disc Authenticate) |
  | `+0x08` | 2 B | Service Echo | `0x5000` |
  | `+0x0A` | 14 B | Reserved | Zeros (`0x00` * 14) |
  | `+0x18` | 8 B | Caller LAID | `0x1020000401000001` (PS2 Emulator Logical Application ID) |
  | `+0x20` | 1 B | Param Byte A | `0x00` (from caller `r4`) |
  | `+0x21` | 1 B | Param Byte B | `0x00` or Disc Type code (from caller `r5`) |
  | `+0x22` | 2 B | Reserved | `0x0000` |
  | `+0x24` | 4 B | Retry Count | `0x0000004B` (75 retries default, from caller `r6`) |
  | `+0x28` | 72 B | Padding | Zeros (`0x00` * 72) |
  - **Total Request Size**: Exactly `0x70` (112) bytes.
- **VUART Communication Protocol**:
  - **Writing**: Issued on **Virtual UART Port 10** (`r3 = 0x0A`) via HV 163 (`lv1_write_virtual_uart`, `sc 1`, `r11 = 0xA3`).
  - **Synchronization**: Emulator registers an event queue on guest interrupt plug `0x15` and event bit `0x08000000`. It blocks on `sys_event_wait` (`sc 0`, `r11 = 7`) awaiting notification from the hypervisor.
  - **Reading Reply**: Once signaled, reads reply from Port 10 via HV 162 (`lv1_read_virtual_uart`, `sc 1`, `r11 = 0xA2`).
- **Reply Layout & Success Criterion**:
  - `reply + 0x00`: Header echo (`0xFACE`, service `0x5000`, op `0x5005`).
  - `reply + 0x22`: Status Code (16-bit big-endian). `0x0000` indicates SUCCESS.
  - `reply + 0x38`: Key Flags (8-bit). Bitmask of generated SPU session keys:
    - If `flags & 4`: 16-byte Session Key 0 copied from `reply + 0x40`.
    - If `flags & 2`: 16-byte Session Key 1 copied from `reply + 0x50`.
    - If `flags & 1`: 16-byte Session Key 2 copied from `reply + 0x60`.
  - **Success Condition**: `status == 0 && flags != 0`.
- **Comparison with Phat Emulators**:
  - `ps2_emu.elf` (`0x2053C`) and `ps2_gxemu.elf` (`0x8FF8C`): Construct the **identical** `0x70`-byte request packet (`magic=0xFACE, svc=0x5000, len=0x60, op=0x5005, laid=0x1020000401000001, retries=0x4B`) over VUART Port 10 and evaluate the exact same status and key flags.

---

### 3. Hypervisor Secure Service Handler (`ss_server1.elf`) (PROVEN)
- Registered at `0x8001BB3C` with vtable at `0x80055C28` for Service `0x5000`, Opcode `0x5005`.
- Core Handler `0x8001EF78`:
  1. Validates caller authorization (checking LAID `0x1020000401000001`).
  2. Queries BD drive configuration via ATAPI `GET CONFIGURATION` to determine disc profile:
     - `0xFF60`: PS2 CD-ROM
     - `0xFF61`: PS2 DVD-ROM
  3. Executes `0x8001E024(buf, 0x4B)`: issues SCSI opcode `0xA3` (`SEND KEY`, parameter class `0xE0`, transfer length `0x14`) to drive controller with up to 75 retries.
  4. Invokes isolated SPU cryptographic modules `me_iso_for_ps2emu` and `sv_iso_for_ps2emu` (via `0x80030818`) to compute disc session keys.
  5. Formats reply buffer with status `0` and session keys at `+0x40..+0x6F`, then sends reply packet over VUART Port 10.

---

### 4. Sysmgr LPAR Profiles and VUART Binding (PROVEN)
- **Profile Construction in `sysmgr_ss.elf`**:
  - `0x8001E2A8` (`PS2_SW_LPAR`):
    - Sets `ability = 0x201226c` (`0x1c8(r29)`).
    - Sets `profile_type = 2` (`0x18(r29)`), `target_type = 2` (`0x8(r29)`).
  - `0x8001E308` (`PS2_NE_LPAR`):
    - Calls `0x8001E2A8` (base constructor).
    - Clears `ability` bits `0x2010008` and sets `0x400000`: `ability = 0x402264`.
    - Sets `profile_type = 4` (`0x18(r29)`), `target_type = 3` (`0x8(r29)`).
  - **Drive Setup Hook (vtable `+0x68`, `0x8001DD00`)**:
    - Both `PS2_SW_LPAR` and `PS2_NE_LPAR` share the **exact same** hook implementation (`0x8001DD00`).
    - Hook loops up to 60 times calling `0x80020454` to verify drive ready state.
    - **Crucial Finding**: Sysmgr does **NOT** authenticate the disc for either partition. Official emulators must authenticate the disc themselves.
  - **VUART Binding**:
    - In LV1, VUART Port 2 is bound to Sysmgr for all partitions.
    - Port 10 is connected to `ss_server1` secure service specifically for partitions granted the PS2 emulator storage ability (`0x2010000` bit in `ability`).
    - In `PS2_NE_LPAR`, bit `0x2010000` was explicitly cleared by Sony developers when creating the netemu profile, raising the question of whether Port 10 is bound for `PS2_NE_LPAR`.

---

### 5. Cobra CFW Analysis (`cobra_storage_ext.c`) (PROVEN)
- Cobra source code implements `patch_ps2emu_entry`:
  - Scans LV1 memory for pattern `0x409E00702FBE0001` (at offset `0x10B44` inside embedded `ss_server3.elf`).
  - Patches `li r3, 2` to `LI(R3, 0x29)` (`sys_ss_disc_auth` DVD/CD auth mode).
  - Explicit comment in Cobra source:
    ```c
    // No need to do the optical disc auth patch for ps2_netemu since there is no optical disc support
    ```
  - **Explanation**: Cobra modders bypassed disc authentication entirely for `ps2_netemu` because netemu was designed exclusively for ISO disk image loading from HDD (`/dev_hdd0/PS2ISO/`). They never patched or enabled optical disc authentication for netemu.

---

### 6. Ranked Analysis: Can `ps2_netemu` Authenticate Physical Discs?
1. **Route 1: Direct VUART Port 10 Request (Plausibility: UNVERIFIED / PROBING IN V1)**:
   - If LV1 accepts Port 10 communication for `PS2_NE_LPAR`, netemu can send the identical `0x70`-byte request (`magic=0xFACE, svc=0x5000, len=0x60, op=0x5005, laid=0x1020000401000001`) to trigger the drive's `SEND KEY` sequence.
   - **Prerequisite**: Port 10 must exist and be accessible in `PS2_NE_LPAR`.
2. **Route 2: Sysmgr VUART Port 2 Proxy (Plausibility: LOW)**:
   - Port 2 is verified bound in netemu (`stock.elf` `0x11810C` thermal management). However, Sysmgr does not expose an optical disc authentication dispatch opcode.
3. **Route 3: Cobra CFW Kernel Hook / LV1 Ability Restoration (Plausibility: HIGH)**:
   - If Port 10 is denied because bit `0x2010000` is missing in `PS2_NE_LPAR` ability flags, a 4-byte CFW patch in `sysmgr_ss.elf` `0x8001E334` (preserving bit `0x2010000`) would restore full Port 10 binding and disc auth capability to `ps2_netemu`.

---

## Part 2: Variant V1 Architecture

### V1 Probe Protocol
Variant V1 executes the full U1 storage sequence up to `READ CAPACITY`, followed by a non-destructive query probe of VUART Port 10, followed by a baseline PIO `READ(10)` of LBA 16:
1. `lv1_open_device(dev_bus=4, dev_id=2)` (HV 170)
2. `lv1_allocate_device_dma_region(dev_bus=4, dev_id=2, size=0x100000, pexp=20)` (HV 174)
3. `lv1_map_device_dma_region(dev_bus=4, dev_id=2, lpar, dma_id, size=0x100000, flags=0xe000000000000800)` (HV 176)
4. ATAPI `TEST UNIT READY` (HV 248)
5. ATAPI `INQUIRY` 36 bytes (HV 248)
6. ATAPI `READ CAPACITY` 8 bytes (HV 248)
7. **Non-Destructive VUART Probes (NO 0x5005 request sent)**:
   - **Probe A (Control)**: `lv1_get_virtual_uart_param(port=2, param_id=3)` (HV 165). Tests known valid Sysmgr port.
   - **Probe B (Target)**: `lv1_get_virtual_uart_param(port=10, param_id=3)` (HV 165). Tests whether Port 10 exists/is bound.
   - **Probe C (Target)**: `lv1_get_virtual_uart_param(port=10, param_id=0)` (HV 165). Tests Port 10 parameter 0.
   - **Probe D (Zero-length read)**: `lv1_read_virtual_uart(port=10, buf=data_lpar, size=0)` (HV 162). Tests read channel validity.
   - **Probe E (Zero-length write)**: `lv1_write_virtual_uart(port=10, buf=data_lpar, size=0)` (HV 163). Tests write channel validity.
8. ATAPI `READ(10)` of LBA 16 (PIO protocol: blocks=2048, bsz=1) for comparison baseline.
9. ATAPI `READ(10)` of LBA 0 (PIO protocol: blocks=2048, bsz=1).
10. ATAPI `READ(10)` of LBA 17 (PIO protocol: blocks=2048, bsz=1).
11. ATAPI `READ(10)` of LBA 16 (DMA protocol: blocks=1, bsz=2048) for comparison baseline.
12. Clean teardown: `unmap` (HV 177) -> `free` (HV 175) -> `close` (HV 171).


---

## Part 3: Build & Verification Audit

### 1. Patch Architecture & Provenance Discipline
- **Safe Hypercall Wrapper (`lv1_hcall`)**:
  - Implemented at code slot `0x4800` (`sc 0` located at `0x4858`).
  - Follows standard Sony LV1 hypercall convention: arguments in `r3..r8`, syscall number in `r11`, returns primary `rc` in `r3`, secondary values in `r4..r5` copied to mailbox `raw_val1` (`0x930F70`) and `raw_val2` (`0x930F78`).
- **Memory Safety & Store Bounds**:
  - Direct stores strictly confined to:
    - Stack (`SP - 0x100000..SP + 0x100000`).
    - Mailbox `0x930F20..0x930F80` (96 bytes).
    - Validated arena (`0x80020000..0x80021000`).
    - Validated CDVD CPU effective address (`0x84000000..0x84002000`).
  - Zero stores to forbidden boundary `0x930F80..0x931000`.
  - Zero CPU stores to physical LPAR address `0x500002c00000`.
- **LLVM IR Pointer Provenance Audit (`audit_ir.py`)**:
  - Analyzed LLVM IR generated by Clang (`build/probe.ll`).
  - Verified every memory write instruction resolves to a verified root (stack, mailbox, arena, cdvd_buf).
  - Provenance audit PASSED with 0 violations.
- **Instruction Audit (`tools/p1a_audit.py`)**:
  - Command: `python -I tools/p1a_audit.py local_only/stock.elf local_only/p10/ps2_netemu_p10_V1.elf`
  - Result: exactly **ONE** `sc` instruction in the binary at offset `0x4858` (`(18520, 0)`). Zero unauthorized syscalls.

### 2. Binary Artifacts & Checksums
| File | Path | Size (Bytes) | SHA-256 Checksum |
|---|---|---|---|
| Patched ELF | `local_only/p10/ps2_netemu_p10_V1.elf` | 10,901,288 | `ce6cd1a408f563b1321141e5fd94e6f6a849159e643789b147ac98669623fad0` |
| Signed SELF | `local_only/p10/ps2_netemu_p10_V1.self` | 2,529,792 | `834a4e538aef2094fa88f1a46af1c8eecbb8bbd9acc68c528b155e1b378d2bee` |
| Decrypted ELF | `local_only/p10/roundtrip_V1.elf` | 10,901,288 | `ce6cd1a408f563b1321141e5fd94e6f6a849159e643789b147ac98669623fad0` |

- **SELF Round-Trip Verification**:
  - `roundtrip_V1.elf` decrypted from `ps2_netemu_p10_V1.self` via `selfdec.py` matches `ps2_netemu_p10_V1.elf` byte-for-byte (SHA-256 match 100%).


---

## Part 4: PC Validation Suite Results (`validate_pc.py`)

All tests were executed against `local_only/p10/ps2_netemu_p10_V1.elf` under PyGhidra emulation with memory write tracking enabled:

1. **Step 1: PowerShell Script Syntax Parse-Check**:
   - `tools/install_netemu.ps1`: PASSED (0 execution, syntax valid).
   - `tools/restore_netemu.ps1`: PASSED (0 execution, syntax valid).
   - `tools/make_log_placeholder.ps1`: PASSED (0 execution, syntax valid).
   - `tools/read_netemu_log.ps1`: PASSED (0 execution, syntax valid).

2. **Step 2: Safe Wrapper & Slot Audit**:
   - `0x4800` wrapper: 29 instructions match stock, `sc 0` at `0x4858`, `mr r8, r9` at `0x4848`. PASSED.

3. **Step 3: Buffer Classification Logic Test**:
   - Tested and verified: `UNCHANGED` (all `0xA5`), `ZEROS` (all `0x00`), `DATA_OK` (`CD001` at offset 1), and `OTHER`. PASSED.

4. **Step 4: Ghidra Emulation Tests**:
   - **Test A1 (V1 VUART Bound Pipeline)**:
     - Hypercall sequence (25 hypercalls): `170, 174, 176, 248, 254, 248, 254, 248, 254, 165, 165, 165, 162, 163, 248, 254, 248, 254, 248, 254, 248, 254, 177, 175, 171`.
     - Menu Row 0: `"P10-V1 PIO16: DATA_OK PVD: CD001"`
     - Menu Row 6: `"VUART: P2=0 P10=0 R0=0 W0=0"`
     - Menu Row 7: `"P10_VAL=0x0000000000000001 P2_VAL=0x0000000000000001"`
     - WAL Log: 40 records logged cleanly with shutdown flag `1`. PASSED.
   - **Test A2 (V1 VUART Unbound Pipeline - Port 10 rc=-6 `LV1_NO_ENTRY`)**:
     - Menu Row 6: `"VUART: P2=0 P10=-6 R0=-6 W0=-6"`
     - Verified graceful handling: non-destructive queries record `-6`, and emulator proceeds cleanly to record baseline sector reads without crash or early abort. PASSED.
   - **Test B (Authentication Required Check Condition)**:
     - CHECK CONDITION status triggers `REQUEST SENSE` (`0x03`), retrieving sense key `0x05`, ASC `0x6F` (Authentication Required). PASSED.
   - **Test C (Bounded Polling Timeout Immediate Halt Discipline)**:
     - Probe halts immediately upon timeout; zero teardown calls issued (no 177, 175, 171). PASSED.
   - **Test D (CDVD Buffer Sanity Guard Refusal & Swapped Fields)**:
     - Corrupted or swapped fields trigger clean refusal with zero hypercalls issued. PASSED.
   - **Test E (Strict Store Bounds & Memory Write Provenance Audit)**:
     - Boundary `0x930F80..0x931000` 100% untouched.
     - Physical LPAR `0x500002c00000` has 0 CPU stores.
     - All memory stores verified within stack, mailbox `0x930F20..0x930F80`, arena `0x80020000..0x80021000`, and CDVD buffer `0x84000000..0x84002000`. PASSED.

---

## Part 5: Summary and Next Steps (P11 Planning)

- **Binary Ready**: `local_only/p10/ps2_netemu_p10_V1.self` is built, signed, round-trip validated, and audited.
- **Ready for Console Test**: Operator can deploy `ps2_netemu_p10_V1.self` to PS3 per [docs/P10_RESULT_TEMPLATE.md](file:///C:/Users/remus\ps2-netemu-disc\docs\P10_RESULT_TEMPLATE.md).
- **Core Unknown Addressed**:
  - Does LV1 accept VUART Port 10 calls from `ps2_netemu`?
  - Console test of V1 will definitively answer this without risking invalid state or lockup, observing Row 6 and WAL log.
