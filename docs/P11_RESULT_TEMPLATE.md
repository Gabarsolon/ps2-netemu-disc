# P11 Result Template: Disc Authentication Command Dispatch & Variant W1 Verification

## Console Execution Instructions for Operator

> [!IMPORTANT]
> - **Test Target**: PS2 Retail Game DVD (e.g. *Test Drive Unlimited* PAL DVD-5 or any retail PS2 DVD) inserted into the PS3 disc drive.
> - **Disc Insertion**: Insert the PS2 DVD into the PS3 disc drive tray **BEFORE** launching netemu. Confirm the PS2 disc icon appears on the XMB.
> - **No Photos Needed**: All telemetry is written directly to `/dev_hdd0/tmp/netemu_log.bin` via the durable write-ahead logger.
> - **Execution Discipline**: Launch game, wait 10 seconds, press PS button once to open menu, wait 3 seconds, exit to XMB. The orchestrator will pull the log.
> - **Owner Approval Granted**: Variant W1 sends the real disc authentication command (`0x5005`) across VUART Port 10 to `ss_server1`.
> - **Security Discipline**: Session keys (`+0x40..+0x6F`) are zeroed immediately upon receipt and **NEVER** logged or displayed.

---

### Step-by-Step Operator Instructions

1. **Insert Disc**:
   - Insert the **PS2 retail game DVD** into the PS3 drive tray.
   - Confirm the PS2 disc icon appears on the XMB.
2. **Setup Placeholder**:
   - Ensure the 64 KiB zeroed placeholder `/dev_hdd0/tmp/netemu_log.bin` exists on `/dev_hdd0/tmp/`.
3. **Install Variant W1**:
   - Run the exact installation command from PowerShell in `C:\Users\remus\ps2-netemu-disc`:
     ```powershell
     powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_netemu.ps1 -File .\local_only\p11\ps2_netemu_p11_W1.self -Force
     ```
4. **Launch & Execution**:
   - Start any standard PS2 ISO game from webMAN-MOD or XMB.
   - Wait 10 seconds for initial netemu boot, drive spinup, and W1 authentication dispatch.
   - Press the **PS Button** once to open the in-game menu (evaluates the glance display hook).
   - Observe the on-screen glance display:
     - **Row 0**: High-Level Auth Verdict & Reply Codes
       - Expected on Success: `P11-W1 AUTH: OK ST=0x00000000 FL=0x00000007`
       - If ss_server1 returns error status: `P11-W1 AUTH: ERR_STAT ST=0x<status> FL=0x<flags>`
       - If read times out: `P11-W1 AUTH: TIMEOUT ST=0x00000000 FL=0x00000000`
       - If short reply: `P11-W1 AUTH: SHORT ...`
     - **Row 1**: Sector 16 PIO Buffer Classification & PVD Detection
       - If authentication unlocked media: `P11-W1 PIO16: DATA_OK PVD: CD001`
       - If media read remains gated: `P11-W1 PIO16: UNCHANGED`
     - **Row 2**: Auth Transfer Metrics
       - Expected: `AUTH BYTES=112 POLLS=<cnt> WR=112`
     - **Row 3**: VUART Return Codes
       - Expected: `VUART: P2=0 P10=0 W=0 R=0`
     - **Row 4**: Hypercall Counts & Log Telemetry
       - Format: `HC=<total_hc> LOG=<recs> SKIP=<skip> TMO=0x<tmo>`
     - **Row 5**: Buffer Pre-fill Pattern Residuals (0xA5 Counts)
       - Format: `PIO: 16_A5=<cnt> 0_A5=<cnt> 17_A5=<cnt>`
     - **Row 6**: CDVD LPAR Address
       - Format: `CDVD LPAR: 0x0000500002c00000`
     - **Row 7**: DMA Region & Bus Address
       - Format: `DMA RGN=0x... BUS=0x...`
   - Exit the game back to XMB (clean game shutdown triggers cache flush and finalizes `/dev_hdd0/tmp/netemu_log.bin`).
5. **Log Retrieval**:
   - Pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/p11/netemu_log_W1.bin`.

---

## What Variant W1 Tests & Staged Pipeline

Variant W1 executes the full storage setup, guards, authentication command dispatch, and sector read investigation:

```
[TUR] -> [INQUIRY] -> [READ CAPACITY] -> [VUART PARAM QUERIES]
                                                   |
                                     (GUARD: TUR ok, CAP ok, bsz=2048, P10 rc=0)
                                                   |
                           +-----------------------+-----------------------+
                           | Passed                                        | Failed
                           v                                               v
               [HV 163 write 0x70]                                 [TAG_GRD reject]
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

## Log Telemetry Parsing Template

When `local_only/p11/netemu_log_W1.bin` is retrieved, verify:

```
[HDR ] magic=NETEMULG version=1 records=<N> shutdown=1
[BOOT] boot_tb=0x...
[SCAN] rom_cnt=1 hdd=1 bus=4 dev=2
[GRD ] lpar=0x0000500002c00000 ea=0x0000000084000000
[PRE ] open: bus=4 dev=2
[POST] open: rc=0
[PRE ] dma_alloc: sz=0x100000 pexp=20
[POST] dma_alloc: rc=0 rgn=0x...
[PRE ] map: lpar=0x0000500002c00000 rgn=0x...
[POST] map: rc=0 bus_addr=0x...
[PRE ] tur: cmd_lpar=0x0000500002c00000
[POST] tur: rc=0 async=0x0
[PRE ] inq: cmd_lpar=0x0000500002c00000 buf_lpar=0x0000500002c01000
[POST] inq: rc=0 async=0x0 resp='SONY    PS3 CD/D'
[PRE ] cap: cmd_lpar=0x0000500002c00000 buf_lpar=0x0000500002c01000
[POST] cap: rc=0 async=0x0 lba=0x... blk=2048
[PRE ] vuart_p2: port=2 param=3
[POST] vuart_p2: rc=0 val=0x0000000000000800
[PRE ] vuart_p10: port=10 param=3
[POST] vuart_p10: rc=0 val=0x0000000000001000
[PRE ] vuart_p10_p0: port=10 param=0
[POST] vuart_p10_p0: rc=0 val=0x0000000000000000
[PRE ] auth_write: port=10 len=0x70
[POST] auth_write: rc=0 bytes=112
[PRE ] auth_read: port=10 max_len=0x70
[POST] auth_read: read=112 polls=<N> stat=0x00000000 flg=0x00000007 vrd=OK
[PRE ] pio_16: lba=16 proto=1 blks=2048 bsz=1
[POST] pio_16: rc=0 async=0x0 cls=DATA_OK a5=0 polls=<N> w0=... vol='...'
[PRE ] pio_0: lba=0 proto=1 blks=2048 bsz=1
[POST] pio_0: rc=0 async=0x0 cls=ZEROS a5=0 polls=<N> w0=... vol='...'
[PRE ] pio_17: lba=17 proto=1 blks=2048 bsz=1
[POST] pio_17: rc=0 async=0x0 cls=DATA_OK a5=0 polls=<N> w0=... vol='...'
[PRE ] dma_16: lba=16 proto=3 blks=1 bsz=2048
[POST] dma_16: rc=0 async=0x0 cls=...
[PRE ] unmap: rgn=0x... len=0x100000
[POST] unmap: rc=0
[PRE ] free: rgn=0x...
[POST] free: rc=0
[PRE ] close: bus=4 dev=2
[POST] close: rc=0
[END ] finish: ps2_netemu_p11_W1 clean success
```

---

## Security & Verification Summary

1. **Zero Key Exposure**:
   - `prefill_buffer(reply_ea + 0x40, 0x30, 0x00)` executed immediately upon receiving reply.
   - Verified in PC emulation: WAL log contains 0 session key bytes; reply buffer in memory is completely zeroed out.
2. **Bounds & Audits**:
   - Payload slot: `0x4800 .. 0x7F30` (14,128 / 14,320 bytes, 192 bytes free margin).
   - Provenance audit: `audit_ir.py` PASSED (only stack, mailbox `[0x930F20, 0x930F80)`, arena, and validated CDVD buffer).
   - Independent audit: `tools/p1a_audit.py` PASSED (exactly 1 `sc` instruction in changed executable ranges at `0x4858`).
   - SELF verification: `selfdec.py` round-trip decrypted ELF matches patched ELF byte-for-byte.
