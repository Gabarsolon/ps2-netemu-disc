# P1c2 Console Result Template: Optical vs HDD Repository Dumper

This document outlines the procedure for the console owner to run the **P1c2** read-only repository probe on the PS3, step through all 24 result pages using the new **Timebase Gap Pager**, photograph the output, and record the repository comparison between the Optical node (ROM) and the HDD node.

---

## 1. Owner Execution Steps

> [!IMPORTANT]
> The automated assistant is strictly forbidden from running console install/restore scripts or communicating with the PS3 over the network. The commands below are for the **human owner** to run manually from their PowerShell terminal.

### Step 1: Install the P1c2 Probe
From the repository root (`C:\Users\remus\ps2-netemu-disc`):
```powershell
tools\install_netemu.ps1 -File local_only\p1c2\ps2_netemu_p1c2.self -Force
```

### Step 2: Launch a PS2 ISO
1. On the PS3, launch any PS2 ISO using webMAN MOD.
2. Wait for the game to start rendering under `ps2_netemu`.

### Step 3: Open the In-Game Menu (Photographic Protocol)
The Evilnat/Cobra netemu menu displays 9 label rows of type `0x13` simultaneously (rows 0 to 8), followed by "Configuration". The menu does not wrap at the bottom. The P1c2 pager detects menu opens by measuring the hardware timebase gap between hook invocations (threshold: 1.5 seconds at 79.8 MHz).

All 24 pages are captured across **3 menu opens**:

#### Open 1 (Pages P00 through P08):
1. Press the **PS button** on the controller to open the in-game menu.
2. The 9 custom rows display:
   - Row 0: **P00** (Summary)
   - Row 1: **P01** (OPT type)
   - Row 2: **P02** (HDD type)
   - Row 3: **P03** (OPT id)
   - Row 4: **P04** (HDD id)
   - Row 5: **P05** (OPT port)
   - Row 6: **P06** (HDD port)
   - Row 7: **P07** (OPT blk_sz)
   - Row 8: **P08** (HDD blk_sz)
3. Photograph the screen (or transcribe all 9 rows).
4. Press **Circle** or the **PS button** to close the in-game menu.
5. **Wait at least 2 seconds** before reopening (this allows the >1.5 s timebase gap to register).

#### Open 2 (Pages P09 through P17):
1. Press the **PS button** to open the in-game menu again.
2. The 9 custom rows now display:
   - Row 0: **P09** (OPT n_blks)
   - Row 1: **P10** (HDD n_blks)
   - Row 2: **P11** (OPT n_regs)
   - Row 3: **P12** (HDD n_regs)
   - Row 4: **P13** (OPT meddl)
   - Row 5: **P14** (HDD meddl)
   - Row 6: **P15** (OPT pci_b)
   - Row 7: **P16** (HDD pci_b)
   - Row 8: **P17** (OPT intr0)
3. Photograph the screen (or transcribe all 9 rows).
4. Press **Circle** or the **PS button** to close the in-game menu.
5. **Wait at least 2 seconds** before reopening.

#### Open 3 (Pages P18 through P23, wrapping to P00..P02):
1. Press the **PS button** to open the in-game menu a third time.
2. The 9 custom rows display the remaining 6 pages, then wrap:
   - Row 0: **P18** (HDD intr0)
   - Row 1: **P19** (OPT reg0_t)
   - Row 2: **P20** (HDD reg0_t)
   - Row 3: **P21** (OPT intr1)
   - Row 4: **P22** (HDD intr1)
   - Row 5: **P23** (BUS4 ndev)
   - Row 6: **P00** (Summary - wrap)
   - Row 7: **P01** (OPT type - wrap)
   - Row 8: **P02** (HDD type - wrap)
3. Photograph the screen (or transcribe all 9 rows).
4. All 24 pages have now been observed!

#### Behavior Notes:
- **In-Open Stability**: While the menu remains continuously open, scrolling between items does not advance pages because successive evaluations occur within less than 1.5 seconds.
- **Redraw / Idle Behavior**: If the menu is left open with no user action for more than 1.5 seconds, pages do NOT change unless the console actually re-renders the menu rows. If an evaluation does occur after >1.5 s, it will advance to the next 9-page bank.
- **Cycle Repeat**: The pager sequence repeats every 8 opens (8 x 9 = 72 = 3 full cycles of 24 pages).

### Step 4: Restore the Stock Binary
After photographing the labels:
```powershell
tools\restore_netemu.ps1
```

---

## 2. Page Inventory (Pages 00 to 23)

Each page label is formatted to a maximum of 31 ASCII characters plus null terminator:

| Page | Open | Row | Key / Target | Expected Output / Meaning |
|---|---|---|---|---|
| **P00** | 1 | 0 | **Summary** | `P00 P1C r=<roms> h=<hdd> id=4/2 p=0` (Optical bus 4, dev 2, port 0, IDs 4/2) |
| **P01** | 1 | 1 | `OPT type` | `P01 OPT type: 5 (ROM)` |
| **P02** | 1 | 2 | `HDD type` | `P02 HDD type: 0 (DISK)` |
| **P03** | 1 | 3 | `OPT id` | `P03 OPT id: 2 (ROM DEV)` |
| **P04** | 1 | 4 | `HDD id` | `P04 HDD id: 0` |
| **P05** | 1 | 5 | `OPT port` | `P05 OPT port: 0 (PORT0)` |
| **P06** | 1 | 6 | `HDD port` | `P06 HDD port: 2 (PORT2)` |
| **P07** | 1 | 7 | `OPT blk_sz` | `P07 OPT blk_sz: 2048 (0x800)` (or `rc=-6 NO_ENT` without media) |
| **P08** | 1 | 8 | `HDD blk_sz` | `P08 HDD blk_sz: 512 (0x200)` |
| **P09** | 2 | 0 | `OPT n_blks` | `P09 OPT n_blks: 0 (NO DISC)` (or sector count) |
| **P10** | 2 | 1 | `HDD n_blks` | `P10 HDD n_blks: 0x<hex>` (HDD total sector count) |
| **P11** | 2 | 2 | `OPT n_regs` | `P11 OPT n_regs: 0 (NO REGS)` (storage-region count) |
| **P12** | 2 | 3 | `HDD n_regs` | `P12 HDD n_regs: <n>` (storage-region count) |
| **P13** | 2 | 4 | `OPT meddl` | `P13 OPT meddl: <val>` (ownership/meddling attribute or `rc=-6`) |
| **P14** | 2 | 5 | `HDD meddl` | `P14 HDD meddl: <val>` (ownership/meddling attribute or `rc=-6`) |
| **P15** | 2 | 6 | `OPT pci_b` | `P15 OPT pci_b: <val>` (PCI bus or `rc=-6 NO_ENT`) |
| **P16** | 2 | 7 | `HDD pci_b` | `P16 HDD pci_b: <val>` (PCI bus or `rc=-6 NO_ENT`) |
| **P17** | 2 | 8 | `OPT intr0` | `P17 OPT intr0: <val>` (Optical interrupt type/ID or `rc=-6`) |
| **P18** | 3 | 0 | `HDD intr0` | `P18 HDD intr0: 18 (0x12 HDD)` |
| **P19** | 3 | 1 | `OPT reg0_t` | `P19 OPT reg0_t: <val>` (MMIO register 0 type or `rc=-6`) |
| **P20** | 3 | 2 | `HDD reg0_t` | `P20 HDD reg0_t: <val>` (MMIO register 0 type or `rc=-6`) |
| **P21** | 3 | 3 | `OPT intr1` | `P21 OPT intr1: <val>` (Optical interrupt 1 or `rc=-6`) |
| **P22** | 3 | 4 | `HDD intr1` | `P22 HDD intr1: <val>` (HDD interrupt 1 or `rc=-6`) |
| **P23** | 3 | 5 | `BUS4 ndev` | `P23 BUS4 ndev: <n> devs` (total devices on Bus 4, typically 4) |

---

## 3. Photographing & Comparison Guide

### Photographing
1. Set the TV / monitor display aspect ratio so text is sharp and legible.
2. Capture a photo of each of the 3 menu opens (Open 1, Open 2, Open 3).
3. Ensure the leading `Pxx` page numbers are clearly readable in each photo.

### Key Comparison Points
When filling in the results below, focus on the following core discriminators between Optical and HDD:

1. **Interrupt Configuration (`intr0`, `intr1`)**:
   - HDD connects to interrupt `18 (0x12)`.
   - Does Optical have an interrupt assigned in the repository (`P17`, `P21`), or does it return `rc=-6 NO_ENT`?
2. **Storage Regions (`n_regs`)**:
   - In Linux/PS3 hypervisor terminology, `n_regs` specifies the number of storage partitions/regions.
   - Does Optical report `n_regs == 0` (`P11`) vs HDD (`P12`)?
3. **Block Size & Geometry (`blk_sz`, `n_blocks`)**:
   - Does Optical report 2048 bytes per sector (`P07`) vs HDD 512 bytes (`P08`)?
   - With/without media in the drive, does `n_blks` report disc sector count (`P09`)?
4. **Attributes (`meddling`, `pci_b`)**:
   - Are there specific flags set on HDD that are absent from Optical (`P13`, `P14`, `P15`, `P16`)?

---

## 4. Console Results Log (To be filled by Owner)

- **Date of Test**: `[YYYY-MM-DD]`
- **Console Model**: CECH-25xx (Slim)
- **Firmware**: 4.93 Evilnat PEX / Cobra 8.5
- **Disc Inserted**: `[Yes / No]` (if Yes, specify disc type: PS2 CD / PS2 DVD / Video DVD / Audio CD)

### Actual Observed Strings:
```text
Open 1:
P00: 
P01: 
P02: 
P03: 
P04: 
P05: 
P06: 
P07: 
P08: 

Open 2:
P09: 
P10: 
P11: 
P12: 
P13: 
P14: 
P15: 
P16: 
P17: 

Open 3:
P18: 
P19: 
P20: 
P21: 
P22: 
P23: 
(Wrap):
P00: 
P01: 
P02: 
```

### Analysis of Differences:
`[Fill in observations based on captured strings]`
