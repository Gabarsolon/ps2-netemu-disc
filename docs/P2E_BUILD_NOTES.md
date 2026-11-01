# P2E Build Notes: Defect Fix for Buffer EA vs LPAR Swap & Pointer Kind Audit

## Status
- **Date**: 2026-11-01
- **Task**: P2E Defect Fix in P2D build.
- **Trigger**:
  - Console test of K0 on PS3 (`docs/P2D_K0_RESULT.md`):
    - K0 executed cleanly (`P2D-K0 DONE: ALL STEPS OK`, `RC: OP=0 DMA=0 CL=0 HC=130`).
    - Printed values:
      - At `0x2458438`: `0x0000500002c00000`
      - At `0x2458428`: `0x0000000084000000`
      - At `0x2458430`: `0x0000000000100000` (1 MiB)
    - Comparison with measured HDD state (`docs/P2C_RESULT.md`):
      - `H+0x20`: `0x0000500002d00000` (CPU Effective Address)
      - `H+0x28`: `0x0000000084800000` (LPAR physical address)
  - **Defect Identified**:
    - The two fields at `0x2458438` and `0x2458428` are SWAPPED relative to P2D's naming!
    - `0x0000500002c00000` is the CPU Effective Address (EA).
    - `0x0000000084000000` is the physical LPAR address.
    - In P2D `probe.c`, `lpar` was loaded from `0x2458438` and `ea` from `0x2458428`. If K1..K3 ran, it would pass an EA to `lv1_map_device_dma_region` (LV1 176) and attempt to write ATAPI command blocks through `0x84000000` (unmapped in CPU HTAB), causing a fatal crash/fault!
    - K0 was unaffected because K0 does not map the buffer or write ATAPI blocks.

---

## 1. Static Reverse Engineering: Root Cause of Address Inversion

### Stock ELF Analysis (`stock.elf`)
1. **Allocator Shim Function (`0x19a5c`) and Backend (`0x19900`)**:
   - Signature: `int allocate_driver_buffer(const char *name, u64 size, u64 *p_ea, u64 *p_lpar)`
   - In `0x19a5c`:
     - `r3` = name string
     - `r4` = size
     - `r5` = `p_ea` (moved to `r7`)
     - `r6` = `p_lpar` (moved to `r8`)
     - Jumps to `0x19900`.
   - In `0x19900`:
     - Line `0x19934: or r27, r7, r7` (`r27 = p_ea`)
     - Line `0x19938: or r26, r8, r8` (`r26 = p_lpar`)
     - Line `0x19954: or r6, r7, r7` -> passes `r6 = p_ea` to `0x1622c` (`lv1_allocate_memory`)
     - Line `0x162c4: std r3, 0x0(r29)` / `0x1632c: std r4, 0x0(r29)` -> `0x1622c` writes the allocated CPU Effective Address (`0x500002xx0000`) into `*p_ea`!
     - Line `0x19984: ld r4, 0x0(r11)` -> loads partition offset cursor from TOC `-0x7b30(r2)` (e.g. `0x04000000`)
     - Line `0x1998c: or r0, r30, r4` -> combines with `0x80000000` to form physical LPAR address `0x84000000`
     - Line `0x19994: std r0, 0x0(r26)` -> **stores LPAR address `0x84000000` into `*p_lpar` (`*r26`)!**
     - Line `0x199a8: bl 0x16790` -> calls page-table insertion routine (`lv1_write_htab_entry`, LV1 95 / `0x5f`) to map the EA (`0x500002xx0000`) to the LPAR (`0x84xx0000`) in the CPU's hardware hash table!

2. **CDVD Driver State Allocation Call Site (`0x133c80`)**:
   - `0x133cb0: bl 0x19a5c`
   - Parameters passed:
     - `r3` = string `"sb_cdvd"`
     - `r4` = `0x100000` (1 MiB)
     - `r5` = `0x2458438` (`0x2456fe0 + 0x1458`) = `&p_ea`
     - `r6` = `0x2458428` (`0x2456fe0 + 0x1448`) = `&p_lpar`
   - **Conclusion**:
     - At offset `+0x1448` (`0x2458428`): stores **LPAR** address (`0x84000000`).
     - At offset `+0x1450` (`0x2458430`): stores **Buffer Size** (`0x100000`).
     - At offset `+0x1458` (`0x2458438`): stores **CPU Effective Address (EA)** (`0x500002c00000`).

3. **HDD Driver State Allocation Call Site (`0x12c010`)**:
   - `r30` = pointer to HDD driver state struct `H` (`0x241c850`)
   - `0x12bffc: addi r5, r30, 0x20` -> `arg3` = `&H[0x20]` (`p_ea`)
   - `0x12c000: addi r6, r1, 0x80` -> `arg4` = `&stack[0x80]` (`p_lpar`)
   - `0x12c008: lis r4, 0x10` -> size = 1 MiB (`0x100000`)
   - `0x12c010: bl 0x19a5c`
   - `0x12c018: ld r0, 0x80(r1)` -> loads `p_lpar` result from stack
   - `0x12c028: std r0, 0x28(r30)` -> stores into `H[0x28]` (`p_lpar`)
   - **Conclusion**:
     - At `H+0x20`: stores **CPU Effective Address (EA)** (`0x500002d00000`).
     - At `H+0x28`: stores **LPAR** address (`0x84800000`).
     - Earlier note in P0 that "H+0x20 was LPAR and H+0x28 was EA" was an inversion made during quick inspection without verifying `0x19900` instruction stores. Console measurement in P2C and static disassembly now match 100%.

---

## 2. Address-Kind Audit & Decision Table

Every pointer and address kind used across P2E is classified below with exact evidence:

| Interface / Field | Parameter Name | Address Kind | Expected Value | Evidence / Reference |
|---|---|---|---|---|
| `lv1_map_device_dma_region` (LV1 176) | `lpar_addr` | **LPAR** (Physical) | `0x0000000084000000` | Stock helper `0x160fc` checks `r5 < 0x3fffffff`, passes directly to `sc 0x0` (LV1 176). Must be physical LPAR address. |
| `lv1_allocate_device_dma_region` (LV1 174) | returns `dma_region` | **DMA Region ID** | `0x0000000000000008` (CDVD) | Returned by LV1 174 into `r4`, passed to LV1 176 and LV1 175. |
| ATAPI Command Block CPU Access | pointer | **CPU EA** | `0x0000500002c00000` | Written by PowerPC CPU store instructions (`std`, `stw`, `stb`). Writing to unmapped LPAR `0x84000000` causes MMU Data Storage Interrupt (DSI crash). |
| `lv1_storage_send_device_command` (LV1 248) | `cmnd_block_lpar` | **LPAR** (Physical) | `0x0000000084000000` | LV1 hypervisor DMA engine reads command block from physical partition memory. |
| ATAPI Command Block `+0x38` | `buffer` | **LPAR** (Physical) | `0x0000000084001000` | Linux kernel `drivers/scsi/ps3rom.c` line 124 / `ps3stor_lib.c`: `cmd.buffer = bounce_lpar`. Hypervisor translates LPAR through DMA region mapping. |
| `lv1_storage_send_device_command` (LV1 248) | `data_lpar` | **LPAR** (Physical) | `0x0000000084001000` | Passed as parameter 6 to LV1 248. |
| `lv1_storage_read` (LV1 245) | `buf_lpar` | **LPAR** (Physical) | `0x0000000084001000` | Stock HDD driver `0x12b674` passes `r8 = r26` (which holds LPAR address loaded from `slot+0x20` / `0xe0(r21)`). |
| CPU INQUIRY / Sector Read | pointer | **CPU EA** | `0x0000500002c01000` | CPU reads returned data directly (`data_ea[i]`). Must be mapped Effective Address. |
| `lv1_unmap_device_dma_region` (LV1 177) | `dma_region` | **DMA Region ID** | `0x0000000000000008` | Takes `dma_region` handle returned by LV1 174. |
| `lv1_free_device_dma_region` (LV1 175) | `dma_region` | **DMA Region ID** | `0x0000000000000008` | Takes `dma_region` handle returned by LV1 174. |
| `lv1_close_device` (LV1 171) | `dev_bus`, `dev_id` | **Device IDs** | `bus=4`, `dev=2` | Closes device handle. |

---

## 3. Runtime Sanity Guard Specification

The guard `check_cdvd_buffer_guard` in `netemu_p2e/src/probe.c` does NOT rely on naming or assumptions. It strictly validates both values loaded from memory:

- `raw_lpar = *(const volatile u64 *)0x2458428ULL` (Offset `+0x1448`)
- `raw_ea   = *(const volatile u64 *)0x2458438ULL` (Offset `+0x1458`)
- `raw_sz   = *(const volatile u64 *)0x2458430ULL` (Offset `+0x1450`)

### Guard Rules:
1. **LPAR Sanity**:
   - `raw_lpar < 0x1_0000_0000ULL` (strictly 32-bit partition physical address).
   - `raw_lpar >= 0x8000_0000ULL` (in partition space).
   - `(raw_lpar & 0x000F_FFFFULL) == 0` (strictly 1 MiB aligned).
2. **EA Sanity**:
   - `raw_ea >= 0x1_0000_0000ULL` (strictly 64-bit CPU address).
   - `(raw_ea & 0xFFFF_0000_0000ULL) == 0x5000_0000_0000ULL` (matches the 64-bit EA map pattern).
   - `raw_ea != raw_lpar` (distinct addresses).
3. **Size Sanity**:
   - `raw_sz >= 0x80000ULL` (at least 512 KiB).

### Guard Actions:
- Always stores raw values to `arena->buf_lpar`, `arena->buf_ea`, `arena->buf_sz` so the pager menu displays exactly what was in memory.
- If any check fails:
  - Sets `S->step_failed = STEP_PREGUARD_FAILED (10)`.
  - Sets `S->first_err_rc = -2` (`RESOURCE_SHORTAGE`).
  - Sets `arena->stock_rc = -2`.
  - Immediately returns with **ZERO hypercalls issued**.
- If fields are swapped (e.g. `0x2458428` holds `0x500002c00000` and `0x2458438` holds `0x84000000`):
  - `raw_lpar >= 0x100000000ULL` immediately triggers guard refusal.
  - Aborts with zero hypercalls.

---

## 4. Build & Audit Results

### Build Artifacts
All 4 variants built cleanly via `python netemu_p2e/build.py`:

| Variant | ELF SHA-256 | SELF SHA-256 | Code Size |
|---|---|---|---|
| **K0** | `0e096b409f53a4e4b9620e003d97f312a6f09a57015a881fa80d7a9457737e9c` | `a0c7f767c5b481ce70bd31aa24a69f8efd1c06299d1f130c7f4c312ebc854f13` | 8,832 bytes |
| **K1** | `5bfd21d4a63b6d55d3b4c9220af3a241e9d91056d95710dd52194e41f848b8e5` | `ade93a38f67822ffe5f8f767de9d86c59165763df7a9ebc330c568d92e69eabf` | 9,432 bytes |
| **K2** | `e13e9bc205d56c4de096948a8d58c7f4f21f1be79395532beb19962474403246` | `3711a6d995a7d48ce2273956a27c6a7df6f45a2078f413221d83c1ce7c552d35` | 10,808 bytes |
| **K3** | `e1dbd01afa801cb16f7d384ee96f8f152b194463ef16e8f74b166f58234d3ae0` | `380b0d4162c24be6538ee012f1c16a91d35ee2434d5fee07b159aceb336d607c` | 12,112 bytes |

### Security & Integrity Audits
1. **LLVM IR Pointer Provenance Audit (`netemu_p2e/audit_ir.py`)**:
   - `inttoptr` casts inspected across all 4 variants.
   - All pointer targets strictly verified to match authorized ranges (mailbox `0x930F20..0x930F80`, stock struct `0x2458428..0x2458438`, arena `0x2458480..0x2459480`).
   - PASS for K0, K1, K2, K3.
2. **`tools/p1a_audit.py` Single `sc` Instruction Check**:
   - Exactly ONE `sc` instruction in `.text` at `0x4858` for all variants.
   - Zero illegal `sc` instructions or accidental byte patterns in `.rodata` (avoided `"GUARD"` string hazard by using `" SANITY REJECT (0 HC)"`).
3. **SELF Round-Trip Decryption**:
   - Each SELF decrypted with `make_fself.exe -d` matches its corresponding patched ELF byte-for-byte.

### PC Validation Harness (`netemu_p2e/validate_pc.py`)
Tested in PyGhidra emulator with console ground-truth addresses:
- **K0**: PASS (130 hypercalls: open, allocate DMA, free DMA, close).
- **K1**: PASS (131 hypercalls: open, allocate DMA, map DMA LPAR `0x84000000`, unmap DMA, free DMA, close).
- **K2**: PASS (131 hypercalls: open, allocate DMA, map DMA, write ATAPI INQUIRY to CPU EA `0x500002c00000` with buffer LPAR `0x84001000`, send cmd LPAR `0x84000000`, unmap DMA, free DMA, close).
- **K3**: PASS (132 hypercalls: open, allocate DMA, map DMA, INQUIRY, READ10 to CPU EA `0x500002c00000` with buffer LPAR `0x84001000`, send cmd LPAR `0x84000000`, unmap DMA, free DMA, close).
- **Negative Test (Swapped Fields)**: PASS. Rejection triggered at Step 10 (`step_failed = 10`), **0 hypercalls issued**, raw values recorded to arena.
- **Unmapped Memory Store Audit**: PASS. Zero writes to unmapped LPAR `0x84000000..0x84002000` or unauthorized RAM. All stores directed to stack, mailbox, arena, or CPU EA `0x500002c00000`.
- **Installer Script Parse Check**: PASS (`tools/install_netemu.ps1` and `tools/restore_netemu.ps1` syntax checked without execution).

