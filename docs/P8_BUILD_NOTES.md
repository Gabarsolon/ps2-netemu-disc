# P8 Build Notes: Disc Sector Read Investigation & Variant T1

## Status
- **Date**: 2026-11-01
- **Task**: P8 - Investigation of `lv1_storage_read` no-data phenomenon on PS2 DVD, static analysis of softemu/gxemu/LV1 optical read path, and building Variant T1.
- **Console Ground Truth (P7 Result on PS3 with TDU DVD-5)**:
  - S0..S2 fully succeeded:
    - `open(4, 2)`: rc = 0
    - `allocate_device_dma_region(1 MiB, exp 20)`: rc = 0, region = `0xC0000000`
    - `map_device_dma_region(lpar=0x500002c00000)`: rc = 0
    - `TEST UNIT READY`: rc = 0, async = 0
    - `INQUIRY`: rc = 0, buffer received `05 80 00 33 9b 00 00 00 53 4f 4e 59 20 20 20 20` ("SONY    ")
    - `READ CAPACITY(10)`: rc = 0, last LBA = `0x001da34f`, block size = 2048 (exactly matching Redump 1,942,352 sectors)
  - S3 (`lv1_storage_read` of Sector 16, 2048 bytes via HV 245):
    - Returned `rc = 0`, `async = 0`, elapsed ~1.9 ms.
    - BUT buffer contents at `0x84001000` remained **completely unchanged** (`00 1d a3 4f 00 00 08 00 53 4f 4e 59...` from READ CAPACITY + INQUIRY).

---

## 1. Static Analysis: Why Did `lv1_storage_read` Return Success with No Data?

### A. How PS2 Emulators Read Data Sectors (`ps2_softemu.elf`)
1. **Targeted Disassembly of `ps2_softemu.elf`**:
   - The optical device command dispatcher is located at `0x00088B9C` (calls HV 248 `r11 = 0xF8` with `dev_id = 2, sub_id = 1, cmdbuf_lpar, 0x40, buf_lpar, size`).
   - The ATAPI command wrapper is located at `0x00088C88`.
   - The sector read function is located at `0x000896C0`:
     - Sets CDB length to 12 at `0x000896E8` (`stw r0, 0x20(r10)`).
     - Formats 32-bit big-endian LBA into `CDB[2..5]` at `0x00089710..0x0008972C`.
     - Jump table at `0x00089758` dispatches by media type:
       - DVD sector read branch at `0x000897DC`:
         - Opcode = `0x28` (`READ(10)`) at `0x000897DC` (`li r9, 0x28; stb r0, 0(r10)`).
         - Blocks = sector count at `0x00089828` (`stw r31, 0x24(r10)`).
         - Block size = `0x800` (2048) at `0x0008982C` (`stw r30, 0x28(r10)`).
         - Protocol = `3` (**DMA protocol**) at `0x00089824` (`stw r0, 0x2c(r10)`).
         - In/Out = `1` (**DATA IN / Read**) at `0x00089840` (`stw r9, 0x30(r10)`).
         - Dispatches via `bl 0x00088C88` (which issues HV 248).
       - CD sector read branch at `0x000898F0`:
         - Opcode = `0xBE` (`READ CD`).
   - **Crucial Discovery**: `ps2_softemu.elf` **NEVER** calls `lv1_storage_read` (HV 245) for optical disc reads!
     - An exhaustive scan of all `sc 1` call-sites in `ps2_softemu.elf` reveals that HV 245 is ONLY invoked by the HDD driver (`0x00067BB4`) and flash storage. The optical storage driver exclusively uses ATAPI packet commands via HV 248 (`lv1_storage_send_device_command`).

### B. Hypervisor Storage Dispatch in LV1 4.93 (`lv1.elf`)
1. **HV 245 Entry (`0x00308B88`) and Storage Dispatch (`0x002514C8`)**:
   - `0x002514D8`: Validates `dev_id < 6` (`cmpldi cr7, r4, 0x6`). Device 2 (ROM) passes.
   - `0x0025152C`: Loads device structure `ld r29, 0xee8(r11)` where `r11 = dev_table + dev_id * 8`.
   - `0x00251540`: Calls vtable method `vtable[0x30]` for permission verification.
   - `0x002515F8`: Dispatches block read via vtable method `vtable[0x100]` with `r3 = device_ptr, r4 = lpar_id, r5 = region_id, r6 = start_sector, r7 = count, r8 = flags, r9 = buffer_lpar, r10 = async_tag`.
   - **Why HV 245 returned success with no data on ROM device**:
     - Device 2 (ROM) in LV1 is an ATAPI device controller, not a partitioned block device with a block translation layer.
     - When `vtable[0x100]` is invoked on device 2 with `region_id = 0`, the block driver finds no partition or mapped sector table for region 0. It reports 0 blocks transferred and immediately returns `rc = 0, async = 0` without submitting any ATA/ATAPI packet to the BDVD Southbridge controller.
     - Real optical reads on PS3 are intended to go through the SCSI/MMC packet interface (HV 248).

### C. Optical Drive Authentication State Machine (`ps2_disc_auth` at `0x0008B2BC`)
1. **Authentication Details**:
   - `0x0008B2BC` builds a communication packet with magic header `0xFACE`, service `0x5000`, and operation `0x5005`.
   - Dispatches the packet to the drive controller via virtual UART 10 (`r3 = 0xA`).
   - Caller at `0x00221354` initiates this authentication during emulator initialization before disc boot.
   - If authentication is omitted, drive firmware may restrict access to PS2 game sectors. Standard MMC commands (TUR `0x00`, INQUIRY `0x12`, READ CAPACITY `0x25`) succeed unconditionally because they are unauthenticated MMC inquiries.
   - Variant T1 will test whether ATAPI `READ(10)` (opcode `0x28`) on LBA 16 succeeds without UART auth, or returns `CHECK CONDITION` with authentication sense codes (`05/6F/00`).

### D. Memory Coherency and Page-Table Flags (`stock.elf`)
1. **Page-Table Helper `0x00016790`**:
   - Maps SB_CDVD buffer (`0x84000000`) into HTAB with WIMG bits `0x0` (normal cacheable, coherent memory: `M=1, I=0, W=0, G=0`).
   - S1 and S2 proved that DMA from the optical drive via Southbridge arrives cache-coherently on Cell PPE: INQUIRY string `"SONY    "` and READ CAPACITY max LBA `0x001da34f` were read immediately by the CPU without cache invalidation (`dcbf`) instructions.
   - Stale CPU cache is **ruled out** as the reason why Sector 16 data was missing.

---

## 2. Ranked Explanations with Concrete Evidence

1. **Rank 1: Wrong Hypercall Architecture (HV 245 Block Read vs HV 248 ATAPI Packet)** [PRIMARY CAUSE]
   - **Evidence**: `ps2_softemu.elf` at `0x000897DC` disassembles directly to ATAPI `READ(10)` (opcode `0x28`), block size 2048, DMA protocol `3`, direction `1` via HV 248. HV 245 is NEVER called for optical reads in official Sony emulators.
   - In LV1, HV 245 is designed for block partition devices (HDD dev 3, flash dev 0/1). On ROM devices, HV 245 region 0 has no block translation and returns 0 blocks transferred (`rc = 0, async = 0`) synchronously without queueing an ATAPI transfer.

2. **Rank 2: Drive State Machine Requiring PS2 Auth Handshake**
   - **Evidence**: `ps2_softemu.elf` contains `ps2_disc_auth` (`0x0008B2BC`), which sends service `0x5000` / op `0x5005` packet `0xFACE` over virtual UART 10.
   - Without authentication, drive firmware may refuse to serve data sectors of a PS2 disc. Testing ATAPI `READ(10)` in Variant T1 will decisively prove whether the drive serves the sector or raises `CHECK CONDITION` (Sense `05/6F/00`).

3. **Rank 3: Region ID / Parameter Interpretation in HV 245**
   - **Evidence**: Dev 2 repository entries show region 0 and region 1. If HV 245 does support ROM reads under specific circumstances, region 0 might be invalid or unmapped while region 1 might represent the raw disc. Variant T1 will test region 1.

4. **Rank 4: Buffer Address Kind / LPAR Offset**
   - **Evidence**: S1 and S2 proved that `data_lpar = cdvd_lpar + 0x1000` was correctly targeted by HV 248 DMA. Pre-filling the entire 2 KiB window with `0xA5` in T1 will decisively verify if DMA writes anywhere in the range.

5. **Rank 5 (Ruled Out): Async Completion Semantics**
   - **Evidence**: The call completed synchronously (`async = 0`). If asynchronous, LV1 returns an async tag and status pending, which was not observed.

6. **Rank 6 (Ruled Out): CPU Reading Stale Cache**
   - **Evidence**: HTAB mapping uses `M=1` (coherence enabled). S1 (INQUIRY) and S2 (READ CAPACITY) were immediately visible to the CPU.

---

## 3. Variant T1 Implementation Plan

### A. Sequence of Operations
1. **S2 Sequence**:
   - `open(4, 2)` (dev 2 = optical drive)
   - `allocate_device_dma_region(1 MiB, exp 20)`
   - `map_device_dma_region(cdvd_lpar)`
   - `TEST UNIT READY` (ATAPI 0x00 via HV 248) -> log rc, async, polls, ticks
   - `INQUIRY` (ATAPI 0x12 via HV 248, 36 bytes) -> log rc, async, first 16 bytes ("SONY    ")
   - `READ CAPACITY(10)` (ATAPI 0x25 via HV 248, 8 bytes) -> log rc, async, max LBA, block size
2. **Step 1: Data Buffer Pre-fill**:
   - Pre-fill `cdvd_ea + 0x1000 .. cdvd_ea + 0x1800` (2048 bytes) with `0xA5` through CPU address before each read attempt.
3. **Step 2: ATAPI `READ(10)` of LBA 16**:
   - CDB: `28 00 00 00 00 10 00 00 01 00 00 00` (12 bytes).
   - Command block: `pktlen = 12, blocks = 1, block_size = 2048, proto = 3 (DMA), in_out = 1 (READ), buf_lpar = cdvd_lpar + 0x1000`.
   - Issue HV 248: `lv1_hcall(248, dev_id, 1, cmnd_block_lpar, 0x40, data_lpar, 2048)`.
   - Poll completion (bounded: 200,000 iterations AND ~2.0s timebase). Immediate halt on timeout.
   - If Check Condition (`status == 2`), issue `REQUEST SENSE` (`0x03`, 18 bytes).
   - Log buffer metrics:
     - Count of remaining `0xA5` bytes in 2048-byte buffer.
     - First 16 bytes (0..15). For ISO9660 PVD, bytes 0..7 must be `01 43 44 30 30 31 01 00` (`\x01CD001\x01\x00`).
     - Bytes 16..31.
     - Volume identifier at bytes 40..47 (check for "TDU" / volume label).
     - Last 16 bytes (2032..2047).
4. **Step 2b: Repeat ATAPI `READ(10)` for LBA 0 and LBA 17**:
   - **LBA 0**: Pre-fill with `0xA5`, issue READ(10), poll, sense if CC, log A5 count, bytes 0..15, bytes 2032..2047.
   - **LBA 17**: Pre-fill with `0xA5`, issue READ(10), poll, sense if CC, log A5 count, bytes 0..7 (expect `FF 43 44 30 30 31 01 00` for Volume Descriptor Terminator), bytes 40..47, bytes 2032..2047.
5. **Step 3: Repeat `lv1_storage_read` (HV 245) of Sector 16**:
   - **Region 0 Attempt**: Pre-fill with `0xA5`, call `lv1_storage_read(2, region=0, lba=16, count=1, flags=0, buffer=data_lpar)`, poll, log A5 count, bytes 0..15, bytes 2032..2047.
   - **Region 1 Attempt**: Pre-fill with `0xA5`, call `lv1_storage_read(2, region=1, lba=16, count=1, flags=0, buffer=data_lpar)`, poll, log A5 count, bytes 0..15, bytes 2032..2047.
6. **Step 4: Cleanup**:
   - On normal exit: unmap DMA region, free DMA region, close device.
   - On timeout: HALT immediately without unmap/free/close.
