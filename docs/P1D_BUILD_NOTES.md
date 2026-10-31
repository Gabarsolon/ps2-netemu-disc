# P1d Build Notes: Diagnostic Hypercall Probes (Variant A & Variant B)

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1d ps2_netemu diagnostic probe build — test whether `lv1_open_device` / `lv1_close_device` return cleanly from the netemu partition when called with parameters that must fail.

---

## 1. Goal and Background

In P1b, calling `lv1_open_device(4, 2, 0)` on the optical node powered off the console (CECH-25xx, Evilnat 4.93 Cobra).
Ablation (`netemu_p1b_noopen`) confirmed that omitting the `lv1_open_device` call completely prevented the shutdown and allowed the menu hook to display diagnostic information cleanly.
According to static analysis of 3.55 LV1 (`docs/P0H_LV1_ANALYSIS.md`):
- `lv1_open_device` never panics on invalid or non-owned devices: outer dispatch rejects `bus_id >= 5` with `-17` (`LV1_NO_BUS` / `LV1_INVALID_PARAMETER`).
- `lv1_close_device` on an unopened device returns `-11` (`LV1_NOT_OWNER`).
- 3.55 maintains two concurrent opener slots per device.

The shutdown in P1b could be caused by:
1. **The hypercall path / context itself**: our leaf wrapper, the guest `sc 0` bridge at `0xc50..0xca0`, or issuing hypercalls from the PS-button menu hook context.
2. **The optical node open**: the open succeeded, followed by an unhandled drive interrupt / event crash, or modern 4.93 LV1 strictly panics on netemu opening the optical node.

To isolate these causes, P1d implements two diagnostic variants:
- **Variant A**: issues `lv1_open_device(bus_id = 9, dev_id = 0, flags = 0)`. Bus 9 is outside 0..4, so LV1 dispatch returns `-17` immediately without touching any hardware device or slot state.
- **Variant B**: issues `lv1_close_device(bus_id = 4, dev_id = 2)` on the optical node without ever opening it. LV1 checks active opener slots, finds caller is not an owner, and returns `-11` without state change.

Neither variant touches real hardware. Both execute exactly ONE test hypercall once lazily during the menu hook evaluation after repository scan.

---

## 2. Reused Component Verification

All components reused from stock and `netemu_p1b_noopen\` have been verified byte-for-byte against `local_only/stock.elf` (SHA-256 `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`):
1. **Hook site `0x270FFC`**:
   - Stock instruction at `0x270FFC` is `e882cea8` (`ld r4, -0x3158(r2)`).
   - Patched with `bl entry_menu` (`0x4880`). Build aborts if original word does not match `0xe882cea8`.
2. **Leaf wrappers at `0x4820` and `0x4830`**:
   - `lv1_open_device` (`0x4820`): `li r11, 0xaa` (`396000aa`), `oris r11, r11, 0x8000` (`656b8000`), `sc 0` (`44000002`), `blr` (`4e800020`). Identical to stock call setup at `0x12bf7c..0x12bf8c`.
   - `lv1_close_device` (`0x4830`): `li r11, 0xab` (`396000ab`), `oris r11, r11, 0x8000` (`656b8000`), `sc 0` (`44000002`), `blr` (`4e800020`). Identical to stock call setup at `0x12d600..0x12d610`.
3. **Mailbox layout (`0x930F20..0x930F80`, 96 bytes)**:
   - Validated zero in stock ELF.
   - All stores are audited and restricted strictly to `[0x930F20, 0x930F80)` and stack (`r1`).
4. **Guest `sc 0` bridge (`0xc50..0xca0`)**:
   - Privilege bank table initialized to 2 (allowing PR=0 and PR=1 for all 256 calls).

---

## 3. Implementation Details (`netemu_p1d\`)

- **Compile-time switch**: `PROBE_VARIANT` (`'A'` or `'B'`).
- `build.py`: builds both `ps2_netemu_p1d_A.self` and `ps2_netemu_p1d_B.self` in a single execution.
- **Probe execution**:
  - Variant A: issues `lv1_open_device(9, 0, 0)` once after repository scan.
  - Variant B: issues `lv1_close_device(4, 2)` once after repository scan.
  - Return code (signed 64-bit and low 32-bit) recorded in mailbox.
  - Sign/width handling: evaluates `s32 s = (s32)rc` to correctly decode 32-bit LV1 status formats (such as `0x1FFFFFFEF` -> `-17`) as well as 64-bit sign-extended formats.
- **Label pages** (immutable tables in extended RO segment, 64-byte aligned entries):
  - Page A: `P1D-A DONE open(9,0,0) rc=<name>` or `P1D-B DONE close(4,2) rc=<name>`.
  - Page B: raw rc in hex (`08X`) plus decoded decimal and common LV1 name (e.g. `RC=FFFFFFEF (-17) INVALID_PARAMETER` or `RC=FFFFFFF5 (-11) NOT_OWNER/WRONG_STATE`).
  - Page C: optical node summary + real HDD control (`ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`).
  - Page D: scan summary (`OP:-17(PARAM) CL:-- RP:-6(FA)` or `OP:SKIP CL:-11(STATE) RP:-6(FA)`).

---

## 4. Built Artifacts and Hashes

All builds are located strictly in `local_only/p1d/` (never committed to git):

| Artifact | File Path | Size (Bytes) | SHA-256 |
|---|---|---:|---|
| **Variant A ELF** | `local_only/p1d/ps2_netemu_p1d_A.elf` | 11,294,504 | `fe27cb45ab4b730bb686bf47102181b76c0f0662e424d4afb34a24e679f9ce80` |
| **Variant A SELF** | `local_only/p1d/ps2_netemu_p1d_A.self` | 2,547,072 | `3067736955252f70698e614a51f0e031d792d8ea521e28573fea9c6186673181` |
| **Variant A Roundtrip** | `local_only/p1d/roundtrip_A.elf` | 11,294,504 | `fe27cb45ab4b730bb686bf47102181b76c0f0662e424d4afb34a24e679f9ce80` |
| **Variant B ELF** | `local_only/p1d/ps2_netemu_p1d_B.elf` | 11,294,504 | `8f0a222d14ead44b533e9174575e321658dae801e8be072455f3fa2c512853df` |
| **Variant B SELF** | `local_only/p1d/ps2_netemu_p1d_B.self` | 2,547,072 | `4eaa097be7f5aa3a817f90940a621a601d5050373265e47980e68dcbdd70bac0` |
| **Variant B Roundtrip** | `local_only/p1d/roundtrip_B.elf` | 11,294,504 | `8f0a222d14ead44b533e9174575e321658dae801e8be072455f3fa2c512853df` |

- **SELF Round-Trip Integrity**: Both `roundtrip_A.elf` and `roundtrip_B.elf` decrypted via `selfdec.py` match their respective patched ELFs byte-for-byte exact.

---

## 5. Strict PC Validation Results (`netemu_p1d\validate_pc.py`)

Emulated via pyghidra `EmulatorHelper` (PowerPC BE 64-bit):

1. **Hypercall Verification**:
   - **Variant A**:
     - Issues exactly ONE call to LV1 170 (`lv1_open_device`) with arguments `(bus_id=9, dev_id=0, flags=0)`.
     - Issues ZERO calls to LV1 171.
     - Issues only LV1 91 calls otherwise (repository traversal).
   - **Variant B**:
     - Issues exactly ONE call to LV1 171 (`lv1_close_device`) with arguments `(bus_id=4, dev_id=2)`.
     - Issues ZERO calls to LV1 170.
     - Issues only LV1 91 calls otherwise.
2. **Once-Only Execution**:
   - Evaluated across repeated menu invocations (`call_menu` rows 0..3 repeated 5 times): zero additional hypercalls issued after first evaluation.
3. **Return Code Edge Cases Tested (both variants)**:
   - Codes tested: `0` (SUCCESS), `-2` (RESOURCE_SHORTAGE), `-3` (NO_PRIVILEGE), `-4` (DENIED_BY_POLICY), `-5` (ACCESS_VIOLATION), `-6` (NO_ENTRY), `-9` (BUSY), `-10` (EMPTY), `-11` (NOT_OWNER/WRONG_STATE), `-17` (INVALID_PARAMETER), `-18` (HEX), `-99` (HEX), and 32-bit unsigned `0x1FFFFFFEF` (-17).
   - All 13 codes displayed matching decoded text and hex representation on Pages A and B.
4. **Memory Write Audit**:
   - Tracked memory writes during emulation confirmed 100% strictly confined to the stack frame (`r1`) or 96-byte mailbox `[0x930F20, 0x930F80)`.
   - Assembly store audit (`tools/p1a_audit.py`): 78 stores in added executable code; base registers are strictly `r1` (stack) and `r22` (mailbox).
   - IR pointer provenance audit (`audit_ir.py`): 50 LLVM stores verified inside stack or mailbox.
5. **Code Slot Sizing**:
   - Variant A code slot: 2,160 bytes / 14,320 capacity (15.1%).
   - Variant B code slot: 2,152 bytes / 14,320 capacity (15.0%).
6. **Exhaustive Index-Bounds Fuzzing**:
   - Page A: max reachable index 11 (table capacity 12 strings).
   - Page B: max reachable index 528 (table capacity 529 strings).
   - Page C: max reachable index 4504 (table capacity 4505 strings).
   - Page D: max reachable index 1151 (table capacity 1152 strings).
   - Zero out-of-bounds combinations across millions of fuzz states.
7. **Installer Script Syntax**:
   - `tools/install_netemu.ps1`: AST syntax valid.
   - `tools/restore_netemu.ps1`: AST syntax valid.

---

## 6. Progress Log
- [x] Initial verification of stock ELF and wrappers against `stock.elf`.
- [x] Initial draft of `docs/P1D_BUILD_NOTES.md`.
- [x] Create `netemu_p1d/` source tree based on `netemu_p1b_noopen/`.
- [x] Implement `PROBE_VARIANT` in `probe.c`, label generator, and `build.py`.
- [x] Build both Variant A and Variant B ELFs and SELFs.
- [x] SELF round-trip verification with `selfdec.py`.
- [x] Strict PC validation (`validate_pc.py` with pyghidra emulator, store audit, bounds fuzzing).
- [x] Write `docs/P1D_RESULT_TEMPLATE.md`.
- [x] Update `docs/P1D_BUILD_NOTES.md` with complete evidence.
