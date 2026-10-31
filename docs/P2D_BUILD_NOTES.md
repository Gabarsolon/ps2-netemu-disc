# P2D Build Notes: Allocator Reverse Engineering & Optical DMA Buffer Strategy

## Status
- **Date**: 2026-11-01
- **Author**: Antigravity
- **Task**: P2D Netemu LPAR memory diagnostics, allocator re-decoding, and optical DMA buffer resolution.
- **Ground Truth**:
  - Console results from `ps2_netemu_p2c.self` verified via owner video (`docs/P2C_RESULT.md`):
    - `0x930F80`: All 16 words read `0x0` (all zero).
    - `HEAP CUR / LIM / FREE`: `0x0` / `0x0` / `0 KB` $\rightarrow$ The P2B pre-guard check `cursor + size > limit` was evaluating `0 + 0x100000 > 0`, firing as a false positive! The stock heap was NOT exhausted; the descriptor location/dereference was misunderstood.
    - HDD driver state $H = \text{0x241c850}$ is **LIVE and IDLE**:
      - `H+08`: Bus 4
      - `H+10`: Dev ID 3
      - `H+20`: LPAR base `0x0000500002d00000` (allocated by LV1 hypercall 0)
      - `H+28`: CPU EA `0x0000000084800000` (constructed as `0x80000000 | cursor`)
      - `H+30`: DMA_RGN `0x00000000d0000000` (from LV1 hypercall 174)
      - `H+38 / +40 / +48`: `0` (Idle)
    - Mapped-EA cursor variable at `0xB28A10`: `0x0000000006000000` (96 MiB = 12 $\times$ 8 MiB allocations).
    - Allocator pool descriptors: `0x934980` $\rightarrow$ `0x80000000`, `0x24565B8` $\rightarrow$ `0x80000000`, `0x2446588` $\rightarrow$ `0x80020000`.
    - Native allocator `0xB9848` returned arena at EA `0x8003e140`.
    - Runtime TOC `r2` = `0x751280`. TOC slots: `-7B30` = `0x749750`, `-7E50` = `0x749430`, `-6F58` = `0x74a328`.
    - P2C Pager worked cleanly on console: `P2C DIAG OK HC=0 OPENS=0007`.

---

## 1. Part 1 Findings & Static Reverse Engineering

### 1(a). Real Allocator & Heap State
1. **Why `0x930F80` Read All Zero on Console**:
   - `0x930F80` is in Section 38 (`0x930f80..0x933f20`), which is zero-initialized BSS.
   - At early startup (`0x11de0..0x11df0`), the CRT explicitly zeroes all memory from `0x930f80` to `0x933f80`.
   - Function `0x17324`, which contains code to write partition parameters into `0x930f80`, has **zero callers** and is dead code in `stock.elf`.
   - Therefore, `0x930f80` remains permanently `0x0` across all words at runtime.
2. **How `0x1622c` Behaves When `0x930f80` is Zero**:
   - `0x1622c` loads `cursor = lwz 0x58(0x930f80)` (0) and `limit = lwz 0x5c(0x930f80)` (0).
   - The test `new_cursor <= limit` evaluates `0 + size <= 0`, which is FALSE (`blt cr7, 0x162fc`).
   - It falls through to `0x16300`, which directly invokes **LV1 Hypercall 0 (`lv1_allocate_memory`)**!
   - `lv1_allocate_memory` allocates physical LPAR memory from the PS3 hypervisor and returns the physical LPAR address in `r4`.
   - `0x1622c` stores this allocated LPAR address into `*p_lpar` (`std r4, 0(r29)` at `0x1632c`).
3. **The Real Mapped-EA Cursor (`0xB28A10`)**:
   - The variable that tracks mapped effective addresses is at `0xB28A10` (pointed to by TOC slot `-0x7b30(r2)` = `0x749750`).
   - On each call to `0x19900`, `0x1999c` executes `addis r9, r9, 0x80`, advancing `*(u64*)0xB28A10` by **8 MiB (`0x800000`)**.
   - On the console, `*(u64*)0xB28A10` held `0x6000000` (96 MiB = 12 allocations).
4. **The Four Stock Boot Allocations via `0x19a5c`**:
   - `0x200b8`: `SB_SIO2` (Serial I/O 2, 16 KiB $\rightarrow$ rounded to 1 MiB)
   - `0x12c010`: `SB_HDD` (HDD driver state $H = \text{0x241c850}$, 1 MiB)
   - `0x12c0e4`: `SB_IOP_HDD` (IOP HDD cache, 128 KiB $\rightarrow$ rounded to 1 MiB)
   - `0x133cb0`: `SB_CDVD` (Optical CDVD driver state `0x2456fe0`, 1 MiB)

---

### 1(b). Page-Table Mapping Helper `0x16790` & EA $\rightarrow$ LPAR Mapping
1. **Hardware HTAB Mapping (Zero Software Table)**:
   - `0x16790` computes the PTEG index from the virtual address (`srd` + `xor` + `and`).
   - It queries the hardware page table via **LV1 Hypercall 95 (`lv1_read_htab_entries`)**.
   - It searches for an unused PTE slot in the PTEG.
   - It writes the mapping directly via **LV1 Hypercall 1 (`lv1_write_htab_entry`)**.
   - **Conclusion**: `0x16790` does **NOT** maintain an in-memory software table of `(ea, lpar, size)`. It only updates internal statistics counters.
2. **EA vs LPAR Address Inversion Discovered**:
   - In P2C notes: `H+20` was labeled `BUF_EA` (`0x500002d00000`) and `H+28` was labeled `LPARBUF` (`0x84800000`).
   - Detailed disassembly of `0x19900` proves that **`H+20` is the physical LPAR address** returned by `lv1_allocate_memory` (hypercall 0), and **`H+28` is the CPU EA** (`0x80000000 | cursor = 0x84800000`)!
   - `0x16790` maps CPU EA `0x74800000` / `0x84800000` to physical LPAR `0x500002d00000`.

---

### 1(c). HDD Buffer Analysis
1. `SB_HDD` allocated 1 MiB (`0x100000`) physical LPAR memory at `H+20` (`0x500002d00000`).
2. The HDD driver calls `lv1_allocate_device_dma_region(bus=4, dev=3, size=0x80000)` $\rightarrow$ region `0xd0000000` (`H+30`).
3. The HDD driver maps only **512 KiB (`0x80000`)** via `lv1_map_device_dma_region`.
4. The HDD cache consists of 1024 sectors $\times$ 512 bytes = 512 KiB (`0x80000`).
5. The upper 512 KiB (`[LPAR + 0x80000, LPAR + 0x100000)`) is provably not mapped to DMA and not used by the HDD driver.
6. However, per project rules, sharing buffer space with the HDD driver is avoided.

---

### 1(d). Optical DMA Buffer Recommendation: `SB_CDVD`
1. **The Discovered Buffer: `SB_CDVD` (`0x2456fe0`)**:
   - Stock netemu executes `0x133c80` at boot (`0x18cbc`), allocating 1 MiB (`0x100000`) specifically for CDVD emulation:
     - LPAR address stored at `0x2458438` (`0x2456fe0 + 0x1458`).
     - CPU EA stored at `0x2458428` (`0x2456fe0 + 0x1448`).
     - Buffer size stored at `0x2458430` (`0x100000` = 1 MiB).
   - **Status**: **PROVEN**. Called unconditionally at `0x18cbc` before HDD init (`0x18cc4`).
   - **Safety Ranking**: **Rank 1 (Safest)**.
     - Already allocated by stock netemu at boot $\rightarrow$ no hypercall 0 needed.
     - Completely independent of HDD driver $\rightarrow$ zero collision risk.
     - Already mapped into CPU page tables $\rightarrow$ CPU can immediately read sectors from EA.
     - 1 MiB capacity provides ample space for 512 KiB DMA region mapping.
2. **Safety Guard**:
   - The pre-guard reads `0x2458438` (LPAR) and `0x2458428` (EA).
   - If `!cdvd_lpar || (cdvd_lpar & 0xFFF) || cdvd_sz < 0x80000`, the payload aborts safely without issuing hypercalls.

---

## 2. Part 2 Plan: Variants K0..K3 in `netemu_p2d/`

| Variant | Purpose | Operations |
|---|---|---|
| **K0** | Baseline Verification | `open(4, 2)` $\rightarrow$ `alloc_dma_region(0x80000)` $\rightarrow$ `free_dma_region` $\rightarrow$ `close(4, 2)`. Reads & displays `cdvd_lpar` and `cdvd_ea`. |
| **K1** | DMA Mapping Test | K0 + read `cdvd_lpar` + `map_device_dma_region(4, 2, dma_rgn, cdvd_lpar, 0x80000, 0xe000000000000800ULL)` $\rightarrow$ `unmap` $\rightarrow$ `free` $\rightarrow$ `close`. |
| **K2** | ATAPI Polling Test | K1 + `TEST UNIT READY` (opcode 0x00) + `INQUIRY` (opcode 0x12, 36 bytes) with bounded poll loop (200k iter / 2s tb). |
| **K3** | Sector 16 Read | K2 + `READ CAPACITY(10)` (opcode 0x25) + `READ(10)` sector 16 (opcode 0x28, 1 sector = 2048 bytes). Verifies ISO primary volume descriptor (`CD001`). |

---

## 4. Build Results & Cryptographic Hashes

All 4 variants were compiled with Clang (PowerPC 64-bit target), injected into the code slot at `0x4800` (hook at `0x270FFC`), packaged into patched ELFs, and signed as NPDRM retail SELFs with `make_fself`. Every SELF was decrypted back to ELF with `scetool` and verified byte-for-byte identical against the input ELF.

| Variant | ELF SHA-256 | SELF SHA-256 | Code Size | Capacity |
|---|---|---|---|---|
| **K0** | `bfc6c058de405d31df63edb40be705c07f96a3f5b2d97e01d7c08457ca7fda26` | `4f415a93c966846da551419c5b9d31903339ba6f60dc419846c4e79433eaade2` | 8,744 B | 61.1% |
| **K1** | `0c5e241fdaaa35a4a9a56a07e3d10128f1b6474787aa52002d8b739667efb53d` | `0e086c9629d984cb39d3c1dc9135d0db7f21514fce5abcd587330bbc24d6ae89` | 9,344 B | 65.3% |
| **K2** | `d1c1e50d9382ee2e1a5094065bf80cdcace6313e5f4e59c73d45dd10e01060dd` | `890367ef8c8f90a4f732f21a9c290ece41ba9199c82e6be085b9d38e17f9c28f` | 10,728 B | 74.9% |
| **K3** | `112e023a332c4dde7a408a2bc27c65a43f0c300e3f2e4a6c8604202b0e02b54f` | `234cc78220ca6181cdda158e3f9ba77b292dc853f00f4ec9c6a41e7f61c4cc77` | 12,032 B | 84.0% |

All binaries reside in `local_only/p2d/`:
- `local_only/p2d/ps2_netemu_p2d_K0.self`
- `local_only/p2d/ps2_netemu_p2d_K1.self`
- `local_only/p2d/ps2_netemu_p2d_K2.self`
- `local_only/p2d/ps2_netemu_p2d_K3.self`

---

## 5. Security & Static Audits

### 5(a). Instruction & System Call Audit (`tools/p1a_audit.py`)
`tools/p1a_audit.py` checks for strict compliance with P1A/P2 safety rules:
- **`sc` instructions**: Exactly ONE system call (`sc 0` at `0x4858`) allowed in changed executable code below `0x300000`.
- **String pattern sanitization**: Checked to ensure no ASCII string data bit-matches `(w & 0xFC000003) == 0x44000002`.
- **Audit Results**:
  - `ps2_netemu_p2d_K0.elf`: **PASS** — Exactly 1 `sc` (`0x4858`), 2 diff ranges, hook at `0x270ffc`.
  - `ps2_netemu_p2d_K1.elf`: **PASS** — Exactly 1 `sc` (`0x4858`), 2 diff ranges, hook at `0x270ffc`.
  - `ps2_netemu_p2d_K2.elf`: **PASS** — Exactly 1 `sc` (`0x4858`), 2 diff ranges, hook at `0x270ffc`.
  - `ps2_netemu_p2d_K3.elf`: **PASS** — Exactly 1 `sc` (`0x4858`), 2 diff ranges, hook at `0x270ffc`.

### 5(b). Pointer Provenance Audit (`audit_ir.py`)
`audit_ir.py` parses LLVM IR emitted during compilation of each variant and checks every `store` instruction:
- Destination pointer must originate strictly from:
  1. Mailbox address space `[0x930F20, 0x930F80)`.
  2. Dynamically allocated arena `arena->row_strings[9][64]`.
  3. Local stack allocations (`alloca`).
  4. Verified CDVD command block pointer.
- **Audit Results**:
  - `K0`: 178 stores analyzed — **ALL DESTINATIONS PROVEN SAFE**.
  - `K1`: 183 stores analyzed — **ALL DESTINATIONS PROVEN SAFE**.
  - `K2`: 208 stores analyzed — **ALL DESTINATIONS PROVEN SAFE**.
  - `K3`: 245 stores analyzed — **ALL DESTINATIONS PROVEN SAFE**.
- **Defect 1 Prevention**: Zero stores write at or above `0x930F80`.

---

## 6. PC Emulation Validation Results (`validate_pc.py`)

Headless PyGhidra emulation (`validate_pc.py`, single JVM, `-Xmx3G`) verified the behavior of all four variants across 5 rigorous test categories:

1. **Exact Hypercall Sequence Verification**:
   - **K0**: `[170, 174, 175, 171]` (open, alloc_dma, free_dma, close) $\rightarrow$ **PASS**.
   - **K1**: `[170, 174, 176, 177, 175, 171]` (open, alloc_dma, map_dma, unmap_dma, free_dma, close). Verified `176` maps `0x0000500002f00000` (`cdvd_lpar`) $\rightarrow$ **PASS**.
   - **K2**: `[170, 174, 176, 248, 254, 248, 254, 177, 175, 171]` (open, alloc, map, TUR send, TUR poll, INQ send, INQ poll, unmap, free, close) $\rightarrow$ **PASS**.
   - **K3**: `[170, 174, 176, 248, 254, 248, 254, 248, 254, 245, 254, 177, 175, 171]` (open, alloc, map, TUR, INQ, CAP, READ sec 16, unmap, free, close) $\rightarrow$ **PASS**.
2. **Defect 1 Memory Bounds Assertion**:
   - Memory range `[0x930F80, 0x931000)` verified unmodified (`post_heap == bytes(128)`) for all variants $\rightarrow$ **PASS**.
   - Mailbox done bit (`status & 2`) verified set for all variants $\rightarrow$ **PASS**.
3. **Timeout Abort Safety (K2 and K3)**:
   - Simulated device hanging (EBUSY past 2,000,000 timebase ticks).
   - Sequence halted at `[170, 174, 176, 248, 254]` with `P2D-K2/K3 TIMEOUT AT STEP=5 (ABORTED)`.
   - Verified that `177` (unmap), `175` (free), and `171` (close) were **NEVER CALLED** $\rightarrow$ **PASS**.
4. **SB_CDVD Buffer Guard Failure Safety (K1, K2, K3)**:
   - Simulated corrupt/missing CDVD buffer state (`cdvd_lpar == 0`).
   - Verified that **ZERO hypercalls were issued** and payload aborted gracefully $\rightarrow$ **PASS**.
5. **Arena Allocation Fail-Open Safety**:
   - Simulated `native_alloc` returning `0x0` (out-of-memory).
   - Verified that menu returns `STOCK_LABEL` (`0x304EC0`) with **ZERO hypercalls issued** $\rightarrow$ **PASS**.
6. **Register Preservation Audit**:
   - Verified that the generic wrapper `lv1_hcall` at `0x4800` preserves 100% of stock registers:
     - Volatile: `r8` (passed as 6th param), `LR`.
     - Condition Register fields: `cr2..cr4`.
     - Non-volatile: `r14..r31`, specifically `r30` and `r31` $\rightarrow$ **100% PRESERVED**.
7. **Installer Script Parse Check**:
   - `install_netemu.ps1` and `restore_netemu.ps1` validated using `[System.Management.Automation.Language.Parser]::ParseFile` without execution $\rightarrow$ **PASS** (zero syntax errors).
