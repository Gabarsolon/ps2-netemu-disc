# P9 Build Notes: Optical Drive DMA Transfer Investigation & Variant U1

## Status
- **Date**: 2026-11-01
- **Task**: P9 - Optical Drive Data Transfer Analysis (DMA vs PIO), stock netemu HDD driver setup comparison, and Variant U1 implementation.
- **Console Ground Truth (P8 T1 Result on PS3 with PS2 DVD & PS3 BD Control)**:
  - Ground truth from `docs/P8_T1_RESULT.md` (TDU PS2 DVD) and `docs/P8_T1_BD_CONTROL_RESULT.md` (GTA IV PS3 BD):
    - `TEST UNIT READY` (ATAPI 0x00): rc = 0, async = 0
    - `INQUIRY` (ATAPI 0x12, 36 bytes inbound, PIO proto 1): rc = 0, buffer received `"SONY    PS3 CD/DVD-ROM  1.00"`
    - `READ CAPACITY(10)` (ATAPI 0x25, 8 bytes inbound, PIO proto 1): rc = 0, max LBA received (`0x001da34f` for TDU DVD, `0x0054185f` for GTA IV BD)
    - `ATAPI READ(10)` (DMA proto 3, 2048 bytes inbound): `rc = 0, async = 0`, but buffer remained 100% `0xA5` (no data transferred)! Sense 0/0/0.
    - `lv1_storage_read` (HV 245, region 0): `rc = 0, async = 0`, buffer remained 100% `0xA5`.
    - `lv1_storage_read` (HV 245, region 1): `rc = 0xFFFFFFFA (-6 NO_ENTRY)`: region 1 does not exist on optical ROM.
  - **Conclusion**: The no-data phenomenon occurs identically on PS3 BD media (GTA IV) as on PS2 DVD media. Media protection / PS2 authentication is ruled out as the primary blocker. Small PIO-protocol inbound commands deliver data into the buffer; 2048-byte DMA-protocol transfers do not deliver data to the buffer despite reporting success.

---

## 1. Comparative Analysis: Stock Netemu HDD Setup vs Probe Optical Setup

A detailed instruction-level comparison was performed by disassembling `local_only/stock.elf` around the complete HDD driver initialization (`0x12BE04`), read submission (`0x12B650`), and interrupt handling (`0x12B320`):

| Setup Stage | Stock Netemu HDD Driver (`0x12BE04`) | Probe Optical Driver (`probe.c`) | Architectural Difference / Significance |
|---|---|---|---|
| **Bus & Dev** | Bus 4, Device 3 (Disk) | Bus 4, Device 2 (ROM) | Different device endpoints on Southbridge storage bus. |
| **Open (HV 170)** | `0x12BF8C`: `lv1_open_device(4, 3, 0)` | `lv1_hcall(170, 4, 2, 0, 0, 0, 0)` | Both succeed with rc = 0. |
| **Event Port (HV 18)** | `0x12BF98`: `lv1_construct_event_receive_port()` -> saves port at `H+0x18` | **OMITTED** | Stock driver creates an LV1 event receive port to handle hardware completion interrupts. |
| **IRQ Connect (HV 197)** | `0x12BFD0`: `lv1_connect_interrupt_event_port(4, 3, port, 0)` | **OMITTED** | Connects physical device interrupt line 0 to the event port. |
| **IRQ Mask (HV 28)** | `0x12BFEC`: `lv1_did_update_interrupt_mask(0x12, port)` | **OMITTED** | Unmasks guest virq 0x12 for hardware interrupt dispatching. |
| **DMA Alloc (HV 174)** | `0x12C03C`: `lv1_allocate_device_dma_region(4, 3, 0x80000, pexp=12, flags=0)` | `lv1_hcall(174, 4, 2, 0x100000, pexp=20, flags=0)` | **CRITICAL DIFFERENCE**: Stock uses **pexp = 12 (4 KiB pages)** for 512 KiB buffer; probe uses **pexp = 20 (1 MiB pages)** for 1 MiB buffer. |
| **DMA Map (HV 176)** | `0x12C0CC`: `lv1_map_device_dma_region(4, 3, lpar, dma_id, 0x80000, flags=0xe000000000000800)` | `lv1_hcall(176, 4, 2, lpar, dma_id, 0x100000, flags=0xe000000000000800)` | Both use exact same flags `0xe000000000000800`. Both return rc = 0 and DMA bus address. |
| **Read Submit** | `0x12B674`: `lv1_storage_read(3, region=1, lba, count, 0, dma_bus_addr)` -> tag | `lv1_hcall(248, 2, 1, cmnd_lpar, 0x40, data_lpar, 2048)` -> tag | Stock uses HV 245 with region 1. Optical probe uses HV 248 ATAPI `READ(10)` with DMA protocol 3. |
| **Completion Wait** | `0x12B70C`: `sc 0` r11=7 (`sys_event_wait` on event 0x2000) | Bounded CPU spinloop polling HV 254 (`lv1_storage_check_async_status`) | Stock blocks on event signaled by interrupt handler; probe polls HV 254. |
| **IRQ Handling** | `0x12B320`: HV 27 (`lv1_end_of_interrupt_ext`), then **HV 249 (`lv1_storage_get_async_status`)**, signals event 0x2000 (`sc 0` r11=8) | **NO IRQ HANDLER** (device interrupt not connected) | Stock acknowledges interrupt with HV 27 and retrieves async status via HV 249. |

### Comparison with Phat PS2 Emulators (`ps2_emu` and `ps2_gxemu`):
- `ps2_emu` optical init (`0x22460`):
  - Uses HV 170 open, HV 18 event port, HV 197 interrupt connect, HV 28 mask update.
  - Allocates DMA with **pexp = 20 (1 MiB)** and maps with `0xe000000000000800`.
  - ATAPI packet helper (`0x22138`) submits HV 248.
  - Interrupt handler (`0x222cc`) polls **HV 254** (`lv1_storage_check_async_status`).
- `ps2_gxemu` optical init (`0x8d510`):
  - Allocates DMA with **pexp = 20 (1 MiB)** and maps with `0xe000000000000800`.
  - Uses HV 18 event port, HV 197 connect, HV 28 update.
  - Submits ATAPI via HV 248 (`0x8da80`).
  - Interrupt handler (`0x8d7d4`) polls **HV 249** (`lv1_storage_get_async_status`) and acknowledges with **HV 27**.

---

## 2. Decoded LV1 4.93 Evidence: Storage Layer Internal Architecture

Disassembly of LV1 4.93 (`local_only/fw493/lv1.elf`) revealed the underlying storage dispatch mechanism:
- **HV 248 entry (`0x3094E4`)**: Dispatches to `0x00251BE0` (`pmi_storage_send_device_command`).
  - Indexes device table at `[TOC - 0x5b70] + 0xEE8 + dev_id * 8`.
  - Calls vtable method at `+0x110` on the device object.
- **HV 249 entry (`0x3093AC`)**: Dispatches to `0x00251E9C` (`pmi_storage_get_async_status`).
  - Calls vtable method at `+0x118` on the device object.
  - In all storage drivers, `+0x118` points to common function `0x00228078`, which acquires spinlock at `dev+0x68`, checks if `dev+0x6c` is busy, stores tag at `dev+0x70`, and returns status.
- **HV 254 entry (`0x30926C`)**: Dispatches to `0x00251D70` (`pmi_storage_check_async_status`).
  - Calls vtable method at `+0x120` on the device object.
  - In all storage drivers, `+0x120` points to common function `0x002545A4`.
  - `0x002545A4` acquires spinlock at `dev+0x9e8`, verifies `dev+0x9f0 == tag`, and returns completion status (`0` if complete, `-9` `LV1_BUSY` if pending).
- **Data Transfer Mechanism**:
  - Neither HV 249 nor HV 254 performs data copy-out! Both are pure completion-status retrieval calls.
  - For DMA transfers (`proto = 3`), the Southbridge SATA/ATAPI controller acts as a PCI bus master, performing direct memory transfer into host physical RAM mapped via IOPTE.
  - For PIO transfers (`proto = 1`), LV1 manages the transfer through internal FIFO buffering and directly writes into the LPAR buffer specified in the command block (`buf_lpar` at offset `+0x38`).

---

## 3. Reference Implementations: Linux `ps3rom.c` and CobraUSB `stor.c`

### Linux Kernel `ps3rom.c` Protocol Selection:
In `drivers/scsi/ps3rom.c`:
- Communication uses `struct ps3_storage_command atapi_cmnd`:
  ```c
  atapi_cmnd.block_size = 1; /* transfer size is block_size * blocks */
  atapi_cmnd.blocks = atapi_cmnd.arglen = scsi_bufflen(cmd);
  atapi_cmnd.buffer = dev->bounce_lpar;
  atapi_cmnd.proto = ...;
  ```
- Protocol constants:
  - `proto = 1`: `PIO_DATA_IN` (data transferred via PIO protocol, byte-granular).
  - `proto = 3`: `DMA` (bus-master DMA, sector-granular).
- For INQUIRY (36 B) and READ CAPACITY (8 B), `proto = 1, blocks = length, block_size = 1` delivers data directly into LPAR RAM through LV1 internal hypervisor handling.
- For sector reads, Linux uses DMA (`proto = 3`) when transfer size >= sector size, but supports PIO data-in for non-DMA devices.

### CobraUSB `stor.c`:
- In `stor.c`, `lv1_storage_read` is called with `stor_var->dma_lpar_addr`, and completion is polled with a busy loop on `lv1_storage_check_async_status` (HV 254) without an event port.
- However, CobraUSB executes within **LV2 (GameOS kernel) context**, where:
  1. The storage device had already been opened and interrupt-connected during GameOS boot initialization.
  2. The Southbridge bus-master DMA channel and interrupt masks were already live in hardware.

---

## 4. Ranked Explanations for DMA Transfer Non-Landing

Based on the static and binary evidence:

### Rank 1: Protocol Handling inside LV1 (PIO vs DMA Transfer Mechanism)
- **Evidence**:
  - In P8, PIO-protocol commands (INQUIRY: 36 B proto 1, READ CAPACITY: 8 B proto 1) succeeded with rc=0 and **delivered valid data** into the exact same buffer (`data_ea` at `0x84001000`).
  - DMA-protocol commands (ATAPI `READ(10)`: proto 3, 2048 B; HV 245 region 0: 2048 B) succeeded with rc=0, async=0, but the buffer remained 100% `0xA5`.
  - In PIO mode (`proto = 1`), LV1 copies the data directly from the drive's FIFO buffer into the LPAR buffer. In DMA mode (`proto = 3`), LV1 programs the Southbridge SATA/ATAPI bus master and immediately awaits a completion status. If bus-master DMA is blocked, unmapped, or un-flushed, the command status register indicates success while RAM remains untouched.
- **Test**: Issuing ATAPI `READ(10)` with **PIO DATA-IN protocol** (`proto = 1`, `in_out = 1`, `blocks = 2048`, `block_size = 1`) will definitively establish if the optical drive will transfer 2048 bytes of sector data through LV1 PIO without relying on Southbridge bus-master DMA.

### Rank 2: Page Size Exponent in HV 174 (Exp 12 vs Exp 20)
- **Evidence**:
  - Stock netemu HDD driver allocates DMA region with `pexp = 12` (4 KiB pages).
  - Our optical probe allocated DMA region with `pexp = 20` (1 MiB pages).
  - While HV 174 and HV 176 accept `pexp = 20`, the slim's Southbridge SATA/ATAPI controller hardware (or its IOPTE address translation unit) may only support 4 KiB (`pexp = 12`) or 64 KiB (`pexp = 16`) page translation for bus-master DMA. If the hardware cannot translate 1 MiB pages, DMA writes drop silently on the bus while completion status is asserted.

### Rank 3: Storage Interrupt & Event Port Connection Requirement (HV 18 + HV 197 + HV 28)
- **Evidence**:
  - Both stock netemu HDD driver and phat emulators (`ps2_emu`, `ps2_gxemu`) construct an event receive port (HV 18), connect device interrupt (HV 197), and update interrupt mask (HV 28).
  - The Southbridge DMA controller may require interrupt servicing / acknowledgement (HV 27) to flush the DMA write FIFO to system memory. Without an active interrupt handshake, the FIFO is never flushed.

### Rank 4: Buffer Address Kind in ATAPI Packet (LPAR vs Bus Address)
- **Evidence**:
  - In `setup_read10_block`, we passed `buf_lpar` at offset `+0x38`. If the hypervisor's DMA dispatcher expects the mapped `dma_bus_addr` rather than `lpar_addr` when `proto = 3`, the controller attempts DMA to an invalid physical address.

---

## 5. Safety & Risk Evaluation: Why Variant U2 (Interrupt Connect) is Not Built

The prompt requested:
> *"If Part 1 identifies a testable DMA fix (for example connecting the event port + interrupt as the stock HDD init does), build it as a SEPARATE variant U2 ... and fully documented risk (an unhandled device interrupt could kill the partition: say how the stock code handles its interrupt and whether our probe needs a handler: do NOT install any interrupt handler of our own unless the stock handler can be reused; if it cannot be made safe, do not build U2 and say so)."*

### Risk Analysis:
1. **Stock Netemu Interrupt Infrastructure**:
   - Stock netemu contains only ONE storage interrupt handler, registered at `0x12B320` for HDD (bus 4, device 3, guest virq `0x12`).
   - Netemu has **NO guest-kernel handler** registered for the optical drive (bus 4, device 2).
2. **Unhandled Guest Interrupt Consequences**:
   - If we call HV 18 (`lv1_construct_event_receive_port`), HV 197 (`lv1_connect_interrupt_event_port` for bus 4 dev 2), and HV 28 (`lv1_did_update_interrupt_mask`), when the optical drive asserts an interrupt on command completion, LV1 routes this interrupt to the guest LPAR.
   - Because the guest kernel has no registered handler for this interrupt vector, the guest kernel executes an unhandled interrupt trap, which triggers an immediate LPAR panic/crash (black screen / console shutdown).
3. **Prohibition on Custom Interrupt Handlers**:
   - The task rules explicitly forbid installing a custom interrupt handler unless the stock handler can be reused. The stock handler at `0x12B320` is hardcoded for HDD (it signals event `0x2000`, accesses HDD context at `H+0x38`/`H+0x40`, and interacts with the stock HDD state machine). It cannot safely handle optical drive completions.
4. **Conclusion**:
   - Connecting the interrupt/event port without an optical interrupt handler is **unsafe** and risks killing the partition.
   - Therefore, per the prompt instruction (*"if it cannot be made safe, do not build U2 and say so"*), **Variant U2 will NOT be built**.
   - All testing will proceed cleanly and safely with **Variant U1**.

---

## 6. Variant U1 Specification & Implementation Plan

### Objective:
Test whether 2048-byte disc sector data lands in our buffer when requested via ATAPI `READ(10)` using the **PIO DATA-IN protocol** (`proto = 1`, `in_out = 1`, `blocks = 2048`, `block_size = 1`), matching the exact protocol format that delivered INQUIRY (36 B) and READ CAPACITY (8 B) data in P8.

### Test Sequence:
1. **S2 Baseline**:
   - Open Device (LV1 170: bus 4 dev 2)
   - Alloc DMA Region (LV1 174: 1 MiB, pexp 20)
   - Map DMA Region (LV1 176: 1 MiB, flags `0xe000000000000800`)
   - `TEST UNIT READY` (ATAPI 0x00, proto 0)
   - `INQUIRY` (ATAPI 0x12, 36 bytes inbound, PIO proto 1)
   - `READ CAPACITY(10)` (ATAPI 0x25, 8 bytes inbound, PIO proto 1)
2. **U1 PIO Sector Reads**:
   - **(1) LBA 16 (PVD Sector) - PIO DATA-IN**:
     - Pre-fill `data_ea` (2048 bytes) with `0xA5`.
     - CDB: `28 00 00 00 00 10 00 00 01 00 00 00` (READ(10), LBA 16, 1 sector).
     - Command block: `pktlen = 12`, `blocks = 2048`, `block_size = 1`, `proto = 1` (PIO DATA-IN), `in_out = 1` (READ), `buf_lpar = data_lpar`.
     - Issue HV 248 with length 2048.
     - Bounded poll HV 254 (200,000 iterations / ~2s).
     - Buffer classification:
       - `UNCHANGED`: 2048 / 2048 bytes remain `0xA5`.
       - `ZEROS`: 2048 / 2048 bytes are `0x00`.
       - `DATA_OK`: bytes 1..5 match ASCII `"CD001"` (ISO9660 PVD identifier).
       - `OTHER`: modified buffer, but not `"CD001"`.
     - Log window samples: `w0` (0..15), `w16` (16..31), `vol` (40..47), `wend` (2032..2047).
   - **(2) LBA 0 (Lead-in / Sector 0) - PIO DATA-IN**:
     - Pre-fill with `0xA5`.
     - CDB: `28 00 00 00 00 00 00 00 01 00 00 00`.
     - Command block: `blocks = 2048, block_size = 1, proto = 1, in_out = 1`.
     - Bounded poll HV 254.
     - Buffer classification and window logging.
   - **(3) LBA 17 (Volume Descriptor Terminator) - PIO DATA-IN**:
     - Pre-fill with `0xA5`.
     - CDB: `28 00 00 00 00 11 00 00 01 00 00 00`.
     - Command block: `blocks = 2048, block_size = 1, proto = 1, in_out = 1`.
     - Bounded poll HV 254.
     - Buffer classification and window logging.
   - **(4) LBA 16 (T1 DMA Repeat Baseline)**:
     - One repeat of T1 DMA `READ(10)` (`proto = 3, blocks = 1, block_size = 2048`) for the record.
     - Bounded poll HV 254.
     - Buffer classification and logging.
3. **Clean Teardown**:
   - Unmap DMA Region (LV1 177)
   - Free DMA Region (LV1 175)
   - Close Device (LV1 171)
   - Complete write-ahead log flush.
