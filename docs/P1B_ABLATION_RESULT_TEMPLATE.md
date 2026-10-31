# P1b Ablation Result Template & Owner Guide

This guide describes how to run and interpret the **P1b Ablation Build** (`ps2_netemu_p1b_noopen.self`).

---

## 1. Owner Steps

> [!WARNING]
> Only the owner should perform installation and testing on the PS3 console. No agent script contacts the console directly.

1. Ensure PS3 is on, at the XMB, with webMAN MOD running (FTP and web server enabled).
2. Install the ablation SELF using PowerShell from the repository root:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_netemu.ps1 -File .\local_only\p1b_noopen\ps2_netemu_p1b_noopen.self -Force
   ```
   *(Note: `-Force` is required because `ps2_netemu_p1b_noopen.self` has a new hash).*
3. **Condition**: Start any PS2 ISO from webMAN MOD, **with NO disc in the drive**.
4. Press the **PS button** on the controller to bring up the in-game menu.
5. Highlight the `Debug Information` row. The label updates lazily on first display.
6. Cycle through or navigate the menu row selector (`selected & 3`) to view all 4 diagnostic pages (**Pages A, B, C, D**).
7. Take clear photographs of each of the 4 pages.
8. Exit the game to the XMB and restore the stock netemu:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore_netemu.ps1
   ```

---

## 2. Expected Labels (P1b Ablation Build)

### Page A (`selected & 3 == 0`): Summary
```
P1B DONE rom=1 open=OFF close=-
```
- `open=OFF`: Confirms that the ablation build is running and that `lv1_open_device` (170) and `lv1_close_device` (171) were **not** issued.

### Page B (`selected & 3 == 1`): Optical Node Details & 64-bit IDs
Expected on console:
```
ROM B=04 D=02 P=0 ID=4/2
```
(or `ID=HEX` if the repository returns non-index IDs).
- Shows the bus index (`04`), device index (`02`), port (`0`), and repository 64-bit IDs.

### Page C (`selected & 3 == 2`): Real HDD Control & Phat Match
Expected on console:
```
HDD B=4 D=0 P=2 PH=BOTH
```
- Confirms the netemu HDD on bus 4, dev 0, port 2, with both phat selectors matching (`PH=BOTH`).

### Page D (`selected & 3 == 3`): Raw Return Codes
Expected on console:
```
OP:SKIP CL:-- RP:-6(FA)
```
- `OP:SKIP`: Open was disabled/skipped.
- `CL:--`: Close was not attempted.
- `RP:-6(FA)`: First repository error code (LV1 -6 `LV1_NO_ENTRY`, expected when scanning empty bus/dev slots).

---

## 3. Decision Table

| Console Observation | Meaning & Diagnosis | Next Step |
|---|---|---|
| **Menu opens successfully, displaying `open=OFF` and IDs (Pages A–D visible)** | **PROVEN Root Cause:** The `open_device` (LV1 170) hypercall is the cause of the shutdown in P1b. LV1 treats an open on the optical drive from `ps2_netemu` as an unhandled security/policy violation, powering off the partition/console. | Documented in `docs/P1B_RESULT.md`. In-emulator direct LV1 open is denied/fatal without hypervisor patches; proceed to evaluate LV1/CFW optical device permission patches or Plan B (LV2 daemon / sector feeding). |
| **Console shuts down immediately upon pressing PS button** | **The cause is NOT the open call.** The shutdown is caused by shared code, table data, or memory access common to P1b. | **Next Suspect:** Suspect C (Extended RO segment size/mapping: 446 KB in P1b vs 127 KB in P1a).<br>**Next Ablation:** Build P1b with reduced string tables (matching P1a's 127 KB footprint) to isolate the loader's mapped memory limit. |
| **Menu displays, but shows garbage or unexpected label text** | An unhandled index calculation or memory corruption occurred. | Photograph all visible pages and report raw text to determine which struct field deviated. |

---

## 4. Binary Identification Hashes
- **Patched ELF**: `local_only/p1b_noopen/ps2_netemu_p1b_noopen.elf`
  - SHA256: `10aed0857daf4200b96537acb1d664e2da976020907301b0c29fbe96d030f5a2`
- **Patched SELF**: `local_only/p1b_noopen/ps2_netemu_p1b_noopen.self`
  - SHA256: `2cf25e816d128193f4e6e2c530192c5e0e425fa739fe706e2ad4055aa8a71cee`
