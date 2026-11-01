# P5 Test Execution & Results Protocol (Console Owner Guide)

## Overview: Diagnostic Search for Optical DMA Mapping Parameters (Variant Q1)

In P4 K1 on console (`docs/P4_K1_RESULT.md`), storage open (`4, 2`) and DMA region creation (`0xC0000000`) succeeded, but mapping the `SB_CDVD` buffer (`0x84000000`) returned `-17` (`LV1_ILLEGAL_PARAMETER_VALUE`).

**P5 Variant Q1** tests a systematic sequence of ranked candidate argument sets (Groups A, B, C, D) directly on console:
- **Group A (Candidates #1..#5)**: Matches official Sony emulator optical standard (`size=0x100000, page_exp=20, len=0x100000`).
- **Group B (Candidates #6..#8)**: Region size `0x100000`, page exponent 12 (4 KiB pages).
- **Group C (Candidates #9..#11)**: Region size `0x80000`, page exponent 12 (HDD-style).
- **Group D (Candidate #12)**: Region size `0x100000`, page exponent 16 (64 KiB pages).

**Stopping rule**: Q1 stops at the **very first candidate that returns `rc == 0`**, immediately unmaps, frees, closes the device cleanly, and writes `TAG_END` to the durable WAL log.

> [!NOTE]
> **Zero-Photo Diagnostic**: No photos or videos required. The entire probe history and results are recorded to `/dev_hdd0/tmp/netemu_log.bin` and decoded on PC with `python tools/decode_netemu_log.py local_only/netemu_log.bin`.

---

## Pre-Flight Checklist

1. **Verify Placeholder Log**:
   Ensure `/dev_hdd0/tmp/netemu_log.bin` (64 KiB) exists on the console. If missing, generate it:
   ```powershell
   powershell -ExecutionPolicy Bypass -File tools\make_log_placeholder.ps1
   ```

2. **Binary Hashes for Q1**:
   - `local_only/p5/ps2_netemu_p5_Q1.self` (2,527,968 bytes)
   - SHA256: `f9e8080f08d88cca79629e13cb882c44e58f5d1e77f0535d0fbc60e9d5652afd`

---

## Step-by-Step Operator Instructions

### Step 1: Deploy Variant Q1
Copy `ps2_netemu_p5_Q1.self` to `/dev_hdd0/game/PS2U10000/USRDIR/ps2_netemu.self`:
```powershell
powershell -ExecutionPolicy Bypass -File tools\install_netemu.ps1 -Variant local_only\p5\ps2_netemu_p5_Q1.self
```

### Step 2: Launch Test PS2 Game
1. On the PS3 XMB, launch any standard PS2 Classic or test ISO (e.g. `SLUS_200.02`).
2. Wait for the game 3D graphics or opening video to begin rendering.

### Step 3: Trigger the Diagnostic Hook
1. **Press the PS button on the controller once** to display the in-game overlay menu.
2. The probe hook executes automatically on the first menu frame.
3. Observe the menu label (optional, e.g. `P5-Q1 DONE: CAND #1 MAP OK`).
4. Select "Quit Game" to return to the PS3 XMB.

### Step 4: Retrieve and Decode the Log
1. Retrieve the log file from the console:
   ```powershell
   powershell -ExecutionPolicy Bypass -File tools\read_netemu_log.ps1
   ```
   *(Or FTP download `/dev_hdd0/tmp/netemu_log.bin` to `local_only/netemu_log.bin`).*
2. Decode the log:
   ```powershell
   python tools/decode_netemu_log.py local_only/netemu_log.bin
   ```
3. Copy the decoded output into the form below.

---

## Candidate Evaluation Matrix

| Cand # | Group | Alloc Size | Alloc Exp | Map Len | Map Flags | Expected Result | Actual Console `rc` |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **#1** | A | `0x100000` | **20** | `0x100000` | `0xe000000000000800` | **Official emulator optical standard** | `________` |
| **#2** | A | `0x100000` | **20** | `0x100000` | `0xe000000000000000` | Flags without 0x800 bit | `________` |
| **#3** | A | `0x100000` | **20** | `0x100000` | `0xf800000000000000` | Linux PS3 IOPTE flags (`SO_RW`) | `________` |
| **#4** | A | `0x100000` | **20** | `0x100000` | `0x6000000000000800` | Read-only permission | `________` |
| **#5** | A | `0x100000` | **20** | `0x80000`  | `0xe000000000000800` | Partial 512 KiB length | `________` |
| **#6** | B | `0x100000` | **12** | `0x100000` | `0xe000000000000800` | 4 KiB pages, 1 MiB region | `________` |
| **#7** | B | `0x100000` | **12** | `0x80000`  | `0xe000000000000800` | 4 KiB pages, 512 KiB length | `________` |
| **#8** | B | `0x100000` | **12** | `0x1000`   | `0xe000000000000800` | 4 KiB pages, 4 KiB length | `________` |
| **#9** | C | `0x80000`  | **12** | `0x80000`  | `0xe000000000000000` | 512 KiB region, no 0x800 | `________` |
| **#10**| C | `0x80000`  | **12** | `0x80000`  | `0xf800000000000000` | 512 KiB region, Linux flags | `________` |
| **#11**| C | `0x80000`  | **12** | `0x1000`   | `0xe000000000000800` | 512 KiB region, 4 KiB length | `________` |
| **#12**| D | `0x100000` | **16** | `0x100000` | `0xe000000000000800` | 64 KiB pages, 1 MiB region | `________` |

---

## Decision Tree for Results Interpretation

```
                                [ Q1 Console Run ]
                                        |
                 +----------------------+----------------------+
                 |                                             |
         [ Candidate #1 rc == 0 ]                     [ Candidate #1 rc != 0 ]
                 |                                             |
     =============================                     +-------+-------+
     PRIMARY HYPOTHESIS CONFIRMED!                     |               |
     - Exp 20 + Len 0x100000 works.              [ Cand #2..#5 rc == 0 ]  [ All 12 rc == -17 ]
     - Matches softemu & gxemu.                        |                       |
     - PROCEED TO P6: Full disc               ===================      ===================
       sector read via ATAPI SCSI             FLAG / LENGTH FIX!       HYPERVISOR SECURITY
       packet commands on console!            - Note winning flags     - Check bus permission
     =============================            - Proceed to P6          - Check storage grant
```

1. **If Candidate #1 succeeds (`rc == 0`)**:
   - Primary hypothesis confirmed: Page Size Exponent 20 (1 MiB) with Length 1 MiB (`0x100000`) and Flags `0xe000000000000800`.
   - Action: **Proceed directly to P6** to issue SCSI ATAPI packets (`TEST UNIT READY`, `INQUIRY`, `READ CAPACITY`, and `READ (10)` of ISO 9660 PVD sector 16) with DMA mapped to real physical drive!

2. **If Candidate #2..#5 succeed (`rc == 0`)**:
   - Page exponent 20 is correct, but specific flag bits or mapping length were required.
   - Action: Adopt the winning flag combination and proceed to P6.

3. **If Candidates #6..#12 succeed (`rc == 0`)**:
   - The hypervisor accepts a different page exponent (12 or 16).
   - Action: Adopt the winning allocation/mapping pair and proceed to P6.

4. **If ALL 12 candidates return `-17` (`LV1_ILLEGAL_PARAMETER_VALUE`)**:
   - The issue is not page size exponent, mapping length, or IOPTE flags.
   - Action: Investigate hypervisor-level storage bus grant/authorization, device state, or alternate DMA allocation flags.

---

## Result Capture Form (Fill in after run)

### Environment
- **Date / Time**: `2026-11-01 __:__`
- **Console Model**: `________________` (e.g. CECH-2501B / CECH-A01)
- **Firmware**: Evilnat 4.91.2 Beta 9 [PEX] (or specify)
- **PS2 Game Used for Test**: `________________` (e.g. SLUS_200.02)
- **On-Screen Menu Row 0 Text**: `________________`

### Decoded Log Output
```text
=== LOG HEADER (Sector 0) ===
Header Magic:     'NETEMULG'
Version:          0x00010000
Header Size:      512 bytes
File Size:        65536 bytes
Sector Size:      512 bytes
Capacity:         127 records
Next Record Idx:  #...
Boot TB:          0x...
Shutdown:         CLEAN / UNCOMMITTED
Record Count:     ...

=== LOG RECORDS ===
(Paste full output from python tools/decode_netemu_log.py local_only/netemu_log.bin here)
```

### Analysis & Next Step
- **Winning Candidate**: `Cand #___` (or `None - All Failed`)
- **DMA Bus Address**: `0x________`
- **Next Task**: `P6 (Optical Sector Read)` / `Investigation Path B`
