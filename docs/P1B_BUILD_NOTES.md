# P1b build notes

Task per `local_only/agy_p1b_prompt.txt`; spec is `docs/P1B_PLAN.md`.
Labels PROVEN / INFERRED / UNKNOWN per NETEMU_KNOWLEDGE.md.
Nothing installed; no console contact.

## Status

- [x] Inputs checked:
  - `local_only/stock.elf` = `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3` — MATCHES expected.
  - `local_only/stock_ps2_netemu.self` = `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a` — MATCHES expected.
- [x] Verify in the stock ELF with pyghidra (`tools/p1b_verify.py`):
  - [x] LV1 170 (`open_device`) and LV1 171 (`close_device`) wrappers/callsites in stock netemu.
  - [x] HDD init calling sequence at `0x12be04`, call near `0x12bf8c`, close near `0x12d610`.
  - [x] Repository ID reading vs HDD init (`bus/N/id`, `bus/N/dev/M/id`).
  - [x] Mailbox layout (96 bytes `[0x930F20, 0x930F80)`).
- [x] Implement `netemu_p1b/`:
  - [x] Probe payload adding open/close (LV1 170, 171) and HDD control (bus 4, dev with type 0, port 2).
  - [x] Immutable label tables for Pages A, B, C, D.
  - [x] Trampolines and linker script.
- [x] Build & roundtrip:
  - [x] Compile with Clang & LLVM.
  - [x] ELF and SELF in `local_only/p1b/`.
  - [x] `selfdec.py` roundtrip byte-for-byte exact match.
- [x] PC Validation (`netemu_p1b/validate_pc.py`):
  - [x] Emulation scenarios with pyghidra EmulatorHelper (all 12 scenarios passed).
  - [x] IR store provenance audit (`audit_ir.py` - 55 stores verified inside stack / mailbox).
  - [x] Assembly store scan & sc instruction scan (exactly two sc instructions in code slot: 0x4828 and 0x4838).
  - [x] Code slot size check (2,280 bytes / 14,320 bytes = 15.9%).
  - [x] Installer script parse check (tools/install_netemu.ps1, tools/restore_netemu.ps1 - 0 errors).
  - [x] Independent ELF diff vs stock.elf (`tools/p1a_audit.py`).
- [x] Write `docs/P1B_RESULT_TEMPLATE.md`.
- [x] Final summary.

## Built Artifacts (in `local_only/p1b/`)

- Patched ELF: `local_only/p1b/ps2_netemu_p1b.elf`
  - Size: 11,360,040 bytes
  - SHA256: `ef55ecb4b5bdf7ed76f20ab4494237e196973130b5dfd9470873572789adcf3b`
- Patched SELF: `local_only/p1b/ps2_netemu_p1b.self`
  - Size: 2,554,240 bytes
  - SHA256: `b49e86f2738af08177207be4d1cfe8253139f0ec292a033dc4065d2e6eba2ee8`
- Decrypted roundtrip ELF: `local_only/p1b/roundtrip.elf`
  - Size: 11,360,040 bytes
  - SHA256: `ef55ecb4b5bdf7ed76f20ab4494237e196973130b5dfd9470873572789adcf3b` (byte-for-byte exact match)
- Code slot reservation: `0x4800..0x7FF0` (capacity 14,320 bytes)
  - Code slot used: 2,280 bytes (`0x4800..0x50E8`, 15.9% usage)
- Extended RO data segment: 445,536 bytes (`0x74E930..0x7BB590`, ends well below `0x821000`)
- Patches applied:
  - Trampolines + payload in code slot `0x4800..0x50E8`
  - Menu-row hook at `0x270FFC`: `bl entry_menu` (`0x4bd93885`, expected original `0xe882cea8` verified)
  - PHDR1 extended to `0x7BB590` to hold immutable diagnostic labels

## PC Validation Results (`netemu_p1b/validate_pc.py`)

All tests PASSED:
1. **Code size check:** 2,280 bytes <= 14,320 bytes (15.9%) (PASS).
2. **SC instruction scan:** Exactly 2 hypercalls in code slot:
   - `0x4828`: `sc 0x0` in `lv1_open_device` (r11 = 0x800000aa, LV1 170)
   - `0x4838`: `sc 0x0` in `lv1_close_device` (r11 = 0x800000ab, LV1 171)
   - Zero other `sc` instructions anywhere in our code (PASS).
3. **IR store provenance audit (`audit_ir.py`):** 55 stores verified strictly inside stack / mailbox `[0x930F20, 0x930F80)` (PASS).
4. **Assembly store scan:** 83 stores in code slot verified on stack `(r1)` or mailbox `(r22 = 0x930F20)` (PASS).
5. **Strict runtime write tracking (`EmulatorHelper`):** All stores during emulation confirmed strictly inside stack frame or mailbox `[0x930F20, 0x930F80)` (PASS).
6. **Emulation Scenarios:**
   - **Scenario 1 (Optical present, open 0, close 0):**
     - Page A: `P1B DONE rom=1 open=OK close=OK`
     - Page B: `ROM B=05 D=00 P=0 ID=500/501`
     - Page C: `HDD B=4 D=0 P=2 PH=EMU`
     - Page D: `OP:0(OK) CL:0(OK) RP:-6(FA)`
     - Hypercalls: exactly one 170 `(0x500, 0x501, 0)` and one 171 `(0x500, 0x501)` (PASS).
   - **Scenario 2 (Open denied -4, no close):**
     - Page A: `P1B DONE rom=1 open=DENIED close=-`
     - Page D: `OP:-4(DENIED) CL:-- RP:-6(FA)`
     - Hypercalls: open called once, close NEVER called (PASS).
   - **Scenario 3 (Open no privilege -3):**
     - Page A: `P1B DONE rom=1 open=DENIED close=-`
     - Page D: `OP:-3(NO_PRIV) CL:--` (PASS).
   - **Scenario 4 (Open busy -9):**
     - Page A: `P1B DONE rom=1 open=ERR close=-`
     - Page D: `OP:-9(BUSY) CL:--` (PASS).
   - **Scenario 5 (Open access violation -5):**
     - Page A: `P1B DONE rom=1 open=DENIED close=-`
     - Page D: `OP:-5(ACC_VIOL) CL:--` (PASS).
   - **Scenario 6 (Close error -2):**
     - Page A: `P1B DONE rom=1 open=OK close=ERR`
     - Page D: `OP:0(OK) CL:-2(SHORT)` (PASS).
   - **Scenario 7 (No optical node):**
     - Page A: `P1B DONE rom=0 open=SKIP close=-`
     - Page B: `P1B NO ROM DEV (R=0)`
     - Page D: `OP:SKIP CL:--`
     - Hypercalls: exactly ZERO 170 and ZERO 171 calls issued (PASS).
   - **Scenario 8 (Two ROM nodes):**
     - Page A: `P1B DONE rom=2 open=OK close=OK`
     - Hypercalls: only first ROM node opened and closed; exactly one 170 call (PASS).
   - **Scenario 9 (Repository errors):**
     - Page A: `P1B DONE rom=0 open=SKIP close=-`
     - Page C: `HDD: NOT FOUND (PROBE INVALID)`
     - Page D: `OP:SKIP CL:-- RP:-6(FA)` (PASS).
   - **Scenario 10 (HDD control found vs absent):**
     - Accurately reports `HDD B=4 D=0 P=2` when present and `HDD: NOT FOUND` when absent (PASS).
   - **Scenario 11 (Fail-open hook check):**
     - Expected original word `0xe882cea8` verified at `0x270FFC` (PASS).
   - **Scenario 12 (Repeated menu opens):**
     - 56 hypercalls executed on first menu display, exactly 0 on subsequent menu calls; open issued once overall (PASS).
7. **Installer script syntax parse check:** `install_netemu.ps1` (0 errors), `restore_netemu.ps1` (0 errors) (PASS).

## Verified in the stock ELF (pyghidra)

| what | expected addr | verified? | evidence (one line) |
|---|---|---|---|
| LV1 170 (`open_device`) | 0x12bf8c | YES | `sc 0x0` at 0x12bf8c with r11=0x800000aa, r3=bus_id, r4=dev_id, r5=0; error branch at 0x12bf94 to 0x12c050 |
| LV1 171 (`close_device`) | 0x12d610 | YES | `sc 0x0` at 0x12d610 with r11=0x800000ab, r3=bus_id, r4=dev_id; called during HDD driver teardown 0x12d420 |
| Other LV1 170 sites | 0x137b68, 0x19d48, 0x1e79a4 | YES | All inline `sc 0x0` with r11=0x800000aa, r3=bus_id, r4=dev_id, r5=flags (0); no shared stock leaf function |
| Other LV1 171 sites | 0x137440, 0x1e77b4 | YES | All inline `sc 0x0` with r11=0x800000ab, r3=bus_id, r4=dev_id; no shared stock leaf function |
| Exception bridge | 0xca0 | YES | `sc 0x1` at 0xca0; 0xc50 strips 0x80000000 from r11, checks privilege table, calls LV1, returns rc in r3 |
| Repository bus ID read | 0x12be74..0x12beb0 | YES | `repo_read(&v1, &v2, KEY_BUS(4), KEY_ID, 0, 0)` -> v1 stored to H+8 (bus_id) |
| Enumerator dev ID read | 0x114ea4 / 0x12bf74 | YES | `0x114ea4(4, 0, info, 0, 2)` -> info+8 (dev_id) passed to open_device as r4; matches P1a repo dev_id read |
| HDD init error handler | 0x12c050 | YES | `li r3, 0; blr` - returns 0 (failure) to caller, does NOT call fatal helper 0x111a7c |
| Menu-row hook site | 0x270FFC | YES | word 0xe882cea8 `ld r4,-0x3158(r2)`, TOC slot holds 0x304ec0 (`Debug Information\0`) |
| RW mailbox | 0x930F20..0x930F80 | YES | 96 bytes all zero in stock ELF |
| Code slot | 0x4800..0x7FF0 | YES | 14,320 bytes all zero in stock ELF |

## Mailbox Layout (96 bytes `[0x930F20, 0x930F80)`)

| offset | size | type | field | purpose |
|---|---|---|---|---|
| 0 | 4 | u32 | `status` | bit 0: started, bit 1: done, bit 2: open_attempted, bit 3: open_ok, bit 4: close_attempted, bit 5: close_ok |
| 4 | 4 | u32 | `total_devices` | count of storage devices enumerated across buses 0..15 |
| 8 | 4 | u32 | `rom_count` | count of type 5 (ROM) devices found |
| 12 | 4 | u32 | `hdd_found` | 1 if HDD control matched on bus 4 (type 0, port 2), else 0 |
| 16 | 4 | u32 | `flags` | status flags |
| 20 | 4 | u32 | `total_hypercalls` | count of LV1 91, 170, 171 hypercalls issued |
| 24 | 4 | u32 | `first_err_rc` | first failed LV1 91 return code (e.g. -6 LV1_NO_ENTRY) |
| 28 | 4 | u32 | `reserved` | alignment padding (0) |
| 32 | 1 | u8 | `rom_bus_idx` | bus index (0..15) of first ROM device (0xFF if none) |
| 33 | 1 | u8 | `rom_dev_idx` | dev index (0..15) of first ROM device (0xFF if none) |
| 34 | 1 | u8 | `rom_port` | port value of first ROM device (0xFF if none) |
| 35 | 1 | u8 | `storage_bus_idx` | bus index that has bus_type == 5 (0xFF if none) |
| 36 | 1 | u8 | `hdd_bus_idx` | bus index of HDD control (expected 4) |
| 37 | 1 | u8 | `hdd_dev_idx` | dev index of HDD control (expected 0) |
| 38 | 1 | u8 | `hdd_port` | port of HDD control (expected 2) |
| 39 | 1 | u8 | `phat_match` | bit 0: bus_type==5, bit 1: rom on bus 4 (expected 3 = PH=BOTH) |
| 40 | 4 | u32 | `open_rc_low` | low 32 bits of open_device return code |
| 44 | 4 | u32 | `close_rc_low` | low 32 bits of close_device return code |
| 48 | 8 | u64 | `hdd_bus_id` | 64-bit bus_id of HDD control |
| 56 | 8 | u64 | `hdd_dev_id` | 64-bit dev_id of HDD control |
| 64 | 8 | u64 | `rom_bus_id` | 64-bit bus_id of first ROM device (preserves P1a offset 64) |
| 72 | 8 | u64 | `rom_dev_id` | 64-bit dev_id of first ROM device (preserves P1a offset 72) |
| 80 | 8 | s64 | `open_rc` | signed 64-bit raw return code from lv1_open_device |
| 88 | 8 | s64 | `close_rc` | signed 64-bit raw return code from lv1_close_device |

## Decisions

- **LV1 170 / 171 Call Wrappers:**
  - Stock netemu does NOT have a shared leaf function for open/close; all stock calls inline `sc 0` with `r11 = 0x800000aa` or `0x800000ab`.
  - We place minimal leaf wrappers `lv1_open_device` (at `0x4820`) and `lv1_close_device` (at `0x4830`) in our trampoline reservation (`0x4800..0x4900`).
  - Each leaf wrapper loads `r11`, executes `sc 0`, and executes `blr`. Return code is received directly in `r3` without side-effects or fatal branches.
- **HDD Control Scan:**
  - Fixed from P1a: specifically checks `bus == 4 && type == 0 && port == 2` to identify the netemu HDD exactly as stock `0x114ea4(4, 0, info, 0, 2)` does. Does NOT open the HDD.
- **Once-Only Open/Close Execution:**
  - Executed only if `rom_count >= 1`.
  - Issues ONE `lv1_open_device(rom_bus_id, rom_dev_id, 0)`.
  - If and only if `open_rc == 0`, issues ONE `lv1_close_device(rom_bus_id, rom_dev_id)`.
  - Flags and return codes recorded in the RW mailbox. Never retries.
- **Immutable Diagnostic Labels:**
  - Page A: Summary `P1B DONE rom=<n> open=<OK|DENIED|ERR|SKIP> close=<OK|-|ERR>`
  - Page B: Optical node `ROM B=%02d D=%02d P=%s ID=%s`
  - Page C: HDD control `HDD B=%s D=%s P=%s %s`
  - Page D: Raw return codes `OP:<rc>(<name>) CL:<rc>(<name>) RP:<rc>(<hex>)`

## Open problems

- None. PC validation is completely clean and ready for console testing.

## Where I stopped / if time ran out

- Task complete. Handing over to user for console testing per `docs/P1B_RESULT_TEMPLATE.md`.
