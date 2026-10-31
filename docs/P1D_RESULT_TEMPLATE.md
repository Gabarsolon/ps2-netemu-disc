# P1d Result Template: Hypercall Return Diagnostics (Variants A & B)

## Context & Purpose

The P1d diagnostic builds isolate the cause of the console power-off observed during P1b:
- **Variant A** (`ps2_netemu_p1d_A.self`): executes `lv1_open_device(bus_id = 9, dev_id = 0, flags = 0)` (HV 170). Bus ID 9 is outside the valid range 0..4; in 3.55 LV1 dispatch this returns `-17` (`LV1_NO_BUS` / `LV1_INVALID_PARAMETER`) immediately without touching any hardware device or slot state.
- **Variant B** (`ps2_netemu_p1d_B.self`): executes `lv1_close_device(bus_id = 4, dev_id = 2)` (HV 171) on the optical node without opening it first. In 3.55 LV1, caller is not an active opener, returning `-11` (`LV1_NOT_OWNER` / `WRONG_STATE`) without hardware mutation.

Neither variant touches real hardware. Both execute their single test call once lazily when opening the in-game PS-button menu.

---

## Owner Test Instructions

> [!IMPORTANT]
> **Safety Protocol:**
> 1. NEVER test Variant B before Variant A has completed and restored cleanly.
> 2. No disc is required in the drive for either test.
> 3. If either test causes the console to shut down, record it immediately and restore firmware using `tools\restore_netemu.ps1`.

### Step 1: Test Variant A (`ps2_netemu_p1d_A.self`)
1. From the PC terminal in `C:\Users\remus\ps2-netemu-disc`, install Variant A:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p1d\ps2_netemu_p1d_A.self -Force
   ```
2. On the PS3 (CECH-25xx, Evilnat 4.93 Cobra):
   - Launch any standard PS2 ISO from webMAN MOD.
   - Once the game reaches the title screen / gameplay, press the **PS button** to display the in-game menu.
3. Observe console behavior:
   - **Case A1 (Console powers off immediately)**: Record that Variant A caused a shutdown. Do NOT proceed to Variant B. Hard power-on and run `tools\restore_netemu.ps1`.
   - **Case A2 (Menu appears normally)**: Navigate down to the `Debug Information` item (rows 0 through 3).
     - Photograph Row 0 (Page A).
     - Photograph Row 1 (Page B).
     - Photograph Row 2 (Page C).
     - Photograph Row 3 (Page D).
4. Restore clean netemu baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

### Step 2: Test Variant B (`ps2_netemu_p1d_B.self`)
> [!WARNING]
> Only execute this step if Variant A returned cleanly (Case A2) and the baseline was restored.
1. Install Variant B:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p1d\ps2_netemu_p1d_B.self -Force
   ```
2. Launch any PS2 ISO, press the **PS button**, and observe:
   - **Case B1 (Console powers off immediately)**: Record shutdown. Hard power-on and run `tools\restore_netemu.ps1`.
   - **Case B2 (Menu appears normally)**: Photograph rows 0..3 (Pages A through D).
3. Restore clean netemu baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

## Expected vs Observed Labels

### Variant A
| Page | Expected (3.55 LV1 behavior) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P1D-A DONE open(9,0,0) rc=INVALID_PARAMETER` | | Confirms Variant A execution & decoded rc |
| **Page B (Row 1)** | `RC=FFFFFFEF (-17) INVALID_PARAMETER` | | Low 32-bit hex & decimal code |
| **Page C (Row 2)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository node and control status |
| **Page D (Row 3)** | `OP:-17(PARAM) CL:-- RP:-6(FA)` | | Hypercall scan summary |

### Variant B
| Page | Expected (3.55 LV1 behavior) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P1D-B DONE close(4,2) rc=NOT_OWNER/WRONG_STATE` | | Confirms Variant B execution & decoded rc |
| **Page B (Row 1)** | `RC=FFFFFFF5 (-11) NOT_OWNER/WRONG_STATE` | | Low 32-bit hex & decimal code |
| **Page C (Row 2)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository node and control status |
| **Page D (Row 3)** | `OP:SKIP CL:-11(STATE) RP:-6(FA)` | | Hypercall scan summary |

---

## Decision Table & Interpretation

| Outcome | Interpretation | Root Cause Location | Next Steps |
|---|---|---|---|
| **Variant A returns `-17` (or other clean error code)** | The hypercall mechanism (`sc 0` wrapper, bridge at `0xc50..0xca0`, TOC/stack restoration, calling from menu hook) is **safe and functional**. The P1b shutdown was **not** caused by hypercall invocation or context. | Specific to the optical open: either optical open succeeded and triggered an unhandled hardware interrupt/event, or 4.93 LV1 enforces a strict partition panic when netemu touches real optical hardware. | Proceed to test Variant B. If both clean, design a controlled optical open with masked interrupts (`MSR.EE=0`) and durable post-open mailbox diagnostic. |
| **Variant A shuts console down** | The failure occurs *inside the hypercall path itself*, before or during dispatch. | The guest `sc 0` bridge, leaf trampoline ABI, register corruption (`r2`, `r1`, `r13`), or calling hypercall 170 from the menu hook thread. | Investigate bridge dispatch at `0xc50..0xca0`, MSR privilege states, and caller thread context. Real optical node was never touched. |
| **Variant B returns `-11` (or other clean error code)** | Calling `lv1_close_device` on an un-owned device returns cleanly without fault. | Close path is verified safe. In P1b, close was only reached if open returned 0. | Confirms close itself is not intrinsically fatal on un-owned devices. |
| **Variant B shuts console down** | Calling `lv1_close_device` triggers a panic or checkstop even on an unopened device. | `lv1_close_device` dispatch / bridge path or hypercall 171 restriction in modern LV1. | Focus on hypercall 171 dispatch differences between 3.55 and 4.93 LV1. |
| **Both Variants return cleanly (`-17` and `-11`)** | Hypercall invocation, argument passing, return code capture, and menu rendering are **100% verified sound**. | The P1b console power-off was caused specifically by `lv1_open_device` on the live optical node `(4, 2, 0)`. | Next diagnostic: perform `lv1_open_device(4, 2, 0)` with interrupts masked (`MSR.EE = 0`), write return code immediately to persistent mailbox, and halt without closing to isolate open success from interrupt delivery. |
