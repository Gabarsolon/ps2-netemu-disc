# P1a build notes

Task per `local_only/opencode_p1a_prompt.txt`; spec is `docs/P1A_PLAN.md`. Labels PROVEN / INFERRED / UNKNOWN per NETEMU_KNOWLEDGE.md. Nothing installed; no console contact.

## Status

- [x] Read required docs (CLAUDE.md, P1A_PLAN, NETEMU_KNOWLEDGE, TOOLING_AND_WORKFLOW, P0_STATIC_ANALYSIS, P0_HYPERCALLS, P0D_PHAT_EMU_ANALYSIS).
- [x] Input hashes checked (step: sha256):
  - `local_only/stock.elf` = `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3` — MATCHES expected.
  - `local_only/stock_ps2_netemu.self` = `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a` — MATCHES expected.
- [x] Verify addresses in the stock ELF with pyghidra (below).
- [x] Verify phat selectors in ps2_emu/ps2_gxemu.
- [x] Design payload (C for PPC64, 96-byte mailbox, fail-open, immutable label tables).
- [x] Build + round trip (netemu\ pipeline, ELF & SELF in local_only\p1a\, selfdec.py round-trip byte-for-byte exact).
- [x] PC validation (pyghidra EmulatorHelper all 6 scenarios, IR store audit, asm store scan, code size check, installer parse check).
- [x] Result template + owner steps (docs\P1A_RESULT_TEMPLATE.md written).

## Built Artifacts (Derivatives in local_only/p1a/)

- Patched ELF: `local_only/p1a/ps2_netemu_p1a.elf`
  - Size: 11,032,360 bytes
  - SHA256: `2dea15b3c0732b9ffa7869bfecddd32d0ac6275a3343a27c710fe94ad75549a5`
- Patched SELF: `local_only/p1a/ps2_netemu_p1a.self`
  - Size: 2,536,816 bytes
  - SHA256: `17d5ed32390e1d5d1dc3a3c74c18d9a81d2cc62edf0732a4c23442380d7700d6`
- Decrypted roundtrip ELF: `local_only/p1a/roundtrip.elf`
  - SHA256: `2dea15b3c0732b9ffa7869bfecddd32d0ac6275a3343a27c710fe94ad75549a5` (byte-for-byte exact match)
- Code slot usage: 1,840 bytes out of 14,320 bytes available (12.8%).
- Extended RO data: 127,232 bytes (immutable label tables).
- Patches applied:
  - Code slot at `0x4800`: 1,840 bytes (trampolines + payload).
  - Hook at `0x270FFC`: `bl entry_menu` (expected original `0xe882cea8` verified).
  - PHDR1 extended to `0x76da30` to include immutable diagnostic labels.
  - No pads/HID/disc file hooks modified. Stock string `Debug Information\0` at `0x304EC0` left untouched.

## PC Validation Results (`netemu/validate_pc.py`)

All tests PASSED:
1. **Code size check:** 1,840 bytes <= 14,320 bytes (PASS).
2. **IR pointer provenance audit (`audit_ir.py`):** 43 stores verified strictly inside stack / mailbox `[0x930F20, 0x930F80)` (PASS).
3. **Assembly store scan:** 71 stores in code slot verified on stack `(r1)` or mailbox (PASS).
4. **PPC64 Emulation scenarios (`EmulatorHelper`):**
   - **Scenario 1 (Optical present):** Page A: `P1A DONE devs=2 rom=1 hdd=1`, Page B: `ROM B=05 D=00 P=0 T=5`, Page C: `HDD B=4 D=0 P=2 PH=EMU`, Page D: `ERR rc=-1 sb=B5 n=32+` (PASS).
   - **Scenario 2 (No optical):** Page A: `P1A DONE devs=1 rom=0 hdd=1`, Page B: `P1A NO ROM DEV (R=0)`, Page C: `HDD B=4 D=0 P=2 PH=-/-` (PASS).
   - **Scenario 3 (Repo errors):** Page A: `P1A DONE devs=0 rom=0 hdd=0`, Page B: `P1A NO ROM DEV (R=0)`, Page C: `HDD: NOT FOUND (PROBE INVALID)`, Page D: `ERR rc=-1 sb=NO n=<32` (PASS).
   - **Scenario 4 (HDD control):** HDD found at Bus 4, Dev 0, Port 2 in Scenarios 1 and 2 (PASS).
   - **Scenario 5 (Fail-open):** Returns stock string `Debug Information` at `0x304EC0` if probe is uninitialized (PASS).
   - **Scenario 6 (Repeated menu opens):** 54 hypercalls executed on first menu open, exactly 0 on subsequent opens (PASS).
5. **Installer script syntax parse check:** `install_netemu.ps1` (0 errors), `restore_netemu.ps1` (0 errors) (PASS).

## Verified in the stock ELF (pyghidra) — fill as verified

| what | expected addr | verified? | evidence (one line) |
|---|---|---|---|
| repository helper | 0x111eb8 | YES | word 0x7d800026 `mfcr r12`, fn_00111eb8(out1,out2,n1,n2,n3,n4), verified in stock.elf |
| key encoder | 0x111f6c | YES | word 0x2c230000 `cmpdi r3,0x0`, fn_00111f6c packs ASCII string into high bits |
| LV1 91 `sc 1` | 0x111f10 | YES | word 0x44000002 `sc 0x0`, r11=0x8000005b (LV1 91 forwarded), r3=1 (lpar 1) |
| enumerator | 0x114ea4 | YES | word 0x7d800026 `mfcr r12`, fn_00114ea4(bus,dev_start,info,type,port) |
| menu-row hook site | 0x270FFC | YES | word 0xe882cea8 `ld r4,-0x3158(r2)`, TOC slot 0x74e128 holds 0x304ec0 |
| label marker string | 0x304EC0 | YES | string `Debug Information\0` at 0x304ec0, 18 bytes |
| RW mailbox start | 0x930F20 | YES | all 96 bytes zero in stock ELF [0x930F20..0x930F80) |
| RW mailbox end | 0x930F80 | YES | end of 96-byte struct State mailbox |
| native allocator | 0xB9848 | YES | word 0xf821ff71 `stdu r1,-0x90(r1)`, allocator (size,3,0) |
| code slot | 0x4800..0x7FF0 | YES | all 14,320 bytes zero in stock ELF |

## Decisions

- Enumeration approach: PROVEN SAFEST is our own bounded loop over bus index `b = 0..15` and dev index `d = 0..15` calling stock helper `0x111eb8` directly.
  - Evidence:
    1. Stock enumerator `0x114ea4` writes a large ~736-byte (0x2e0) `info` structure that exceeds our 96-byte mailbox `[0x930F20, 0x930F80)`.
    2. `0x114ea4` searches a single bus and loops device index until an LV1 failure or match; our bounded loop checks buses 0..15 and devices 0..15 with strict upper bounds.
    3. `0x111eb8` argument safety: `0x111eb8` verifies `(n1_hi & n1_lo) == 0`. With `n1 = ("bus", b) = 0x62757300_00000000 | b`, `0x62757300 & b == 0` for all `b < 256`, so the panic branch `0x111f60` is NEVER taken.
    4. Only LV1 call 91 is issued; no open_device (170), no storage commands, no locks held, no blocking.
- Phat optical selectors used as primary candidates:
  - In `ps2_emu`: `fn_00022460` at `0x224b0` calls `fn_0001d954(5, 5, 0)` -> storage bus (type 5), ROM device (type 5), skip 0.
  - In `ps2_gxemu`: `fn_0008d510` at `0x8d538` calls `fn_0004199c(4, 5, 0)` -> bus index 4, ROM device (type 5), dev_start 0.
  - In `ps2_netemu`: HDD init `0x12be04` calls `0x114ea4(4, 0, info, 0, 2)` -> bus index 4, dev type 0 (DISK), port 2.
  - Candidate selectors: Bus index 4 and Bus type 5 are both evaluated. Our bounded loop checks all buses 0..15, guaranteeing coverage of both candidates.
- Label pages A/B/C/D:
  - Selected by `selected & 3`:
    - Page A: Summary: `P1A DONE devs=<n> rom=<n> hdd=<0/1>`
    - Page B: First ROM device: `ROM B=<b idx> D=<d idx> P=<port> T=<type>` (or `NO ROM FOUND`)
    - Page C: HDD control & phat match: `HDD B=4 D=<d> P=2 PHAT=<Y/N>`
    - Page D: Errors & diagnostics: `ERR rc=<last_rc> n91=<count> b5=<type5_bus_idx>`
  - Strings are immutable in the extended RO section; fail-open returns stock pointer `0x304EC0`.

## Open problems

- (none yet)

## Where I stopped / if time ran out

- This file is updated as work proceeds; the last unchecked box above is the stopping point.
