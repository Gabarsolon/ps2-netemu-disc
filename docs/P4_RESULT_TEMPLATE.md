# P4 Test Execution & Results Protocol (Console Owner Guide)

## Overview & Zero-Photo Diagnostic Workflow
With P4, **photos of the TV screen and smartphone videos are no longer required**. All execution state, repository scan data, hypercall arguments, return codes, sense data, and crash locations are recorded durably to `/dev_hdd0/tmp/netemu_log.bin` via write-ahead logging (WAL).

Even if a hypercall causes the console to freeze, crash, or shut down, the `PRE` log record was already flushed to physical HDD sectors before the call was issued. Upon restarting the console, the offline log decoder automatically identifies the exact hypercall where execution terminated (`[CRASH POINT]`).

---

## Prerequisites & Pre-Flight Checks

1. **Pre-allocated Log File**:
   - The file `/dev_hdd0/tmp/netemu_log.bin` (exactly 64 KiB) should already exist on the console HDD from P3B.
   - If missing, run:
     ```powershell
     powershell -ExecutionPolicy Bypass -File tools\make_log_placeholder.ps1
     ```

2. **Decryption & Inspection Tooling Ready**:
   - `python tools\decode_netemu_log.py local_only\netemu_log.bin`
   - Or PowerShell helper:
     ```powershell
     powershell -ExecutionPolicy Bypass -File tools\read_netemu_log.ps1
     ```

3. **Recommended Execution Sequence**:
   - **Step 1: K1** (Map / Unmap of `SB_CDVD` buffer - low risk, tests hypervisor memory mapping).
   - **Step 2: K2** (K1 + `TEST UNIT READY` & `INQUIRY` - commands drive controller without reading disc media).
   - **Step 3: K3 (Empty Drive)** (K2 + `READ CAPACITY` & sector 16 read on empty drive - tests disc absent sense handling `02023a00`).
   - **Step 4: K3 (PS2 DVD Inserted)** (Full end-to-end optical read of ISO 9660 PVD sector 16 from real disc media).

---

## Step-by-Step Operator Procedure per Variant

### Step A: Deploy the Test Variant
Copy the desired SELF binary to the console:
- Target path on console: `/dev_hdd0/game/PS2U10000/USRDIR/ps2_netemu.self`
- Example using `install_netemu.ps1`:
  ```powershell
  powershell -ExecutionPolicy Bypass -File tools\install_netemu.ps1 -Variant local_only\p4\ps2_netemu_p4_K1.self
  ```

### Step B: Launch Test PS2 Game
1. On the PS3 XMB, launch any standard PS2 Classic or test ISO (e.g. `SLUS_200.02`).
2. Wait for the game to start rendering.

### Step C: Trigger the Diagnostic Hook
1. **Press the PS button on the controller once** to display the in-game overlay menu.
2. The probe hook executes immediately upon the first overlay label evaluation (`0x270FFC`).
3. You can dismiss the PS menu or observe the on-screen status label (optional).
4. Exit the game back to XMB via "Quit Game".

> [!NOTE]
> **What to do if the console hangs or turns off?**
> Do not panic. Simply power the console back on and boot to XMB. The write-ahead log was flushed to disk *before* the crash occurred. Proceed directly to Step D.

### Step D: Retrieve and Decode the Durable Log
1. Run the log retrieval script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File tools\read_netemu_log.ps1
   ```
2. Or manually FTP download `/dev_hdd0/tmp/netemu_log.bin` to `local_only\netemu_log.bin` and run:
   ```powershell
   python tools\decode_netemu_log.py local_only\netemu_log.bin
   ```
3. Copy the decoded text output into the result template below.

---

## Result Capture Form (Fill in for each run)

### Run Information
- **Date / Time**: `YYYY-MM-DD HH:MM`
- **Variant Tested**: `K1` / `K2` / `K3 (Empty)` / `K3 (Disc)`
- **ELF / SELF Hash Tested**: 
- **Console Model**: CECH-A01 / CECH-E01 / CECH-C02 / CECH-2501 / etc.
- **Disc Media Present**: None / PS2 DVD-ROM (Game Title: `__________________`)

### Decoded Log Summary
```text
=== NETEMU LOG SUMMARY ===
Session Boot TB: 0x...
Clean Shutdown:  YES / NO
Records Written: ...
Crash Point:     NONE / [CRASH POINT detected at PRE <STEP>]

=== RECORD LIST ===
(Paste decoder output here)
```

### Analysis Checklist
- [ ] Session `Boot TB` matches Sector 0 header (`[CURRENT SESSION]` displayed on records).
- [ ] `SCAN` record displays correct `rom_count`, `hdd_found`, and device IDs.
- [ ] `GRD ` record indicates `GUARD_OK` (EA: `0x32000000`, LPAR: `0x70000000`, Size: `0x02000000`).
- [ ] All `PRE <step>` records are paired with matching `POST <step> rc=0x0`.
- [ ] (For K2/K3): `INQ` returns valid drive model string (e.g. `SONY    PS3 DVD-ROM...`).
- [ ] (For K3 with disc): `READ` returns sector 16 PVD header (`CD001`).
- [ ] If stopped prematurely: `[CRASH POINT]` pinpoints the exact hypercall step.
