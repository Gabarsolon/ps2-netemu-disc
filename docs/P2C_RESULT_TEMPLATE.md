# P2C Console Result Template: Netemu LPAR Memory Diagnostics

This document outlines the procedure for the console owner to run the **P2C Zero-Hypercall Diagnostic Probe** (`ps2_netemu_p2c.self`) on the PS3, step through all 4 menu pages (36 items total) using the **Timebase Gap Pager**, photograph the output, and record the live memory diagnostics.

---

## 1. Owner Execution Steps

> [!IMPORTANT]
> The automated assistant is strictly forbidden from running console install/restore scripts or communicating with the PS3 over the network. The commands below are for the **human owner** to run manually from their PowerShell terminal.

### Step 1: Install the P2C Diagnostic Probe
From the repository root (`C:\Users\remus\ps2-netemu-disc`):
```powershell
tools\install_netemu.ps1 -File local_only\p2c\ps2_netemu_p2c.self -Force
```

### Step 2: Launch a PS2 ISO
1. Ensure a genuine PS2 DVD disc is inserted into the PS3 drive.
2. Launch any PS2 ISO using webMAN MOD.
3. Wait for the game to boot and start rendering under `ps2_netemu`.

### Step 3: Photographic Protocol (4 Menu Opens)
The Evilnat/Cobra in-game menu displays 9 label rows simultaneously (rows 0 to 8). The P2C pager detects menu opens by measuring the hardware timebase gap between hook invocations (threshold: 1.5 seconds at 79.8 MHz).

All 36 diagnostic items are captured across **4 menu opens**:

---

#### Open 0: Stock Heap Block (Offsets 0x00..0x40)
1. Press the **PS button** on the controller to open the in-game menu.
2. The 9 custom rows display:
   - Row 0 (Item 00): `P2C H+00: <u64>` (Stock Heap Base LPAR)
   - Row 1 (Item 01): `P2C H+08: <u64>` (Stock Heap Limit LPAR)
   - Row 2 (Item 02): `P2C H+10: <u64>` (Stock Heap Capacity)
   - Row 3 (Item 03): `P2C H+18: <u64>`
   - Row 4 (Item 04): `P2C H+20: <u64>`
   - Row 5 (Item 05): `P2C H+28: <u64>`
   - Row 6 (Item 06): `P2C H+30: <u64>`
   - Row 7 (Item 07): `P2C H+38: <u64>`
   - Row 8 (Item 08): `P2C H+40: <u64>`
3. **Photograph the screen** (or record values in the table below).
4. Press **Circle** or the **PS button** to close the menu.
5. **Wait at least 2 seconds** before reopening (allows the >1.5 s timebase gap to register).

---

#### Open 1: Stock Heap Block (Offsets 0x48..0x78) & Free Heap Bytes
1. Press the **PS button** to open the in-game menu a second time.
2. The 9 custom rows now display:
   - Row 0 (Item 09): `P2C H+48: <u64>`
   - Row 1 (Item 10): `P2C H+50: <u64>`
   - Row 2 (Item 11): `P2C H+58: <u64>` (Raw cursor & limit 64-bit word)
   - Row 3 (Item 12): `P2C H+60: <u64>`
   - Row 4 (Item 13): `P2C H+68: <u64>`
   - Row 5 (Item 14): `P2C H+70: <u64>`
   - Row 6 (Item 15): `P2C H+78: <u64>`
   - Row 7 (Item 16): `HEAP CUR=0x<u32> LIM=0x<u32>`
   - Row 8 (Item 17): `HEAP FREE=0x<u32> (<dec> KB)`
3. **Photograph the screen**.
4. Press **Circle** or the **PS button** to close the menu.
5. **Wait at least 2 seconds** before reopening.

---

#### Open 2: Mapped-EA Cursor & HDD Driver State (H = 0x241C850)
1. Press the **PS button** to open the in-game menu a third time.
2. The 9 custom rows now display:
   - Row 0 (Item 18): `MAPPED_EA 0xB28A10=<u64>`
   - Row 1 (Item 19): `H+08 BUS/DEV  =<u64>`
   - Row 2 (Item 20): `H+10 DEV_ID   =<u64>`
   - Row 3 (Item 21): `H+20 BUF_EA   =<u64>` (HDD Buffer Effective Address)
   - Row 4 (Item 22): `H+28 LPARBUF  =<u64>` (HDD Buffer Physical LPAR Address)
   - Row 5 (Item 23): `H+30 DMA_RGN  =<u64>` (HDD DMA Region ID)
   - Row 6 (Item 24): `H+38 TAGSTAT  =<u64>`
   - Row 7 (Item 25): `H+40 STATUS   =<u64>`
   - Row 8 (Item 26): `H+48 STATUS   =<u64>`
3. **Photograph the screen**.
4. Press **Circle** or the **PS button** to close the menu.
5. **Wait at least 2 seconds** before reopening.

---

#### Open 3: Allocator Pool Descriptors, Runtime TOC, and Summary
1. Press the **PS button** to open the in-game menu a fourth time.
2. The 9 custom rows now display:
   - Row 0 (Item 27): `POOL 934980   =<u64>`
   - Row 1 (Item 28): `POOL 24565B8  =<u64>`
   - Row 2 (Item 29): `POOL 2446588  =<u64>`
   - Row 3 (Item 30): `ARENA 0xB9848 =<u64>` (4 KiB Arena EA from native_alloc)
   - Row 4 (Item 31): `RUNTIME TOC r2=<u64>` (Captured stock TOC register)
   - Row 5 (Item 32): `TOC -7B30 ADDR=<u64>` (Resolved address of Mapped-EA global)
   - Row 6 (Item 33): `TOC -7E50 ADDR=<u64>` (Resolved address of Heap block)
   - Row 7 (Item 34): `TOC -6F58 ADDR=<u64>` (Resolved address of HDD struct)
   - Row 8 (Item 35): `P2C DIAG OK HC=0 OPENS=0003`
3. **Photograph the screen**.
4. Opening the menu a fifth time cleanly wraps back to Open 0.

---

### Step 4: Restore the Stock Binary
After photographing all 4 pages:
```powershell
tools\restore_netemu.ps1
```

---

## 2. Results Recording Table

### Open 0: Stock Heap Block (0x930F80 Offsets 0x00..0x40)
| Item | Row | Field / Offset | Expected / Derivation | Observed Live Value | Notes |
|:---:|:---:|:---|:---|:---|:---|
| **00** | 0 | `H+00` | `0x0000000003200000` (Base LPAR) | | |
| **01** | 1 | `H+08` | `0x0000000003C00000` (Limit LPAR) | | |
| **02** | 2 | `H+10` | `0x0000000000A00000` (10 MiB Capacity) | | |
| **03** | 3 | `H+18` | `0x0000000000000000` | | |
| **04** | 4 | `H+20` | Unknown / Hypercall 0 state | | |
| **05** | 5 | `H+28` | Unknown | | |
| **06** | 6 | `H+30` | Unknown | | |
| **07** | 7 | `H+38` | Unknown | | |
| **08** | 8 | `H+40` | Unknown | | |

### Open 1: Stock Heap Block (0x930F80 Offsets 0x48..0x78) & Free Heap
| Item | Row | Field / Offset | Expected / Derivation | Observed Live Value | Notes |
|:---:|:---:|:---|:---|:---|:---|
| **09** | 0 | `H+48` | Unknown | | |
| **10** | 1 | `H+50` | Unknown | | |
| **11** | 2 | `H+58` | Cursor (high 32) + Limit (low 32) | | |
| **12** | 3 | `H+60` | Unknown | | |
| **13** | 4 | `H+68` | Unknown | | |
| **14** | 5 | `H+70` | Unknown | | |
| **15** | 6 | `H+78` | Unknown | | |
| **16** | 7 | `HEAP CUR / LIM` | `CUR >= 0x03B00000 LIM = 0x03C00000` | | Real Cursor & Limit |
| **17** | 8 | `HEAP FREE` | `< 1024 KB (< 0x100000)` | | Exact Free Heap Available |

### Open 2: Mapped-EA & HDD Driver State (H = 0x241C850)
| Item | Row | Field / Offset | Expected / Derivation | Observed Live Value | Notes |
|:---:|:---:|:---|:---|:---|:---|
| **18** | 0 | `MAPPED_EA 0xB28A10` | `*(u64*)0xB28A10` | | Current Mapped EA Cursor |
| **19** | 1 | `H+08 BUS/DEV` | Bus 4 / Dev 3 (if present) | | |
| **20** | 2 | `H+10 DEV_ID` | Dev ID 3 (if present) | | |
| **21** | 3 | `H+20 BUF_EA` | CPU EA of 1 MiB HDD Buffer | | |
| **22** | 4 | `H+28 LPARBUF` | Physical LPAR of HDD Buffer | | **Key test: is this != 0?** |
| **23** | 5 | `H+30 DMA_RGN` | HDD DMA Region ID | | |
| **24** | 6 | `H+38 TAGSTAT` | Tag / Status | | |
| **25** | 7 | `H+40 STATUS` | Driver Status | | |
| **26** | 8 | `H+48 STATUS` | Driver Status | | |

### Open 3: Allocator Pools, Runtime TOC, and Summary
| Item | Row | Field / Offset | Expected / Derivation | Observed Live Value | Notes |
|:---:|:---:|:---|:---|:---|:---|
| **27** | 0 | `POOL 934980` | `0x0000000080000000` | | Stock Pool Base |
| **28** | 1 | `POOL 24565B8` | `0x0000000080000000` | | Stock Pool Base Copy |
| **29** | 2 | `POOL 2446588` | `0x0000000080020000` | | Pool Check Boundary |
| **30** | 3 | `ARENA 0xB9848` | `0x0000000080020000`..`0x8005F000` | | EA returned by `native_alloc` |
| **31** | 4 | `RUNTIME TOC r2`| `0x0000000000751280` | | Real stock TOC |
| **32** | 5 | `TOC -7B30 ADDR`| `0x0000000000749750` | | Pointer to Mapped-EA |
| **33** | 6 | `TOC -7E50 ADDR`| `0x0000000000749430` | | Pointer to Heap Block |
| **34** | 7 | `TOC -6F58 ADDR`| `0x000000000074A328` | | Pointer to HDD struct |
| **35** | 8 | `SUMMARY` | `P2C DIAG OK HC=0 OPENS=0003` | | Confirms 0 hypercalls made |
