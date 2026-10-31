# P1c Console Result Template: Optical vs HDD Repository Dumper

This document outlines the procedure for the console owner to run the **P1c** read-only repository probe on the PS3, step through all 24 result pages, photograph the output, and record the repository comparison between the Optical node (ROM) and the HDD node.

---

## 1. Owner Execution Steps

> [!IMPORTANT]
> The automated assistant is strictly forbidden from running console install/restore scripts or communicating with the PS3 over the network. The commands below are for the **human owner** to run manually from their PowerShell terminal.

### Step 1: Install the P1c Probe
From the repository root (`C:\Users\remus\ps2-netemu-disc`):
```powershell
tools\install_netemu.ps1 -File local_only\p1c\ps2_netemu_p1c.self -Force
```

### Step 2: Launch a PS2 ISO
1. On the PS3, launch any PS2 ISO using webMAN MOD.
2. Wait for the game to start rendering under `ps2_netemu`.

### Step 3: Open the In-Game Menu
1. Press the **PS button** on the Sixaxis/DualShock 3 controller to bring up the in-game menu.
2. Locate the row with the modified label (replaces the stock `"Debug Information"` label).

### Step 4: Step Through All 24 Pages
The pager uses a 6-bank x 4-row scheme:
- Moving the selection cursor up and down within the 4 visible menu rows displays subpages (0, 1, 2, 3) for the current bank.
- **To advance to the next bank**: Move the cursor down to the 4th row (Row 3), then press **D-pad Down** once more to wrap around to the 1st row (Row 0). Each downward loop through the rows advances to the next bank (`Bank 0 -> Bank 1 -> Bank 2 -> Bank 3 -> Bank 4 -> Bank 5 -> wraps to Bank 0`).
- **To go back to the previous bank**: From Row 0, press **D-pad Up** to wrap around to Row 3.

### Step 5: Restore the Stock Binary
After recording/photographing the labels:
```powershell
tools\restore_netemu.ps1
```

---

## 2. Page Inventory (Pages 00 to 23)

Each page label is formatted to a maximum of 31 ASCII characters plus null terminator:

| Page | Bank | Row | Key / Target | Expected Output / Meaning |
|---|---|---|---|---|
| **P00** | 0 | 0 | **Summary** | `P00 P1C r=<roms> h=<hdd> id=4/2 p=0` (Optical bus 4, dev 2, port 0, IDs 4/2) |
| **P01** | 0 | 1 | `OPT type` | `P01 OPT type: 5 (ROM)` |
| **P02** | 0 | 2 | `HDD type` | `P02 HDD type: 0 (DISK)` |
| **P03** | 0 | 3 | `OPT id` | `P03 OPT id: 2 (ROM DEV)` |
| **P04** | 1 | 0 | `HDD id` | `P04 HDD id: 0` |
| **P05** | 1 | 1 | `OPT port` | `P05 OPT port: 0 (PORT0)` |
| **P06** | 1 | 2 | `HDD port` | `P06 HDD port: 2 (PORT2)` |
| **P07** | 1 | 3 | `OPT blk_sz` | `P07 OPT blk_sz: 2048 (0x800)` (or `rc=-6 NO_ENT` without media) |
| **P08** | 2 | 0 | `HDD blk_sz` | `P08 HDD blk_sz: 512 (0x200)` |
| **P09** | 2 | 1 | `OPT n_blks` | `P09 OPT n_blks: 0 (NO DISC)` (or sector count) |
| **P10** | 2 | 2 | `HDD n_blks` | `P10 HDD n_blks: 0x<hex>` (HDD total sector count) |
| **P11** | 2 | 3 | `OPT n_regs` | `P11 OPT n_regs: 0 (NO REGS)` (storage-region count) |
| **P12** | 3 | 0 | `HDD n_regs` | `P12 HDD n_regs: <n>` (storage-region count) |
| **P13** | 3 | 1 | `OPT meddl` | `P13 OPT meddl: <val>` (ownership/meddling attribute or `rc=-6`) |
| **P14** | 3 | 2 | `HDD meddl` | `P14 HDD meddl: <val>` (ownership/meddling attribute or `rc=-6`) |
| **P15** | 3 | 3 | `OPT pci_b` | `P15 OPT pci_b: <val>` (PCI bus or `rc=-6 NO_ENT`) |
| **P16** | 4 | 0 | `HDD pci_b` | `P16 HDD pci_b: <val>` (PCI bus or `rc=-6 NO_ENT`) |
| **P17** | 4 | 1 | `OPT intr0` | `P17 OPT intr0: <val>` (Optical interrupt type/ID or `rc=-6`) |
| **P18** | 4 | 2 | `HDD intr0` | `P18 HDD intr0: 18 (0x12 HDD)` |
| **P19** | 4 | 3 | `OPT reg0_t` | `P19 OPT reg0_t: <val>` (MMIO register 0 type or `rc=-6`) |
| **P20** | 5 | 0 | `HDD reg0_t` | `P20 HDD reg0_t: <val>` (MMIO register 0 type or `rc=-6`) |
| **P21** | 5 | 1 | `OPT intr1` | `P21 OPT intr1: <val>` (Optical interrupt 1 or `rc=-6`) |
| **P22** | 5 | 2 | `HDD intr1` | `P22 HDD intr1: <val>` (HDD interrupt 1 or `rc=-6`) |
| **P23** | 5 | 3 | `BUS4 ndev` | `P23 BUS4 ndev: <n> devs` (total devices on Bus 4, typically 4) |

---

## 3. Photographing & Comparison Guide

### Photographing
1. Set the TV / monitor display aspect ratio so text is sharp and legible.
2. Capture a photo of each page from **P00** through **P23** (or at minimum, note down the text string for each page).
3. Ensure the leading `Pxx` page marker is clearly visible.

### Key Comparison Points
When filling in the results below, focus on the following core discriminators between Optical and HDD:

1. **Interrupt Configuration (`intr0`, `intr1`)**:
   - HDD connects to interrupt `18 (0x12)`.
   - Does Optical have an interrupt assigned in the repository, or does it return `rc=-6 NO_ENT`?
2. **Storage Regions (`n_regs`)**:
   - In Linux/PS3 hypervisor terminology, `n_regs` specifies the number of storage partitions/regions.
   - Does Optical have `n_regs == 0`?
3. **Block Size & Geometry (`blk_sz`, `n_blocks`)**:
   - Does Optical report 2048 bytes per sector?
4. **Attributes (`meddling`, `pci_b`)**:
   - Are there specific flags set on HDD that are absent from Optical?

---

## 4. Console Results Log (To be filled by Owner)

- **Date of Test**: `[YYYY-MM-DD]`
- **Console Model**: CECH-25xx (Slim)
- **Firmware**: 4.93 Evilnat PEX / Cobra 8.5
- **Disc Inserted**: `[Yes / No]` (if Yes, specify disc type: PS2 CD / PS2 DVD / Video DVD)

### Actual Observed Strings:
```text
P00: 
P01: 
P02: 
P03: 
P04: 
P05: 
P06: 
P07: 
P08: 
P09: 
P10: 
P11: 
P12: 
P13: 
P14: 
P15: 
P16: 
P17: 
P18: 
P19: 
P20: 
P21: 
P22: 
P23: 
```

### Analysis of Differences:
`[Fill in observations based on captured strings]`
