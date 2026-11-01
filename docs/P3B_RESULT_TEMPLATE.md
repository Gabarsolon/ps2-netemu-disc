# P3B Result Template: L0 Durable HDD Logger Hardware Verification

## Summary
- **Target SELF**: `local_only/p3b/ps2_netemu_p3b_L0.self`
- **SHA-256**: `57507f5daafc67084ad94d9fb7250c5ee50a33db65027063a3c73fbdf4a0ddb1`
- **Test Variant**: L0 (Writes 4 test log records to `/dev_hdd0/tmp/netemu_log.bin` on first PS-button menu open).
- **Console Environment**: PS3 slim CECH-25xx, Evilnat 4.93 Cobra, webMAN MOD 1.47.48, IP `192.168.0.169`.

---

## 1. Owner Preparation & Safety Checks (ONLY THE OWNER RUNS THESE)

> [!IMPORTANT]
> The automated agent NEVER connects to the console or runs install scripts. The owner performs the following manual steps.

### Step 1: Create the Placeholder File (Once Only)
The netemu log requires a 64 KiB zero-filled placeholder file on `/dev_hdd0/tmp/netemu_log.bin`.
The owner runs from their workstation:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\make_log_placeholder.ps1 -Ps3Host 192.168.0.169
```
*Expected Output*:
- Creates local 65,536-byte zero buffer.
- Uploads to `ftp://192.168.0.169/dev_hdd0/tmp/netemu_log.bin`.
- Reads back and verifies 100% all zeros.
- If the file already exists with non-zero bytes (from a prior run), pass `-Force` to overwrite if desired.

### Step 2: Install L0 Test Build
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_netemu.ps1 -Source .\local_only\p3b\ps2_netemu_p3b_L0.self
```
*Verification*: Script takes a backup of current netemu, writes `/dev_blind/ps2emu/ps2_netemu.self`, reads back and verifies hash, and disables `dev_blind`.

---

## 2. Console Test Execution

1. **Launch a PS2 game**:
   - Mount any PS2 ISO via webMAN MOD and start it from the XMB.
   - Wait for the game to boot to its title screen or gameplay.
2. **Open the PS-button menu ONCE**:
   - Press the controller's PS button to bring up the netemu in-game menu.
   - Observe the first menu rows on screen:
     - **Row 0**: Should display `P3B-L0 OK RECS=4 BYTES=2048 FLUSH=OK` (or similar).
     - **Row 1**: Should display `H IDLE: 38=0 40=0 48=0 85=1 78=0`.
     - **If placeholder was missing**: Row 0 will display `P3B-L0 FAIL: NO FILE rc=-2` and no write is attempted.
3. **Exit the game**:
   - Select "Quit Game" from the PS menu to return cleanly to the XMB.

---

## 3. Telemetry Retrieval & Verification

Run the read-only log decoder:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\read_netemu_log.ps1 -Ps3Host 192.168.0.169 -OutFile .\local_only\p3b\last_log.bin
```
Or use the Python parser directly on the downloaded binary:
```powershell
python tools/decode_netemu_log.py local_only/p3b/last_log.bin
```

### Expected Log Output:
```
--- LOG HEADER (Sector 0) ---
Header Magic: 'NETEMULG'
Version:      0x00010000
Header Size:  512 bytes
File Size:    65536 bytes
Sector Size:  512 bytes
Capacity:     127 records
Next Record:  #5
Boot TB:      0x00000000... (> 0)
Shutdown:     UNCOMMITTED / CRASH (or CLEAN)

--- LOG RECORDS ---
[Sector 001] Seq=0001 Tag=0x424F4F54 ('BOOT') TB=0x... A=0x0000000000000000 B=0x0000000000000000 -> L0 BOOT
[Sector 002] Seq=0002 Tag=0x54312020 ('T1  ') TB=0x... A=0x0000000000000001 B=0x0000000000001111 -> L0 T1 after BOOT
[Sector 003] Seq=0003 Tag=0x54322020 ('T2  ') TB=0x... A=0x0000000000000002 B=0x0000000000002222 -> L0 T2 test record
[Sector 004] Seq=0004 Tag=0x454E4420 ('END ') TB=0x... A=0x0000000000000004 B=0x0000000000004444 -> L0 END complete

Total populated log records found: 4
```

---

## 4. Troubleshooting & Filesystem Safety Check

- **If the PS menu shows `NO FILE`**:
  - The placeholder `/dev_hdd0/tmp/netemu_log.bin` was not created or has incorrect permissions. Run `tools\make_log_placeholder.ps1`.
- **If the PS menu shows `BUSY` (`H+48 != 0` or `H+38 != 0`)**:
  - Netemu was actively loading game data or accessing VMC when menu was opened. Close menu and re-open once title screen is fully idle.
- **If the console ever prompts "Restore File System" on boot**:
  - This is standard PS3 GameOS behavior after any unexpected power cycle. Let the PS3 complete the check (~1-2 minutes).
  - Netemu writes strictly into pre-allocated sectors within `i_size` (65,536 bytes) without modifying UFS block maps or superblocks.
- **Restore original netemu**:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore_netemu.ps1
  ```
