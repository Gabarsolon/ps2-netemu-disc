# P11b Result Template: Disc Authentication Variant W2 Verification

## Console Execution Instructions for Operator

> [!IMPORTANT]
> - **Test Target**: PS2 Retail Game DVD (e.g. *Test Drive Unlimited* PAL DVD-5 or any retail PS2 DVD) inserted into the PS3 disc drive.
> - **Disc Insertion**: Insert the PS2 DVD into the PS3 disc drive tray **BEFORE** launching netemu. Confirm the PS2 disc icon appears on the XMB.
> - **No Photos Needed**: All telemetry is written directly to `/dev_hdd0/tmp/netemu_log.bin` via the resilient durable write-ahead logger.
> - **Execution Discipline**: Launch game, wait 10 seconds, press PS button once to open menu, wait 3 seconds, exit to XMB. The orchestrator will pull the log.
> - **What Variant W2 Adds**:
>   - Preparatory ATAPI commands (`GET CONFIGURATION` 0x46 and `READ DISC STRUCTURE` 0xAD) before VUART auth dispatch to transition drive profile from generic DVD-ROM (`0x0010`) to PS2 DVD (`0xFF61`).
>   - Concurrency resilience loop in `hddlog.c` to prevent probe silence during background netemu HDD streaming.
>   - Glance menu telemetry tracking drive profiles before and after structure read (`PROF1` and `PROF2`).
> - **Security Discipline**: Session keys (`+0x40..+0x6F`) are zeroed immediately upon receipt and **NEVER** logged or displayed.

---

### Step-by-Step Operator Instructions

1. **Insert Disc**:
   - Insert the **PS2 retail game DVD** into the PS3 drive tray.
   - Confirm the PS2 disc icon appears on the XMB.
2. **Setup Placeholder**:
   - Ensure the 64 KiB zeroed placeholder `/dev_hdd0/tmp/netemu_log.bin` exists on `/dev_hdd0/tmp/`.
3. **Install Variant W2**:
   - Run the exact installation command from PowerShell in `C:\Users\remus\ps2-netemu-disc`:
     ```powershell
     powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_netemu.ps1 -File .\local_only\p11\ps2_netemu_p11_W2.self -Force
     ```
4. **Launch & Execution**:
   - Start any standard PS2 ISO game from webMAN-MOD or XMB.
   - Wait 10 seconds for initial netemu boot, drive spinup, preparatory ATAPI reads, and W2 authentication dispatch.
   - Press the **PS Button** once to open the in-game menu (evaluates the glance display hook).
   - Observe the on-screen glance display:
     - **Row 0**: High-Level Auth Verdict & Reply Codes
       - Expected on Success: `P11-W2 AUTH: OK ST=0x00000000 FL=0x00000007`
       - If status error persists: `P11-W2 AUTH: ERR_STAT ST=0x<status> FL=0x<flags>`
       - If read times out: `P11-W2 AUTH: TIMEOUT ST=0x00000000 FL=0x00000000`
       - If short reply: `P11-W2 AUTH: SHORT ST=0x00000000 FL=0x00000000`
       - If write error: `P11-W2 AUTH: ERR_WRITE ST=0x00000000 FL=0x00000000`
       - If guard skips: `P11-W2 AUTH: SKIPPED ST=0x00000000 FL=0x00000000`
     - **Row 1**: Preparatory Drive Profiles & RDS Status
       - Expected on Profile Transition: `PROF1=0x0010 PROF2=0xff61 RDS=0x00000000`
       - If RDS fails: `PROF1=0x0010 PROF2=0x0010 RDS=0x<rds_status>`
     - **Row 2**: Auth Transfer Metrics
       - Format: `AUTH: READ=<read_bytes> POLLS=<poll_count> WR=<write_bytes>`
       - Expected: `AUTH: READ=112 POLLS=<cnt> WR=112`
     - **Row 3**: Sector 16 Buffer Classification & Residual Pattern
       - Format: `PIO16: <class> A5=<cnt> POLLS=<cnt>`
       - If unlocked: `PIO16: DATA_OK A5=0 POLLS=<cnt>`
       - If still gated: `PIO16: UNCHANGED A5=2048 POLLS=<cnt>`
     - **Row 4**: Hypercall Counts & Log Telemetry
       - Format: `HC=<total_hc> LOG=<recs> SKIP=<skip> TMO=0x<tmo>`
     - **Row 5**: Buffer Pre-fill Residuals across Sector Reads
       - Format: `PIO: 16_A5=<cnt> 0_A5=<cnt> 17_A5=<cnt>`
     - **Row 6**: CDVD LPAR Address
       - Format: `CDVD LPAR: 0x0000500002c00000`
     - **Row 7**: DMA Region & Bus Address
       - Format: `DMA RGN=0x... BUS=0x...`
   - Exit the game back to XMB (clean game shutdown triggers cache flush and finalizes `/dev_hdd0/tmp/netemu_log.bin`).
5. **Log Retrieval**:
   - Pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/p11/netemu_log_W2.bin`.

---

## What Variant W2 Tests & Staged Pipeline

Variant W2 implements the preparatory ATAPI sequence reverse engineered from `ss_server1.elf` and `ps2_softemu.elf`:

```
[TUR] -> [INQUIRY] -> [READ CAPACITY] -> [VUART PARAM QUERIES]
                                                   |
                                     (GUARD: TUR ok, CAP ok, bsz=2048, P10 rc=0)
                                                   |
                           +-----------------------+-----------------------+
                           | Passed                                        | Failed
                           v                                               v
               [GET CONFIGURATION 1 (0x46)]                        [TAG_GRD reject]
                           |                                               |
               [READ DISC STRUCTURE (0xAD)]                                |
                           |                                               |
               [GET CONFIGURATION 2 (0x46)]                                |
                           |                                               |
               [HV 163 write 0x70]                                         |
                           |                                               |
               [HV 162 read 0x70 (polling)]                                |
                           |                                               |
             [Zero Keys & Parse Status]                                    |
                           |                                               |
                           +-----------------------+-----------------------+
                                                   |
                                                   v
                         [READ(10) PIO LBA 16 (PVD)]
                         [READ(10) PIO LBA 0 (Lead-in)]
                         [READ(10) PIO LBA 17 (VD Term)]
                         [READ(10) DMA LBA 16 (Comparison)]
                                                   |
                                                   v
                                     [Unmap -> Free -> Close]
```

### Key Request Packet Fields (HV 163)
- `+0x00`: `0x0000FACE` (Header magic)
- `+0x04`: `0x00005000` (Storage authentication service)
- `+0x08`: `0x00000060` (Payload length = 96 bytes)
- `+0x0C`: `0x00000060` (Length echo)
- `+0x10`: `0x0000000000005005` (PS2 optical disc authenticate opcode)
- `+0x18`: `0x0000000000005000` (Service echo)
- `+0x30`: `0x1020000401000001` (PS2 emulator partition LAID)
- `+0x38`: `0x00` (byte A)
- `+0x39`: `0x13` (byte B = DVD-5)
- `+0x40`: `0x0000004B` (Retries = 75)

---

## Artifact Verification Table

| File | Size (Bytes) | SHA-256 |
|---|---|---|
| `local_only/p11/ps2_netemu_p11_W2.elf` | 10,901,288 | `5a572a24e25991607952c921814568681270b833ce7464179f9a2974038860b9` |
| `local_only/p11/ps2_netemu_p11_W2.self` | 2,530,160 | `ea58d1c6a1e886c85ed328e1bc2db7abf71657d14a65a5fc1eb7fc7e9ca88f02` |
| `local_only/p11/roundtrip_W2.elf` | 10,901,288 | `5a572a24e25991607952c921814568681270b833ce7464179f9a2974038860b9` |

---

## Operator Reporting Form

When the run is complete, please record the on-screen menu rows and log decode:

```markdown
### W2 Console Execution Observation
- **Date/Time**: 
- **Disc Model**: (e.g. Test Drive Unlimited PAL DVD-5)
- **Menu Row 0**: 
- **Menu Row 1**: 
- **Menu Row 2**: 
- **Menu Row 3**: 
- **Menu Row 4**: 
- **Menu Row 5**: 
- **Menu Row 6**: 
- **Menu Row 7**: 
- **Log Decoder Output Summary**:
```
