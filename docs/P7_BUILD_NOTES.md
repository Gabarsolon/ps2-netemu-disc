# P7 Build Notes: Optical Read Pipeline & Address-Kind Architecture

## Status
- **Date**: 2026-11-01
- **Target**: Official 4.93 LV1 (`local_only/fw493/lv1.elf`), stock netemu (`local_only/stock.elf`), and console ground truth (`docs/P6_R1_RESULT.md`, `local_only/netemu_log_R1.bin`).
- **Milestone Achieved (P6 R1)**:
  - `lv1_map_device_dma_region(4, 2, lpar 0x0000500002c00000, bus 0xC0000000, len 0x100000, flags 0xe000000000000800)` returned **`rc = 0` (SUCCESS)** on console!
  - Unmap `rc = 0`, Free `rc = 0`, Close `rc = 0`.
  - Proven: Partition CAN map a 1 MiB DMA buffer for optical BDVD (bus 4, dev 2).
  - Proven: `0x2458438` is the 64-bit physical LPAR address (`0x500002c00000`); `0x2458428` is the 32-bit CPU Effective Address (`0x84000000`).

---

## 1. Address-Kind Architecture & Concrete Evidence

### 1.1 Verified Address Decisions Table

| Role | CPU vs Hypervisor | Address Value (P6 R1 / Console) | Buffer Source | Concrete Evidence & Verification |
|---|---|---|---|---|
| **CPU Command Block Pointer** | CPU Effective Address (EA) | `0x0000000084000000` | `*(0x2458428)` | CPU executes stores into CDB and header fields. HTAB PTE maps EA `0x84000000` to LPAR `0x500002c00000`. |
| **Command Block Physical Base** | Physical LPAR Address | `0x0000500002c00000` | `*(0x2458438)` | Passed as param 3 (`r5`) to `lv1_storage_send_device_command` (HV 248). Hypervisor reads 64-byte command block from physical partition memory. |
| **ATAPI Packet Buffer Pointer (`+0x38`)** | Physical LPAR Address | `0x0000500002c01000` | `*(0x2458438) + 0x1000` | Linux `drivers/scsi/ps3rom.c` line 124 / `ps3stor_lib.c`: `cmd.buffer = bounce_lpar`. Hypervisor translates LPAR through DMA region mapping. |
| **HV 248 Data Buffer Parameter** | Physical LPAR Address | `0x0000500002c01000` | `*(0x2458438) + 0x1000` | Passed as param 5 (`r7`) to HV 248. |
| **HV 245 Storage Read Data Buffer** | Physical LPAR Address | `0x0000500002c01000` | `*(0x2458438) + 0x1000` | Stock HDD driver `0x12d364` loads `H+0x20` (physical LPAR `0x500002d00000`) and passes as `r8` to `lv1_storage_read` (HV 245 at `0x12b674`). Cobra `stor.c` line 52: passes `stor_var->dma_lpar_addr`. |
| **CPU Data Inbound Read Pointer** | CPU Effective Address (EA) | `0x0000000084001000` | `*(0x2458428) + 0x1000` | CPU reads INQUIRY response, READ CAPACITY, and sector 16 bytes through CPU cache/effective address space. |
| **DMA Region Handle / Bus Address** | Bus Address | `0x00000000C0000000` | Returned by HV 174 | Allocated by `lv1_allocate_device_dma_region(4, 2, 0x100000, 20)`. HV 176 maps LPAR `0x500002c00000` to this bus address. |

### 1.2 Hypervisor Verification (Official 4.93 LV1)
- **HV 245 (`0x308b88`, `lv1_storage_read`)**:
  - `FUN_00308b88(dev_id, region_id, start_sector, num_sectors, flags, lpar_addr, &tag)`
  - Calls `func_0x002514c8(dev, dev_id, region_id, start_sector, num_sectors, flags, lpar_addr, &tag)`.
  - The buffer argument is explicitly validated against the calling partition's DMA regions mapped for `dev_id`. The hypervisor performs the physical LPAR $\rightarrow$ bus translation internally.
- **HV 248 (`0x3094e4`, `lv1_storage_send_device_command`)**:
  - `FUN_003094e4(dev_id, sub_channel, cmnd_block_lpar, cmnd_size, data_lpar, data_size, &tag)`
  - Calls `func_0x00251be0(dev, dev_id, cmnd_block_lpar, flags, buffer, size, data_lpar, &tag)`.
  - Hypervisor copies the 64-byte ATAPI packet using `cmnd_block_lpar` and programs the Southbridge DMA controller with the mapped region for `data_lpar`.

---

## 2. Sequence Variants (S0, S1, S2, S3)

### Variant S0: Baseline Verification
- Sequence: `open(4,2)` $\rightarrow$ `alloc_dma_region(0x100000, 20)` $\rightarrow$ `map_dma_region(0x500002c00000, 0xC0000000, 0x100000, 0xe000000000000800)` $\rightarrow$ `unmap` $\rightarrow$ `free` $\rightarrow$ `close`.
- Purpose: Confirms the P6 R1 baseline behaves identically in the P7 build harness.

### Variant S1: ATAPI Discovery (TUR & INQUIRY)
- Extends S0 by holding the DMA mapping active:
  1. `TEST UNIT READY` (CDB `0x00`, 0 bytes inbound):
     - Hypercall 248 (`cmnd_block_lpar = 0x500002c00000`, size 64, data 0, size 0).
     - Bounded async status polling via HV 254 (`poll_completion`, 200,000 iter / ~2s timebase).
     - Log status word. (If drive empty, expect check condition / not ready).
  2. `INQUIRY` (CDB `0x12`, allocation length 36 bytes):
     - Hypercall 248 (`data_lpar = 0x500002c01000`, size 36, proto 1, in_out 1).
     - Bounded async status polling via HV 254.
     - Logs status and the 36-byte vendor/product string read from `data_ea = 0x84001000`.
  3. Clean teardown: `unmap` $\rightarrow$ `free` $\rightarrow$ `close`.

### Variant S2: Medium Geometry (READ CAPACITY)
- Extends S1:
  1. `READ CAPACITY(10)` (CDB `0x25`, 8 bytes inbound):
     - Hypercall 248 (`data_lpar = 0x500002c01000`, size 8).
     - Bounded async status polling via HV 254.
     - Logs Max LBA and Block Size.
  2. Clean teardown: `unmap` $\rightarrow$ `free` $\rightarrow$ `close`.

### Variant S3: ISO9660 PVD Sector 16 Read
- Extends S2:
  1. Read Sector 16 (2048 bytes via HV 245 `lv1_storage_read`):
     - `lv1_storage_read(dev_id=2, region=rom_reg, start_lba=16, count=1, flags=0, buf_lpar=0x500002c01000)`.
     - Bounded async status polling via HV 254.
     - If success: logs first 16 bytes (expected `01 43 44 30 30 31 01 00` for `CD001` ISO9660 PVD).
     - If failure / Check Condition: issues `REQUEST SENSE` (CDB `0x03`, 18 bytes inbound via HV 248) to capture detailed Sense Key, ASC, and ASCQ.
  2. Clean teardown: `unmap` $\rightarrow$ `free` $\rightarrow$ `close`.

---

## 3. Safety & Concurrency Architecture
1. **Durable Write-Ahead Logging (WAL)**:
   - Sector 0 header updated on every commit with write cursor and session boot ID.
   - PRE records logged before every hypercall, POST records after return.
   - In-memory circular staging guarantees zero loss even on sudden power-off.
2. **HDD Driver Idle Discipline**:
   - HDD singleton `H = 0x241C850` checked before issuing UFS operations.
   - If busy, logging gracefully skips without blocking game execution.
   - Never write to disk during async polling loops.
3. **Timeout Discipline**:
   - If 200,000 iterations or ~2.0s timebase elapses without async completion:
   - Log `TAG_TMO` with poll count and elapsed ticks.
   - **HALT IMMEDIATELY**: Never unmap, free, or close after a timeout to prevent hypervisor DMA memory corruption while hardware is potentially active.
4. **Memory Protection & Audit Rules**:
   - Mailbox strictly within `[0x930F20, 0x930F80)`.
   - Zero stores at or above `0x930F80`.
   - Payload executable contains exactly 1 `sc` at `0x4858`.

---

## 4. Build Artifacts & PC Validation Results

### 4.1 Built Binaries & Hashes

| Variant | Code Size | Payload Range | ELF SHA-256 | SELF SHA-256 | SELF Size |
|---|---|---|---|---|---|
| **S0** | 6576 bytes (45.9%) | `0x4800..0x61B0` | `a0550a893e12326b18bff6c4b6b617b092534e269552fa77999bf5fc8cc42cd9` | `02d78acc6da9198369564bf26f7fe45fbe58c7d232e3228bd136d78816db37ca` | 2,527,568 |
| **S1** | 8224 bytes (57.4%) | `0x4800..0x6820` | `7970cef2ed66cfe68bb235327f8526a1822569772bda603ad4aa9dac0bf556d3` | `0cb28bd0e46556dc13aeaf415bb326b7b0cfc742ca7010a076ea4a47f9eb13bf` | 2,528,368 |
| **S2** | 8888 bytes (62.1%) | `0x4800..0x6AB8` | `d94df44a260a1fb9043413c1a1f04b858a34824c8b6666e425dfa75bf849d471` | `0c31a97ef2cc2b4c700ab7106d9b73ba798faf5c2693ec5802fb694a0c2c2de4` | 2,528,512 |
| **S3** | 10232 bytes (71.5%) | `0x4800..0x6FF8` | `32add03ea4d9025efe0eac37e1e69f23d62f942853c2c28327f2390878911a4a` | `006e9526821a0c45a8c9051f6dbb675ff719b667b0324790ebb8d0d2792330a8` | 2,528,896 |

### 4.2 Security & Strict Static Audits
- **IR Provenance Audit**: PASSED for S0, S1, S2, S3. All stores strictly restricted to stack, mailbox `[0x930F20, 0x930F80)`, arena, and verified command block at CPU EA `0x84000000`.
- **Instruction Audit (`tools/p1a_audit.py`)**: PASSED for all 4 variants.
  - Exactly one `sc` instruction in changed ranges at `0x4858`.
  - Phdr types, flags, offsets, virtual addresses, filesz, and memsz identical to stock ELF.
  - Zero stores to `0x930F80..0x931000`.
- **SELF Decryption Round-Trip (`selfdec.py`)**: Byte-for-byte exact roundtrip verified for all 4 SELFs against their patched ELFs.
- **PowerShell Script Syntax**: Parse-checked with zero syntax errors (parse-only, zero network contact).

### 4.3 PC Emulation Results (`netemu_p7/validate_pc.py`)
- **Step 1: PowerShell Syntax**: All 4 operator scripts parse-clean.
- **Step 2: Wrapper Bytes**: 29 instructions match stock, `sc` at `0x4858`, `mr r8, r9` at `0x4848`.
- **Step 3: Variant S0 Emulation**: Baseline sequence verified (`open` -> `alloc` -> `map` -> `unmap` -> `free` -> `close`). Row 0 displays `P7-S0 BASELINE MAP OK`. Clean WAL header and records verified.
- **Step 4: Register Preservation**: Generic wrapper `lv1_hcall` at `0x4800` preserves `r8`, `cr2..cr4`, `LR`, `r30`, `r31`, and non-volatile `r14..r29` 100% identically to stock helper.
- **Test A (S3 Normal Read Path)**: Full sequence simulated (TUR -> INQ -> CAP -> Sector 16). Read succeeds with ISO9660 PVD starting `\x01CD001\x01\x00`. Row 0: `P7-S3 PVD: CD001 READ OK`.
- **Test B (S3 Disc Absent)**: Read returns Check Condition; probe triggers `REQUEST SENSE` (CDB 0x03, 18 bytes); receives Sense Key 0x02, ASC 0x3A, ASCQ 0x00. Row 0: `P7-S3 SENSE: 00000002/0000003a/00000000`.
- **Test C (S3 Authentication Required)**: Read returns Check Condition; probe issues `REQUEST SENSE`; receives Sense Key 0x05, ASC 0x6F, ASCQ 0x00. Row 0: `P7-S3 SENSE: 00000005/0000006f/00000000`.
- **Test D (S3 Timeout Discipline)**: Bounded poll times out; probe logs `TAG_TMO` and immediately halts. Unmap, free, and close are NOT called.
- **Test E (S3 Guard Refusal)**: Corrupt LPAR/EA or swapped values rejected with 0 hypercalls; Row 0: `P7-S3 SANITY REJECT (0 HC)`.
- **Test F (S3 Concurrency)**: Stock HDD busy flag tested; 25 records safely skipped; zero disk writes while busy.
- **Test G (S3 UFS Open Error Fail-Open)**: UFS open error handled without crashing; probe runs cleanly.
- **Test H (Strict Store Bounds & Memory Write Provenance)**:
  - All stores strictly within stack, mailbox, arena, and verified command block.
  - Zero stores to `0x930F80..0x931000`.
  - Zero stores to physical LPAR (`0x500002c00000`).

