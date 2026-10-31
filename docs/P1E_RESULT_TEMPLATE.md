# P1e Result Template: Hypercall Isolation Diagnostic (Stock sc vs Code Slot sc)

## Context & Purpose

The P1e diagnostic build isolates the cause of the console crashes observed in P1b (real optical open) and P1d-A (invalid bus 9 open):
- In P1d-A, issuing `lv1_open_device(bus_id=9, dev_id=0, flags=0)` crashed (powered off) the CECH-25xx console immediately. Because bus 9 is invalid and touches no real hardware or device slots, the failure proved that either:
  1. **Our own `sc 0` wrapper in the code slot (or the menu hook context)** is fatal when executing hypercalls (whereas normal repository reads LV1 91 execute through the stock helper `0x111eb8` whose `sc 0` is at `0x111f10` in stock text).
  2. **LV1 call 170 (`open_device`) itself is fatal** from this partition after initialization (or in 4.93 / Evilnat).

P1e directly tests this distinction by issuing a **harmless, known-good hypercall (LV1 91 repository read of `bus/4/dev/2/type`)** through a **brand-new own `sc 0` wrapper in the code slot** (`lv1_repo_raw` at `0x4800`, with `sc 0` at `0x4828`), passing the identical register arguments that stock helper `0x111eb8` passes.
Both the stock helper's result (already in the mailbox from the normal scan) and our raw wrapper's result are displayed side-by-side.

---

## Owner Test Instructions

> [!IMPORTANT]
> **Safety Protocol:**
> 1. No disc is required in the drive for this test.
> 2. If the console shuts down when the PS button is pressed, record that immediately and restore firmware using `tools\restore_netemu.ps1`.
> 3. Do not run any other tools or modified builds until results are recorded.

### Test Procedure (`ps2_netemu_p1e.self`)
1. From the PC terminal in `C:\Users\remus\ps2-netemu-disc`, install P1e:
   ```powershell
   tools\install_netemu.ps1 -File local_only\p1e\ps2_netemu_p1e.self -Force
   ```
2. On the PS3 (CECH-25xx, Evilnat 4.93 Cobra):
   - Launch any standard PS2 ISO from webMAN MOD (no disc inserted).
   - Once the game reaches the title screen / gameplay, press the **PS button** to display the in-game menu.
3. Observe console behavior:
   - **Case 1 (Console powers off immediately)**: Record that P1e caused a power-off. No label will be seen. Power on the console and restore clean netemu:
     ```powershell
     tools\restore_netemu.ps1
     ```
   - **Case 2 (Menu appears normally)**: Navigate down to the `Debug Information` item. Cycle through rows 0..3 using the D-pad (highlighting row `selected & 3` selects Page A, B, C, D):
     - Photograph Row 0 (Page A).
     - Photograph Row 1 (Page B).
     - Photograph Row 2 (Page C).
     - Photograph Row 3 (Page D).
4. Restore clean netemu baseline:
   ```powershell
   tools\restore_netemu.ps1
   ```

---

## Expected vs Observed Labels

| Page | Expected (Code Slot Wrapper Safe) | Observed on Console (Owner) | Notes |
|---|---|---|---|
| **Page A (Row 0)** | `P1E-RAW DONE rc=SUCCESS v=5(ROM)` | | Value read through our own `sc 0` wrapper in code slot |
| **Page B (Row 1)** | `P1E-STOCK DONE rc=SUCCESS v=5(ROM)` | | Value read through stock helper `0x111eb8` for the same node |
| **Page C (Row 2)** | `P1E MATCH: RAW==STOCK (RC=0 SUCCESS, V=5 ROM)` | | Verification that raw wrapper matches stock helper |
| **Page D (Row 3)** | `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH` | | Repository scan summary (ROM & HDD detection) |

---

## Decision Table & Interpretation

| Console Outcome | Interpretation | Root Cause Conclusion | Next Step |
|---|---|---|---|
| **Case 1: Console powers off immediately upon pressing PS button** | Issuing hypercalls from our own `sc` wrapper in the code slot (or from the menu-hook context outside the stock text) is fatal. | The P1b and P1d-A crashes were **NOT** caused by `lv1_open_device` (170). The crash was triggered because the hypercall executed from our code slot / own wrapper. | The way forward is to **call hypercalls strictly through stock call sites** (e.g. hijacking/hooking stock functions like `0x111eb8` or trampoline into stock text), never issuing `sc 0` directly from the code slot. |
| **Case 2: Menu appears, Page C shows `MATCH` (raw == stock == 5)** | Our own `sc 0` wrapper in the code slot and the menu-hook evaluation context are **100% safe and functional**. | The P1b and P1d-A crashes were **NOT** caused by the wrapper, code slot execution, or the menu context. Therefore, **LV1 call 170 (`open_device`) itself is fatal** for this partition after initialization (or strictly forbidden by Evilnat 4.93 / LV1 policy). | Stop trying to open storage devices with `lv1_open_device` from netemu. Pursue Plan B (external USB optical drive through netemu's working USB stack) or Plan C (CFW/Cobra kernel patches before netemu launch). |
| **Case 3: Menu appears, Page C shows `DIFF` (raw != stock)** | The raw wrapper executed and returned cleanly without crashing, but returned a different value or error code compared to the stock helper. | **Register or convention mismatch**: our raw wrapper did not pass identical registers, or partition-ID handling differed, or LV1 returned a specific error code. | Inspect Page A (`rc` and `v`) and Page B to determine exact mismatch and refine register arguments. |
