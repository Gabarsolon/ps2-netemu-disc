# P7 Result: Optical Drive Real Read Suite (Variants S0..S3)

## Console Execution Instructions for Operator

> [!IMPORTANT]
> - **Execution Order**: Test the variants in sequence: **S0 -> S1 -> S2 -> S3**.
> - **No Photos Needed**: All telemetry is written directly to `/dev_hdd0/tmp/netemu_log.bin` via the durable write-ahead logger.
> - **Variant S3 Two-Phase Test**:
>   1. **Phase 1 (Disc Absent)**: Test **S3** with the optical drive completely **EMPTY** (no disc inserted).
>   2. **Phase 2 (PS2 DVD Present)**: Insert the real **PS2 DVD** into the drive tray **BEFORE** launching the game, then test **S3**.

---

### Step-by-Step Procedure per Variant

For each variant `S<n>` (`S0`, `S1`, `S2`, `S3`):

1. **Install Variant**:
   - Copy `local_only/p7/ps2_netemu_p7_S<n>.self` to `/dev_hdd0/game/PS2NETEMU/USRDIR/ps2_netemu.self` on the PS3 (via FTP or local deployment script).
   - Ensure the 64 KiB placeholder file `/dev_hdd0/tmp/netemu_log.bin` is initialized or cleared (e.g. via `tools/make_log_placeholder.ps1`).

2. **Launch & Probe Execution**:
   - Start any standard PS2 ISO game from webMAN-MOD or XMB.
   - Wait 10 seconds for initial netemu boot, drive spinup, and probe execution.
   - Press the **PS Button** once to open the in-game menu (this evaluates the display hook at `0x270FFC`).
   - Observe **Row 0** on the screen (secondary visual glance):
     - For **S0**: `P7-S0 BASELINE MAP OK`
     - For **S1**: `P7-S1 INQ: <Vendor Product String>`
     - For **S2**: `P7-S2 CAP LBA=0x... BLK=2048`
     - For **S3 (Empty Drive)**: `P7-S3 SENSE: 00000002/0000003a/00000000` (Medium Not Present)
     - For **S3 (PS2 DVD)**: `P7-S3 PVD: CD001 READ OK` (or SENSE auth error if copy protection handshake required)
     - On Timeout: `P7-S3 FAIL STEP=... RC=...` (with immediate halt)
   - Exit the game back to XMB (clean game shutdown triggers cache flush and finalizes `/dev_hdd0/tmp/netemu_log.bin`).

3. **Log Retrieval**:
   - Pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/p7/netemu_log_S<n>.bin` (or `_S3_nodisc.bin` / `_S3_disc.bin`).
   - Decode and analyze records using `tools/read_netemu_log.ps1` or python harness.

---

## Variant Reference & Expected Behavior

| Variant | Scope / Commands Issued | Buffer Translation Architecture | Expected Result (Row 0 / WAL Log) |
|---|---|---|---|
| **S0** | Baseline: open (4,2), alloc (0x100000, exp 20), map (LPAR `0x500002c00000`), unmap, free, close | Verified P6 R1 real LPAR baseline | `P7-S0 BASELINE MAP OK` |
| **S1** | S0 + TEST UNIT READY (0x00) + INQUIRY (0x12, 36 bytes) with bounded polling (254) | ATAPI CDB at CPU EA `0x84000000` / LPAR `0x500002c00000`; Data at CPU EA `0x84001000` / LPAR `0x500002c01000` | `P7-S1 INQ: Sony PS3 CD/DVD-ROM` |
| **S2** | S1 + READ CAPACITY(10) (0x25, 8 bytes inbound) | ATAPI CDB at CPU EA `0x84000000`; Data at CPU EA `0x84001000` / LPAR `0x500002c01000` | `P7-S2 CAP LBA=0x... BLK=2048` |
| **S3 (Empty)** | S2 + READ Sector 16 (2048 bytes via HV 245) + REQUEST SENSE (0x03, 18 bytes) on error | HV 245 buffer arg = LPAR `0x500002c01000`; Sense CDB at EA `0x84000000` | `P7-S3 SENSE: 00000002/0000003a/00000000` (Sense Key 2 = Not Ready, ASC 3A = Medium Not Present) |
| **S3 (PS2 DVD)** | S2 + READ Sector 16 (2048 bytes via HV 245) + REQUEST SENSE on error | HV 245 buffer arg = LPAR `0x500002c01000`; CPU reads ISO9660 PVD from EA `0x84001000` | `P7-S3 PVD: CD001 READ OK` (or SENSE auth error `05/6f/00`) |

---

## Safety & Recovery Guarantees

1. **Immediate Halt on Timeout**: If any async poll operation reaches 200,000 iterations or ~2.0 seconds timebase, a `TAG_TMO` record is immediately written and all subsequent hypercalls are bypassed. Unmap, free, and close are NOT called to prevent corrupting hypervisor state while DMA may be pending.
2. **Fail-Open Concurrency**: Write-ahead log records are only written when the stock HDD driver state is completely idle (`H->status == 1`). If the stock netemu HDD driver is busy, records are safely skipped (`log_records_skipped` incremented) without blocking game execution.
3. **Read-Only Operation**: Probe issues strictly non-destructive read commands (0x00, 0x12, 0x25, 0x03, HV 245 read). No writes (no 246, no write CDBs), no tray eject/load commands, and no secure UART commands are executed.
