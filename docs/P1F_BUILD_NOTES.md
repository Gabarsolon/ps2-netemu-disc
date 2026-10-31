# P1f Build Notes: Stock Helper Clone Diagnostic Probe (sc 0 Isolation)

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1f ps2_netemu diagnostic probe build — build a label-only `ps2_netemu.self` diagnostic that issues ONE LV1 91 repository read through a byte-for-byte relocated clone of the stock helper (`0x111eb8`) placed in the code slot (`0x4800`), to determine whether the `sc` location (stock text vs code slot) or our hand-written wrapper caused the P1e power-off. Validate on the PC; do not install.

---

## 1. Goal and Hypotheses

### Background
- In P1b and P1d-A, hypercalls issued through our hand-written wrappers (`open_device` 170) powered off the console (CECH-25xx, Evilnat 4.93 Cobra).
- In P1e, we tested a harmless, known-good call: LV1 91 (repository read) for `bus/4/dev/2/type` (optical ROM device type, expected value 5) through our own hand-written wrapper in the code slot at `0x4800` (`sc 0` at `0x4828`).
- **PROVEN on console (P1e result):** The console powered off immediately upon entering the menu hook!
- Meanwhile, LV1 91 through the stock helper `0x111eb8` (`sc 0` at `0x111f10` in stock text) from the exact same menu hook works cleanly and repeatedly.

### Hypotheses Under Test
- **Hypothesis A (Location / Context Dependency):** The guest kernel bridge, LV1 hypervisor, or CFW/Cobra enforces that `sc 0` must be executed from stock text (e.g. caller address / SRR0 check, or code slot memory execution restrictions):
  - *Prediction:* The stock helper clone relocated to the code slot will also power off the console.
- **Hypothesis B (Wrapper Defect):** The crash was caused by defects in our hand-written wrapper (e.g. Condition Register preservation, stack frame layout, register corruption, non-volatile register preservation):
  - *Prediction:* The byte-for-byte clone of the stock helper in the code slot will succeed (Page C MATCH).
  - *Implication:* A generic clone with variable `r11` can be used to safely issue hypercalls (including 170/171), and the P1b/P1d crashes were caused by the wrapper rather than LV1 rejecting device opens.

---

## 2. Re-Check of Guest Bridge Analysis (0xc00..0xca0)

In `docs/P1E_BUILD_NOTES.md`, the previous agent analyzed `0xc50..0xca0` and concluded that since the privilege table at `0x238c` is initialized to `2`, and the bridge performs no checks on SRR0, our hand-written wrapper should work.
However, P1e crashed on hardware. We re-examined `0xc00..0xca0` and the stock helper `0x111eb8` to identify what was overlooked:

1. **Condition Register (CR) Destruction in Bridge:**
   - At `0x0c04`, the bridge executes `mfcr r4` to read CR into `r4`.
   - In the hypercall branch (`cmpwi r11, 0` -> `blt 0xc4c`), at `0x0c54`, `r4` is immediately overwritten: `0x0c54: rlwinm r4, r5, 0x5, 0x1c, 0x1c`.
   - CR is **never saved to SPRGs or memory**, and `rfid` at `0x0cbc` restores only PC (SRR0) and MSR (SRR1) — **it does NOT restore CR**!
   - Consequently, executing `sc 0` clobbers CR with whatever comparison results the bridge produced (`cmpdi r11, 0x100`, `cmpd r6, r5`).
   - In the PPC64 ELF ABI, CR fields `cr2`, `cr3`, and `cr4` are **non-volatile** (callee-saved). Compilers (like Clang `-Oz` compiling `run_probe`) rely on non-volatile CR fields across function calls.
   - Stock helper `0x111eb8` explicitly saves CR before `sc 0` (`0x111eb8: mfcr r12; 0x111ee4: stw r12, 0x88(r1)`) and restores `cr4` after `sc 0` (`0x111f38: lwz r12, 0x88(r1); 0x111f48: mtocrf 0x8, r12`).
   - P1e's hand-written wrapper did **NOT** save or restore CR! Clobbering CR in `run_probe` could cause control flow corruption leading to unauthorized stores into read-only memory (triggering immediate power off).

2. **Stack Frame Geometry and Caller Linkage Area:**
   - Stock helper `0x111eb8` allocates a standard `0x80` (128-byte) stack frame (`stdu r1, -0x80(r1)`).
   - In standard PPC64 ABI, the caller's linkage area sits at `+0` (backchain), `+8` (CR), `+16` (LR) relative to caller's SP. From the callee's new SP, these offsets are `+0x88` and `+0x90`. Stock helper stores CR at `0x88(r1)` and LR at `0x90(r1)`.
   - P1e created a non-standard 64-byte frame (`stdu r1, -64(r1)`), did not save LR or CR, and placed output pointers in `32(r1)` and `40(r1)` (the callee parameter area).

3. **Output Pointer Storage and Error Handling:**
   - Stock helper `0x111eb8` preserves `out1*` and `out2*` in non-volatile registers `r30` and `r31`.
   - After `sc 0`, stock helper checks `rc == 0`. If `rc != 0`, it branches around the stores to `0x111f34`, leaving `*out1` and `*out2` completely untouched!
   - P1e unconditionally stored returned `r4` and `r5` into `*out1` and `*out2`, regardless of `rc`.

4. **Node 1 Argument Folding:**
   - Stock helper expects incoming `r5 = node1` (e.g. `KEY_BUS(4) = 0x6275730000000004`), folds `lo32` and `hi32` together into `r4 = 0x62757304`, and guards with `and r0, r11, r5; cmpdi cr7, r0, 0; bne cr7, panic`.
   - P1e had a completely different argument order and passed pre-folded `0x62757304ULL` manually.

---

## 3. Stock Helper Instruction Decoding (0x111eb8..0x111f6c, 180 bytes)

Verified in `local_only/stock.elf` using pyghidra (`tools/p1f_inspect_stock_helper.py`):

| Offset | Address | Raw Word | Instruction | Function / Role |
|---|---|---|---|---|
| +0x00 | `0x111eb8` | `7d800026` | `mfcr r12` | Save CR into r12 |
| +0x04 | `0x111ebc` | `78ab0020` | `rldicl r11, r5, 0, 32` | r11 = lo32(node1) |
| +0x08 | `0x111ec0` | `78a50022` | `rldicl r5, r5, 32, 32` | r5 = hi32(node1) |
| +0x0C | `0x111ec4` | `f821ff81` | `stdu r1, -128(r1)` | Allocate 0x80 (128-byte) stack frame |
| +0x10 | `0x111ec8` | `fbc10070` | `std r30, 112(r1)` | Save non-volatile r30 |
| +0x14 | `0x111ecc` | `fbe10078` | `std r31, 120(r1)` | Save non-volatile r31 |
| +0x18 | `0x111ed0` | `7c7e1b78` | `or r30, r3, r3` | r30 = out1* |
| +0x1C | `0x111ed4` | `7c9f2378` | `or r31, r4, r4` | r31 = out2* |
| +0x20 | `0x111ed8` | `7cc33378` | `or r3, r6, r6` | r3 = node2 (temp) |
| +0x24 | `0x111edc` | `7ce63b78` | `or r6, r7, r7` | r6 = node3 |
| +0x28 | `0x111ee0` | `7d074378` | `or r7, r8, r8` | r7 = node4 |
| +0x2C | `0x111ee4` | `91810088` | `stw r12, 136(r1)` | Save CR at SP+0x88 (caller frame) |
| +0x30 | `0x111ee8` | `7c0802a6` | `mfspr r0, LR` | Read LR |
| +0x34 | `0x111eec` | `f8010090` | `std r0, 144(r1)` | Save LR at SP+0x90 (caller frame) |
| +0x38 | `0x111ef0` | `7d602838` | `and r0, r11, r5` | Guard: check if lo32 & hi32 != 0 |
| +0x3C | `0x111ef4` | `2fa00000` | `cmpdi cr7, r0, 0` | Compare r0 with 0 |
| +0x40 | `0x111ef8` | `40de0068` | `bne cr7, 0x111f60` | Internal branch (+0x68) to panic path |
| +0x44 | `0x111efc` | `7d642b78` | `or r4, r11, r5` | r4 = folded node1 |
| +0x48 | `0x111f00` | `7c651b78` | `or r5, r3, r3` | r5 = node2 |
| +0x4C | `0x111f04` | `3960005b` | `li r11, 91` | Hypercall number = 91 |
| +0x50 | `0x111f08` | `38600001` | `li r3, 1` | Partition ID = 1 |
| +0x54 | `0x111f0c` | `656b8000` | `oris r11, r11, 0x8000` | r11 = 0x8000005b |
| +0x58 | `0x111f10` | `44000002` | `sc 0` | Issue hypercall |
| +0x5C | `0x111f14` | `2e230000` | `cmpdi cr4, r3, 0` | Check rc == 0 in cr4 |
| +0x60 | `0x111f18` | `39200000` | `li r9, 0` | Default r9 = 0 |
| +0x64 | `0x111f1c` | `38000000` | `li r0, 0` | Default r0 = 0 |
| +0x68 | `0x111f20` | `41920034` | `beq cr4, 0x111f54` | Internal branch (+0x34) if rc == 0 |
| +0x6C | `0x111f24` | `2fa30000` | `cmpdi cr7, r3, 0` | Compare rc with 0 in cr7 |
| +0x70 | `0x111f28` | `409e000c` | `bne cr7, 0x111f34` | Internal branch (+0x0C) if rc != 0 |
| +0x74 | `0x111f2c` | `f81e0000` | `std r0, 0(r30)` | *out1 = val1 |
| +0x78 | `0x111f30` | `f93f0000` | `std r9, 0(r31)` | *out2 = val2 |
| +0x7C | `0x111f34` | `e8010090` | `ld r0, 144(r1)` | Restore LR from caller frame |
| +0x80 | `0x111f38` | `81810088` | `lwz r12, 136(r1)` | Restore CR from caller frame |
| +0x84 | `0x111f3c` | `ebc10070` | `ld r30, 112(r1)` | Restore r30 |
| +0x88 | `0x111f40` | `7c0803a6` | `mtspr LR, r0` | Set LR |
| +0x8C | `0x111f44` | `ebe10078` | `ld r31, 120(r1)` | Restore r31 |
| +0x90 | `0x111f48` | `7d908120` | `mtocrf 8, r12` | Restore cr4 field of CR |
| +0x94 | `0x111f4c` | `38210080` | `addi r1, r1, 128` | Deallocate stack frame |
| +0x98 | `0x111f50` | `4e800020` | `blr` | Return |
| +0x9C | `0x111f54` | `7c802378` | `or r0, r4, r4` | r0 = returned val1 (r4) |
| +0xA0 | `0x111f58` | `7ca92b78` | `or r9, r5, r5` | r9 = returned val2 (r5) |
| +0xA4 | `0x111f5c` | `4bffffc8` | `b 0x111f24` | Internal branch (-0x38) to store |
| +0xA8 | `0x111f60` | `38600001` | `li r3, 1` | Panic arg r3 = 1 |
| +0xAC | `0x111f64` | `4bfffb19` | `bl 0x111a7c` | **External branch** to panic helper |
| +0xB0 | `0x111f68` | `60000000` | `ori r0, r0, 0` | nop |

### Branch Relocation Analysis
- Total instructions: 45 (180 bytes, `0xB4` bytes).
- **Internal branches:**
  - `+0x40` (`bne cr7, +0x68` -> `+0xA8`)
  - `+0x68` (`beq cr4, +0x34` -> `+0x9C`)
  - `+0x70` (`bne cr7, +0x0C` -> `+0x7C`)
  - `+0xA4` (`b -0x38` -> `+0x6C`)
  All four internal branch displacements are strictly relative within the contiguous 180-byte block. When copied contiguously into the code slot, **these 4 branch words remain 100% identical to stock**!
- **External branch:**
  - `+0xAC` (`bl 0x111a7c`): calls panic helper at `0x111a7c`.
  - When relocated to `0x4800 + 0xAC = 0x48AC`, the displacement is `0x111a7c - 0x48ac = +0x10d1d0` (+1,102,288 bytes).
  - This fits comfortably in the 24-bit branch displacement field (+/- 32 MB).
  - The branch is re-targeted to the exact same absolute address `0x111a7c`.
  - (Note: in the test, `n1 = KEY_BUS(4) = 0x6275730000000004`, so `lo32 & hi32 = 4 & 0x62757300 = 0`, so this panic branch is never taken).
- **Byte Equality:**
  - Exactly 176 out of 180 bytes (44 out of 45 instructions) are **byte-for-byte identical** between stock and clone.
  - Exactly 1 word (+0xAC) is adjusted for the PC-relative displacement of the `bl` to `0x111a7c`.

---

## 4. Netemu P1f Implementation Architecture

### Relocated Clone (`lv1_repo_clone`)
- Placed at `0x4800` in the code slot.
- Extent: `0x4800..0x48B4` (180 bytes).
- Contains its own `sc 0` instruction at `0x4858`.
- C Signature:
  `s64 lv1_repo_clone(u64 *out1, u64 *out2, u64 node1, u64 node2, u64 node3, u64 node4);`
  Identical signature and register convention to stock `repo_read`.

### Trampolines & Code Slot Layout
- `0x4800..0x48B4`: `lv1_repo_clone` (180 bytes, relocated stock helper).
- `0x48C0..0x48FC`: `repo_read` trampoline (calls stock `0x111eb8`).
- `0x4900..0x493C`: `entry_menu` hook trampoline (calls `s4_menu`).
- `0x4A00..0x5340`: C payload `.text` (`probe.c`).
- Total code slot footprint: 2,880 bytes (`0x4800..0x5340`), using 20.1% of the 14,320-byte capacity.

### Mailbox (0x930F20..0x930F80, 96 bytes)
- Target node stock helper results: `stock_rc` (offset 40), `stock_val1` (offset 48), `stock_val2` (offset 56).
- Target node clone results: `raw_rc` (offset 44), `raw_val1` (offset 80), `raw_val2` (offset 88).
- Match status: `match_status` (offset 28: 1=MATCH, 2=DIFF).
- Status flags: bit 0 (STARTED), bit 1 (DONE), bit 2 (RAW_ATTEMPTED), bit 3 (RAW_OK).

### Diagnostic Labels (Extended RO Segment at 0x74E930)
- Page A (`selected & 3 == 0`): `P1F-CLONE DONE rc=<name> v=<value>` (96 strings)
- Page B (`selected & 3 == 1`): `P1F-STOCK DONE rc=<name> v=<value>` (96 strings)
- Page C (`selected & 3 == 2`): `P1F MATCH: CLONE==STOCK (...)` or `P1F DIFF: ...` (230 strings)
- Page D (`selected & 3 == 3`): Scan summary (`ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`) (4505 strings)

---

## 5. Built Artifacts and Hashes

All builds are located strictly in `local_only/p1f/` (gitignored, never committed to git):

| Artifact | File Path | Size (Bytes) | SHA-256 |
|---|---|---:|---|
| **P1f Patched ELF** | `local_only/p1f/ps2_netemu_p1f.elf` | 11,228,968 | `aab7d2ed6fb9e1bb575c74a0ec352c7a5109142223b72c592d0a0b266ed5edbe` |
| **P1f Resigned SELF** | `local_only/p1f/ps2_netemu_p1f.self` | 2,541,008 | `abc8eeeed7a51fc093a87469540e785b9a06d2f917da88b3c38596b5a456d655` |
| **P1f Decrypted Roundtrip** | `local_only/p1f/roundtrip.elf` | 11,228,968 | `aab7d2ed6fb9e1bb575c74a0ec352c7a5109142223b72c592d0a0b266ed5edbe` |

- **SELF Round-Trip Integrity**: Decrypted `roundtrip.elf` via `selfdec.py` matches `ps2_netemu_p1f.elf` byte for byte.

---

## 6. Strict PC Validation Results (`netemu_p1f\validate_pc.py`)

Emulated via pyghidra `EmulatorHelper` (PowerPC BE 64-bit):

1. **Clone Byte Equality**:
   - 176 out of 180 bytes equal stock helper byte-for-byte exact.
   - Exactly 1 branch instruction at `0xAC` (`bl 0x111a7c`) relocated; displacement resolves to `0x111A7C` exact.
2. **Hypercall Verification**:
   - Exactly ONE clone repository read issued through relocated clone at `0x4858` with args `(partition_id=1, node1=0x62757304, node2=KEY_DEV(2), node3=KEY_TYPE, node4=0)`.
   - Exactly ZERO calls to LV1 170 (`open_device`) or LV1 171 (`close_device`).
   - All hypercalls are LV1 91 only.
3. **Once-Only Execution**:
   - Evaluated across repeated menu invocations (`call_menu` rows 0..3 repeated 5 times): zero additional hypercalls issued after first evaluation.
4. **Baseline Scenario Labels**:
   - Page A (row 0): `P1F-CLONE DONE rc=SUCCESS v=5(ROM)`
   - Page B (row 1): `P1F-STOCK DONE rc=SUCCESS v=5(ROM)`
   - Page C (row 2): `P1F MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)`
   - Page D (row 3): `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`
5. **Edge Cases Tested**:
   - Success match (`rc=0, v=5`), error match (`rc=-4`, `rc=-6`, `rc=-17`), RC mismatch (DIFF in RC), value mismatch (DIFF in VAL).
   - All edge cases verified against Pages A, B, and C.
6. **Memory Write Tracking**:
   - 100% of memory writes during emulation stayed strictly inside stack (`[SP - 0x10000, SP + 0x1000]`) and mailbox (`[0x930F20, 0x930F80)`).
   - Zero stores into read-only memory.
7. **Bounds Fuzzing**:
   - Fuzzed all table indices over full range: Page A/B max reachable index 95 (< 96), Page C max reachable index 229 (< 230), Page D max reachable index 4504 (< 4505). All bounded.
8. **Strict Store & SC Audit (`tools/p1a_audit.py`)**:
   - Exactly ONE `sc` instruction found in changed executable ranges: `[(18520, 0)]` (`18520 = 0x4858`).
   - Store base registers: `r1` (stack), `r22` (mailbox `0x930F20`), `r30`/`r31` (stock clone out pointers).
9. **Installer Syntax**:
   - `tools/install_netemu.ps1` and `tools/restore_netemu.ps1` parse-checked with zero syntax errors.
