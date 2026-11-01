# P9 Result Template: Optical Drive Data Transfer Investigation (Variant U1)

## Console Execution Instructions for Operator

> [!IMPORTANT]
> - **Two-Stage Test Order**:
>   1. **First: PS3 Game Blu-ray Disc (GTA IV or any retail PS3 BD)** as known readable hardware control.
>   2. **Second: PS2 Game DVD (Test Drive Unlimited PAL DVD-5 or any PS2 DVD)**.
> - **Disc Insertion**: Insert the respective disc into the PS3 disc drive tray **BEFORE** launching netemu.
> - **No Photos Needed**: All telemetry is written directly to `/dev_hdd0/tmp/netemu_log.bin` via the durable write-ahead logger.
> - **Execution Discipline**: Launch game, wait 10 seconds, press PS button once to open menu, wait 3 seconds, exit to XMB. The orchestrator will pull the log.

---

### Step-by-Step Operator Instructions

#### Run 1: Control Run with PS3 Game Disc (Retail Blu-ray, e.g. GTA IV)
1. **Insert Disc**:
   - Insert the **PS3 retail game Blu-ray disc** into the drive and confirm the disc icon appears on the XMB.
2. **Install Variant U1**:
   - Copy `local_only/p9/ps2_netemu_p9_U1.self` to `/dev_hdd0/game/PS2NETEMU/USRDIR/ps2_netemu.self` on the PS3 (via FTP).
   - Ensure the placeholder `/dev_hdd0/tmp/netemu_log.bin` exists on `/dev_hdd0/tmp/`.
3. **Launch & Execution**:
   - Start any standard PS2 ISO game from webMAN-MOD or XMB.
   - Wait 10 seconds for initial netemu boot, drive spinup, and probe execution.
   - Press the **PS Button** once to open the in-game menu (evaluates the glance display hook).
   - Observe **Row 0** on the screen (glance display):
     - If PIO `READ(10)` succeeded and read the ISO9660 PVD: `P9-U1 PIO16: DATA_OK PVD: CD001`
     - If PIO `READ(10)` returned no data (unchanged buffer): `P9-U1 PIO16: UNCHANGED`
     - If PIO `READ(10)` was rejected by drive: `P9-U1 FAIL STEP=8 RC=...`
     - On Timeout: `P9-U1 FAIL STEP=... RC=...` (immediate halt)
   - Exit the game back to XMB (clean game shutdown triggers cache flush and finalizes `/dev_hdd0/tmp/netemu_log.bin`).
4. **Log Retrieval**:
   - Pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/p9/netemu_log_U1_bd.bin`.

#### Run 2: Test Run with PS2 Game DVD (e.g. Test Drive Unlimited PAL DVD-5)
1. **Insert Disc**:
   - Eject the PS3 BD and insert the **PS2 Game DVD** (e.g. Test Drive Unlimited PAL) into the drive.
   - Confirm the PS2 disc icon appears on the XMB.
2. **Re-initialize Placeholder**:
   - Overwrite or clear `/dev_hdd0/tmp/netemu_log.bin` with the 64 KiB zeroed placeholder.
3. **Launch & Execution**:
   - Start the PS2 ISO game from webMAN-MOD or XMB.
   - Wait 10 seconds, press PS button once, observe Row 0 on screen.
   - Exit to XMB.
4. **Log Retrieval**:
   - Pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/p9/netemu_log_U1_ps2dvd.bin`.

---

## What Variant U1 Tests & Expected Telemetry

Variant U1 tests whether 2048-byte sector data is delivered to our buffer when requested via ATAPI `READ(10)` using the **PIO DATA-IN protocol** (`proto = 1`, `in_out = 1`, `blocks = 2048`, `block_size = 1`), matching the exact protocol format that delivered INQUIRY (36 B) and READ CAPACITY (8 B) data in P8.

1. **S2 Sequence Baseline**:
   - `open(4, 2)`: rc = 0
   - `allocate_device_dma_region(1 MiB, exp 20)`: rc = 0
   - `map_device_dma_region(lpar=0x500002c00000)`: rc = 0
   - `TEST UNIT READY` (ATAPI 0x00 via HV 248): rc = 0, async = 0
   - `INQUIRY` (ATAPI 0x12 via HV 248): rc = 0, buffer receives `"SONY    PS3 CD/DVD-ROM  1.00"`
   - `READ CAPACITY(10)` (ATAPI 0x25 via HV 248): rc = 0, max LBA, block size = 2048

2. **Step 7: ATAPI `READ(10)` on LBA 16 (ISO9660 PVD) with PIO Protocol**:
   - CDB: `28 00 00 00 00 10 00 00 01 00 00 00` (Opcode 0x28, LBA 16, 1 sector).
   - Command block: `pktlen = 12, blocks = 2048, block_size = 1, proto = 1 (PIO DATA-IN), in_out = 1, buf_lpar = data_lpar`.
   - Pre-fill `data_ea` (2048 bytes) with `0xA5`.
   - Issue HV 248 with length 2048.
   - Bounded poll HV 254 (200,000 iterations / ~2s).
   - Buffer telemetry logged:
     - Classification: `DATA_OK` (`CD001`), `UNCHANGED`, `ZEROS`, `OTHER`.
     - Count of remaining `0xA5` bytes (0 = fully written, 2048 = unchanged).
     - First 16 bytes (`w0`): expected `01 43 44 30 30 31 01 00` (`\x01CD001\x01\x00`).
     - Bytes 16..31 (`w16`).
     - Volume identifier at bytes 40..47 (`vol`).
     - Last 16 bytes (`wend`: 2032..2047).
   - If Check Condition (`status == 2`), immediately executes `REQUEST SENSE` (`0x03`, 18 bytes).

3. **Step 8: ATAPI `READ(10)` on LBA 0 (Lead-in Sector) with PIO Protocol**:
   - CDB: `28 00 00 00 00 00 00 00 01 00 00 00`.
   - Command block: `blocks = 2048, block_size = 1, proto = 1, in_out = 1`.
   - Pre-fill with `0xA5`, issue HV 248, poll HV 254, classify buffer, log window samples.

4. **Step 9: ATAPI `READ(10)` on LBA 17 (Volume Descriptor Terminator) with PIO Protocol**:
   - CDB: `28 00 00 00 00 11 00 00 01 00 00 00`.
   - Command block: `blocks = 2048, block_size = 1, proto = 1, in_out = 1`.
   - Pre-fill with `0xA5`, issue HV 248, poll HV 254, classify buffer, log window samples.

5. **Step 10: Repeat T1 DMA `READ(10)` on LBA 16 (Comparison Baseline)**:
   - CDB: `28 00 00 00 00 10 00 00 01 00 00 00`.
   - Command block: `blocks = 1, block_size = 2048, proto = 3 (DMA), in_out = 1`.
   - Pre-fill with `0xA5`, issue HV 248, poll HV 254, classify buffer, log window samples.
   - Serves as back-to-back reference against PIO results.

6. **Clean Teardown**:
   - `unmap` (HV 177) -> `free` (HV 175) -> `close` (HV 171).
   - Immediate halt on timeout: if polling reaches 200,000 iterations or ~2.0s timebase, logs `TAG_TMO` and terminates immediately without teardown.

---

## Buffer Classification Reference

| Classification | Meaning | Criteria |
|---|---|---|
| **`DATA_OK`** | Disc data successfully delivered into buffer | Bytes 1..5 match ASCII `"CD001"` (ISO9660 PVD/Terminator identifier) |
| **`UNCHANGED`** | No data delivered by device / hypervisor | 2048 / 2048 bytes remain `0xA5` (identical to pre-fill) |
| **`ZEROS`** | Zero-filled buffer delivered | 2048 / 2048 bytes are `0x00` |
| **`OTHER`** | Data delivered, but not ISO9660 standard | Modified buffer, not `"CD001"`, not all zeros |

---

## Build Hashes & Artifact Verification

| Component | Path | Size | SHA-256 |
|---|---|---|---|
| **Patched ELF** | `local_only/p9/ps2_netemu_p9_U1.elf` | 10,901,288 | `c759afa2056da0f11af47d931c57abfbd62bb2bb9b71ea55000e79d607f9f7a8` |
| **Repacked SELF** | `local_only/p9/ps2_netemu_p9_U1.self` | 2,529,232 | `434b9c2fac885f8a522306b3076db7b9fc4e3d5300a1de15d6c5d5adf5717f9a` |
| **Decrypted ELF** | `local_only/p9/roundtrip_U1.elf` | 10,901,288 | `c759afa2056da0f11af47d931c57abfbd62bb2bb9b71ea55000e79d607f9f7a8` (100% Byte-for-Byte Match) |
| **Payload Size** | In code slot `0x4800..0x77E8` | 12,264 bytes | 85.6% of 14,320-byte slot (2,056 bytes headroom) |
| **Audit (`p1a_audit.py`)** | Exactly one `sc` at `0x4858` | Verified | Zero stores outside stack, mailbox, arena, and verified CDVD buffer |
