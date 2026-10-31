# P1a Result Template & Owner Guide

Guide for decoding the `Debug Information` row labels on the PS-button menu when running `ps2_netemu_p1a.self`.

---

## 1. How to Test (Owner Steps)

> [!WARNING]
> Only the owner should perform installation and testing on the PS3 console. No agent script contacts the console directly.

1. Ensure PS3 is on, at the XMB, with webMAN MOD running (FTP and web server enabled).
2. Install the probe SELF using PowerShell:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_netemu.ps1 -File .\local_only\p1a\ps2_netemu_p1a.self -Force
   ```
   *(Note: `-Force` is required because `ps2_netemu_p1a.self` has a new hash not in the legacy allow-list).*
3. Launch any PS2 game from webMAN MOD as usual.
4. Press the **PS button** on the controller to bring up the in-game menu.
5. Highlight the `Debug Information` row. The label will update lazily on the first display.
6. The menu row selector (`selected & 3`) provides 4 diagnostic pages. Navigate or cycle through the sub-items to view each page.
7. Take a clear photo or screenshot of each of the 4 pages (A, B, C, D).
8. Once finished testing, exit the game to the XMB and restore the stock netemu:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\restore_netemu.ps1
   ```

---

## 2. Label Page Decoding

### Page A (`selected & 3 == 0`): Summary Page
Format:
```
P1A DONE devs=<D> rom=<R> hdd=<H>
```
- `devs=<D>`: Total number of storage devices discovered across all buses (0..16+).
- `rom=<R>`: Total number of optical/ROM devices (device type 5) discovered (0..4+).
  - If `rom >= 1`: **OPTICAL NODE FOUND IN REPOSITORY!**
  - If `rom == 0`: No optical storage node was seen from the netemu partition.
- `hdd=<H>`: Sanity control.
  - `hdd=1`: HDD (type 0) was found (probe is VALID).
  - `hdd=0`: HDD was NOT found (probe is INVALID; repository lookups failed or netemu partition has different mapping).

---

### Page B (`selected & 3 == 1`): First ROM Device Details
If `rom == 0`:
```
P1A NO ROM DEV (R=0)
```
If `rom >= 1`:
```
ROM B=<BB> D=<DD> P=<P> T=5
```
- `B=<BB>`: Bus index (00..15) where the optical device was found.
- `D=<DD>`: Device index (00..15) on that bus.
- `P=<P>`: Port value (`0`..`7`, or `?` if unknown/unreadable).
- `T=5`: Device type (5 = ROM / optical storage).

---

### Page C (`selected & 3 == 2`): HDD Control & Phat Selector Match
If `hdd == 0`:
```
HDD: NOT FOUND (PROBE INVALID)
```
If `hdd == 1`:
```
HDD B=<B> D=<D> P=<P> <PHAT>
```
- `B=<B>`: Bus index where the HDD was found (expected: `4`).
- `D=<D>`: Device index of HDD (expected: `0`).
- `P=<P>`: Port of HDD (expected: `2`).
- `<PHAT>`: Indicates whether the optical device matches phat emulator selection patterns:
  - `PH=-/-`: Optical device found on another bus/index.
  - `PH=EMU`: Matches `ps2_emu` selector (`bus_type == 5` storage bus).
  - `PH=GX`: Matches `ps2_gxemu` selector (`bus_index == 4`).
  - `PH=BOTH`: Both conditions matched.

---

### Page D (`selected & 3 == 3`): Error & Hypercall Diagnostics
Format:
```
ERR rc=<RC> sb=<SB> n=<N>
```
- `rc=<RC>`: First non-zero LV1 return code encountered during enumeration:
  - `0`: All attempted lookups succeeded.
  - `-1`: `LV1_ENOENT` (node not found: normal when scanning empty bus/device slots).
  - `-2..-9`: Specific LV1 errors.
  - `-1x`: LV1 errors between -10 and -15.
  - `ER`: Other error.
- `sb=<SB>`: Bus index having `bus_type == 5` (storage bus):
  - `B0`..`B7`, `B8+`: Storage bus found at that index (e.g. `B5`).
  - `NO`: No bus had `bus_type == 5`.
- `n=<N>`: Total number of LV1 call 91 hypercalls executed:
  - `<32`, `32+`, `65+`, `129+`, `256+`.

---

## 3. Decision Table

| Outcome | Page A | Page B | Page C | Meaning & Next Project Step |
|---|---|---|---|---|
| **OPTICAL NODE FOUND (Primary Success)** | `rom>=1, hdd=1` | `ROM B=.. D=..` | `HDD B=4 D=0 P=2` | **The netemu partition CAN see the optical drive in LV1 repository.** Proceed to **P1b**: bounded `open_device` (LV1 170) probe to test partition device assignment and permission. |
| **OPTICAL NODE ABSENT** | `rom=0, hdd=1` | `P1A NO ROM DEV` | `HDD B=4 D=0 P=2` | The netemu partition has repository access (HDD was verified), but the optical node is absent from its repository view. The direct in-emulator route is blocked without LV1/CFW node assignment changes (Plan C) or USB disc route (Plan B). |
| **PROBE INVALID** | `hdd=0` | Any | `HDD: NOT FOUND` | Inconclusive. The probe could not even find the known stock HDD. Do not draw conclusions about the drive. Re-verify repository calling convention or partition privileges. |
| **REPOSITORY ERROR** | `devs=0, hdd=0` | Any | `HDD: NOT FOUND` | LV1 call 91 failed or partition lacks repository read access. Check Page D for the exact `rc` code. |
