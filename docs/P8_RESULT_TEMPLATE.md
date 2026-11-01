# P8 Result: Optical Drive Real Sector Read Investigation (Variant T1)

## Console Execution Instructions for Operator

> [!IMPORTANT]
> - **Disc Setup**: Insert the real **Test Drive Unlimited (TDU) PAL DVD-5** into the PS3 disc drive tray **BEFORE** launching the game.
> - **No Photos Needed**: All telemetry is written directly to `/dev_hdd0/tmp/netemu_log.bin` via the durable write-ahead logger.
> - **Execution Discipline**: Launch game, wait 10 seconds, press PS button once to open menu, wait 3 seconds, exit to XMB. The orchestrator will pull the log.

---

### Step-by-Step Operator Instructions

1. **Insert Disc**:
   - Insert the **Test Drive Unlimited PAL DVD-5** into the PS3 Blu-ray/DVD drive and verify the disc icon appears on the XMB.

2. **Install Variant T1**:
   - Copy `local_only/p8/ps2_netemu_p8_T1.self` to `/dev_hdd0/game/PS2NETEMU/USRDIR/ps2_netemu.self` on the PS3 (via FTP or existing deployment script).
   - Ensure the placeholder `/dev_hdd0/tmp/netemu_log.bin` exists on `/dev_hdd0/tmp/`.

3. **Launch & Execution**:
   - Start any standard PS2 ISO game from webMAN-MOD or XMB.
   - Wait 10 seconds for initial netemu boot, drive spinup, and probe execution.
   - Press the **PS Button** once to open the in-game menu (evaluates the menu display hook at `0x270FFC`).
   - Observe **Row 0** on the screen (glance display):
     - If ATAPI `READ(10)` succeeded and read the ISO9660 PVD: `P8-T1 R10_16: DATA_OK PVD: CD001`
     - If ATAPI `READ(10)` was rejected by drive auth: `P8-T1 R10_16: SENSE/ERR`
     - If buffer remained unchanged: `P8-T1 R10_16: UNCHANGED (NO DATA)`
     - On Timeout: `P8-T1 FAIL STEP=... RC=...` (immediate halt)
   - Exit the game back to XMB (clean game shutdown triggers cache flush and finalizes `/dev_hdd0/tmp/netemu_log.bin`).

4. **Log Retrieval**:
   - The orchestrator will pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/p8/netemu_log_T1.bin` and decode all records.

---

## What Variant T1 Tests & Expected Telemetry

Variant T1 tests the following sequence with the Test Drive Unlimited DVD-5 inserted:

1. **S2 Sequence Baseline**:
   - `open(4, 2)`: rc = 0
   - `allocate_device_dma_region(1 MiB, exp 20)`: rc = 0
   - `map_device_dma_region(lpar=0x500002c00000)`: rc = 0
   - `TEST UNIT READY` (ATAPI 0x00 via HV 248): rc = 0, async = 0
   - `INQUIRY` (ATAPI 0x12 via HV 248): rc = 0, buffer receives `"SONY    "`
   - `READ CAPACITY(10)` (ATAPI 0x25 via HV 248): rc = 0, last LBA = `0x001da34f`, block size = 2048

2. **Step 1: Buffer Pre-fill with Pattern `0xA5`**:
   - The entire 2048-byte sector buffer (`0x84001000..0x84001800`) is pre-filled with `0xA5` before each read attempt.
   - Stores are strictly confined to the verified SB_CDVD buffer data range.

3. **Step 2: ATAPI `READ(10)` on LBA 16 (ISO9660 PVD)**:
   - Dispatched via HV 248 (`lv1_storage_send_device_command`) matching official `ps2_softemu.elf` optical sector read driver (`0x897DC`).
   - CDB: `28 00 00 00 00 10 00 00 01 00 00 00` (Opcode 0x28, LBA 16, 1 sector, proto 3 DMA, in_out 1).
   - If Check Condition (`status == 2`), immediately executes `REQUEST SENSE` (`0x03`, 18 bytes) to capture Sense Key / ASC / ASCQ.
   - Buffer telemetry logged:
     - Count of remaining `0xA5` bytes (0 = fully written, 2048 = unchanged).
     - First 16 bytes: expected `01 43 44 30 30 31 01 00` (`\x01CD001\x01\x00`).
     - Bytes 16..31.
     - Volume identifier at bytes 40..47: expected `"TDU"` or disc volume label.
     - Last 16 bytes (2032..2047).

4. **Step 2b: Repeat ATAPI `READ(10)` for LBA 0 and LBA 17**:
   - **LBA 0**: Pre-fill with `0xA5`, issue READ(10), poll, sense if CC, log A5 count, window 0..15, window 2032..2047.
   - **LBA 17**: Pre-fill with `0xA5`, issue READ(10), poll, sense if CC, log A5 count, window 0..7 (expect `FF 43 44 30 30 31 01 00` for Volume Descriptor Terminator), volume ID at bytes 40..47, window 2032..2047.

5. **Step 3: Repeat `lv1_storage_read` (HV 245) of Sector 16**:
   - **Attempt 1 (Region 0, matching S3)**: Pre-fill with `0xA5`, issue HV 245, poll, log A5 count, windows. Tests whether HV 245 writes anything when pre-filled with `0xA5`.
   - **Attempt 2 (Region 1)**: Pre-fill with `0xA5`, issue HV 245 with region 1, poll, log A5 count, windows.

6. **Step 4: Cleanup & Safeguards**:
   - Clean shutdown: `unmap` (HV 177) -> `free` (HV 175) -> `close` (HV 171).
   - Immediate halt on timeout: if polling reaches 200,000 iterations or ~2.0s timebase, logs `TAG_TMO` and terminates immediately without teardown.

---

## Buffer Classification Reference

| Classification | Condition | Meaning |
|---|---|---|
| **UNCHANGED** | All 2048 bytes remain `0xA5` | DMA did not touch buffer (indicates HV 245 block translation skipped transfer). |
| **ZEROS** | All 2048 bytes are `0x00` | Buffer cleared or zero-filled by hardware. |
| **DATA_OK** | Bytes 0..5 match `\x01CD001` (or `\xFFCD001`) | Valid ISO9660 volume descriptor read successfully from optical disc! |
| **OTHER** | Partial write or non-PVD data | Data transfer arrived at buffer with non-standard format. |
