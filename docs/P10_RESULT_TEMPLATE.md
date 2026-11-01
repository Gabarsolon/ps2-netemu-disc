# P10 Result Template: Optical Disc Authentication Investigation & Variant V1 Verification

## Console Execution Instructions for Operator

> [!IMPORTANT]
> - **Test Target**: PS2 Game DVD (e.g. *Test Drive Unlimited* PAL DVD-5 or any retail PS2 DVD) inserted into the PS3 disc drive.
> - **Disc Insertion**: Insert the PS2 DVD into the PS3 disc drive tray **BEFORE** launching netemu. Confirm the PS2 disc icon appears on the XMB.
> - **No Photos Needed**: All telemetry is written directly to `/dev_hdd0/tmp/netemu_log.bin` via the durable write-ahead logger.
> - **Execution Discipline**: Launch game, wait 10 seconds, press PS button once to open menu, wait 3 seconds, exit to XMB. The orchestrator will pull the log.
> - **Safety Guarantee**: Variant V1 sends **ZERO** authentication commands (no `0x5005` secure service request). It performs only read-only status queries and zero-length VUART calls to determine whether Port 10 is bound for `ps2_netemu`.

---

### Step-by-Step Operator Instructions

1. **Insert Disc**:
   - Insert the **PS2 retail game DVD** into the drive and confirm the disc icon appears on the XMB.
2. **Setup Placeholder**:
   - Ensure the 64 KiB zeroed placeholder `/dev_hdd0/tmp/netemu_log.bin` exists on `/dev_hdd0/tmp/` (via FTP or script `tools/make_log_placeholder.ps1`).
3. **Install Variant V1**:
   - Copy `local_only/p10/ps2_netemu_p10_V1.self` to `/dev_hdd0/game/PS2NETEMU/USRDIR/ps2_netemu.self` on the PS3 (via FTP).
4. **Launch & Execution**:
   - Start any standard PS2 ISO game from webMAN-MOD or XMB.
   - Wait 10 seconds for initial netemu boot, drive spinup, and probe execution.
   - Press the **PS Button** once to open the in-game menu (evaluates the glance display hook).
   - Observe the on-screen glance display:
     - **Row 0**: Overall Status
       - Expected: `P10-V1 PIO16: UNCHANGED` (if auth gating withholds data) or `P10-V1 PIO16: DATA_OK PVD: CD001` (if unlocked)
     - **Row 6**: VUART Probe Return Codes
       - Expected: `VUART: P2=0 P10=<rc> R0=<rc> W0=<rc>`
       - If Port 10 is unbound in LV1: `VUART: P2=0 P10=-6 R0=-6 W0=-6` (`LV1_NO_ENTRY`)
       - If Port 10 is bound and active: `VUART: P2=0 P10=0 R0=0 W0=0`
     - **Row 7**: VUART Query Return Values
       - Format: `P10_VAL=0x... P2_VAL=0x...`
   - Exit the game back to XMB (clean game shutdown triggers cache flush and finalizes `/dev_hdd0/tmp/netemu_log.bin`).
5. **Log Retrieval**:
   - Pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/p10/netemu_log_V1.bin`.

---

## What Variant V1 Tests & Telemetry Layout

Variant V1 executes the full U1 storage sequence up to `READ CAPACITY`, executes non-destructive VUART status queries, and then records baseline ATAPI `READ(10)` operations.

### 1. Storage Baseline
- `lv1_open_device(dev_bus=4, dev_id=2)` (HV 170): rc = 0
- `lv1_allocate_device_dma_region(size=0x100000, pexp=20)` (HV 174): rc = 0, region = 0xC0000000
- `lv1_map_device_dma_region(lpar=0x500002c00000)` (HV 176): rc = 0, bus_addr = 0xC0000000
- ATAPI `TEST UNIT READY` (HV 248): rc = 0, async = 0
- ATAPI `INQUIRY` 36 bytes (HV 248): rc = 0, delivers `"SONY    PS3 CD/DVD-ROM  1.00"`
- ATAPI `READ CAPACITY(10)` 8 bytes (HV 248): rc = 0, max LBA, block size = 2048

### 2. V1 Non-Destructive VUART Probes (NO Auth Command Sent)
- **Probe A (Control)**: `lv1_get_virtual_uart_param(port=2, param_id=3)` (HV 165)
  - Control check on known valid Sysmgr port. Expected: `rc = 0`.
- **Probe B (Target Port 10 Param 3)**: `lv1_get_virtual_uart_param(port=10, param_id=3)` (HV 165)
  - Query parameter 3 (interrupt/event configuration) on Port 10.
- **Probe C (Target Port 10 Param 0)**: `lv1_get_virtual_uart_param(port=10, param_id=0)` (HV 165)
  - Query parameter 0 on Port 10.
- **Probe D (Zero-Length Read Query)**: `lv1_read_virtual_uart(port=10, buf=data_lpar, size=0)` (HV 162)
  - Query read channel on Port 10 with 0-byte buffer.
- **Probe E (Zero-Length Write Query)**: `lv1_write_virtual_uart(port=10, buf=data_lpar, size=0)` (HV 163)
  - Query write channel on Port 10 with 0-byte buffer.

### 3. Baseline ATAPI Sector Reads
- ATAPI `READ(10)` LBA 16 (PIO protocol: blocks=2048, bsz=1)
- ATAPI `READ(10)` LBA 0 (PIO protocol: blocks=2048, bsz=1)
- ATAPI `READ(10)` LBA 17 (PIO protocol: blocks=2048, bsz=1)
- ATAPI `READ(10)` LBA 16 (DMA protocol: blocks=1, bsz=2048)

### 4. Clean Teardown
- `unmap` (HV 177) -> `free` (HV 175) -> `close` (HV 171).
- Immediate halt on timeout: if any command polls >= 200,000 iterations (~2.0s), logs `TAG_TMO` and halts immediately without teardown.

---

## Log Telemetry Parsing Template

When `local_only/p10/netemu_log_V1.bin` is retrieved, verify:

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
[POST] vuart_p2: rc=<rc_p2> val=0x<val_p2>
[PRE ] vuart_p10: port=10 param=3
[POST] vuart_p10: rc=<rc_p10> val=0x<val_p10>
[PRE ] vuart_p10_p0: port=10 param=0
[POST] vuart_p10_p0: rc=<rc_p10_p0> val=0x<val_p10_p0>
[PRE ] vuart_r0: port=10 len=0
[POST] vuart_r0: rc=<rc_r0> bytes=<bytes_r0>
[PRE ] vuart_w0: port=10 len=0
[POST] vuart_w0: rc=<rc_w0> bytes=<bytes_w0>
[PRE ] pio_16: cmd_lpar=0x0000500002c00000 buf_lpar=0x0000500002c01000
[POST] pio_16: rc=0 async=0x0 class=<UNCHANGED|DATA_OK> a5_cnt=<count>
...
[PRE ] unmap: rgn=0x... len=0x100000
[POST] unmap: rc=0
[PRE ] free: rgn=0x...
[POST] free: rc=0
[PRE ] close: bus=4 dev=2
[POST] close: rc=0
[END ] finish: ps2_netemu_p10_V1 clean success
```

---

## Verdict Decision Tree

| VUART Port 10 Status (`rc_p10`) | Interpretation | Next Action |
|---|---|---|
| `0` (`SUCCESS`) | Port 10 is **bound and active** in `ps2_netemu`! LV1 accepts communication on secure service channel. | Proceed to task P11: issue full `0x5005` disc authentication packet from netemu. |
| `-6` (`LV1_NO_ENTRY`) or `-4` (`LV1_RESOURCE_SHORTAGE`) | Port 10 is **not bound** for `PS2_NE_LPAR` because Sony cleared ability bit `0x2010000`. | Deploy 4-byte CFW patch in `sysmgr_ss.elf` `0x8001E334` to preserve bit `0x2010000` for `PS2_NE_LPAR`, then re-probe. |
