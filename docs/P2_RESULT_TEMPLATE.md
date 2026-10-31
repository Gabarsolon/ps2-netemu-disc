# P2 Result Template: Netemu Optical Read Diagnostic Stages (H0..H3)

## Context & Objectives

Following the successful P1g milestone on the owner's CECH-25xx console—where `lv1_open_device(4, 2, 0)` and `lv1_close_device(4, 2)` both returned `0` (`SUCCESS`) from within the `ps2_netemu` partition—Phase 2 (P2) systematically advances from claiming the device to reading physical optical media sectors.

Four staged, label-only diagnostic variants test each hardware and hypercall dependency in strict sequential progression:
- **Variant H0** (`ps2_netemu_p2_H0.self`):
  - Sequence: `open(4, 2, 0)` -> `lv1_allocate_device_dma_region(4, 2, 0x80000, 12, 0)` (LV1 174) -> `lv1_free_device_dma_region(4, 2, dma_region)` (LV1 175) -> `close(4, 2)`.
  - Purpose: Validates DMA region allocation from the netemu partition without allocating or mapping guest buffers. Records returned DMA region handle.
- **Variant H1** (`ps2_netemu_p2_H1.self`):
  - Sequence: H0 + stock allocator shim `0x19a5c` (`"SB_OPT"`, 1 MiB) + `lv1_map_device_dma_region(4, 2, lpar, dma_region, 0x80000, 0xe000000000000800)` (LV1 176) + `lv1_unmap_device_dma_region(4, 2, dma_region, 0x80000)` (LV1 177) before free.
  - Purpose: Validates LPAR physical buffer acquisition and IOMMU translation mapping into the optical device.
- **Variant H2** (`ps2_netemu_p2_H2.self`):
  - Sequence: H1 + ATAPI command execution via `lv1_storage_send_device_command` (LV1 248) and bounded polling via `lv1_storage_check_async_status` (LV1 254).
  - Commands:
    1. `TEST UNIT READY` (Opcode `0x00`, 0 bytes transfer)
    2. `INQUIRY` (Opcode `0x12`, 36 bytes inbound; expected: `"SONY    PS-SYSTEM   308R"`)
  - Safety: Hard timeout bound (200,000 iterations OR ~2.0 seconds timebase via `0xb9cd0` `mftb`). If a timeout occurs, execution halts immediately **without** unmapping, freeing, or closing, avoiding IOMMU race conditions.
- **Variant H3** (`ps2_netemu_p2_H3.self`):
  - Sequence: H2 + `READ CAPACITY(10)` (Opcode `0x25`, 8 bytes inbound) + `lv1_storage_read` (LV1 245) for Sector 16 (1 sector = 2048 bytes; expected ISO9660 PVD header: `01 43 44 30 30 31 01 00`).
  - Testing: Tested first with an **empty drive**, then with a **genuine PS2 DVD inserted**.
  - Purpose: Demonstrates whether the netemu partition can directly read disc sectors or whether optical media authentication via virtual UART 10 (`0x5000` op `0x5005`) is strictly enforced by the drive firmware.

---

## Owner Test Instructions

> [!IMPORTANT]
> **Safety Protocol:**
> 1. **STRICT SEQUENCE**: Test **H0 FIRST**. Only proceed to H1 if H0 reports clean success and powers on normally. Only proceed to H2 if H1 passes. Only proceed to H3 if H2 passes.
> 2. **NO PHYSICAL DISC NEEDED** for H0, H1, and H2. Drive can be empty.
> 3. For **H3**:
>    - **Test 4A**: Run first **WITHOUT a disc** in the drive (drive empty).
>    - **Test 4B**: Run second **WITH a genuine PS2 DVD inserted** before launching the ISO.
> 4. If any test causes a console freeze or power-off, record it immediately. Hard power-on and run `tools\restore_netemu.ps1`. **DO NOT proceed to subsequent variants!**

---

### Step 1: Test Variant H0 (`ps2_netemu_p2_H0.self`)
1. From the PC terminal in `C:\Users\remus\ps2-netemu-disc`:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2\ps2_netemu_p2_H0.self -Force
   ```
2. On the PS3 (CECH-25xx, Evilnat 4.93 Cobra):
   - Ensure the Blu-ray drive is **empty**.
   - Launch any standard PS2 ISO from webMAN MOD.
   - Once the game reaches the title screen or gameplay, press the **PS button** to display the in-game menu.
3. Observe console behavior:
   - **Case H0-Fail (Console powers off or freezes)**: Record power-off. Hard power-on and run `tools\restore_netemu.ps1`. Do NOT proceed to H1.
   - **Case H0-Pass (Menu appears normally)**:
     - Navigate to `Debug Information` (rows 0 through 3).
     - Photograph Row 0 (Page A).
     - Photograph Row 1 (Page B).
     - Photograph Row 2 (Page C).
     - Photograph Row 3 (Page D).
4. Restore clean netemu baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 2: Test Variant H1 (`ps2_netemu_p2_H1.self`)
> [!WARNING]
> Only execute this step if Variant H0 produced a clean `DONE ALL OK` on Page A.
1. Install Variant H1:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2\ps2_netemu_p2_H1.self -Force
   ```
2. Launch PS2 ISO (drive empty), press **PS button**, and observe:
   - **Case H1-Fail (Shutdown/Freeze)**: Record failure. Restore with `tools\restore_netemu.ps1`.
   - **Case H1-Pass (Menu appears)**: Photograph rows 0..3 (Pages A through D).
3. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 3: Test Variant H2 (`ps2_netemu_p2_H2.self`)
> [!WARNING]
> Only execute this step if Variant H1 confirmed `MAP & UNMAP SUCCESSFUL` on Page C.
1. Install Variant H2:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2\ps2_netemu_p2_H2.self -Force
   ```
2. Launch PS2 ISO (drive empty), press **PS button**, and observe:
   - Note: Command polling is bounded to 2 seconds. The menu may take 1-2 seconds longer to appear if the drive returns not-ready.
   - **Case H2-Pass (Menu appears)**: Photograph rows 0..3 (Pages A through D). Record Page C INQUIRY result!
   - **Case H2-Fail (Shutdown/Freeze)**: Record failure. Restore with `tools\restore_netemu.ps1`.
3. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 4A: Test Variant H3 Without Disc (`ps2_netemu_p2_H3.self`)
> [!CAUTION]
> Tests Sector 16 storage read path. Execute first without a disc to verify clean not-ready handling.
1. Install Variant H3:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2\ps2_netemu_p2_H3.self -Force
   ```
2. With drive **EMPTY**, launch PS2 ISO, press **PS button**, and observe:
   - Expect: Page C reports `READ STATUS=NOT READY (NO DISC)` or similar clean status without crashing.
   - Photograph rows 0..3 (Pages A through D).

---

### Step 4B: Test Variant H3 With PS2 DVD Inserted (`ps2_netemu_p2_H3.self`)
> [!IMPORTANT]
> The defining test of Phase 2!
1. With Variant H3 still installed:
   - Insert a genuine **PS2 DVD-ROM game disc** into the PS3 slot.
   - Wait 5 seconds for the drive mechanism to spin up and identify the media.
2. Launch any standard PS2 ISO from webMAN MOD.
3. Once in-game, press the **PS button**:
   - Observe Page C:
     - If `PVD MATCH (01 43 44 30 30 31 01 00 ISO9660 OK!)`: **COMPLETE SUCCESS!** Netemu can read sectors directly!
     - If `READ STATUS=AUTH REQ (EXPECTED PS2 DISC)`: **CRITICAL DISCOVERY!** Optical hardware functions, sector reading requires drive authentication via UART 10 (`0x5000` op `0x5005`).
   - Photograph rows 0..3 (Pages A through D).
4. Restore clean netemu baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

## Expected vs Observed Labels

### Variant H0 (`ps2_netemu_p2_H0.self`)
| Page | Expected (DMA Region Alloc & Free) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P2-H0 DONE ALL OK (STEPS COMPLETE)` | | All steps (open, alloc, free, close) succeeded |
| **Page B (Row 1)** | `P2-H0 RC: ALL CALLS SUCCESS (RC=00000000)` | | All hypercalls returned 0 |
| **Page C (Row 2)** | `P2-H0 DATA: DMA REGION ID = 0` (or `1`) | | Allocated DMA region ID handle |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

---

### Variant H1 (`ps2_netemu_p2_H1.self`)
| Page | Expected (Buffer Alloc & DMA Map/Unmap) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P2-H1 DONE ALL OK (STEPS COMPLETE)` | | Open, alloc_buffer, alloc_dma, map, unmap, free, close |
| **Page B (Row 1)** | `P2-H1 RC: ALL CALLS SUCCESS (RC=00000000)` | | All hypercalls returned 0 |
| **Page C (Row 2)** | `P2-H1 DATA: MAP & UNMAP SUCCESSFUL (BUFFER OK)` | | Buffer allocated via shim `0x19a5c` and mapped cleanly |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

---

### Variant H2 (`ps2_netemu_p2_H2.self`)
| Page | Expected (TUR & INQUIRY ATAPI Commands) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P2-H2 DONE ALL OK (STEPS COMPLETE)` | | ATAPI commands dispatched and completed |
| **Page B (Row 1)** | `P2-H2 RC: ALL CALLS SUCCESS (RC=00000000)` | | Submission & poll calls returned 0 |
| **Page C (Row 2)** | `P2-H2 DATA: INQ "SONY    PS-SYSTEM   308R" OK!` | | INQUIRY string matches PS3 Blu-ray drive |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

---

### Variant H3 — Test 4A: Drive Empty (`ps2_netemu_p2_H3.self`)
| Page | Expected (Read with No Disc) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P2-H3 DONE ALL OK (STEPS COMPLETE)` (or `P2-H3 FAIL READ rc=HEX`) | | Clean handling of empty drive |
| **Page B (Row 1)** | `P2-H3 RC: ALL CALLS SUCCESS (RC=00000000)` (or hex status) | | Low 32-bit async status code |
| **Page C (Row 2)** | `P2-H3 DATA: READ STATUS=NOT READY (NO DISC)` | | Drive reports not ready (`0x02023a00`) |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

---

### Variant H3 — Test 4B: PS2 DVD Inserted (`ps2_netemu_p2_H3.self`)
| Page | Potential Outcomes | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P2-H3 DONE ALL OK (STEPS COMPLETE)` | | Command executed |
| **Page B (Row 1)** | `P2-H3 RC: ALL CALLS SUCCESS (RC=00000000)` | | Low 32-bit status |
| **Page C (Row 2)** | **Outcome 1**: `P2-H3 DATA: PVD MATCH (01 43 44 30 30 31 01 00 ISO9660 OK!)`<br>**Outcome 2**: `P2-H3 DATA: READ STATUS=AUTH REQ (EXPECTED PS2 DISC)` | | **Outcome 1**: Direct sector read proven!<br>**Outcome 2**: Optical hardware functional; auth required |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

---

## Decision Table & Root Cause Analysis

| Variant | Observed Outcome | Interpretation | Root Cause / Technical Context | Next Action |
|---|---|---|---|---|
| **H0** | **`DONE ALL OK`, `DMA REGION ID = 0` or `1`** | **PROVEN**: Netemu partition has full authority to allocate device DMA regions on the optical node via LV1 174! | IOMMU region allocator functions without restriction. | Proceed to **Variant H1**. |
| **H0** | **`FAIL DMA_ALLOC rc=DENIED_BY_POLICY` (-4)** | Hypercall 174 checks caller partition authority and rejects `SCE_CELLOS_SYSTEM_MGR_PS2_NE`. | LV1 partition permission table (`0x31ce8c`). | Investigate Cobra stage2 patch for LV1 174 permission check. |
| **H0** | **`FAIL DMA_ALLOC rc=RESOURCE_SHORTAGE` (-2)** | All DMA regions for optical node are allocated or limit is 0. | Optical node DMA region table in LV1. | Check if GameOS left a region allocated or if region count is exhausted. |
| **H0** | **Console powers off / freezes** | Execution fault in wrapper or unhandled exception in LV1 174/175. | ABI register mismatch or hypercall trap. | Inspect register preservation across wrapper; compare with stock `0x111eb8`. |
| **H1** | **`DONE ALL OK`, `MAP & UNMAP SUCCESSFUL`** | **PROVEN**: Stock allocator shim `0x19a5c("SB_OPT", 1 MiB)` produces valid LPAR physical memory, and LV1 176 maps it to device DMA! | Physical buffer management & IOMMU mapping functional. | Proceed to **Variant H2**. |
| **H1** | **`FAIL ALLOC_SHIM`** | Stock allocator shim failed to allocate 1 MiB buffer or returned NULL pointers. | Netemu memory pool exhausted or heap cursor error. | Adjust allocation size from 1 MiB to 64 KiB or 512 KiB. |
| **H1** | **`FAIL MAP rc=INVALID_PARAMETER` (-17)** | LV1 176 rejected mapping parameters (page alignment, size, or flags `0xe000000000000800`). | IOMMU translation parameters. | Re-verify flags against stock helper `0x160fc`. |
| **H1** | **`FAIL MAP rc=ACCESS_VIOLATION` (-5)** | LPAR physical address is not owned by the netemu partition. | Partition physical memory bounds. | Inspect `0x1622c` pool bounds against LPAR memory descriptor. |
| **H2** | **`INQ "SONY    PS-SYSTEM   308R" OK!`** | **BREAKTHROUGH**: Direct ATAPI communication with Blu-ray drive is fully operational from netemu! Drive controller responds to inquiry! | ATAPI 64-byte command block & PIO DMA inbound transfer work. | Proceed to **Variant H3**. |
| **H2** | **`DATA: TUR NOT READY (NO DISC)`** | TUR reported disc absent (`0x02023a00`), but INQUIRY responded normally. | Normal behavior for an empty optical drive. | Expected if drive is empty. Proceed to **Variant H3**. |
| **H2** | **`TIMEOUT AT TUR` or `TIMEOUT AT INQUIRY`** | Drive controller never acknowledged command within 200k polls / 2s. | Drive interrupt / status register unresponsive on PCI bus. | Safe timeout mechanism caught the hang without unmapping. Check physical bus clock/power. |
| **H3 (Empty)** | **`READ STATUS=NOT READY (NO DISC)`** | LV1 245 storage_read gracefully returned media-not-present status without crash. | Drive media sensor reporting empty drive. | Proceed to **Test 4B (Insert PS2 DVD)**. |
| **H3 (PS2 DVD)** | **`PVD MATCH (01 43 44 30 30 31 01 00)`** | **PROJECT GOAL FEASIBLE!** The `ps2_netemu` partition can directly read raw PS2 DVD sectors without pre-authentication! | Drive hardware allows direct sector reads or CFW/Cobra left drive in authenticated state. | Proceed directly to backend implementation (virtual CDVD driver routing to physical optical drive). |
| **H3 (PS2 DVD)** | **`READ STATUS=AUTH REQ (0x02052100 / ENXIO)`** | **CRITICAL ARCHITECTURAL FINDING**: Sector read is blocked by drive firmware because PS2 media authentication has not been performed. | Optical drive firmware requires PS2 disc handshake via virtual UART 10 (`0x5000` op `0x5005`). | Implement the secure service UART 10 handshake before sector reading (as documented in `docs/P0G_SOFTEMU_ANALYSIS.md`). |
| **H3 (PS2 DVD)** | **`READ SUCCESSFUL (NON-PVD HEADER)`** | Sector 16 was read successfully, but header does not match standard ISO9660 PVD. | Media format is non-standard (e.g. CD-ROM mode 2, raw audio, or encrypted track). | Check disc type (CD vs DVD) and inspect raw bytes in mailbox. |
