# P2E Result Template: Netemu Optical Read Stages (K0..K3) [Defect Fix Build]

## Context & Defect Fix Overview

In Phase 2D (P2D), the console owner executed baseline variant K0 on hardware (`docs/P2D_K0_RESULT.md`), confirming clean hypercall execution (`RC: OP=0 DMA=0 CL=0 HC=130`). However, the diagnostic output revealed a critical address swap:
- Field at `0x2458438`: `0x0000500002c00000`
- Field at `0x2458428`: `0x0000000084000000`
- Field at `0x2458430`: `0x0000000000100000` (1 MiB)

Comparing with the measured HDD driver state (`docs/P2C_RESULT.md`), `0x500002c00000` is the CPU Effective Address (EA), and `0x84000000` is the physical partition (LPAR) address.
In P2D, the two fields were swapped relative to naming. If K1..K3 had executed, it would have passed the CPU EA to `lv1_map_device_dma_region` (LV1 176) and attempted to write the ATAPI command block through `0x84000000` (an unmapped pointer in CPU HTAB), causing a fatal Data Storage Interrupt (DSI crash).

### What Was Fixed in P2E:
1. **Field Assignment Fixed**:
   - Physical LPAR address loaded from `0x2458428` (`0x0000000084000000`).
   - CPU Effective Address loaded from `0x2458438` (`0x0000500002c00000`).
   - Capacity loaded from `0x2458430` (`0x0000000000100000`, 1 MiB).
2. **Symmetric Runtime Sanity Guard**:
   - Does NOT rely on naming or assumptions:
     - LPAR must be `< 0x1_0000_0000`, `>= 0x80000000`, and 1 MiB aligned (`(lpar & 0xFFFFF) == 0`).
     - EA must be `>= 0x1_0000_0000`, match the `0x5000_0000_0000` pattern, and `ea != lpar`.
     - Size must be $\ge$ 512 KiB (`0x80000`).
   - If ANY condition fails (including swapped fields):
     - Issues **ZERO hypercalls**.
     - Displays `P2E-K<n> SANITY REJECT (0 HC)`.
     - Displays raw values on Row 2 and Row 3 for debugging.
3. **Address-Kind Audit Across All Stages**:
   - `lv1_map_device_dma_region` (LV1 176): passes `cdvd_lpar` (`0x84000000`).
   - ATAPI command block write by CPU: writes directly to mapped CPU EA `cdvd_ea` (`0x500002c00000`).
   - `lv1_storage_send_device_command` (LV1 248): passes `cmnd_block_lpar` (`0x84000000`).
   - ATAPI command packet `+0x38`: passes `buffer = data_lpar` (`0x84001000`).
   - `lv1_storage_read` (LV1 245): passes `data_lpar` (`0x84001000`).
   - CPU reads of INQUIRY and Sector 16: reads directly from mapped CPU EA `data_ea` (`0x500002c01000`).
4. **PC Validation Harness**:
   - Verified that command block writes occur at CPU EA (`0x500002c00000`) and DMA mappings use LPAR (`0x84000000`).
   - Negative test with swapped fields: verified that guard refuses with 0 hypercalls.
   - Memory write audit: verified that stores are strictly restricted to stack, mailbox, arena, and mapped EA, with zero writes to unmapped EA (`0x84000000`).
   - Exactly ONE `sc` instruction in changed executable ranges (`0x4858`).

---

## Verified Build Hashes (P2E)

| Variant | PROBE_VARIANT | Patched ELF SHA-256 | Signed SELF SHA-256 | Code Size |
|---|---|---|---|---|
| **K0** | `0` | `0e096b409f53a4e4b9620e003d97f312a6f09a57015a881fa80d7a9457737e9c` | `a0c7f767c5b481ce70bd31aa24a69f8efd1c06299d1f130c7f4c312ebc854f13` | 8,832 bytes (61.7%) |
| **K1** | `1` | `5bfd21d4a63b6d55d3b4c9220af3a241e9d91056d95710dd52194e41f848b8e5` | `ade93a38f67822ffe5f8f767de9d86c59165763df7a9ebc330c568d92e69eabf` | 9,432 bytes (65.9%) |
| **K2** | `2` | `e13e9bc205d56c4de096948a8d58c7f4f21f1be79395532beb19962474403246` | `3711a6d995a7d48ce2273956a27c6a7df6f45a2078f413221d83c1ce7c552d35` | 10,808 bytes (75.5%) |
| **K3** | `3` | `e1dbd01afa801cb16f7d384ee96f8f152b194463ef16e8f74b166f58234d3ae0` | `380b0d4162c24be6538ee012f1c16a91d35ee2434d5fee07b159aceb336d607c` | 12,112 bytes (84.6%) |

All 4 variants verified byte-for-byte round-trip decryption matching via `tools/selfdec.py`.

---

## Owner Test Instructions

> [!IMPORTANT]
> The automated assistant is strictly forbidden from running console install/restore scripts or communicating with the PS3 over the network. The commands below are for the **human owner** to run manually from their PowerShell terminal.

### Safety Protocol
1. **STRICT TESTING ORDER**: Test **K1 FIRST**. Only proceed to K2 if K1 displays `DONE: ALL STEPS OK`. Only proceed to K3 if K2 passes.
   *(Note: K0 can be rerun if desired to verify the corrected label display, but K0 was already proven in P2D).*
2. **PHYSICAL DISC REQUIREMENTS**:
   - **K1, K2**: Drive can be empty (no disc needed).
   - **K3 Test A**: Run first with drive **EMPTY** (validates disc-absent handling).
   - **K3 Test B**: Run second with a **GENUINE PS2 DVD** inserted before launching the ISO.
3. **PAGER OPERATION**:
   - Each variant uses the hardware timebase gap pager.
   - Opening the in-game menu displays **Group 0** (Main Status).
   - Closing the menu and **waiting at least 2.0 seconds** before reopening advances to **Group 1** (Async Status / Counters), then **Group 2** (Hex Dumps), then wraps back to Group 0.
4. **EMERGENCY RECOVERY**:
   - If any variant freezes the console or causes a power-off, hard power on the PS3 and run:
     ```powershell
     tools\restore_netemu.ps1
     ```
   - Do NOT proceed to subsequent variants.

---

### Step 1: Test Variant K1 (`ps2_netemu_p2e_K1.self`)

1. Install Variant K1 from repository root:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2e\ps2_netemu_p2e_K1.self -Force
   ```
2. On PS3 (Blu-ray drive empty):
   - Launch any standard PS2 ISO via webMAN MOD.
   - Once rendering starts, press the **PS button** to display the in-game menu.
3. Observe and photograph the menu rows:
   - **Row 0**: Should read `P2E-K1 DONE: ALL STEPS OK`
   - **Row 1**: `RC: OP=0 DMA=0 MAP=0 CL=0 HC=44` (or similar)
   - **Row 2**: `CDVD LPAR: 0x0000000084000000`
   - **Row 3**: `CDVD EA:   0x0000500002c00000 SZ=100000`
   - **Row 4**: `DMA RGN=0x00000008 BUS=0x00000000` (or returned bus address)
   - **Rows 5..8**: `TUR / INQ / CAP / LBA16: NOT RUN IN K1`
4. Advance pager (close menu, wait 2.0 seconds, reopen):
   - **Row 0**: `P2E-K1 - GROUP 1: ASYNC STATUS`
   - **Row 5**: `UNMAP=0 REL=0 CLS=0`
   - Verify `TIMEOUTS: 0x0`.
5. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 2: Test Variant K2 (`ps2_netemu_p2e_K2.self`)

> [!WARNING]
> Only proceed if K1 passed cleanly with `MAP=0`.

1. Install Variant K2:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2e\ps2_netemu_p2e_K2.self -Force
   ```
2. On PS3 (drive empty):
   - Launch PS2 ISO via webMAN MOD.
   - Press **PS button** to display the menu.
3. Observe and photograph the menu rows:
   - **Row 0**: Should read `P2E-K2 DONE: ALL STEPS OK`
   - **Row 1**: `RC: OP=0 DMA=0 MAP=0 CL=0 HC=48` (or similar)
   - **Row 5**:
     - With empty drive: `TUR RC=0 STAT=0x02023a00 (NO DISC)` (or similar sense code)
     - With disc: `TUR RC=0 STAT=0x00000000 (READY)`
   - **Row 6**: `INQ RC=0: "SONY    PS-SYSTEM   ..."`
4. Advance pager to Group 2 (close, wait 2s, reopen twice):
   - **Row 1**: `INQ[00..07]: ...`
   - **Row 2**: `INQ[08..15]: ...`
   - Verify non-zero inquiry data from the drive firmware.
5. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 3: Test Variant K3 (`ps2_netemu_p2e_K3.self`)

> [!WARNING]
> Only proceed if K2 passed cleanly with valid INQUIRY response.

#### Run A: Drive Empty (Baseline)
1. Install Variant K3:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p2e\ps2_netemu_p2e_K3.self -Force
   ```
2. Launch PS2 ISO with drive EMPTY.
3. Observe menu:
   - **Row 7**: `CAP RC=...` (should report media not present)
   - **Row 8**: `LBA16 RC=...` (should report media not present)
   - Verify console does not hang and menu renders cleanly.

#### Run B: Genuine PS2 DVD Inserted
1. Insert genuine PS2 DVD into drive.
2. Launch PS2 ISO via webMAN MOD.
3. Press **PS button** and observe Group 0:
   - **Row 7**: `CAP RC=0 LBA=0x... BLK=2048`
   - **Row 8**: `LBA16 RC=0 ISO PVD "CD001" MATCH!`
4. Advance pager to Group 2 (Hex Dump):
   - **Rows 5..8**: `LBA16[00..31]` displaying the raw sector 16 bytes.
5. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

## Observation Log & Decision Matrix

| Variant | Test Condition | Observed Row 0 Summary | Observed Return Codes | Physical Address Displays | Status / Outcome |
|---|---|---|---|---|---|
| **K1** | Drive Empty | | `OP=? DMA=? MAP=? CL=?` | `LPAR=0x... EA=0x...` | |
| **K2** | Drive Empty | | `TUR=? INQ=?` | | |
| **K3** | Drive Empty | | `CAP=? LBA16=?` | | |
| **K3** | PS2 Disc Inserted | | `CAP=? LBA16=?` | | |
