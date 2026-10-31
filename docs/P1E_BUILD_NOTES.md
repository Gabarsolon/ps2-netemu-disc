# P1e Build Notes: Hypercall Isolation Diagnostic Probe (Stock sc vs Code Slot sc)

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1e ps2_netemu diagnostic probe build — test whether issuing a harmless, known-good hypercall (LV1 91 repository read) through our own `sc 0` wrapper in the code slot succeeds or powers off the console.

---

## 1. Goal and Background

In P1b, `lv1_open_device(4, 2, 0)` on the optical node powered off the console (CECH-25xx, Evilnat 4.93 Cobra).
Ablation (`netemu_p1b_noopen`) confirmed that skipping `lv1_open_device` allowed the menu hook to run cleanly and display diagnostic labels.
In P1d, Variant A issued `lv1_open_device(bus_id=9, dev_id=0, flags=0)` through our own `sc 0` wrapper at `0x4820` from the menu hook. Bus 9 touches no device. The console crashed (powered off).

This established three candidate causes for the shutdown:
1. **LV1 call 170 (`open_device`) itself is fatal** in this partition context (or in 4.93 / Evilnat, or after partition initialization).
2. **Hypercalls executed from our code slot / own `sc 0` wrapper** are fatal (e.g. guest kernel bridge rejecting based on caller address SRR0, or code slot execution restrictions). Note that normal repository reads (LV1 91) succeed because they execute through the stock helper `0x111eb8` whose `sc 0` instruction is at `0x111f10` in stock text.
3. **Hypercall timing / caller context**: executing hypercalls from the PS-button menu hook context outside the stock helper.

P1e directly tests Candidate 2 vs Candidates 1 & 3:
- It issues a harmless, known-good LV1 91 repository read (`bus/4/dev/2/type` or `bus/4/id`) through a **brand-new own wrapper in the code slot** (`lv1_repo_raw`), passing identical registers to stock `0x111eb8`.
- If the raw read returns the expected value (e.g., 5 for type or matching stock id), our own wrapper in the code slot and the menu hook context are fully validated, proving that LV1 170 itself caused the previous crashes.
- If the console powers off, executing hypercalls from our own code slot wrapper is fatal, explaining both P1b and P1d-A crashes without implicating 170.

---

## 2. Stock ELF Verification Findings (pyghidra, stock.elf)

Byte-level and pseudo-disassembly verification performed with pyghidra (`tools/p1e_verify_stock.py`, `tools/p1e_inspect_repo.py`, `tools/p1e_check_bridge_table.py`):

### 2.1 Repository Helper `0x111eb8` and `sc 0` at `0x111f10`
- Helper entry `0x111eb8`:
  - Receives arguments: `r3 = out1*`, `r4 = out2*`, `r5 = node1` (folded high/low 32-bit), `r6 = node2`, `r7 = node3`, `r8 = node4`.
  - Saves `out1*` into `r30`, `out2*` into `r31`.
  - Sets up hypercall registers:
    - `r3 = 0x1` (partition-id argument = 1, PME repository selector).
    - `r4 = node1` (from folded r5).
    - `r5 = node2` (from r6).
    - `r6 = node3` (from r7).
    - `r7 = node4` (from r8).
    - `r11 = 0x8000005b` (`li r11, 0x5b; oris r11, r11, 0x8000`).
  - Executes `sc 0` at `0x111f10`.
  - Post-call return processing (`0x111f14..0x111f5c`):
    - `r3` contains return code (`rc`, 0 on success).
    - `r4` contains returned `val1`.
    - `r5` contains returned `val2`.
    - If `rc == 0`: branches to `0x111f54`, which moves `r4 -> r0` and `r5 -> r9`, then falls through to store `std r0, 0(r30)` (`*out1 = val1`) and `std r9, 0(r31)` (`*out2 = val2`).
    - If `rc != 0`: stores are skipped, leaving `*out1` and `*out2` untouched; returns `rc` in `r3`.

### 2.2 Guest `sc 0` Bridge (`0x0c50..0x0ca0`)
- Vector entry `0x0c00` saves registers to SPRGs, extracts USPRG0 (`spr088`) into `r5`, checks if `r11` has high bit set (`cmpwi r11, 0; blt 0xc4c`), and enters bridge at `0x0c50`.
- Strips high marker: `0x0c50: xoris r11, r11, 0x8000`.
- Call counter: increments per-bank counter at `0x27e0(r4)`.
- Bounds check: `0x0c64: cmpdi r11, 0x100; bge 0x0f48`. Rejects call numbers >= 256.
- Privilege byte lookup:
  - Bank selection via USPRG0: `0x0c6c: rlwinm r4, r5, 0xa, 0x17, 0x17` (bank offset 0 or 0x100).
  - Inserts call number: `0x0c70: rldimi r4, r11, 0x0, 0x38`.
  - Loads table byte: `0x0c74: lbz r6, 0x238c(r4)`. Table base is `0x238c`.
- Privilege check:
  - Caller status: `0x0c78: mfspr r4, SRR1`.
  - Extracts caller PR bit: `0x0c7c: rldicl r5, r4, 0x32, 0x3f`. In PPC64 BE, bit 49 is MSR.PR (0 = supervisor, 1 = user/problem state).
  - Check: `0x0c80: cmpd r6, r5; 0x0c84: ble 0x0f58`.
  - If `r6 <= PR`, branches to panic (`0x0f58: li r3, 0x11f; li r11, 0xff; sc 1`).
  - Thus: byte `2` admits both `PR=0` (2 > 0) and `PR=1` (2 > 1).
- Table initialization at runtime:
  - Initializer `0x10550` (called at `0x16f38` and `0x175e0`) and `0x10834` (called at `0x11cac`) loops 256 times (`li r9, 0x100; mtspr CTR, r9`).
  - Table base from TOC (`-0x7ff8(r2)` = `0x1c30`). Base + `0x750` + `0xc` = `0x238c`.
  - Sets ALL 256 bytes to `2` (`li r10, 0x2; stb r10, 0xc(r9); bdnz ...`).
  - Therefore, at runtime, table bytes for `n=0x5b` (91), `n=0xaa` (170), and `n=0xab` (171) are all initialized to `2`.
- Calling Address (SRR0) Dependency:
  - `0x0c94: mfspr r4, SRR0; mtspr SPRG1, r4` saves SRR0 to SPRG1 before `sc 1`.
  - After `sc 1`, `0x0cac: mtspr SRR0, r4` restores SRR0.
  - The bridge performs ZERO checks, comparisons, or branches on SRR0.
  - Guest bridge handling depends strictly on call number < 256 and the privilege byte vs SRR1.PR, with NO dependency on caller address (SRR0).

---

## 3. Implementation Details (`netemu_p1e\`)

- **Probe Target Node**: `bus/4/dev/2/type` (optical ROM device type, expected `v1 = 5`, `v2 = 0`, `rc = 0`).
- **Code Slot Layout (`0x4800..0x4900`)**:
  - `0x4800..0x4844` (68 bytes): `lv1_repo_raw` wrapper:
    - Sets up stack frame (`stdu r1, -64(r1)`).
    - Preserves `out1*` (`std r7, 32(r1)`) and `out2*` (`std r8, 40(r1)`).
    - Rearranges arguments to match `0x111eb8`: `r7=n4`, `r6=n3`, `r5=n2`, `r4=n1`.
    - Sets partition ID: `li r3, 1`.
    - Sets hypercall number: `li r11, 0x5b; oris r11, r11, 0x8000` (`0x8000005b`).
    - Issues `sc 0` at `0x4828`.
    - Restores output pointers: `ld r7, 32(r1)`, `ld r8, 40(r1)`.
    - Stores outputs: `std r4, 0(r7)` (`*out1 = val1`), `std r5, 0(r8)` (`*out2 = val2`).
    - Deallocates stack frame: `addi r1, r1, 64`.
    - Returns `blr` with `rc` in `r3`.
  - `0x4850..0x488c` (60 bytes): `repo_read` trampoline (calls stock helper `0x111eb8`).
  - `0x4890..0x48cc` (60 bytes): `entry_menu` hook trampoline (calls `s4_menu`).
  - `0x4900..0x5238` (2360 bytes): compiled C payload from `probe.c`.
  - Total code slot footprint: 2616 bytes (`0x4800..0x5238`), well under 14,320-byte capacity.
- **Fail-open Hook at `0x270FFC`**:
  - Patched with `bl entry_menu` (`0x4890`).
  - Expected original word `0xe882cea8` verified; fails open if mismatched.
- **Mailbox (`struct ProbeState`, 96 bytes at `0x930F20`)**:
  - Status flags: `STATUS_STARTED` (bit 0), `STATUS_DONE` (bit 1), `STATUS_RAW_ATTEMPTED` (bit 2), `STATUS_RAW_OK` (bit 3).
  - Target node stock helper results: `stock_rc` (offset 40), `stock_val1` (offset 48), `stock_val2` (offset 56).
  - Target node raw wrapper results: `raw_rc` (offset 44), `raw_val1` (offset 80), `raw_val2` (offset 88).
  - Match status: `match_status` (offset 28: 1=MATCH, 2=DIFF, 0=NOT_RUN).
  - Preserves standard scan offsets: `rom_bus_id` (offset 64), `rom_dev_id` (offset 72).
  - All writes strictly audited to mailbox and stack.
- **Immutable Label Tables (Extended RO Segment at `0x74E930..0x79B8F0`, 315,328 bytes)**:
  - Page A (`selected & 3 == 0`): `P1E-RAW DONE rc=<name> v=<value>` (96 strings).
  - Page B (`selected & 3 == 1`): `P1E-STOCK DONE rc=<name> v=<value>` (96 strings).
  - Page C (`selected & 3 == 2`): `P1E MATCH: RAW==STOCK (...)` or `P1E DIFF: ...` (230 strings).
  - Page D (`selected & 3 == 3`): Scan summary (`ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`) (4505 strings).

---

## 4. Built Artifacts and Hashes

All builds are located strictly in `local_only/p1e/` (never committed to git):

| Artifact | File Path | Size (Bytes) | SHA-256 |
|---|---|---:|---|
| **P1e Patched ELF** | `local_only/p1e/ps2_netemu_p1e.elf` | 11,228,968 | `81a672f33c5d247ed7d71014ba0da5a27e6285881c5db7630870eb1eb2b3e12e` |
| **P1e Resigned SELF** | `local_only/p1e/ps2_netemu_p1e.self` | 2,540,944 | `c9cfcea2d218c62f7d6add5d0f62700ad431868641dcf4e292bd845ae968c33d` |
| **P1e Decrypted Roundtrip** | `local_only/p1e/roundtrip.elf` | 11,228,968 | `81a672f33c5d247ed7d71014ba0da5a27e6285881c5db7630870eb1eb2b3e12e` |

- **SELF Round-Trip Integrity**: `roundtrip.elf` decrypted via `selfdec.py` matches `ps2_netemu_p1e.elf` byte-for-byte exact.

---

## 5. Strict PC Validation Results (`netemu_p1e\validate_pc.py`)

Emulated via pyghidra `EmulatorHelper` (PowerPC BE 64-bit):

1. **Hypercall Verification**:
   - Exactly ONE raw repository read issued through our own wrapper at `0x4828` with args `(partition_id=1, node1=0x62757304, node2=KEY_DEV(2), node3=KEY_TYPE, node4=0)`.
   - Exactly ZERO calls to LV1 170 (`open_device`) or LV1 171 (`close_device`).
   - All hypercalls are LV1 91 only.
2. **Once-Only Execution**:
   - Evaluated across repeated menu invocations (`call_menu` rows 0..3 repeated 5 times): zero additional hypercalls issued after first evaluation.
3. **Baseline Scenario Labels**:
   - Page A (row 0): `P1E-RAW DONE rc=SUCCESS v=5(ROM)`
   - Page B (row 1): `P1E-STOCK DONE rc=SUCCESS v=5(ROM)`
   - Page C (row 2): `P1E MATCH: RAW==STOCK (RC=0 SUCCESS, V=5 ROM)`
   - Page D (row 3): `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`
4. **Edge Cases Tested**:
   - Success match (`rc=0, v=5`), error match (`rc=-4`, `rc=-6`, `rc=-17`), RC mismatch (DIFF in RC), value mismatch (DIFF in VAL).
   - All edge cases verified against Pages A, B, and C.
5. **Memory Write Audit**:
   - 100% of memory writes during emulation stayed strictly inside stack (`[SP - 0x10000, SP + 0x1000]`) and mailbox (`[0x930F20, 0x930F80)`).
   - Zero stores into read-only memory.
6. **Bounds Fuzzing**:
   - Fuzzed all table indices over full range: Page A/B max reachable index 95 (< 96), Page C max reachable index 229 (< 230), Page D max reachable index 4504 (< 4505). All bounded.
7. **Strict Store & SC Audit (`tools/p1a_audit.py`)**:
   - Exactly ONE `sc` instruction found in changed executable ranges: `[(18472, 0)]` (`18472 = 0x4828`).
   - Store base registers: `r1` (stack), `r7`/`r8` (wrapper output pointers), `r22` (mailbox `0x930F20`).
8. **Installer Syntax**:
   - `tools/install_netemu.ps1` and `tools/restore_netemu.ps1` parse-checked with zero syntax errors.
