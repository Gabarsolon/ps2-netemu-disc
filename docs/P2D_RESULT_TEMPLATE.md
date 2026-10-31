# P2D Result Template: Netemu Optical DMA & ATAPI Command Variants (K0..K3)

## Context & Objectives

Following the ground truth obtained from the P2C diagnostic probe (`docs/P2C_RESULT.md`), Phase 2D (P2D) resolves the stock allocator model and implements the optical DMA buffer strategy:
1. **Allocator Ground Truth**:
   - The global heap block at `0x930F80` is explicitly zero-initialized by the CRT at startup (`0x11de0..0x11df0`), and its initialization function `0x17324` has zero callers in `stock.elf`.
   - The stock allocator `0x1622c` always falls through to **LV1 Hypercall 0 (`lv1_allocate_memory`)**, successfully allocating physical LPAR memory from the PS3 hypervisor. The P2B "RESOURCE_SHORTAGE" pre-guard was a false positive.
   - The false-positive pre-guard has been **completely removed**.
2. **Buffer Strategy Resolution**:
   - Stock netemu unconditionally allocates a dedicated 1 MiB buffer for CDVD emulation at boot (`0x18cbc` $\rightarrow$ `0x133c80`).
   - Descriptor addresses:
     - Physical LPAR address: `0x2458438`
     - CPU Effective Address: `0x2458428`
     - Buffer capacity: `0x2458430` (`0x100000` = 1 MiB)
   - This buffer (`SB_CDVD`) is **completely isolated** from the HDD driver (`0x241c850`), requires zero runtime hypercalls to allocate, and is already mapped into the guest CPU page table.
   - A verified guard checks `cdvd_lpar != 0`, 4 KiB alignment, and capacity $\ge$ 512 KiB before issuing any hypercalls.
3. **Four Staged Diagnostic Variants**:
   - **K0** (`ps2_netemu_p2d_K0.self`): Baseline verification. `open(4, 2)` $\rightarrow$ `alloc_device_dma_region(0x80000)` $\rightarrow$ `free_device_dma_region` $\rightarrow$ `close(4, 2)`. Reads and displays `cdvd_lpar` and `cdvd_ea`.
   - **K1** (`ps2_netemu_p2d_K1.self`): DMA buffer mapping test. K0 + `map_device_dma_region` (`0x80000` = 512 KiB of `cdvd_lpar`) $\rightarrow$ `unmap_device_dma_region` $\rightarrow$ `free` $\rightarrow$ `close`.
   - **K2** (`ps2_netemu_p2d_K2.self`): ATAPI command test. K1 + `TEST UNIT READY` (opcode 0x00) + `INQUIRY` (opcode 0x12, 36 bytes) with bounded polling loop (200,000 iter / ~2.0s timebase).
   - **K3** (`ps2_netemu_p2d_K3.self`): Disc read test. K2 + `READ CAPACITY(10)` (opcode 0x25) + `lv1_storage_read` (LV1 245) for Sector 16 (ISO 9660 PVD header: `01 43 44 30 30 31 01 00`).
4. **Safety Guarantees**:
   - Bounded polling: On timeout, execution aborts **immediately without unmapping, freeing, or closing** to prevent IOMMU race conditions.
   - Zero writes at or above `0x930F80`. Stores strictly restricted to stack, 96-byte mailbox `[0x930F20, 0x930F80)`, 4 KiB arena, and verified command block.

---

## Owner Test Instructions

> [!IMPORTANT]
> The automated assistant is strictly forbidden from running console install/restore scripts or communicating with the PS3 over the network. The commands below are for the **human owner** to run manually from their PowerShell terminal.

### Safety Protocol
1. **STRICT TESTING ORDER**: Test **K0 FIRST**. Only proceed to K1 if K0 displays `DONE: ALL STEPS OK`. Only proceed to K2 if K1 passes. Only proceed to K3 if K2 passes.
2. **PHYSICAL DISC REQUIREMENTS**:
   - **K0, K1, K2**: Drive can be empty (no disc needed).
   - **K3 Test A**: Run first with drive **EMPTY**.
   - **K3 Test B**: Run second with a **GENUINE PS2 DVD** inserted before launching the ISO.
3. **PAGER OPERATION**:
   - Each variant uses the P2C hardware timebase gap pager.
   - Opening the menu displays **Group 0** (Main Status).
   - Closing the menu and **waiting at least 2.0 seconds** before reopening advances to **Group 1** (Async Status / Counters), then **Group 2** (Hex Dumps), then wraps back to Group 0.
4. **EMERGENCY RECOVERY**:
   - If any variant freezes the console or causes a power-off, hard power on the PS3 and run:
     ```powershell
     tools\restore_netemu.ps1
     ```
   - Do NOT proceed to subsequent variants.

---

### Step 1: Test Variant K0 (`ps2_netemu_p2d_K0.self`)

1. Install Variant K0 from repository root:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2d\ps2_netemu_p2d_K0.self -Force
   ```
2. On PS3 (Blu-ray drive empty):
   - Launch any standard PS2 ISO via webMAN MOD.
   - Once rendering starts, press the **PS button** to display the in-game menu.
3. Observe and photograph the menu rows:
   - **Row 0**: Should read `P2D-K0 DONE: ALL STEPS OK`
   - **Row 1**: `RC: OP=0 DMA=0 CL=0 HC=42`
   - **Row 2**: `CDVD LPAR: 0x0000500002f00000` (or similar physical address)
   - **Row 3**: `CDVD EA:   0x0000000085000000 SZ=100000`
   - **Row 4**: `DMA RGN=0x00000008` (or returned region handle)
   - **Rows 5..8**: `TUR / INQ / CAP / LBA16: NOT RUN IN K0`
4. Advance pager (close menu, wait 2 seconds, reopen):
   - **Row 0**: `P2D-K0 - GROUP 1: ASYNC STATUS`
   - Verify `FAIL: STEP=0` and `TIMEOUTS: 0x0`.
5. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 2: Test Variant K1 (`ps2_netemu_p2d_K1.self`)

> [!WARNING]
> Only proceed if K0 passed cleanly with zero errors.

1. Install Variant K1:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2d\ps2_netemu_p2d_K1.self -Force
   ```
2. On PS3 (drive empty):
   - Launch PS2 ISO via webMAN MOD.
   - Press **PS button** to display the menu.
3. Observe and photograph the menu rows:
   - **Row 0**: Should read `P2D-K1 DONE: ALL STEPS OK`
   - **Row 1**: `RC: OP=0 DMA=0 MAP=0 CL=0 HC=44`
   - **Row 2**: `CDVD LPAR: 0x...`
   - **Row 3**: `CDVD EA:   0x... SZ=100000`
   - **Row 4**: `DMA RGN=0x... BUS=0x00000000`
4. Advance pager (close menu, wait 2 seconds, reopen):
   - Verify `MAP RC=0`, `UNMAP RC=0`, and `FAIL: STEP=0`.
5. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 3: Test Variant K2 (`ps2_netemu_p2d_K2.self`)

> [!WARNING]
> Only proceed if K1 passed cleanly.

1. Install Variant K2:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2d\ps2_netemu_p2d_K2.self -Force
   ```
2. On PS3 (drive empty):
   - Launch PS2 ISO via webMAN MOD.
   - Press **PS button** to display the menu.
3. Observe and photograph the menu rows:
   - **Row 0**: `P2D-K2 DONE: ALL STEPS OK` (or `P2D-K2 TIMEOUT AT STEP=...`)
   - **Row 4**: `DMA RGN=0x... BUS=0x00000000`
   - **Row 5**: `TUR RC=<rc> STAT=0x<stat>`
   - **Row 6**: `INQ RC=<rc>: "SONY    PS-SYSTEM   308R"` (or drive model string)
4. Advance pager to Group 1 & Group 2:
   - Group 1: Record `TUR ASYNC STAT` and `INQ ASYNC STAT`.
   - Group 2: Record `INQ[00..07]` through `INQ[24..31]` raw hex values.
5. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 4: Test Variant K3 (`ps2_netemu_p2d_K3.self`)

> [!WARNING]
> Only proceed if K2 passed cleanly.

#### Test 4A: With Drive EMPTY
1. Install Variant K3:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2d\ps2_netemu_p2d_K3.self -Force
   ```
2. Launch PS2 ISO with Blu-ray drive empty.
3. Press **PS button** and record:
   - Expected: `TUR STAT` indicates medium not present (e.g. `0x00000002` NOT READY), or `CAP RC` returns medium error.
   - Photograph Rows 0..8 for Groups 0, 1, and 2.
4. Exit game.

#### Test 4B: With Genuine PS2 DVD Inserted
1. Insert a genuine PS2 DVD disc into the PS3 drive.
2. Launch the PS2 ISO via webMAN MOD.
3. Press **PS button** once in-game.
4. Observe and photograph the menu rows:
   - **Row 0**: `P2D-K3 DONE: ALL STEPS OK`
   - **Row 5**: `TUR RC=0 STAT=0x00000000 (READY)`
   - **Row 6**: `INQ RC=0: "SONY    PS-SYSTEM   308R"`
   - **Row 7**: `CAP RC=0 LBA=0x... BLK=2048`
   - **Row 8**: `LBA16 RC=0 ISO PVD "CD001" MATCH!` (or raw hex if non-standard)
5. Advance pager to Group 1 & Group 2:
   - Group 1: Record async statuses for TUR, INQ, CAP, and READ.
   - Group 2: Record raw hex data of Sector 16 (`LBA16[00..07]` through `LBA16[24..31]`).
6. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

## Result Recording Form

### Variant K0 Recording
- **Menu Open 0 (Group 0)**:
  - Row 0: `______________________________________`
  - Row 1: `______________________________________`
  - Row 2 (`CDVD LPAR`): `0x_______________________`
  - Row 3 (`CDVD EA`): `0x_________________________`
  - Row 4 (`DMA RGN`): `0x_________________________`
- **Menu Open 1 (Group 1)**:
  - Fail Step: `____` | Total HC: `____` | Timeouts: `0x____`

### Variant K1 Recording
- **Menu Open 0 (Group 0)**:
  - Row 0: `______________________________________`
  - Row 1: `______________________________________`
  - Row 4 (`DMA RGN / BUS`): `_____________________`
- **Menu Open 1 (Group 1)**:
  - Map RC: `____` | Unmap RC: `____` | Fail Step: `____`

### Variant K2 Recording
- **Menu Open 0 (Group 0)**:
  - Row 0: `______________________________________`
  - Row 5 (`TUR RC / STAT`): `_____________________`
  - Row 6 (`INQ RC / STRING`): `___________________`
- **Menu Open 1 (Group 1)**:
  - TUR Async Stat: `0x___________________________`
  - INQ Async Stat: `0x___________________________`
- **Menu Open 2 (Group 2)**:
  - INQ[00..07]: `________________________________`
  - INQ[08..15]: `________________________________`
  - INQ[16..23]: `________________________________`
  - INQ[24..31]: `________________________________`

### Variant K3 Recording (Drive EMPTY)
- Row 0: `______________________________________`
- Row 5 (`TUR`): `_______________________________`
- Row 6 (`INQ`): `_______________________________`
- Row 7 (`CAP`): `_______________________________`
- Row 8 (`LBA16`): `_____________________________`

### Variant K3 Recording (PS2 DVD Inserted)
- **Menu Open 0 (Group 0)**:
  - Row 0: `______________________________________`
  - Row 5 (`TUR`): `_______________________________`
  - Row 6 (`INQ`): `_______________________________`
  - Row 7 (`CAP`): `_______________________________`
  - Row 8 (`LBA16`): `_____________________________`
- **Menu Open 1 (Group 1)**:
  - CAP Async Stat:  `0x__________________________`
  - READ Async Stat: `0x__________________________`
- **Menu Open 2 (Group 2)**:
  - LBA16[00..07]: `______________________________`
  - LBA16[08..15]: `______________________________`
  - LBA16[16..23]: `______________________________`
  - LBA16[24..31]: `______________________________`

---

## Decision Table for Console Outcomes

| Variant | Observed Console Result | Meaning | Next Action |
|---|---|---|---|
| **K0** | `DONE: ALL STEPS OK`, `OP=0`, `DMA=0`, `CL=0` | Baseline hypercalls 170, 174, 175, 171 function identically to P1g. `SB_CDVD` addresses successfully read. | **Proceed to Variant K1**. |
| **K0** | Console freezes or powers off | Severe hypervisor regression on LV1 174/175. | Restore netemu. Stop. |
| **K1** | `DONE: ALL STEPS OK`, `MAP=0`, `BUS=0x0` | LV1 176 successfully mapped physical `SB_CDVD` into optical device DMA. LV1 177 unmapped cleanly. | **Proceed to Variant K2**. |
| **K1** | `FAIL: STEP=3 RC=-X` | `lv1_map_device_dma_region` rejected `cdvd_lpar` or flags. | Inspect error code `-X`. Check if LPAR address requires different permission flags or alignment. |
| **K2** | `DONE: ALL STEPS OK`, INQUIRY displays `"SONY PS-SYSTEM"` | Optical ATAPI controller responds to commands from netemu partition! Storage command protocol verified. | **Proceed to Variant K3**. |
| **K2** | `TIMEOUT AT STEP=5 (ABORTED)` | `lv1_storage_check_async_status` timed out after 200,000 iterations (~2.0s). Safety abort preserved system state. | Check if ATAPI tag was dropped or requires interrupt acknowledgement. |
| **K3 (Empty)** | `TUR STAT=0x2` / `CAP RC=-X`, console stable | Drive correctly reports no medium present. Partition remains stable. | **Proceed to K3 with PS2 DVD**. |
| **K3 (DVD)** | `LBA16 RC=0 ISO PVD "CD001" MATCH!` | **FULL MILESTONE ACHIEVED**: Netemu successfully read raw physical sectors from a genuine PS2 DVD! Phase 3 (CDVD hooks) can proceed immediately. | Provide results to agent to begin Phase 3 payload integration. |
| **K3 (DVD)** | `READ STAT=0x00000004` (Auth Error / Media Error) | Drive requires media authentication handshake before allowing sector reads (virtual UART 10 / opcode 0x5005). | Record exact status. Next step is implementing authentication command sequence. |
| **Any** | `FAIL: CDVD GUARD` | `0x2458438` held zero or invalid LPAR address. | Record raw values from K0 Menu Row 2 & 3. |
