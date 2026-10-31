# P1b Result Template & Owner Guide

Guide for decoding the `Debug Information` row labels on the PS-button menu when running `ps2_netemu_p1b.self`.

---

## 1. How to Test (Owner Steps)

> [!WARNING]
> Only the owner should perform installation and testing on the PS3 console. No agent script contacts the console directly.

1. Ensure PS3 is on, at the XMB, with webMAN MOD running (FTP and web server enabled).
2. Install the probe SELF using PowerShell:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_netemu.ps1 -File .\local_only\p1b\ps2_netemu_p1b.self -Force
   ```
   *(Note: `-Force` is required because `ps2_netemu_p1b.self` has a new hash not in the legacy allow-list).*
3. Launch any PS2 game from webMAN MOD as usual.
4. Press the **PS button** on the controller to bring up the in-game menu.
5. Highlight the `Debug Information` row. The label updates lazily on first display.
6. The menu row selector (`selected & 3`) provides 4 diagnostic pages (A, B, C, D). Navigate or cycle through the sub-items to view each page.
7. Take a clear photo of each of the 4 pages (A, B, C, D).
8. Once finished testing, exit the game to the XMB and restore the stock netemu:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore_netemu.ps1
   ```

---

## 2. Label Page Decoding

### Page A (`selected & 3 == 0`): Summary Page
Format:
```
P1B DONE rom=<R> open=<OPEN> close=<CLOSE>
```
- `rom=<R>`: Total count of optical/ROM storage devices discovered (device type 5):
  - `rom=1`: Optical drive node was found in repository.
  - `rom=0`: No optical drive node was found (open is skipped).
- `open=<OPEN>`: Outcome of `lv1_open_device(rom_bus_id, rom_dev_id, 0)`:
  - `open=OK`: Hypercall returned 0 (`LV1_SUCCESS`). Partition was granted permission to open the optical drive!
  - `open=DENIED`: Hypercall returned `-4` (`LV1_DENIED_BY_POLICY`), `-3` (`LV1_NO_PRIVILEGE`), or `-5` (`LV1_ACCESS_VIOLATION`). Hypervisor policy disallows direct access from ps2_netemu partition.
  - `open=ERR`: Hypercall returned another error (e.g. `-9` `LV1_BUSY`, `-17` `LV1_INVALID_PARAMETER`).
  - `open=SKIP`: No optical device found; open was not attempted.
- `close=<CLOSE>`: Outcome of `lv1_close_device(rom_bus_id, rom_dev_id)`:
  - `close=OK`: Close hypercall returned 0. Device released cleanly.
  - `close=-`: Close was not attempted (e.g. open was skipped or open failed).
  - `close=ERR`: Close hypercall returned nonzero.

---

### Page B (`selected & 3 == 1`): Optical Node Details & 64-bit IDs
If `rom == 0`:
```
P1B NO ROM DEV (R=0)
```
If `rom >= 1`:
```
ROM B=<BB> D=<DD> P=<P> ID=<BUS_ID>/<DEV_ID>
```
- `B=<BB>`: Bus index (00..15) where the optical device was found (expected: `04` on CECH-25xx).
- `D=<DD>`: Device index (00..15) on that bus (expected: `02` per P1a).
- `P=<P>`: Port value (`0`, `1`, `2`, or `?`). Expected: `0`.
- `ID=<BUS_ID>/<DEV_ID>`: 64-bit bus ID and device ID read from the repository:
  - `ID=4/2`: Standard repository mapping (`bus_id == 4`, `dev_id == 2`).
  - `ID=500/501`: Emulation fixture ID mapping.
  - `ID=HEX`: Other non-standard ID values.

---

### Page C (`selected & 3 == 2`): Real HDD Control & Phat Selector Match
If `hdd == 0`:
```
HDD: NOT FOUND (PROBE INVALID)
```
If `hdd == 1`:
```
HDD B=<B> D=<D> P=<P> <PHAT>
```
- `B=<B>`: Bus index of the netemu HDD control (expected: `4`).
- `D=<D>`: Device index of HDD control (expected: `0`).
- `P=<P>`: Port of HDD control (expected: `2`).
- `<PHAT>`: Phat emulator selector match:
  - `PH=-/-`: Neither phat selector matched.
  - `PH=EMU`: Matches `ps2_emu` selector (`bus_type == 5` storage bus).
  - `PH=GX`: Matches `ps2_gxemu` selector (`bus_index == 4`).
  - `PH=BOTH`: Both conditions matched (expected on CECH-25xx: bus 4 is type 5).

---

### Page D (`selected & 3 == 3`): Raw Return Codes & Diagnostics
Format:
```
OP:<OPEN_RC> CL:<CLOSE_RC> RP:<REPO_RC>
```
- `OP:<OPEN_RC>`: Detailed return code from `lv1_open_device`:
  - `OP:0(OK)`: 0 (`LV1_SUCCESS`).
  - `OP:-4(DENIED)`: `-4` / `0xFFFFFFFC` (`LV1_DENIED_BY_POLICY`).
  - `OP:-3(NO_PRIV)`: `-3` / `0xFFFFFFFD` (`LV1_NO_PRIVILEGE`).
  - `OP:-5(ACC_VIOL)`: `-5` / `0xFFFFFFFB` (`LV1_ACCESS_VIOLATION`).
  - `OP:-9(BUSY)`: `-9` / `0xFFFFFFF7` (`LV1_BUSY`).
  - `OP:-2(SHORT)`: `-2` / `0xFFFFFFFE` (`LV1_RESOURCE_SHORTAGE`).
  - `OP:-17(PARAM)`: `-17` / `0xFFFFFFEF` (`LV1_INVALID_PARAMETER`).
  - `OP:SKIP`: Open was skipped.
  - `OP:ERR(HEX)`: Other error code.
- `CL:<CLOSE_RC>`: Detailed return code from `lv1_close_device`:
  - `CL:0(OK)`: 0 (`LV1_SUCCESS`).
  - `CL:--`: Close not attempted.
  - `CL:<RC>(<NAME>)`: Error code if close failed.
- `RP:<REPO_RC>`: First non-zero repository lookup error:
  - `RP:0(OK)`: All lookups succeeded.
  - `RP:-6(FA)`: `-6` / `0xFFFFFFFA` (`LV1_NO_ENTRY`, expected when scanning empty slots).
  - `RP:-1(ENOENT)`: `-1` lookup error.
  - `RP:<RC>(<HEX>)`: Specific error.

---

## 3. Decision Table

| Outcome | Page A | Page B | Page C | Page D | Meaning & Next Project Step |
|---|---|---|---|---|---|
| **OPEN OK (PRIMARY SUCCESS)** | `rom=1, open=OK, close=OK` | `ROM B=04 D=02 P=0 ID=4/2` | `HDD B=4 D=0 P=2 PH=BOTH` | `OP:0(OK) CL:0(OK)` | **The ps2_netemu partition HAS PERMISSION to open the optical drive!** Proceed to **P2**: test DMA allocation (`lv1_allocate_device_dma_region`, 174), mapping (176), and sector-16 PVD read. |
| **DENIED BY POLICY** | `rom=1, open=DENIED, close=-` | `ROM B=04 D=02 P=0 ID=4/2` | `HDD B=4 D=0 P=2 PH=BOTH` | `OP:-4(DENIED) CL:--` | The drive node is visible in repository, but LV1 policy explicitly blocks the netemu partition from claiming it. Requires an LV1/CFW patch to permit partition device assignment, or pivot to Plan B (USB optical drive). |
| **NO PRIVILEGE / ACCESS VIOLATION** | `rom=1, open=DENIED, close=-` | `ROM B=04 D=02 P=0 ID=4/2` | `HDD B=4 D=0 P=2 PH=BOTH` | `OP:-3(NO_PRIV)` or `OP:-5(ACC_VIOL)` | Partition lacks privilege for LV1 170 on this node. Same conclusion as policy denial. |
| **BUSY** | `rom=1, open=ERR, close=-` | `ROM B=04 D=02 P=0 ID=4/2` | `HDD B=4 D=0 P=2 PH=BOTH` | `OP:-9(BUSY) CL:--` | The drive is held open by another partition (e.g. Game OS / LV2). Retest with drive empty/idle or after cold boot. |
| **OPTICAL NODE ABSENT** | `rom=0, open=SKIP, close=-` | `P1B NO ROM DEV` | `HDD B=4 D=0 P=2 PH=-/-` | `OP:SKIP CL:--` | Mismatch with P1a console findings. Verify game launch conditions or repository changes. |
| **PROBE INVALID** | Any | Any | `HDD: NOT FOUND` | Any | Inconclusive. The probe did not find the known stock HDD. Do not draw conclusions about the optical drive. |

## Two runs (owner request)

Run the test twice: once with NO disc inserted and once with the PS2 DVD inserted, photographing pages A-D each time, and compare the open/close return codes (page D). Restore the stock netemu afterwards.

## Independent audit (orchestrator, 2026-10-31)

ELF diff vs stock via tools/p1a_audit.py (word-aligned scan): exactly two sc instructions (0x4828 LV1 170, 0x4838 LV1 171), all stores based on r1 (stack) or r22 (mailbox), SELF round trip reproduces the ELF (sha256 ef55ecb4...f3b). The wrappers match the stock call site at 0x12bf8c (r3=bus id, r4=dev id, r5=flags, r11=0x800000aa, sc 0, rc in r3). Not tested on the console.
