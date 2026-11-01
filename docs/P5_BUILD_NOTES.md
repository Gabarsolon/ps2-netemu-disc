# P5 Build Notes: DMA Mapping Investigation & Argument Search (Variant Q1)

## Status
- **Date**: 2026-11-01
- **Task**: P5 - Identify and validate the correct DMA allocation and mapping parameters for PS3 optical storage (Bus 4, Dev 2).
- **Trigger**: First console run of P4 K1 (`docs/P4_K1_RESULT.md`) successfully initialized WAL, opened the device, and allocated a DMA region, but `lv1_map_device_dma_region(4, 2, lpar=0x84000000, bus_addr=0xC0000000, len=0x80000, flags=0xe000000000000800)` returned `-17` (`LV1_ILLEGAL_PARAMETER_VALUE`).

---

## 1. Ground Truth from Console (P4 K1 Run)

From `docs/P4_K1_RESULT.md`:
- `open(4, 2)`: `rc = 0` (Storage device successfully opened).
- `lv1_allocate_device_dma_region(4, 2, sz=0x80000, exp=12, flags=0, &bus_addr)`: `rc = 0`, returned `bus_addr = 0xC0000000`.
- `lv1_map_device_dma_region(4, 2, lpar=0x84000000, bus_addr=0xC0000000, len=0x80000, flags=0xe000000000000800)`: **`rc = 0xFFFFFFEF = -17`**.
- `free_device_dma_region(4, 2, 0xC0000000)`: `rc = 0`.
- `close(4, 2)`: `rc = 0`.
- **Conclusion**: The hypervisor accepted the device open and DMA region creation, but rejected the mapping request. The error was a clean `-17`, confirming parameter validation failure rather than a hardware crash or hang.

---

## 2. Evidence from Sony Official Emulators

Static analysis of official Sony emulator binaries (`local_only/fw355/out/`):

### 2.1 `ps2_softemu.elf` (Firmware 3.55)
Optical device initialization is performed in function `0x088724`:
1. **Device Open (`0x088800`)**:
   - `li r11, 170` (LV1 storage open)
   - `ld r3, 0(r29)`: Bus ID = 4
   - `ld r4, 0(r31)`: Dev ID = 2
   - `li r5, 0`
   - `sc 2` at `0x088814` -> `rc == 0`
2. **Buffer Allocation (`0x086a3c..0x086a5c`)**:
   - `lis r3, 16` (`0x100000` = 1,048,576 bytes = 1 MiB)
   - `std r0, 0(r9)`: Size stored into `0x16c9a20` is **`0x100000` (1 MiB)**.
   - Calls `0x3d290` (memory allocator):
     - At `0x03d2ec`: `li r5, 20` (0x14) -> **Page Size Exponent = 20** (2^20 = 1 MiB)!
     - Calls `0x48f60` -> `lv1_allocate_memory(size=0x100000, page_size_exp=20, flags=0, 0, &lpar)`.
3. **DMA Region Allocation (`0x088838`)**:
   - `li r11, 174` (LV1 allocate_device_dma_region)
   - `ld r3, 0(r29)`: Bus ID = 4
   - `ld r4, 0(r31)`: Dev ID = 2
   - `ld r5, 0(r30)`: **Size = `0x100000` (1 MiB)** (NOT `0x80000`!)
   - `li r6, 20` (0x14): **Page Size Exponent = 20 (1 MiB)** (NOT `12` / 4 KiB!)
   - `li r7, 0`: Flags = 0
   - `sc 2` at `0x088850`
   - Returns allocated bus address in `r4`.
4. **DMA Region Mapping (`0x088870`)**:
   - `li r11, 176` (LV1 map_device_dma_region)
   - `ld r3, 0(r29)`: Bus ID = 4
   - `ld r4, 0(r31)`: Dev ID = 2
   - `ld r5, 0(r8)`: LPAR address of the 1 MiB buffer
   - `mr r6, r4`: Bus address returned by alloc
   - `ld r7, 0(r30)`: **Length = `0x100000` (1 MiB)** (NOT `0x80000`!)
   - `ld r8, -23008(r2)`: Loaded from TOC `0x5c3220` = **`0xe000000000000800`**
   - `sc 2` at `0x088884`

### 2.2 `ps2_gxemu.elf` (Firmware 3.55)
- DMA Region Allocation at VA `0x08d4b4`:
  - `ld r3, 0(r29)`: Bus 4
  - `ld r4, 0(r31)`: Dev 2
  - `ld r5, 0(r30)`: Size = `0x100000` (1 MiB)
  - `li r6, 20` (0x14): **Page Size Exponent = 20 (1 MiB)**
  - `li r7, 0`: Flags = 0
  - `sc 2` at `0x08d4cc`

**Evidence Summary from Official Emulators**:
Both `ps2_softemu` and `ps2_gxemu` configure the optical device DMA region with **Page Size Exponent 20 (1 MiB)**, **Region Size 1 MiB (`0x100000`)**, and **Map Length 1 MiB (`0x100000`)**.

---

## 3. Evidence from Stock `ps2_netemu.self`

Static analysis of `local_only/stock.elf`:

### 3.1 Buffer Allocations (`0x19a5c` shim)
Both the `SB_HDD` buffer and the `SB_CDVD` buffer are allocated via helper `0x19a5c` calling `0x19900`:
- At `0x12c010`: Allocates `SB_HDD` (name `"SB_HDD"`, size `lis r4, 16` = `0x100000` = 1 MiB).
- At `0x133cb0`: Allocates `SB_CDVD` (name `"SB_CDVD"`, size `lis r4, 16` = `0x100000` = 1 MiB, stored in state `0x2456fe0 + 5200`).
- Inside `0x19900`:
  - `0x01995c`: `li r5, 20` (0x14) -> **Page Size Exponent = 20 (1 MiB)**!
  - `0x01996c`: calls `0x1622c` -> `lv1_allocate_memory(size=0x100000, page_exp=20, flags, 0, &lpar)`.
- **Crucial Finding**: The `SB_CDVD` buffer on console (`0x84000000`) is a **1 MiB allocation backed by 1 MiB pages (exponent 20)**.

### 3.2 Stock HDD Mapping vs Optical
In `stock.elf` (`0x12c01c`):
- The HDD driver maps dev 3 using `size = 0x80000`, `page_exp = 12`, `len = 0x80000`, `flags = 0xe000000000000800`.
- In P4 K1, we copied the HDD parameters (`size=0x80000`, `page_exp=12`, `len=0x80000`) to the optical device (dev 2).
- This failed with `-17` because:
  1. Optical DMA region was allocated with `page_exp = 12` (4 KiB pages), whereas the `SB_CDVD` LPAR buffer was allocated with `page_exp = 20` (1 MiB pages). The hypervisor enforces page-size alignment between the DMA region and the memory backing.
  2. Mapping length `0x80000` (512 KiB) represents a fractional/partial page of a 1 MiB allocation (`0x100000`).

---

## 4. Evidence from Linux PS3 Kernel & CBE Architecture

From `arch/powerpc/platforms/ps3/mm.c` and `arch/powerpc/include/asm/cell-regs.h`:
- `lv1_map_device_dma_region(bus_id, dev_id, lpar_addr, bus_addr, len, iopte_flag)`:
  - `CBE_IOPTE_PP_W = 0x8000000000000000` (Write permission)
  - `CBE_IOPTE_PP_R = 0x4000000000000000` (Read permission)
  - `CBE_IOPTE_M    = 0x2000000000000000` (Coherency required)
  - `CBE_IOPTE_SO_RW = 0x1800000000000000` (Strong ordering)
  - `CBE_IOPTE_IOID_Mask = 0x00000000000007FF` (I/O Identifier)
- In Sony emulators:
  - `0xe000000000000800` = `PP_W | PP_R | M | 0x800`.
  - Bit 11 (`0x800`) is an I/O controller configuration attribute or IOID bit set by Sony firmware.
- In Linux PS3 `mm.c`:
  - `iopte_flag` is checked via `BUG_ON(iopte_flag != 0xf800000000000000UL)`.
  - Both `0xe000000000000800` and `0xe000000000000000` and `0xf800000000000000` are valid architectural variations.

---

## 5. Hypotheses & Ranked Candidate Argument Sets

### Hypothesis 1 (Primary - Highest Probability: ~95%):
**Root cause is Region Page Size Exponent and Map Length mismatch.**
- Allocation must use `size = 0x100000`, `page_exp = 20` (1 MiB) to match the `SB_CDVD` 1 MiB page size.
- Map length must be `len = 0x100000` (1 MiB full page).
- Flags: `0xe000000000000800`.
- Evidence: Exact match to `ps2_softemu` (`0x088838`, `0x088870`), `ps2_gxemu` (`0x08d4b4`), and `SB_CDVD` allocator (`0x133cb0` / `0x1995c`).

### Hypothesis 2 (Secondary):
**Bit 11 (`0x800`) in IOPTE flags is restricted for optical storage.**
- Flags: `0xe000000000000000` (without `0x800`) or `0xf800000000000000` (Linux `SO_RW`).

### Hypothesis 3 (Tertiary):
**Optical device requires smaller page size or partial map.**
- Page exponent 12 (4 KiB) or 16 (64 KiB), or length `0x1000` (4 KiB) / `0x80000` (512 KiB).

---

## 6. Variant Q1 Search Sequence

Variant Q1 will execute a systematic, logged sequence of candidate sets.
For each candidate:
1. Re-check stock HDD drive idle status.
2. If region parameters change: free existing region (`175`), allocate new region (`174`).
3. Log `PRE MAP: lpar=0x... bus=0x... len=0x... flags=0x...`
4. Issue `lv1_map_device_dma_region(4, 2, lpar, bus_addr, len, flags)`.
5. Log `POST MAP: rc=<rc>`.
6. **If `rc == 0`**:
   - SUCCESS!
   - Immediately issue `lv1_unmap_device_dma_region(4, 2, bus_addr, len)` and log `POST UNMAP`.
   - Issue `lv1_free_device_dma_region(4, 2, bus_addr)` and log `POST FREE`.
   - Issue `lv1_storage_close(4, 2)` and log `POST CLOSE`.
   - Log `TAG_END` with summary and candidate ID.
   - STOP all further attempts.
7. **If `rc != 0`**:
   - Continue to next candidate.
8. If all candidates fail:
   - Cleanly free active region, close device, and log `TAG_END`.

### Candidate Test Matrix in Q1:

| Cand # | Group | Region Alloc Size | Alloc Exp | Map Length | Map Flags | Description / Rationale |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **#1** | A | `0x100000` | **20** | **`0x100000`** | `0xe000000000000800` | **Official emulator optical standard** (`softemu` & `gxemu`) |
| **#2** | A | `0x100000` | **20** | **`0x100000`** | `0xe000000000000000` | Exp 20, 1 MiB, flags without 0x800 bit |
| **#3** | A | `0x100000` | **20** | **`0x100000`** | `0xf800000000000000` | Exp 20, 1 MiB, Linux PS3 IOPTE flags (`SO_RW`) |
| **#4** | A | `0x100000` | **20** | **`0x100000`** | `0x6000000000000800` | Exp 20, 1 MiB, Read-Only permission (`PP_R | M | 0x800`) |
| **#5** | A | `0x100000` | **20** | `0x80000` | `0xe000000000000800` | Exp 20, partial 512 KiB length |
| **#6** | B | `0x100000` | **12** | `0x100000` | `0xe000000000000800` | Exp 12 (4 KiB pages), 1 MiB region & length |
| **#7** | B | `0x100000` | **12** | `0x80000` | `0xe000000000000800` | Exp 12, 1 MiB region, 512 KiB length |
| **#8** | B | `0x100000` | **12** | `0x1000` | `0xe000000000000800` | Exp 12, single 4 KiB page length |
| **#9** | C | `0x80000` | **12** | `0x80000` | `0xe000000000000000` | P4 K1 region, flags without 0x800 bit |
| **#10** | C | `0x80000` | **12** | `0x80000` | `0xf800000000000000` | P4 K1 region, Linux PS3 IOPTE flags |
| **#11** | C | `0x80000` | **12** | `0x1000` | `0xe000000000000800` | P4 K1 region, 4 KiB length |
| **#12** | D | `0x100000` | **16** | `0x100000` | `0xe000000000000800` | Exp 16 (64 KiB pages), 1 MiB region & length |

---

## 7. Binary Build Artifacts & Hash Verification

| Artifact | File Path | File Size | SHA256 Hash |
|---|---|---|---|
| **Patched ELF** | `local_only/p5/ps2_netemu_p5_Q1.elf` | 10,901,288 B | `8dd796e8644b767c9e230cba88bef6c5615f7f15a5d345617be3448385b34427` |
| **Repacked SELF** | `local_only/p5/ps2_netemu_p5_Q1.self` | 2,527,968 B | `f9e8080f08d88cca79629e13cb882c44e58f5d1e77f0535d0fbc60e9d5652afd` |
| **Roundtrip ELF** | `local_only/p5/roundtrip_Q1.elf` | 10,901,288 B | `8dd796e8644b767c9e230cba88bef6c5615f7f15a5d345617be3448385b34427` |

- **Payload Code Size**: 7,416 bytes (0x4800..0x64f8)
- **Code Slot Capacity**: 14,320 bytes (0x4800..0x8000)
- **Slot Utilization**: **51.8%** (6,904 bytes headroom remaining)
- **SELF Encryption / HMAC**: 100% byte-for-byte exact round-trip match verified with `selfdec.py`.

---

## 8. Strict Audits (Provenance & Instruction Checks)

### 8.1 Single Hypercall Instruction Check (`tools/p1a_audit.py`)
- Command: `python tools/p1a_audit.py local_only/stock.elf local_only/p5/ps2_netemu_p5_Q1.elf`
- **Result**: `sc instructions in changed/added executable ranges: [(18520, 0)]`
- Address `18520 = 0x4858` (`lv1_hcall` generic wrapper).
- **Zero other `sc` instructions** present in the payload or modified ranges.

### 8.2 IR Pointer Provenance & Store Bounds Audit
- LLVM IR audit (`netemu_p5/audit_ir.py`):
  - Stack pointer stores (`r1`): Verified safe.
  - Mailbox stores (`0x930F20..0x930F7F`): Verified safe.
  - Heap arena stores (`native_alloc` return): Verified safe.
  - Verified command block stores: Verified safe.
  - **Zero stores at or above `0x930F80`**.

---

## 9. PC Validation Results (`netemu_p5/validate_pc.py`)

Emulated with Ghidra `EmulatorHelper` (JVM limited to `-Xmx3G`, single instance):

| Test # | Test Case Description | Result | Details |
|:---:|---|:---:|---|
| **Syntax** | PowerShell parse-only validation | **PASS** | `install_netemu.ps1`, `restore_netemu.ps1`, `make_log_placeholder.ps1`, `read_netemu_log.ps1` |
| **Regs** | Register preservation (wrapper vs stock) | **PASS** | r8 (6th param), cr2..cr4, LR, r30, r31, r14..r29 100% preserved |
| **Test 1** | Candidate #1 Acceptance (Official Sony Emulator Standard) | **PASS** | Stopped immediately at cand #1, unmapped, freed, closed, clean shutdown, 16 WAL records decoded |
| **Test 2** | Candidate #3 Acceptance (Progression across failures) | **PASS** | Candidates 1 and 2 returned -17, sequence continued, Candidate 3 accepted and stopped |
| **Test 3** | All Candidates Rejected Negative Test (`accept=0`) | **PASS** | All 12 candidates tested cleanly, final failure logged to menu and disk, region freed, device closed |
| **Test 4** | Concurrency Safety (H singleton busy) | **PASS** | 17 records skipped fail-open, count recorded in mailbox `0x930F6C`, 0 unsafe disk writes |
| **Test 5** | UFS Open Failure Fail-Open | **PASS** | Probe runs to completion cleanly if UFS open fails, error recorded in mailbox |
| **Test 6** | Guard Refusal & Swapped Fields | **PASS** | Zero hypercalls issued when buffer pointer guard checks fail |
| **Test 7** | Memory Write Provenance & Store Bounds | **PASS** | Tracked memory write set verifies zero writes outside allowable bounds (`0x930F80..0x931000` untouched) |

