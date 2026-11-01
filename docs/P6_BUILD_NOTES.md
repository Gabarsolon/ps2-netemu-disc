# P6 Build Notes: LV1 DMA Mapping Decompilation & Root Cause Analysis

## Status
- **Date**: 2026-11-01
- **Target**: Official 4.93 LV1 (`local_only/fw493/lv1.elf`) cross-referenced with 3.55 LV1 (`local_only/fw355/out/lv1.elf`), stock netemu (`local_only/stock.elf`), and console log ground truth (`docs/P5_Q1_RESULT.md`, `local_only/netemu_log_Q1.bin`).
- **Goal**: Identify the exact check returning `-17` (`LV1_ILLEGAL_PARAMETER_VALUE`) for `lv1_map_device_dma_region(4, 2, lpar 0x84000000, bus 0xC0000000, len, flags)` while stock HDD map (`lv1_map_device_dma_region(4, 3, lpar, bus 0xd0000000, len 0x80000, flags 0xe000000000000800)`) succeeds.

---

## 1. Ground Truth Alignment with PS3 Console

From `docs/P5_Q1_RESULT.md` and raw log decoding of `local_only/netemu_log_Q1.bin`:
- **Record #03 [GRD]**:
  - `a = 0x0000000084000000` (read from `0x2458428`)
  - `b = 0x0000500002c00000` (read from `0x2458438`)
- **Candidate #5** (`len = 0x80000`, `exp = 20` (1MB)): returned `0x00000010FFFFFFEF`.
  - Bit 36 set -> reason code `5` (`1L << (5 + 31) = 0x1000000000`).
  - Proves `FUN_00227218` line 69 executed on console:
    `len % page_size != 0` (`0x80000 % 0x100000 != 0`) -> sets `*reason = 5`, returns `-17`.
- **All other 11 candidates** (#1-#4, #6-#12): returned `0x00000000FFFFFFEF`.
  - Reason code was cleared to `0` at line 62 of `FUN_00227218` before delegating to `*dev->vtable[0xa8]`.
  - The virtual method returned `-17` without setting an outer reason code.

---

## 2. LV1 Hypercall Call Tree (HV 174..177)

### 2.1 Hypercall Table (VA `0x3c2630` registration)
- **HV 170 (`0x305a38`)**: `lv1_open_device`
- **HV 171 (`0x306eec`)**: `lv1_close_device`
- **HV 172 (`0x306d64`)**: `lv1_map_device_mmio_region`
- **HV 173 (`0x306c10`)**: `lv1_unmap_device_mmio_region`
- **HV 174 (`0x306a6c`)**: `lv1_allocate_device_dma_region`
- **HV 175 (`0x306918`)**: `lv1_free_device_dma_region`
- **HV 176 (`0x306770`)**: `lv1_map_device_dma_region`
- **HV 177 (`0x30660c`)**: `lv1_unmap_device_dma_region`

### 2.2 HV 176 Entry Point (`FUN_00306770`)
1. Checks `bus_id < 5` (else `-17`, reason 1).
2. Checks flags mask: `(flags >> 12 & 0x7fffffffffff) == 0 && (flags & 0x7ff) == 0` (else `-17`, reason 32). Allowed bits: top 5 bits `0xf800000000000000` + bit 11 `0x800`.
3. Calls `FUN_00236d1c`.

### 2.3 Dispatcher (`FUN_00236d1c`)
1. Looks up device object: `FUN_00236594(bus_id, dev_id)`:
   - For `bus_id = 4`: returns `*(long *)(dev_id * 8 + *plRam0000000000353818 + 0xee8)`.
   - Device 2 (optical BDVD): device object at heap, vtable `0x35e370`.
   - Device 3 (HDD): device object at heap, vtable `0x35e1c8`.
2. Calls `FUN_00227218(dev_obj, lpar_obj, bus_addr, lpar_addr, len, flags, &reason)`.

### 2.4 Device Virtual Method Level (`FUN_00227218`)
1. Device spinlock at `dev + 0xb`.
2. DMA Region lookup: `region = (*dev->vtable[0xc8])(dev, bus_addr)`. Returns `-6` (reason 4) if null.
3. Checks `len != 0 && len <= region->size` (else `-17`, reason 5).
4. Checks overlap via `func_0x002257c4` (else `-9`, reason 4).
5. Checks page alignment: `bus_addr % page_size == 0` (else `-17`, reason 4).
6. Checks page alignment: `lpar_addr % page_size == 0` (else `-17`, reason 3).
7. Checks `len % page_size == 0` (else `-17`, reason 5).
8. Clears `*reason = 0`.
9. Calls `*dev->vtable[0xa8](dev, region, bus_addr, len, lpar_addr, &scratch, flags, lpar_obj)`.

---

## 3. Structural Vtable & Deep Implementation (`FUN_0025804c` -> `FUN_00227124`)

- Device 2 (BDVD) and Device 3 (HDD) both share the exact same method `FUN_0025804c` at `vtable[0xa8]`.
- Inside `FUN_0025804c`:
  - Line 17: `uVar2 = (*dev->vtable[0xe0])();` (underlying Southbridge controller).
  - Line 18: `iVar5 = FUN_00227218(uVar2, lpar_obj, bus_addr, lpar_addr, len, flags, auStack_70);`
  - In `uVar2`, `vtable[0xa8]` is `FUN_00227b34`.
- Inside `FUN_00227b34`:
  - Translates bus address: `(*uVar2->vtable[0x78])(uVar2, bus_addr, &translated_bus);`
  - Calls `(*uVar2->vtable[0x88])(uVar2, translated_bus, lpar_addr, uVar2->ioid, flags, len, page_size);`
- `*uVar2->vtable[0x88]` is `FUN_00227124` (`storage_device::put_ioptes`):
  ```c
  undefined8 FUN_00227124(undefined8 param_1, long param_2, ulong param_3,
                          undefined8 param_4, undefined8 param_5, long param_6, long param_7)
  {
    ...
    do {
      lVar1 = func_0x002d7e9c(0, param_2, param_3, param_4, param_5, 0);
      param_2 = param_2 + param_7;
      param_3 = param_3 + param_7;
      if (lVar1 != 0) {
        return 0xffffffffffffffef; // -17 (LV1_ILLEGAL_PARAMETER_VALUE)
      }
    } while (...);
    return 0;
  }
  ```
  **CRITICAL**: `FUN_00227124` line 20 discards the inner return code from `FUN_002d7e9c` and returns `0xffffffffffffffef` (`-17`)!

---

## 4. The Exact Check Returning `-17`: `FUN_002ce74c` LPAR Memory Segment Validation

Inside `FUN_002d7e9c` -> `FUN_002d6248` -> `FUN_002d58b4`:
```c
long FUN_002d58b4(long param_1, long *param_2, ulong param_3)
{
  ...
  while (lVar1 = func_0x002d406c(param_1 + 0x60, &uStack_60), lVar1 == 0) {
    lVar2 = func_0x002ce74c(*(long *)(*(long *)(param_1 + 0x38) + 0x38) + 0x9e0, param_3, 0);
    if (lVar2 == 0) goto LAB_002d5a58;
    ...
  }
  ...
LAB_002d5a58:
  lVar1 = 0;
  *param_2 = 0x997997d2b58e3c01; // internal error: LPAR segment not found in partition tree
  return 0;
}
```

Inside `FUN_002ce74c` (`local_only/analysis/p0i/lv1/fn_002ce74c.c`):
```c
long FUN_002ce74c(undefined8 param_1, ulong param_2, undefined1 param_3)
{
  ulong uVar1;
  long lVar2;
  ulong uVar3;

  uVar3 = param_2 >> 0x2a & 0x3f;
  uVar1 = 0xfffffc0000000000;
  if ((int)uVar3 != 0) {
    uVar1 = -1L << uVar3;
  }
  lVar2 = func_0x002ce5e4(param_1, param_2 & uVar1, param_3);
  if ((lVar2 != 0) && ((param_2 & uVar1) + *(long *)(lVar2 + 0x58) <= param_2)) {
    lVar2 = 0;
  }
  return lVar2;
}
```

### 4.1 Why `0x84000000` Was Refused
1. `param_2` is `lpar_addr`.
2. When `0x84000000` is passed:
   - `0x84000000 >> 42` is `0` (`uVar3 = 0`).
   - `uVar1` defaults to `0xfffffc0000000000`.
   - `param_2 & uVar1` is `0x84000000 & 0xfffffc0000000000 = 0`!
   - `func_0x002ce5e4` searches the partition's physical LPAR memory segment tree for base `0`.
   - No memory segment exists at base `0` (or `0x84000000`), so `func_0x002ce5e4` returns `NULL`.
3. `FUN_002ce74c` returns `0`.
4. `FUN_002d58b4` jumps to `LAB_002d5a58`, setting `*param_2 = 0x997997d2b58e3c01`.
5. `FUN_002d6248` returns `0x997997d2b58e3c01`.
6. `FUN_002d7e9c` maps `0x997997d2b58e3c01` to `0x2fffffffa` (non-zero).
7. `FUN_00227124` line 20 converts non-zero to `0xffffffffffffffef` (`-17`).
8. `FUN_0025804c` returns `-17`.
9. `FUN_00227218` returns `-17` with reason `0` (cleared at line 62).

---

## 5. Root Cause: Effective Address vs. Physical LPAR Address in Netemu

### 5.1 Stock Netemu Buffer Allocation Disassembly (`stock.elf`)
Both the HDD driver and the CDVD driver allocate their 1 MiB DMA buffers by calling helper `0x19a5c` -> `0x19900`:
- Inside `0x19900`:
  - Calls `0x1622c`, which executes `li r11, 0; sc` (HV 0: `lv1_allocate_memory`).
  - HV 0 returns the 64-bit physical LPAR address (e.g., `0x500002c00000` or `0x500002d00000`).
  - `0x19900` stores this physical LPAR address into `*r5` (`std r0, 0(r26)`).
  - `0x19900` generates a 32-bit CPU Effective Address by taking a cursor and OR-ing `0x80000000` (e.g., `0x84000000` or `0x84800000`).
  - Calls `0x16790` to insert HTAB page table entries mapping the EA to the LPAR address.
  - Stores this CPU EA into `*r6`.

### 5.2 Stock HDD Driver (`0x12c000` - `0x12c0cc`)
```
0x12bffc: addi r5, r30, 0x20    ; r5 = &H[0x20] (receives LPAR address)
0x12c000: addi r6, r1, 0x80     ; r6 = &stack[0x80] (receives CPU EA)
0x12c010: bl 0x19a5c            ; allocate memory
0x12c018: ld r0, 0x80(r1)       ; load CPU EA from stack
0x12c028: std r0, 0x28(r30)     ; store CPU EA to H+0x28 (0x84800000)
...
0x12c0ac: lis r8, 0xe000        ; flags = 0xe000000000000800
0x12c0b0: ld r3, 0x08(r28)      ; bus_id = 4
0x12c0b4: ld r4, 0x10(r28)      ; dev_id = 3
0x12c0b8: lis r7, 0x8           ; len = 0x80000
0x12c0c0: ld r5, 0x20(r28)      ; r5 = H+0x20 (LPAR ADDRESS 0x500002d00000!)
0x12c0c4: ld r6, 0x30(r28)      ; bus_addr = 0xd0000000
0x12c0cc: bl 0x160fd            ; lv1_map_device_dma_region(4, 3, lpar, bus, len, flags)
```
**PROVEN**: The stock HDD driver passes `H+0x20` (physical LPAR address `0x500002d00000`), NOT `H+0x28` (`0x84800000`)!

### 5.3 Stock CDVD Driver (`0x133c90` - `0x133cb4`)
```
0x133c9c: ld r3, -0x5838(rtoc)  ; allocator object
0x133ca0: addi r5, r29, 0x1458  ; r5 = 0x2456fe0 + 0x1458 = 0x2458438 (receives LPAR address!)
0x133ca4: addi r6, r29, 0x1448  ; r6 = 0x2456fe0 + 0x1448 = 0x2458428 (receives CPU EA!)
0x133ca8: std r0, 0x1450(r29)   ; buffer size = 0x100000 (0x2458430)
0x133cb0: bl 0x19a5c            ; allocate memory
```
**PROVEN**:
- `0x2458438` is the **REAL PHYSICAL LPAR ADDRESS** (`0x500002c00000` in P5 Q1 log record #03)!
- `0x2458428` is the **CPU EFFECTIVE ADDRESS** (`0x84000000`)!

### 5.4 The Bug in P5 `probe.c`
In P5 `probe.c` lines 202-217:
```c
u64 raw_lpar = *(const volatile u64 *)0x2458428ULL; // loaded 0x84000000 (CPU EA!)
u64 raw_ea   = *(const volatile u64 *)0x2458438ULL; // loaded 0x500002c00000 (real LPAR!)
```
`probe.c` inverted the two fields and passed `0x84000000` to `lv1_map_device_dma_region`.
LV1's `FUN_002ce74c` rejected `0x84000000` because effective addresses are not registered in the partition's physical LPAR memory segment tree.

---

## 6. Ranked Hypotheses for P6 Variant R1

### Hypothesis 1 (Rank 1 - Highest Confidence):
- **Hypothesis**: Passing the real physical LPAR address of the CDVD buffer (`0x2458438`, value `0x500002c00000`) to `lv1_map_device_dma_region(4, 2, lpar, 0xC0000000, 0x100000, 0xe000000000000800)` will succeed (`rc = 0`).
- **Rationale**: The optical device (Device 2) and HDD device (Device 3) use the exact same DMA mapping code path (`FUN_0025804c` -> `FUN_00227124` -> `FUN_002d7e9c`). The stock HDD driver maps its physical LPAR address (`H+0x20`) with identical flags (`0xe000000000000800`).

### Hypothesis 2 (Rank 2):
- **Hypothesis**: Testing cross-device mapping using the HDD driver's verified LPAR address (`H+0x20`, `0x500002d00000`) on Device 2 without DMA, then immediately unmapping.
- **Rationale**: Isolates whether Device 2 has any restriction on which partition LPAR segments it can map versus Device 3.

### Hypothesis 3 (Rank 3):
- **Hypothesis**: If full 1 MiB length is rejected, test lengths `0x80000` and `0x1000` with region page exponent 12.
- **Rationale**: Covers potential length limitations or page size requirements.

---

## 7. Action Plan for P6 Variant R1
1. Clone `netemu_p5/` to `netemu_p6/`.
2. Fix `check_cdvd_buffer_guard` in `netemu_p6/src/probe.c`:
   - Load `raw_lpar` from `0x2458438` (physical LPAR).
   - Load `raw_ea` from `0x2458428` (CPU EA).
   - Guard: `raw_lpar` must match `0x500000000000ULL` prefix and 1MB alignment; `raw_ea` must match `0x84000000ULL`.
   - Also read `H+0x20` (HDD LPAR) from HDD struct pointer for candidate fallback.
3. Test Candidates in R1:
   - Candidate 1: `lpar = *(0x2458438)` (CDVD real LPAR), `bus = 0xC0000000`, `len = 0x100000`, `flags = 0xe000000000000800`, `pexp = 20`.
   - Candidate 2: `lpar = *(0x2458438)`, `bus = 0xC0000000`, `len = 0x80000`, `flags = 0xe000000000000800`, `pexp = 16`.
   - Candidate 3: `lpar = *(0x2458438)`, `bus = 0xC0000000`, `len = 0x1000`, `flags = 0xe000000000000800`, `pexp = 12`.
   - Candidate 4: `lpar = *(H+0x20)` (HDD real LPAR), `bus = 0xC0000000`, `len = 0x80000`, `flags = 0xe000000000000800`, `pexp = 16`.
4. Mandatory Safety:
   - Unmap immediately upon any successful map.
   - Stop testing upon first success.
   - Zero stores at or above `0x930F80`. Exactly one `sc`. Stores only in stack/mailbox/arena/command block.
   - PC harness verification with configurable fake LV1.
   - SELF build and audit.
