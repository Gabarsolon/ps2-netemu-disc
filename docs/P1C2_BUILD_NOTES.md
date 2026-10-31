# P1c2 Build Notes: Pager Redesign via Timebase Gap Detection

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1c2 fix for project "ps2-netemu-disc": Fix the P1c probe's pager so all 24 diagnostic pages are reachable on the real PS3 console menu via menu open/close cycles, rebuild binary, validate on PC, DO NOT INSTALL.
- **Rules**: Read-only repository calls (LV1 91) only. Stores strictly in 96-byte mailbox, allocator arena, or stack. No network access. Fail-open.

---

## 1. Stock ELF Verification & Root Cause Analysis (PROVEN via pyghidra on stock.elf)

### Stock Binary Hashes
- **Stock ELF**: `local_only/stock.elf`
  - SHA256: `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`
- **Stock SELF**: `local_only/stock_ps2_netemu.self`
  - SHA256: `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`

### Hook Site & Menu Function Disassembly (`0x270FFC`)
- Disassembly around `0x270FFC`:
  ```asm
  0x270FF8:  ld  r25, -0x3498(r2)   ; font/string manager
  0x270FFC:  ld  r4, -0x3158(r2)    ; TOC string pointer 0x304EC0 ("Debug Information\0")
  0x271000:  or  r3, r25, r25
  0x271004:  bl  0x0027e4a8         ; registers label string
  0x271008:  ori r0, r0, 0
  0x27100C:  or  r31, r3, r3
  0x271010:  b   0x00270cf0         ; stores handle into menu item list
  ```
- Function Context: `menu_func_270c24` at `0x270C24` (called via vtable entry `0x948A68` / descriptor `0x746600` when the in-game PS-button menu widget renders).
- Menu Iteration Loop (`0x270C98` .. `0x270D34`):
  - In `menu_func_270c24`, a loop iterates over menu items using counter `r30` (`0, 1, 2, ..., N-1`).
  - Item type `0x13` corresponds to `"Debug Information"`. In the Evilnat 4.93 / Cobra debug menu, there are **9 consecutive items** of type `0x13` (rows 0 through 8), followed by item type `0x14` (`"Configuration"`).
  - The hook at `0x270FFC` is evaluated **once per row** in sequential order (`row = 0, 1, ..., 8`) as the menu list is built/refreshed.
  - The trampoline `entry_menu` at `0x4880`:
    ```asm
    lwz r3, 44(r24)
    bl  s4_menu
    mr  r4, r3
    ```
    passes `selected = 0..8` as the row index being populated.

### Why P1c Failed on Hardware (PROVEN)
- In P1c, `s4_menu` implemented a 6-bank x 4-row scheme with:
  ```c
  u32 cur_row = (u32)(selected & 3);
  if (prev_row == 3 && cur_row == 0) S->bank = (S->bank + 1) % 6;
  ```
- When the menu was opened, rows 0..8 were evaluated sequentially:
  - Row 0 (`selected = 0`): `cur_row = 0`, Bank 0 -> displays **P00**
  - Row 1 (`selected = 1`): `cur_row = 1`, Bank 0 -> displays **P01**
  - Row 2 (`selected = 2`): `cur_row = 2`, Bank 0 -> displays **P02**
  - Row 3 (`selected = 3`): `cur_row = 3`, Bank 0 -> displays **P03**
  - Row 4 (`selected = 4`): `cur_row = 0`, `prev == 3` -> `bank` advances to 1 -> displays **P04**
  - Row 5 (`selected = 5`): `cur_row = 1`, Bank 1 -> displays **P05**
  - Row 6 (`selected = 6`): `cur_row = 2`, Bank 1 -> displays **P06**
  - Row 7 (`selected = 7`): `cur_row = 3`, Bank 1 -> displays **P07**
  - Row 8 (`selected = 8`): `cur_row = 0`, `prev == 3` -> `bank` advances to 2 -> displays **P08**
- After Row 8, the stock menu has row 9 (`"Configuration"`).
- Crucially, the menu **does NOT wrap** vertically: pressing D-pad Down on the last item does not return to the top item. Thus, the owner could never scroll past the bottom to advance the bank further, permanently stranding Pages 09..23.

---

## 2. P1c2 Pager Architecture & Redesign

### Design Principles
1. **Zero navigation wrapping requirement**: Paging is driven exclusively by opening and closing the in-game menu.
2. **Deterministic page mapping**:
   - For menu open $N$ (where $N = 0, 1, 2, \dots$), row $r \in [0, 8]$ displays page:
     $$\text{page} = (N \times 9 + r) \pmod{24}$$
   - Any `selected` value $> 8$ is safely clamped to 8 (`selected > 8 ? 8 : selected`).
   - Page indices are mathematically bounded to $[0, 23]$.
3. **Robust New-Open Detection via Timebase Gap**:
   - PPC64 read-only instruction `mftb` reads the 64-bit hardware timebase register (frequency 79.8 MHz).
   - $1.5\text{ s} \times 79,800,000\text{ ticks/s} = 119,700,000\text{ ticks}$ (`0x07228360`).
   - An evaluation occurring more than 1.5 seconds after the previous evaluation (`now > last && (now - last) > TB_GAP_TICKS`) triggers a single increment of `open_count`.
   - All subsequent evaluations within that same open (gaps $\le 1.5\text{ s}$) update `last_eval_tb` without incrementing `open_count`.
   - On the first open after boot (`last == 0`), `open_count` remains 0, ensuring Open 1 always starts on P00..P08.

### Paging Progression Across Opens
- **Open 1** ($N=0$): Rows 0..8 $\rightarrow$ **P00, P01, P02, P03, P04, P05, P06, P07, P08**
- **Open 2** ($N=1$): Rows 0..8 $\rightarrow$ **P09, P10, P11, P12, P13, P14, P15, P16, P17**
- **Open 3** ($N=2$): Rows 0..8 $\rightarrow$ **P18, P19, P20, P21, P22, P23, P00, P01, P02**
- **Open 4** ($N=3$): Rows 0..8 $\rightarrow$ **P03, P04, P05, P06, P07, P08, P09, P10, P11**
- **Open 5** ($N=4$): Rows 0..8 $\rightarrow$ **P12, P13, P14, P15, P16, P17, P18, P19, P20**
- **Open 6** ($N=5$): Rows 0..8 $\rightarrow$ **P21, P22, P23, P00, P01, P02, P03, P04, P05**
- **Open 7** ($N=6$): Rows 0..8 $\rightarrow$ **P06, P07, P08, P09, P10, P11, P12, P13, P14**
- **Open 8** ($N=7$): Rows 0..8 $\rightarrow$ **P15, P16, P17, P18, P19, P20, P21, P22, P23**
- **Open 9** ($N=8$): Cycles cleanly back to Open 1 (P00..P08).

---

## 3. 96-Byte Mailbox Layout (`0x930F20`)

The mailbox layout maintains strict 96-byte sizing and natural 8-byte alignment for all 64-bit fields:

| Offset | Type | Field Name | Description |
|---|---|---|---|
| `0x00` | `u32` | `status` | Status flags (`STATUS_STARTED`, `STATUS_DONE`, `STATUS_ALLOC_OK`, etc.) |
| `0x04` | `u32` | `total_hypercalls` | Total LV1 91 repository calls executed |
| `0x08` | `u32` | `rom_count` | Number of type 5 (ROM) devices found on bus 4 |
| `0x0C` | `u32` | `hdd_found` | 1 if HDD storage device found on bus 4 |
| `0x10` | `u32` | `first_err_rc` | First non-zero LV1 91 return code (or 0) |
| `0x14` | `u32` | `open_count` | Counter of menu open cycles (increments on >1.5 s gap) |
| `0x18` | `u32[2]`| `pad1[2]` | Padding to align `arena_ptr` to offset 32 |
| `0x20` | `u64` | `arena_ptr` | Pointer to 4 KiB arena allocated via `native_alloc 0xB9848` |
| `0x28` | `u8` | `rom_bus_idx` | Bus index of Optical node (4) |
| `0x29` | `u8` | `rom_dev_idx` | Device index of Optical node (2) |
| `0x2A` | `u8` | `rom_port` | Port of Optical node (0) |
| `0x2B` | `u8` | `hdd_bus_idx` | Bus index of HDD node (4) |
| `0x2C` | `u8` | `hdd_dev_idx` | Device index of HDD node (3) |
| `0x2D` | `u8` | `hdd_port` | Port of HDD node (2) |
| `0x2E` | `u8[2]`| `pad2[2]` | Padding to offset 48 |
| `0x30` | `u64` | `rom_bus_id` | Bus ID of Optical node (4) |
| `0x38` | `u64` | `rom_dev_id` | Device ID of Optical node (2) |
| `0x40` | `u64` | `hdd_bus_id` | Bus ID of HDD node (4) |
| `0x48` | `u64` | `hdd_dev_id` | Device ID of HDD node (0) |
| `0x50` | `u64` | `last_eval_tb` | 64-bit hardware timebase of previous hook evaluation |
| `0x58` | `u64` | `reserved` | Padding to exactly 96 bytes |

Compile-time static assertions verify:
```c
_Static_assert(sizeof(struct ProbeState) == 96, "ProbeState must be 96 bytes");
_Static_assert(__builtin_offsetof(struct ProbeState, open_count) == 20, "open_count offset 20");
_Static_assert(__builtin_offsetof(struct ProbeState, arena_ptr) == 32, "arena_ptr offset 32");
_Static_assert(__builtin_offsetof(struct ProbeState, last_eval_tb) == 80, "last_eval_tb offset 80");
```

---

## 4. Safety & Fail-Open Invariants
- **No stores outside RW memory**: Stores restricted strictly to Stack (`r1`), Mailbox (`0x930F20..0x930F80`), and Allocator Arena (`[base+0x20000, base+0x60000)`).
- **Zero hypercalls in code slot**: All LV1 repository queries route through stock helper `0x111eb8`. Zero `sc` instructions in payload.
- **Fail-open behavior**: If `native_alloc` fails, or if repository probe cannot complete, `s4_menu` returns stock string `"Debug Information\0"` at `0x304EC0`.
