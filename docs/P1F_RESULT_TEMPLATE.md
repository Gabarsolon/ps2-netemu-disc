# P1f Result Template: Stock Helper Clone (sc 0 Isolation Probe)

## Build Metadata
- **ELF**: `local_only/p1f/ps2_netemu_p1f.elf` (`aab7d2ed6fb9e1bb575c74a0ec352c7a5109142223b72c592d0a0b266ed5edbe`)
- **SELF**: `local_only/p1f/ps2_netemu_p1f.self` (`abc8eeeed7a51fc093a87469540e785b9a06d2f917da88b3c38596b5a456d655`)
- **Round-Trip ELF**: `local_only/p1f/roundtrip.elf` (matches `ps2_netemu_p1f.elf` byte for byte)

---

## Owner Test Instructions

### Step 1: Install P1f SELF
Open PowerShell (as Administrator if needed) and run:
```powershell
powershell -ExecutionPolicy Bypass -File tools\install_netemu.ps1 -File local_only\p1f\ps2_netemu_p1f.self -Force
```
*(The installer verifies hashes, mounts `dev_blind`, uploads `ps2_netemu.self` to `/dev_blind/ps2emu/`, verifies MD5/SHA256 of the uploaded file, and unmounts `dev_blind` in a `finally` block).*

### Step 2: Launch and Observe
1. Launch any normal PS2 ISO from webMAN MOD (no disc in the drive needed).
2. Once the game boots, press the **PS button** to display the in-game menu.
3. Highlight the menu row containing **Debug Information**.
4. By cycling menu rows (`selected & 3`), observe Pages A, B, C, D:
   - **Page A** (`selected & 3 == 0`): Clone LV1 91 result:
     - Expected: `P1F-CLONE DONE rc=SUCCESS v=5(ROM)`
   - **Page B** (`selected & 3 == 1`): Stock helper LV1 91 result for the same node:
     - Expected: `P1F-STOCK DONE rc=SUCCESS v=5(ROM)`
   - **Page C** (`selected & 3 == 2`): Match determination:
     - Expected: `P1F MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)`
   - **Page D** (`selected & 3 == 3`): Scan summary:
     - Expected: `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`
5. Photograph or record the TV screen showing the Debug Information row on each page.

### Step 3: Restore Stock Emulator
When testing is complete, restore the stock emulator binary:
```powershell
powershell -ExecutionPolicy Bypass -File tools\restore_netemu.ps1 -Force
```

---

## Decision Table

| Console Outcome | Interpretation | Architectural Meaning & Next Steps |
|---|---|---|
| **Console boots menu cleanly, Page C shows `P1F MATCH: CLONE==STOCK`** | **Hypothesis B Confirmed: Wrapper Defect** | - Executing `sc 0` from the code slot (`0x4800..0x7FF0`) is **100% fine** on CECH-25xx Evilnat 4.93 Cobra.<br>- The P1b, P1d-A, and P1e crashes were caused by defects in our hand-written wrapper (specifically CR preservation, standard 0x80 stack frame geometry, and non-volatile register usage), **NOT by LV1 rejecting the call or restricting `sc 0` to stock text**.<br>- **Next Step**: Build a generic clone with variable `r11` (allowing any hypercall number, including 170 `lv1_open_device` and 171 `lv1_close_device`). Issuing 170 on the optical node through this validated clone approach is the viable path forward. |
| **Console powers off upon opening menu** | **Hypothesis A Confirmed: Location / Memory Constraint** | - The `sc 0` location matters (or the code slot memory page has execution permissions that fault on hypercall entry, or guest kernel / LV1 / Cobra checks caller address SRR0).<br>- Even with the exact instructions, stack layout, and CR preservation of the stock helper, an `sc` in the code slot is fatal.<br>- **Next Step**: Do not issue hypercalls from the code slot. Instead, find stock text sites we can reuse (e.g. existing stock hypercall wrappers or spare `sc` sites in stock text) or investigate SRR0 checks in LV1 / Cobra. |
| **Console runs, Page C shows `P1F DIFF: ...`** | **Result Divergence** | - The clone executed without crashing, but returned a different return code or value than the stock helper for the identical repository node.<br>- Compare the reported `rc` and `v` on Pages A and B to identify discrepancy (e.g. partition selector, argument folding, or out pointer writeback). |
| **Menu displays stock label `Debug Information`** | **Hook Inactive / Fail-Open** | - The hook at `0x270FFC` was bypassed or failed open due to word mismatch. Check console firmware version and hook offset. |
