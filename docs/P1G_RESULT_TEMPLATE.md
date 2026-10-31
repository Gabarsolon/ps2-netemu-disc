# P1g Result Template: Generic Safe Hypercall Wrapper & Diagnostic Variants (G0..G3)

## Context & Purpose

The P1g builds introduce `lv1_hcall(num, a1, a2, a3, a4, a5)`: a generic, safe hypercall wrapper modeled directly on the proven stock helper (`0x111eb8`), maintaining its exact 0x80 stack frame geometry, Condition Register saving/restoration (`cr2`, `cr3`, `cr4`), Link Register preservation, and non-volatile register discipline (`r30`, `r31`, `r14..r29`).

Four variants test this wrapper on hardware in strict order:
- **Variant G0** (`ps2_netemu_p1g_G0.self`): executes LV1 91 (repository read of optical node type) through the NEW generic wrapper. Expected to match the stock helper (`rc=0`, `val=5 ROM`). Validates the wrapper on console before any open/close call is attempted.
- **Variant G1** (`ps2_netemu_p1g_G1.self`): executes `lv1_hcall(170, 9, 0, 0)` (`lv1_open_device` with invalid bus 9). Bus 9 is rejected at outer dispatch; expected `-17` (`LV1_INVALID_PARAMETER`). Touches no device or hardware.
- **Variant G2** (`ps2_netemu_p1g_G2.self`): executes `lv1_hcall(171, 4, 2)` (`lv1_close_device` on optical node without opening). Expected `-11` (`LV1_NOT_OWNER`).
- **Variant G3** (`ps2_netemu_p1g_G3.self`): executes `lv1_hcall(170, 4, 2, 0)` (the REAL open of optical node, flags 0); if rc == 0, immediately executes `lv1_hcall(171, 4, 2)` to close it. Records both return codes. NOTE: Netemu partition profile leaves the physical PCI bus unpowered (`docs/P0I_LV1_493_ANALYSIS.md`); a real open carries hardware risk (hang or Syscon power-off).

---

## Owner Test Instructions

> [!IMPORTANT]
> **Safety Protocol:**
> 1. **STRICT SEQUENCE**: Test **G0 FIRST**. Only proceed to G1 if G0 matches stock and powers on normally. Only proceed to G2 after G1 returns cleanly. Only proceed to G3 after G2 returns cleanly.
> 2. **NO DISC NEEDED** for G0, G1, and G2.
> 3. For **G3**: run **first WITHOUT a disc in the drive**. If that succeeds, run a second time **WITH a PS2 disc inserted**.
> 4. If any test causes the console to shut down, record it immediately. Hard power-on and run `tools\restore_netemu.ps1`. DO NOT proceed to subsequent variants!

---

### Step 1: Test Variant G0 (`ps2_netemu_p1g_G0.self`)
1. From the PC terminal in `C:\Users\remus\ps2-netemu-disc`:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p1g\ps2_netemu_p1g_G0.self -Force
   ```
2. On the PS3 (CECH-25xx, Evilnat 4.93 Cobra):
   - Launch any standard PS2 ISO from webMAN MOD (no physical disc required).
   - Once the game reaches the title screen / gameplay, press the **PS button** to display the in-game menu.
3. Observe console behavior:
   - **Case G0-Fail (Console powers off immediately)**: Record that the generic wrapper is still defective. Do NOT proceed to G1! Hard power-on and run `tools\restore_netemu.ps1`.
   - **Case G0-Pass (Menu appears normally)**:
     - Navigate to `Debug Information` (rows 0 through 3).
     - Photograph Row 0 (Page A).
     - Photograph Row 1 (Page B).
     - Photograph Row 2 (Page C).
     - Photograph Row 3 (Page D).
4. Restore clean netemu baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 2: Test Variant G1 (`ps2_netemu_p1g_G1.self`)
> [!WARNING]
> Only execute this step if Variant G0 produced a clean MATCH on Page C and restored cleanly.
1. Install Variant G1:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p1g\ps2_netemu_p1g_G1.self -Force
   ```
2. Launch any PS2 ISO, press the **PS button**, and observe:
   - **Case G1-Fail (Shutdown)**: Record shutdown. Run `tools\restore_netemu.ps1`.
   - **Case G1-Pass (Menu appears)**: Photograph rows 0..3 (Pages A through D).
3. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 3: Test Variant G2 (`ps2_netemu_p1g_G2.self`)
> [!WARNING]
> Only execute this step if Variant G1 returned cleanly (-17) and restored cleanly.
1. Install Variant G2:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p1g\ps2_netemu_p1g_G2.self -Force
   ```
2. Launch any PS2 ISO, press the **PS button**, and observe:
   - **Case G2-Fail (Shutdown)**: Record shutdown. Run `tools\restore_netemu.ps1`.
   - **Case G2-Pass (Menu appears)**: Photograph rows 0..3 (Pages A through D).
3. Restore clean baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

### Step 4: Test Variant G3 (`ps2_netemu_p1g_G3.self`)
> [!CAUTION]
> Highest hardware risk. Run **first without a disc**, then (if successful) **with a PS2 disc inserted**.
1. Install Variant G3:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p1g\ps2_netemu_p1g_G3.self -Force
   ```
2. Launch any PS2 ISO (drive empty), press the **PS button**, and observe:
   - **Case G3-Shutdown / Hang**: The console cuts power or freezes upon opening optical node. Record shutdown.
   - **Case G3-Menu appears**: Photograph rows 0..3 (Pages A through D). Record both open and close return codes on Page C!
3. If Step 2 succeeded without shutdown, insert a genuine PS2 disc into the drive, launch PS2 ISO, press **PS button**, and photograph Pages A through D again.
4. Restore clean netemu baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

## Expected vs Observed Labels

### Variant G0 (`ps2_netemu_p1g_G0.self`)
| Page | Expected (Wrapper Validation) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P1G-G0 DONE read(4,2) rc=SUCCESS v=5(ROM)` | | Generic wrapper repository read |
| **Page B (Row 1)** | `RC=00000000 (0) SUCCESS` | | Raw return code in hex & decimal |
| **Page C (Row 2)** | `P1G MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)` | | Confirms generic wrapper equals stock |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

### Variant G1 (`ps2_netemu_p1g_G1.self`)
| Page | Expected (4.93 LV1 Outer Dispatch) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P1G-G1 DONE open(9,0,0) rc=INVALID_PARAMETER` | | Bus 9 open result |
| **Page B (Row 1)** | `RC=FFFFFFEF (-17) INVALID_PARAMETER` | | Low 32-bit hex return code |
| **Page C (Row 2)** | `P1G-G1 OP:INVALID_PARAMETER CL:--` | | Single hypercall status |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

### Variant G2 (`ps2_netemu_p1g_G2.self`)
| Page | Expected (4.93 LV1 Device Slot Check) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P1G-G2 DONE close(4,2) rc=NOT_OWNER/WRONG_STATE` | | Unopened optical close result |
| **Page B (Row 1)** | `RC=FFFFFFF5 (-11) NOT_OWNER` | | Low 32-bit hex return code |
| **Page C (Row 2)** | `P1G-G2 OP:-- CL:NOT_OWNER/WRONG_STATE` | | Single hypercall status |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

### Variant G3 (`ps2_netemu_p1g_G3.self`)
| Page | Expected (Hypothetical Outcomes) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P1G-G3 DONE open(4,2,0) rc=<name>` | | Real optical open rc |
| **Page B (Row 1)** | `RC=<hex> (<dec>) <name>` | | Raw return code |
| **Page C (Row 2)** | `P1G-G3 OP:SUCCESS CL:SUCCESS` (or `OP:<name> CL:NONE`) | | Both open and close return codes |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary |

---

## Decision Table & Root Cause Analysis

| Variant | Observed Outcome | Interpretation | Root Cause Location | Next Steps |
|---|---|---|---|---|
| **G0** | **MATCH (`rc=0, v=5 ROM`)** | **PROVEN**: Generic wrapper `lv1_hcall` is 100% sound, ABI-compliant, and safe on hardware. | Wrapper validated. | Proceed immediately to **Variant G1**. |
| **G0** | **Console powers off** | Generic wrapper still has a register/stack/ABI defect. | Calling convention or epilogue store. | **STOP immediately**. Do NOT test G1/G2/G3. Re-examine stock helper disassembly. |
| **G1** | **`rc = -17` (`INVALID_PARAMETER`)** | **PROVEN**: `lv1_open_device` (HV 170) path works from the netemu partition. Outer dispatch rejects invalid bus cleanly. | Hypercall 170 dispatcher is functional. | Proceed to **Variant G2**. |
| **G1** | **Console powers off** | HV 170 itself is strictly prohibited or hooked/panicked by CFW/Cobra stage2. | LV1 hypercall 170 privilege or CFW hook. | Inspect Cobra stage2 HV 170 handling. Optical node is NOT the cause. |
| **G2** | **`rc = -11` (`NOT_OWNER`)** | **PROVEN**: `lv1_close_device` (HV 171) works cleanly on non-owned devices without panic. | Close path verified. | Proceed to **Variant G3**. |
| **G2** | **Console powers off** | HV 171 triggers panic or checkstop even on unowned devices. | LV1 hypercall 171 restriction in modern LV1. | Focus on HV 171 dispatch in LV1. |
| **G3** | **`OP:SUCCESS CL:SUCCESS` (`rc=0 + close rc=0`)** | **MASSIVE BREAKTHROUGH**: The netemu partition **CAN** open and claim the physical Blu-ray / DVD optical drive! The physical PCI bus is usable! | Optical drive hardware interface is active. | Proceed to **Phase 2 (P2)**: Construct event port (HV 18), interrupt binding (HV 197), and issue read commands! Direct disc play is viable! |
| **G3** | **`OP:DENIED_BY_POLICY` (`rc = -4`)** | Storage open checks caller LAID via `0x31ce8c` (`ss/laid`) and policy denies netemu partition. | Partition authority profile (`SCE_CELLOS_SYSTEM_MGR_PS2_NE`). | Investigate Cobra patch to grant optical authority to netemu partition in LV1. |
| **G3** | **`OP:NO_PRIVILEGE` (`rc = -3`)** | Hypercall privilege table rejects call 170 for current privilege level. | Privilege configuration. | Investigate bridge table at `0x238c`. |
| **G3** | **`OP:BUSY` (`rc = -9`)** | Optical device Slot 0 is already claimed by GameOS/VSH or another LPAR. | Opener slot collision (`+0x9f0`). | Release drive from VSH/GameOS before entering netemu, or claim Slot 1. |
| **G3** | **Console powers off / hangs** | **CONFIRMED**: `PS2_NE_LPAR` profile leaves physical PCI bus unpowered (`0x8001dad8`). Claiming the live drive object triggers hardware bus fault / Syscon shutdown. | Hardware bus power in LPAR profile. | Investigate enabling PCI bus power method (`0x8001decc`) via LV1 patch in Cobra stage2, or Plan B (USB optical drive). |
