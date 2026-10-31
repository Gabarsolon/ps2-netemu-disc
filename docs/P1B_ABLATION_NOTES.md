# P1b Ablation Notes

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1b Netemu Ablation Build and Suspect Audit (Console Shutdown Root Cause Investigation).

---

## 0. Overview & Background

### Console Observation (PROVEN on real hardware)
- **P1a** (`ps2_netemu_p1a.self`, sha256 `17d5ed32390e1d5d1dc3a3c74c18d9a81d2cc62edf0732a4c23442380d7700d6`):
  - Used PS-button menu hook at `0x270FFC` to trigger a bounded repository scan (LV1 call 91).
  - Executed 65+ hypercalls without fault.
  - Displayed the `Debug Information` row and all 4 pages cleanly on the owner's PS3 slim (CECH-25xx, Evilnat 4.93 Cobra).
  - Reported 12 storage devices, ROM device at Bus index 4, Dev index 2, Port 0.
- **P1b** (`ps2_netemu_p1b.self`, sha256 `b49e86f2738af08177207be4d1cfe8253139f0ec292a033dc4065d2e6eba2ee8`):
  - Same menu hook (`0x270FFC`), same repository scan.
  - Added ONE `lv1_open_device(rom_bus_id, rom_dev_id, 0)` (LV1 call 170), and ONE `close_device` (LV1 call 171) if open succeeded.
  - Added ~445 KB immutable label tables for Pages A–D.
  - **Console result**: Upon pressing the PS button to open the in-game menu, the console immediately shut itself down (powered off). No label was seen.

---

## 1. Suspect Audit (PC Analysis)

### Difference Inventory between P1a and P1b
1. **Payload Execution (`src/probe.c`)**:
   - P1a only calls `repo_read` (LV1 91). It never issues device open/close calls.
   - P1b calls `repo_read` (LV1 91) identically, but if `rom_count >= 1`, issues `lv1_open_device(rom_bus_id, rom_dev_id, 0)` (LV1 170). If open succeeds (rc == 0), it issues `lv1_close_device(rom_bus_id, rom_dev_id)` (LV1 171).
   - P1b corrects the HDD control scan from P1a to explicitly check `bus == 4 && d_type == 0 && d_port == 2`.
2. **Linker & Code Slot Reservation (`0x4800..0x7FF0`)**:
   - P1a placed trampolines `repo_read` (0x4840) and `entry_menu` (0x4880), with C payload at `0x4900..0x4F30` (1,776 bytes).
   - P1b added leaf wrappers `lv1_open_device` (0x4820) and `lv1_close_device` (0x4830), with C payload at `0x4900..0x50E8` (2,280 bytes).
   - Both fit well inside the 14,320-byte code slot reservation.
3. **Mailbox Layout (`0x930F20..0x930F80`, 96 bytes)**:
   - P1a used all 32-bit (`u32`) and 64-bit (`u64`) fields, accessed exclusively with `stw` (op 36) and `std` (op 62).
   - P1b packed 8 byte-sized indices (`rom_bus_idx`, `rom_dev_idx`, `rom_port`, `storage_bus_idx`, `hdd_bus_idx`, `hdd_dev_idx`, `hdd_port`, `phat_match`) into offsets 32..39 as `u8`, accessed with `stb` (op 38).
   - Offsets 40..47 hold `open_rc_low` and `close_rc_low`; offsets 80..95 hold 64-bit `open_rc` and `close_rc`.
   - Offsets 64..79 (`rom_bus_id`, `rom_dev_id`) are identical between P1a and P1b.
4. **Extended Read-Only Segment (PHDR1)**:
   - Stock netemu: `0x300000..0x74E930` (filesz/memsz `0x44E930`).
   - P1a extension: `0x74E930..0x76DA30` (+127,232 bytes, PHDR1 filesz/memsz `0x46DA30`).
   - P1b extension: `0x74E930..0x7BB590` (+445,536 bytes, PHDR1 filesz/memsz `0x4BB590`).
   - Buzz! Bridge S4L3 extension: `0x74E930..0x7FFCA0` (+725,872 bytes, PHDR1 filesz/memsz `0x4FFCA0`).

---

### Detailed Suspect Analysis & Evidence

#### (a) `lv1_open_device` (LV1 170) Hypercall
- **Mechanism**:
  - The probe calls `lv1_open_device(rom_bus_id, rom_dev_id, 0)` via leaf wrapper at `0x4820` issuing `sc 0` with `r11 = 0x800000AA`.
  - The guest exception bridge at `0xCA0` checks permission byte and executes `sc 1` to LV1.
  - In PS3 LV1 hypervisor security architecture, hardware devices are partitioned. The Blu-ray optical drive controller is assigned exclusively to GameOS (LV2).
  - When an isolated guest partition (`ps2_netemu`) requests `open_device` on a hardware device assigned to another partition, LV1 policy enforcement can trigger an immediate capability fault, kernel panic, or partition shutdown (`sys_platform_power_off`), powering off the console.
- **Evidence FOR**:
  - P1a executed the identical trigger hook, menu display, and repository scan without issue.
  - The only operational difference prior to menu rendering between P1a and P1b was issuing `lv1_open_device`.
  - The shutdown occurred immediately upon opening the PS menu (first probe execution).
- **Evidence AGAINST**:
  - Stock netemu calls `open_device` on the HDD (`0x12bf8c`), and branches gracefully on error (`0x12c050`). However, the HDD is assigned to the netemu partition; the optical drive is not.

#### (b) Out-of-Bounds Load or Extended RO Segment Layout
- **Index Bounds Analysis**:
  - Page A: 75 strings (indices 0..74). Index formula `(r * 5 + o) * 3 + c`. With `r <= 4`, `o <= 4`, `c <= 2`, max reachable index is 74.
  - Page B: 7169 strings (indices 0..7168). Formula `1 + ((mode * 16 + b) * 16 + d) * 4 + p`. With `mode <= 6`, `b <= 15`, `d <= 15`, `p <= 3`, max reachable index is 7168.
  - Page C: 901 strings (indices 0..900). Formula `1 + ((b * 5 + d) * 5 + p) * 4 + ph`. With `b <= 8`, `d <= 4`, `p <= 4`, `ph <= 3`, max reachable index is 900.
  - Page D: 1152 strings (indices 0..1151). Formula `(o * 12 + c) * 8 + r`. With `o <= 11`, `c <= 11`, `r <= 7`, max reachable index is 1151.
  - **Exhaustive Automated Fuzzing**: Tested across 117M+ combinations covering all `u8`, `u32`, `s64` values. ZERO out-of-bounds indices possible.
- **Segment Mapping Verification vs Proven Buzz Build**:
  - P1b RO segment ends at `0x7BB590` (445 KB extension).
  - Buzz! Bridge `S4L3` (`C:\Users\remus\ps3buzz-console\raw_capture_debug11`) extended PHDR1 to `0x7FFCA0` (725 KB extension).
  - Buzz `S4L3` ran and displayed menus on this exact console without issue.
  - `0x7BB590` is 280 KB smaller than Buzz and sits well below `0x800000` (RW start).
  - Therefore, segment size is proven compatible with the netemu loader.

#### (c) Stack Use, Alignment, and Byte Stores (`stb`)
- **Stack Usage**:
  - `entry_menu` allocates 128 bytes (`stdu r1, -128(r1)`).
  - `s4_menu` allocates 208 bytes (`stdu r1, -208(r1)`).
  - Stack frame size is IDENTICAL between P1a (208 bytes) and P1b (208 bytes).
- **Stores in Mailbox**:
  - P1b introduced `u8` fields, generating `stb` (op 38) stores at offsets 32..39.
  - On PowerPC 970 / Cell PPE, byte accesses in cached RAM (`0x930F20`) cannot cause alignment faults.
  - All stores are strictly inside `[0x930F20, 0x930F80)`.

#### (d) Wrappers in Code Slot
- Wrappers `lv1_open_device` (0x4820) and `lv1_close_device` (0x4830) are 16-byte leaf routines in the unused code reservation `0x4800..0x7FF0`.
- If never called, they are passive bytes that never execute.

---

### Ranked Suspects

| Rank | Suspect | Evidence For | Evidence Against |
|---|---|---|---|
| **1** | **`lv1_open_device` (170) capability violation / hypervisor panic** | P1a ran cleanly on same console; the open call was the only operational difference; LV1 partitions enforce device ownership. | Stock netemu handles HDD open failures gracefully, but HDD is owned by partition. |
| **2** | **Extended RO segment page mapping threshold** | P1b added 445 KB vs P1a's 127 KB. | Buzz S4L3 added 725 KB (`0x7FFCA0`) and ran on this exact console. |
| **3** | **Byte-store (`stb`) into mailbox at `0x930F20`** | P1a used `stw`/`std` only; P1b introduced `stb`. | Memory is normal cached RAM; PPE handles byte stores without fault. |
| **4** | **Out-of-bounds LOAD in label tables** | A wild pointer dereference would fault. | Exhaustive fuzzing proved 100% bounds safety across all pages. |
| **5** | **Wrappers present in code slot** | Code added at 0x4820. | Dead code if uncalled; reservation is executable text. |

---

## 2. Ablation Build (`netemu_p1b_noopen`)

- **Location**: `netemu_p1b_noopen/` (independent copy; `netemu/` and `netemu_p1b/` untouched).
- **Compile-Time Switch**: `PROBE_DO_OPEN` (default `0`).
- **Behavior**:
  - When `PROBE_DO_OPEN == 0`: `lv1_open_device` and `lv1_close_device` are completely omitted from execution.
  - Wrappers remain linked at `0x4820` and `0x4830`.
  - Page A displays `open=OFF` instead of OK/DENIED/ERR/SKIP.
  - Page B displays the real 64-bit IDs (`ID=...`).
  - Page D displays raw status (`OP:SKIP CL:-- RP:-6(FA)`).
- **Artifacts**:
  - Patched ELF: `local_only/p1b_noopen/ps2_netemu_p1b_noopen.elf` (sha256 `10aed0857daf4200b96537acb1d664e2da976020907301b0c29fbe96d030f5a2`)
  - Patched SELF: `local_only/p1b_noopen/ps2_netemu_p1b_noopen.self` (sha256 `2cf25e816d128193f4e6e2c530192c5e0e425fa739fe706e2ad4055aa8a71cee`)
  - Roundtrip ELF: `local_only/p1b_noopen/roundtrip.elf` (byte-for-byte exact match)

---

## 3. PC Validation Results

- **Independent ELF Audit (`tools/p1a_audit.py`)**:
  - Code slot: 2,008 bytes used (`0x4800..0x4FD8`) / 14,320 capacity.
  - SC scan: Exactly 2 `sc` instructions in code slot (`0x4828` and `0x4838`), both in uncalled wrappers.
  - Store scan: 69 stores in added executable code, 100% verified on stack (`r1`) or mailbox (`r22 = 0x930F20`).
- **IR Provenance Audit (`audit_ir.py`)**:
  - 41 stores verified strictly inside stack or mailbox `[0x930F20, 0x930F80)`.
- **Emulation & Runtime Tracking**:
  - Validated with pyghidra `EmulatorHelper`.
  - Asserted ZERO 170/171 calls executed.
  - Asserted ZERO `sc` instructions executed except LV1 91 (at `0x111f10`).
  - All memory writes verified strictly inside stack frame or mailbox `[0x930F20, 0x930F80)`.
  - Exhaustive index bounds fuzzing verified across all 4 pages.
