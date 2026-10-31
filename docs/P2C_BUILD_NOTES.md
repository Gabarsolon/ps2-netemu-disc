# P2C Build Notes: Netemu LPAR Memory Diagnostics & Safe Buffer Strategy

## Status
- **Date**: 2026-11-01
- **Author**: Antigravity
- **Task**: P2C Netemu LPAR memory diagnostics & safe buffer exploration.
- **Context**:
  - P2B Variant H0 ran on console with a genuine PS2 DVD inserted: **PROVEN ALL OK** (`open(4, 2, 0)`, `lv1_allocate_device_dma_region(4, 2, 0x80000, 12, 0)`, `free_dma`, `close` all returned `rc=0`; DMA region ID >= 8; no shutdown).
  - P2B Variant H1 stopped cleanly at the pre-guard (`ALLOC_SHIM rc=RESOURCE_SHORTAGE (-2)`) without calling the crashing stock allocator shim `0x19a5c`.
  - Static estimate of ~9 MiB free heap was incorrect: capacity was 10 MiB (not 13 MiB), and boot allocations consumed ~8 MiB before game startup.
- **Goal**:
  1. Build a zero-hypercall diagnostic probe (`ps2_netemu_p2c.self`) in `netemu_p2c/` using the console-proven P1c2 label pager to read and display on the PS menu:
     - The first 0x80 bytes of the stock global heap block at `0x930F80` (16 x 64-bit hex values).
     - The cursor, limit, and computed free bytes at `0x930F80`.
     - The mapped-EA cursor (`-0x7b30(r2)` -> `*(u64*)0xb28a10`).
     - HDD driver state at `H = 0x241c850` (`H+0x08`, `+10`, `+20` BUF_EA, `+28` LPARBUF, `+30` DMA_RGN, `+38` TAGSTAT, `+40` STATUS, `+48` STATUS).
     - Native allocator pool descriptors (`0x934980`, `0x24565b8`, `0x2446588`) and the returned EA arena pointer from `0xB9848`.
     - Runtime TOC register `r2` and resolved TOC addresses.
  2. Perform rigorous static analysis of `stock.elf` via PyGhidra:
     - Re-derive heap block layout (`0x17710`, `0x1622c`, `0x19a5c`, `0x16790`).
     - Rank all alternative buffer strategies and recommend the safest path.

---

## 1. Static Analysis: Why the Pre-Guard Fired

### 1.1 Heap Block Layout & Capacity Derivation
Stock initialization at `0x17710` sets up the global heap descriptor at `0x930F80`:
- `0x930F80 + 0x00`: `0x0000000003200000` (Base LPAR address = 50 MiB)
- `0x930F80 + 0x08`: `0x0000000003C00000` (Limit LPAR address = 60 MiB)
- `0x930F80 + 0x10`: `0x0000000000A00000` (Total Capacity = **10 MiB**, NOT 13 MiB!)
- `0x930F80 + 0x58`: `u32` Allocation Cursor (initialized to `0x03200000`)
- `0x930F80 + 0x5c`: `u32` Allocation Limit (initialized to `0x03C00000`)

### 1.2 Heap Allocator Shim (`0x1622c`) & Panic Path
`0x1622c` is called by `0x19a5c` ("SB_OPT", 1 MiB):
```c
// 0x1622c excerpt:
cursor = *(u32 *)(0x930F80 + 0x58);
limit  = *(u32 *)(0x930F80 + 0x5c);
new_cursor = align_up(cursor, 1 << align_log2) + size;
if (new_cursor > limit) {
    // Mode r7 == 0 (fixed partition):
    branch_to_panic_0x111a7c(); // FREEZES CONSOLE
}
```
If `new_cursor > limit`, `0x1622c` unconditionally branches to panic routine `0x111a7c`, locking up the PS3! The P2B pre-guard prevented this fatal panic.

### 1.3 Fixed Boot Allocations Consuming the 10 MiB Heap
Static analysis of all callers to `0x1622c` and `0x19a5c` reveals fixed boot allocations:
1. `0x200b8`: 16 KiB (aligned to 1 MiB boundary = 1 MiB consumed)
2. `0x20324`: 2 MiB
3. `0x27c10c`: 2 MiB
4. `0x12c010`: 1 MiB ("SB_HDD", HDD DMA buffer)
5. `0x12c0e4`: 128 KiB (aligned to 1 MiB = 1 MiB consumed)
6. `0x133cb0`: 1 MiB ("SB_OPT" optical buffer in normal boot paths)
**Total fixed boot allocations = 8 MiB** out of 10 MiB capacity!
The remaining 2 MiB is subject to runtime dynamic allocations by the PS2 emulation core (EE/GS state, page tables, SIF buffers). When an active PS2 game ISO is running, available free heap drops strictly **below 1 MiB**.

---

## 2. Buffer Strategies Evaluation & Ranking

The goal is to obtain a physically backed buffer of 4 KiB..64 KiB with a known LPAR address for `lv1_map_device_dma_region(4, 2, lpar_buf, 1, 0x80000, 0xe000000000000800)`.

| Strategy | Description | Pros | Cons / Hazards | Safety Rank |
| :--- | :--- | :--- | :--- | :---: |
| **Strategy 1: Direct `0x1622c` (64 KiB)** | Call `0x1622c(16, 0x10000, 0)` directly bypassing the 1 MiB shim. | Native heap chunk. | (1) Fails if remaining heap is < 64 KiB. (2) Mutates `0x58(0x930f80)`, violating the store rule. (3) Panics at `0x111a7c` on failure. | **Rank 3 (High Risk)** |
| **Strategy 2: HDD 1 MiB Buffer Reuse (`H+20` / `H+28`)** | Reuse stock 1 MiB HDD buffer at `H = 0x241C850` (`H+20` EA, `H+28` LPAR). | 100% physically backed, 1 MiB size, already DMA mapped. | (1) On console P2B H0 run: `rom_count = 1, hdd_found = 0` (HDD is not present/mounted on dev 3!). `H+28` may be NULL. (2) Taking mutex at `H+00` is fragile. | **Rank 2 (Medium)** |
| **Strategy 3: Cobra Payload Area (`0x3940..0x46B0`)** | Use unused padding in code segment. | Zero heap impact. | Resides in executable text segment; not mapped in guest HPT as writable RAM; physical LPAR address cannot be registered for LV1 DMA. | **Rank 4 (Unviable)** |
| **Strategy 4: Native Allocator Pool (`0xB9848`)** | Allocate 4 KiB..64 KiB via `0xB9848(size, 3, 0)`. | Proven safe in P1C2/P2B; never touches heap block `0x930F80`; never panics. | Returns EA pointer (`0x80020000`); LPAR address must be derived from page table mapping `0x16790`. | **Rank 1 (Best Potential)** |

### Recommendation
**Ship the diagnostic build `ps2_netemu_p2c.self` FIRST.**
Before building K1..K3, we must observe the real live numbers from hardware:
- Exact free heap bytes (`limit - cursor`).
- Whether `H+28` (HDD LPAR buffer) is valid (`!= 0`) or NULL on the owner's PS3.
- The exact EA value returned by `0xB9848` and the pool base descriptors (`0x934980`, `0x24565b8`, `0x2446588`).
Once live values are observed from the 4 menu pages, the optimal strategy can be implemented with zero guesswork.

---

## 3. Diagnostic Probe Architecture (`ps2_netemu_p2c`)

### 3.1 Zero-Hypercall Discipline
The diagnostic build contains **EXACTLY ZERO hypercalls**:
- Zero `sc` instructions in code cave (`tools/p1a_audit.py` confirmed `sc_list: []`).
- No optical device open/close.
- No storage hypercalls.
- LOADS ONLY from verified stock data structures.

### 3.2 Label Pager Catalog (36 Items across 4 Opens)
Evaluated once per row (rows 0..8) with timebase gap detection (>1.5s = 119,700,000 cycles at 79.8 MHz via `native_clock 0xB9CD0`):

- **Open 0 (Items 00..08): Heap Block Offsets 0x00..0x40**
  - Item 00 (Row 0): `P2C H+00: <u64>` (Stock Heap Base)
  - Item 01 (Row 1): `P2C H+08: <u64>` (Stock Heap Limit)
  - Item 02 (Row 2): `P2C H+10: <u64>` (Stock Heap Capacity)
  - Item 03 (Row 3): `P2C H+18: <u64>`
  - Item 04 (Row 4): `P2C H+20: <u64>`
  - Item 05 (Row 5): `P2C H+28: <u64>`
  - Item 06 (Row 6): `P2C H+30: <u64>`
  - Item 07 (Row 7): `P2C H+38: <u64>`
  - Item 08 (Row 8): `P2C H+40: <u64>`

- **Open 1 (Items 09..17): Heap Block Offsets 0x48..0x78 & Free Bytes**
  - Item 09 (Row 0): `P2C H+48: <u64>`
  - Item 10 (Row 1): `P2C H+50: <u64>`
  - Item 11 (Row 2): `P2C H+58: <u64>` (Raw 64-bit cursor/limit word)
  - Item 12 (Row 3): `P2C H+60: <u64>`
  - Item 13 (Row 4): `P2C H+68: <u64>`
  - Item 14 (Row 5): `P2C H+70: <u64>`
  - Item 15 (Row 6): `P2C H+78: <u64>`
  - Item 16 (Row 7): `HEAP CUR=0x<u32> LIM=0x<u32>`
  - Item 17 (Row 8): `HEAP FREE=0x<u32> (<dec> KB)`

- **Open 2 (Items 18..26): Mapped EA Cursor & HDD Driver State**
  - Item 18 (Row 0): `MAPPED_EA 0xB28A10=<u64>`
  - Item 19 (Row 1): `H+08 BUS/DEV  =<u64>`
  - Item 20 (Row 2): `H+10 DEV_ID   =<u64>`
  - Item 21 (Row 3): `H+20 BUF_EA   =<u64>`
  - Item 22 (Row 4): `H+28 LPARBUF  =<u64>`
  - Item 23 (Row 5): `H+30 DMA_RGN  =<u64>`
  - Item 24 (Row 6): `H+38 TAGSTAT  =<u64>`
  - Item 25 (Row 7): `H+40 STATUS   =<u64>`
  - Item 26 (Row 8): `H+48 STATUS   =<u64>`

- **Open 3 (Items 27..35): Pools, Arena EA, TOC, and Summary**
  - Item 27 (Row 0): `POOL 934980   =<u64>`
  - Item 28 (Row 1): `POOL 24565B8  =<u64>`
  - Item 29 (Row 2): `POOL 2446588  =<u64>`
  - Item 30 (Row 3): `ARENA 0xB9848 =<u64>`
  - Item 31 (Row 4): `RUNTIME TOC r2=<u64>`
  - Item 32 (Row 5): `TOC -7B30 ADDR=<u64>`
  - Item 33 (Row 6): `TOC -7E50 ADDR=<u64>`
  - Item 34 (Row 7): `TOC -6F58 ADDR=<u64>`
  - Item 35 (Row 8): `P2C DIAG OK HC=0 OPENS=<u32>`

---

## 4. Build Artifacts & Cryptographic Hashes

- **ELF Output**: `local_only/p2c/ps2_netemu_p2c.elf`
  - Size: `10,901,288` bytes
  - SHA-256: `77caef8b9de4cdc8508f4e8f443e5affc3123aaf578447ad2e5b5d612f0fd51c`
- **SELF Output**: `local_only/p2c/ps2_netemu_p2c.self`
  - Size: `2,525,808` bytes
  - SHA-256: `32a346ba9c1fc73eab6ab36851542ad3d4ad0edc7acde1c9bda1ceed46bca07b`
- **Decrypted Roundtrip ELF**: `local_only/p2c/roundtrip_p2c.elf`
  - Byte-for-byte identical to patched ELF (`selfdec_roundtrip_exact: true`).
- **Code Cave Usage**:
  - Size: `3,448` bytes / `14,320` bytes capacity (**24.1%**).

---

## 5. PC Validation Results

- **Strict Store Audit (`tools/p1a_audit.py`)**:
  - `sc instructions in changed/added executable ranges`: `[]` (0 `sc` instructions).
  - Store bases strictly in: `r1` (stack), `r3/r4/r5/r8` (string/arena pointers), `r27` (mailbox), `r29` (arena).
- **PyGhidra Emulation**:
  - 4 Open cycles emulated with timebase gap detection (>1.5s).
  - All 36 items verified for accurate string formatting and hex values.
  - Pager wrap-around tested (Open 4 cleanly wraps to Items 0..8).
  - Memory write tracking: strictly stack, mailbox 96 bytes, arena. ZERO writes to `[0x930F80, 0x931000)`.
  - Fail-open tested: allocator returning 0 cleanly yields stock label `Debug Information` (`0x304EC0`).
- **Installer Script Parse Check**:
  - `tools/install_netemu.ps1`: Syntax OK.
  - `tools/restore_netemu.ps1`: Syntax OK.
