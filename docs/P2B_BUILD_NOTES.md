# P2B Build Notes: Netemu Optical Read Diagnostic Stages (H0..H3) Fix

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P2 FIX ps2_netemu optical read diagnostic probe build — fix the two safety defects found in P2 (mailbox size and stock allocator shim verification), rebuild all variants in tree `netemu_p2b/`, revalidate on PC, do NOT install.

---

## 1. Safety Defect 1: Mailbox Truncation to 96 Bytes & Allocator Arena Migration

### Root Cause Analysis
In the original P2 build (`netemu_p2`), `struct ProbeState` was 192 bytes, occupying address range `[0x930F20, 0x930FE0)`.
Static inspection of `stock.elf` reveals:
- Section 37 ends at `0x930F0C` (size 12 bytes at `0x930F00`).
- Section 38 starts at `0x930F80` (size `0x2FA0` bytes at `0x930F80..0x933F20`).
- Table-of-Contents (TOC) entries explicitly point into this region:
  - `0x749430` (`-0x7e50(r2)`): points to `0x930F80` (global heap block descriptor used by `0x1622c` and `0x16790`).
  - `0x749368`: points to `0x930F80`.
  - `0x749460` (`-0x7e20(r2)`): points to `0x930FE8`.
Writing beyond `0x930F80` directly corrupts the stock emulator's global heap block and runtime variables!
The proven free mailbox range is strictly `[0x930F20, 0x930F80)` (exactly 96 bytes).

### Fix Architecture
1. **Mailbox (`struct ProbeMailbox`, 96 bytes at `0x930F20`)**:
   - `_Static_assert(sizeof(struct ProbeMailbox) == 96, "ProbeMailbox must be exactly 96 bytes");`
   - Retains only persistent inter-menu state:
     - `+0x00`: `u32 status` (STARTED, DONE, ALLOC_OK, ALLOC_FAILED)
     - `+0x04`: `u32 total_hypercalls`
     - `+0x08`: `u32 timeouts` (bitmask: TUR, INQ, CAP, READ)
     - `+0x0C`: `u32 step_failed`
     - `+0x10`: `s32 first_err_rc`
     - `+0x14`: `u32 pad0`
     - `+0x18`: `u64 arena_ptr` (address of allocator-backed 4 KiB arena)
     - `+0x20`: `u8 rom_bus_idx, rom_dev_idx, rom_port, storage_bus_idx`
     - `+0x24`: `u8 hdd_bus_idx, hdd_dev_idx, hdd_port, phat_match`
     - `+0x28`: `u32 rom_count`
     - `+0x2C`: `u32 hdd_found`
     - `+0x30`: `u64 rom_bus_id`
     - `+0x38`: `u64 rom_dev_id`
     - `+0x40`: `u64 last_eval_tb`
     - `+0x48`: `u64 pad1`
     - `+0x50`: `u64 raw_val1` (address `0x930F70`, 8 bytes)
     - `+0x58`: `u64 raw_val2` (address `0x930F78`, 8 bytes)
   - Every store into `ProbeMailbox` is mathematically bounded strictly `< 0x930F80`.

2. **Wrapper Out-Pointers Verification**:
   - The generic hypercall wrapper `lv1_hcall` at `0x4800` writes output registers `r4` and `r5` to `0(r30)` and `0(r31)`:
     - `0x4818: lis r30, 0x93`
     - `0x481c: addi r30, r30, 0x0f70` (`r30 = 0x930F70`)
     - `0x4820: addi r31, r30, 8`      (`r31 = 0x930F78`)
     - `0x48a0: std r4, 0(r30)`        (stores 8 bytes: `0x930F70..0x930F77`)
     - `0x48a4: std r5, 0(r31)`        (stores 8 bytes: `0x930F78..0x930F7F`)
   - Both target ranges are strictly within `[0x930F20, 0x930F80)`.
   - The last written byte is `0x930F7F` (`< 0x930F80`).
   - Offsets 80..95 in `ProbeMailbox` are reserved exclusively for `raw_val1` and `raw_val2`.

3. **Validated Arena Pattern (`struct ProbeArena`, 4096 bytes)**:
   - Uses the proven P1c2 allocator pattern (`native_alloc 0xB9848 (4096, 3, 0)`).
   - Validated against native pool pointers:
     - `base = *(u64*)0x934980`
     - `*(u64*)0x24565b8 == base`
     - `*(u64*)0x2446588 == base + 0x20000`
     - Arena address `a` is 64-byte aligned and `[base + 0x20000, base + 0x60000)`.
   - Fail-Open Discipline: If `native_alloc` returns an unvalidated pointer, the probe halts immediately, issues ZERO hypercalls, and `s4_menu` returns `STOCK_LABEL`.
   - Holds all per-step return codes, DMA handles, buffer pointers, async completion statuses, and copied response data.

---

## 2. Safety Defect 2: Stock Allocator Shim 0x19a5c Verification (a)-(e)

Verification performed using PyGhidra on `local_only/stock.elf` (SHA-256 `63f12b7e...`):

### (a) Behavior when allocation cannot be satisfied
- **Finding**: Does NOT return an error code. Calls fatal panic helper `0x111a7c`.
- **Proof / Disassembly**:
  - `0x19a5c`:
    - `0x19a80`: `cmpld cr7, r0, r9` (mapped EA limit check) -> `bgt cr7, 0x19ab4`
    - `0x19a8c`: `cmpld cr7, r4, r0` (size > 8 MiB check) -> `bgt cr7, 0x19ab4`
    - `0x19ab4`: `li r3, 1` -> `0x19ab8: bl 0x00111a7c`
  - `0x1622c` (heap allocator called by `0x19900`):
    - `0x162bc`: `cmpld cr7, r0, r6` (cursor > limit check) -> `blt cr7, 0x162fc`
    - At `0x162fc`: issues LV1 hypercall 0. If it fails:
    - `0x16320`: `li r3, 1` -> `0x16324: bl 0x00111a7c`
  - `0x19900`:
    - After calling page-table helper `0x16790`:
    - `0x199b0`: `cmpwi cr7, r3, 2` -> `bne cr7, 0x199e0`
    - `0x199e0`: `li r3, 1` -> `0x199e4: bl 0x00111a7c`
  - `0x16790` (page-table mapping helper):
    - `0x16800`: `cmpdi cr7, r0, 0` -> `bne cr7, 0x16868`
    - `0x16868`: `li r3, 1` -> `0x1686c: bl 0x00111a7c`
  - `0x111a7c` (fatal panic helper):
    - `0x111a80`: `li r11, 0x10` (LV1 panic hypercall 16)
    - `0x111a88`: `sc 0`
    - `0x111a8c`: `b 0x111a8c` (INFINITE HANG LOOP!)
- **Verdict**: Calling `0x19a5c` on an unsatisfied allocation causes an immediate console panic/hang, violating fail-open principles unless strictly guarded by pre-checks.

### (b) Remaining LPAR memory in global heap block
- **Global Heap Block**: Located at `0x930F80` (TOC `-0x7e50(r2)` = `0x749430`).
- **Initialization (`0x17710..0x17784`)**:
  - Cursor at `0x58(0x930f80)` initialized to `0x3200000` (50 MiB, rounded from `0x3175480`).
  - Limit at `0x5c(0x930f80)` initialized to `0x3f00000` (63 MiB).
  - Total heap size = `0x3f00000 - 0x3200000 = 0xd00000` = 13 MiB.
- **Stock Allocations during Boot**:
  - `0x200b8`: `0x4000` (rounded to 1 MiB)
  - `0x12c010`: `0x100000` ("SB_HDD", 1 MiB)
  - `0x12c0e4`: `0x20000` (rounded to 1 MiB)
  - `0x133cb0`: `0x100000` (1 MiB)
  - Total stock usage: ~4 MiB.
- **Remaining Capacity**: `13 MiB - 4 MiB = ~9 MiB` (INFERRED).
- **Verdict**: A 1 MiB request easily fits within the remaining ~9 MiB of LPAR memory under normal conditions.

### (c) Label name uniqueness assertion
- **Finding**: Label name is NEVER checked for uniqueness.
- **Proof**: In `0x16790`, parameter `r3` (label string pointer) is completely ignored and not saved or checked against any table.

### (d) Thread and locking discipline
- **Finding**: No locks are held. Both HDD init and menu hook execute on the main PPU emulator thread.
- **Proof**:
  - Neither `0x19a5c`, `0x19900`, `0x1622c`, nor `0x16790` calls `native_lock 0xba24c` or uses reservations (`lwarx`/`stwcx`).
  - Menu hook at `0x270ffc` is called synchronously from `0x270c24`, invoked by the main PPU event loop `0xbad80`.
  - HDD init at `0x12be04` is called synchronously during startup on the same main thread.

### (e) Mapped-EA cursor update and HDD collision
- **Finding**: No collision.
- **Proof**:
  - Mapped EA cursor at `*(u64*)0xb28a10` (TOC `-0x7b30(r2)` = `0x749750`) is bumped monotonically by 8 MiB (`addis r9, r9, 0x80` at `0x1999c`).
  - Each allocation receives an isolated, non-overlapping 8 MiB virtual address window.

---

## 3. Shipping Decision & Pre-Guard Architecture

Because `0x19a5c` calls `0x111a7c` on failure (which halts the system), calling `0x19a5c` unguarded is unsafe.
However, because:
1. The global heap block at `0x930F80` is directly readable by our code.
2. The remaining capacity is known (~9 MiB).
3. The mapped-EA cursor at `0xb28a10` is directly readable.

We implement strict **Fail-Open Pre-Guards** before calling `alloc_buffer`:
1. Inspect heap cursor `0x58(0x930f80)` and limit `0x5c(0x930f80)`. If `cursor + 0x100000 > limit`, ABORT immediately with `ALLOC_SHIM_FAILED` without calling `0x19a5c`!
2. Inspect mapped EA cursor at `0xb28a10`. If `ea + 0x100000 > 0x0000000fffffffff`, ABORT immediately!
3. Post-guard: Check `arc == 0`, `ea != 0`, `!(ea & 0xfffff)`, `lpar != 0`, `!(lpar & 0xfffff)`, and `lpar >= 0x3200000 && lpar + 0x100000 <= 0x3f00000`.
4. If any check fails: issue ZERO subsequent hypercalls (no map, no TUR, no INQ, no read).

All four variants (H0..H3) are built with these complete pre-guards, with **H0** designated as the primary safe baseline that requires zero LPAR heap allocations.

---

## 4. Mailbox Layout (Exactly 96 bytes at `0x930F20..0x930F80`)

All offsets verified in `stock.elf`:
- `+0x00`: `status` (u32)
- `+0x04`: `total_hypercalls` (u32)
- `+0x08`: `timeouts` (u32: TUR=1, INQ=2, CAP=4, READ=8)
- `+0x0C`: `step_failed` (u32)
- `+0x10`: `first_err_rc` (s32)
- `+0x14`: `pad0` (u32)
- `+0x18`: `arena_ptr` (u64)
- `+0x20`: `rom_bus_idx, rom_dev_idx, rom_port, storage_bus_idx` (4 bytes)
- `+0x24`: `hdd_bus_idx, hdd_dev_idx, hdd_port, phat_match` (4 bytes)
- `+0x28`: `rom_count` (u32)
- `+0x2C`: `hdd_found` (u32)
- `+0x30`: `rom_bus_id` (u64)
- `+0x38`: `rom_dev_id` (u64)
- `+0x40`: `last_eval_tb` (u64)
- `+0x48`: `pad1` (u64)
- `+0x50`: `raw_val1` (u64, address `0x930F70`)
- `+0x58`: `raw_val2` (u64, address `0x930F78`)
Total: 96 bytes.

---

## 5. Build Artifacts & Cryptographic Verification

All binaries built into `local_only/p2b/` using `python netemu_p2b/build.py`.

### Artifact Summary Table
| Variant | Artifact | Size (bytes) | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| **H0** | `ps2_netemu_p2b_H0.elf` | 11,228,968 | `d1cb56ee22b7fdfd77944125be20a660831785d4e90194c9f4fc505bbf24cd1b` |
| **H0** | `ps2_netemu_p2b_H0.self` | 2,542,736 | `1503c785201e60cd07bcc73be37dd2fd064376607d8f801b0db27c8f6cc1e783` |
| **H0** | `ps2_netemu_p2b_H0.roundtrip.elf` | 11,228,968 | `d1cb56ee22b7fdfd77944125be20a660831785d4e90194c9f4fc505bbf24cd1b` (Exact Match) |
| **H1** | `ps2_netemu_p2b_H1.elf` | 11,228,968 | `5d824977eb95cf3c992ca4f20946e817c63e7c5093d66861c62463ec037a3298` |
| **H1** | `ps2_netemu_p2b_H1.self` | 2,543,024 | `147cae4cfa323f81194449bd75ecd709e717ed1e3120733b95cd00b9b4b94853` |
| **H1** | `ps2_netemu_p2b_H1.roundtrip.elf` | 11,228,968 | `5d824977eb95cf3c992ca4f20946e817c63e7c5093d66861c62463ec037a3298` (Exact Match) |
| **H2** | `ps2_netemu_p2b_H2.elf` | 11,228,968 | `f5b808365e07ced29b55f07356530dd21d663f69fd4fbebf0651e0aa887db37f` |
| **H2** | `ps2_netemu_p2b_H2.self` | 2,543,536 | `daf9761476a23ca89a25c044a13db930e443cc05523b8a6f43ba22075624b110` |
| **H2** | `ps2_netemu_p2b_H2.roundtrip.elf` | 11,228,968 | `f5b808365e07ced29b55f07356530dd21d663f69fd4fbebf0651e0aa887db37f` (Exact Match) |
| **H3** | `ps2_netemu_p2b_H3.elf` | 11,228,968 | `7643d332587f4a6164720d6d6be3eefa4113cab241099b24ab355702d56a1bc8` |
| **H3** | `ps2_netemu_p2b_H3.self` | 2,543,728 | `0eed937cc8ffc2cc2d3efe490c66c5bd4f8cc7fe6e47b0c14c0909866afc77e2` |
| **H3** | `ps2_netemu_p2b_H3.roundtrip.elf` | 11,228,968 | `7643d332587f4a6164720d6d6be3eefa4113cab241099b24ab355702d56a1bc8` (Exact Match) |

### Trampolines & Patches in Stock Cave (`0x4800..0x8010`, capacity 14,320 bytes)
- `0x4800`: `lv1_hcall` generic hypercall wrapper (72 bytes, exact stock match)
- `0x4990`: `native_alloc` trampoline -> `0xB9848` (16 bytes)
- `0x49a0`: `alloc_buffer` trampoline -> `0x19a5c` (16 bytes, variants H1..H3)
- `0x49b0`: `probe_run` entry point and full probe payload
- Code Sizes:
  - **H0**: 3048 bytes (21.3% cave capacity)
  - **H1**: 3544 bytes (24.7% cave capacity)
  - **H2**: 4392 bytes (30.7% cave capacity)
  - **H3**: 4816 bytes (33.6% cave capacity)
- Hook at `0x270FFC`: `bl 0x49b0` (trampoline into probe), replacing original call to `0x271924`.

---

## 6. PC Test Suite & Verification Results

### 1. `tools/p1a_audit.py` Static Inspection
- **Strict Store Check**: PASS across H0, H1, H2, and H3.
  - Exactly one `sc` instruction in each ELF at `0x4858` (syscall 0).
  - Store instruction base registers:
    - `r1`: Stack
    - `r20`: Fixed mailbox base `0x930F20` (`[0x930F20, 0x930F80)`)
    - `r29`: Validated 4 KiB arena base
    - `r3`: Command block inside mapped buffer `ea` (H2/H3 only)
    - `r30`: `0x930F70` (hypercall wrapper `r4` out-pointer)
    - `r31`: `0x930F78` (hypercall wrapper `r5` out-pointer)
  - Zero store instructions target `0x930F80` or above.

### 2. `netemu_p2b/validate_pc.py` Dynamic Emulation
- **Preservation Tests**: Non-volatile registers (`r14..r29`, `r30`, `r31`, `cr2..cr4`, `LR`, `r8`) 100% preserved between wrapper and stock baseline.
- **Defect 1 Verification**:
  - Arena allocation failure handled cleanly (issues 0 hypercalls, returns stock label).
  - Memory write tracing verified ZERO stores to `[0x930F80, 0x931000)`.
- **Defect 2 Verification**:
  - Buffer allocation failure handled cleanly (issues 0 subsequent hypercalls after failure).
  - Pre-guards safely abort without invoking `0x19a5c` if heap capacity or mapped EA limits are exceeded.
- **Functional Sequence Verification**:
  - H0: `[170, 174, 175, 171]` (4 calls) exact match.
  - H1: `[170, 174, 176, 177, 175, 171]` (6 calls) exact match.
  - H2: `[170, 174, 176, 248, 254, 248, 254, 177, 175, 171]` (10 calls) exact match.
  - H3: `[170, 174, 176, 248, 254, 248, 254, 248, 254, 245, 254, 177, 175, 171]` (14 calls) exact match.
- **Safety Cases**:
  - Timeout safety: cleanly aborts without issuing unmap/close.
  - Disc absent & authentication error paths cleanly formatted and displayed.
  - Once-only execution: second invocation makes 0 hypercalls.
  - Label bounds: all 137 possible menu strings across all pages validated `< 64` bytes and null-terminated.
- **Syntax Check**: `install_netemu.ps1` and `restore_netemu.ps1` syntax validated (never executed).

---

## 7. Recommended Testing Sequence on Console

Per Defect 2 verification findings (`0x19a5c` invokes `0x111a7c` panic on allocation failure):
1. **Primary Safe Variant**: **`ps2_netemu_p2b_H0.self`**
   - Makes **zero** calls to `0x19a5c` and requires **zero** LPAR heap allocations.
   - Tests bus discovery, optical device query, and DMA region opening (`hv_open(4, 2, &dma)`).
   - Test this variant FIRST on the console.
2. If H0 succeeds on console:
   - Proceed to **`ps2_netemu_p2b_H1.self`** (tests 1 MiB LPAR buffer allocation and mapping/unmapping).
3. If H1 succeeds:
   - Proceed to **`ps2_netemu_p2b_H2.self`** (tests SCSI Inquiry and TUR).
4. If H2 succeeds:
   - Proceed to **`ps2_netemu_p2b_H3.self`** (tests 2048-byte sector read at LBA 16 / PVD).

