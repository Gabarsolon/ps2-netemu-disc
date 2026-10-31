# P1g Build Notes: Generic Safe LV1 Hypercall Wrapper & Diagnostic Variants (G0..G3)

## Status
- **Date**: 2026-10-31
- **Author**: Antigravity
- **Task**: P1g ps2_netemu diagnostic probe build — build a generic, safe LV1 hypercall wrapper `lv1_hcall(num, a1, a2, a3, a4, a5)` modeled exactly on the stock helper (`0x111eb8..0x111f6c`), and four diagnostic variants (G0, G1, G2, G3). Validate on PC; do not install.

---

## 1. Goal and Background

In P1e, our hand-written wrapper (`stdu r1, -64(r1)`, no CR/LR save, outputs placed on the stack) triggered an immediate console power-off upon entering the menu hook, even for a known-good repository read (LV1 91).
In P1f, a byte-for-byte relocated clone of the stock repository helper (`0x111eb8`) placed in the code slot at `0x4800` (`sc 0` at `0x4858`) worked cleanly and repeatedly on the console (reporting `P1F MATCH CLONE==STOCK`).
This proved on hardware:
1. Executing `sc 0` from the code slot is 100% safe when adhering to the stock helper's register discipline and prologue/epilogue.
2. The guest bridge at `0xc50..0xca0` does not restore the Condition Register (`rfid` at `0x0cbc` restores only SRR0 and SRR1), and clobbers CR.
3. The previous shutdowns in P1b (open optical node) and P1d-A (open invalid bus) were caused by defects in our hand-written wrapper, NOT by LV1 170.

Therefore, `open_device` (HV 170) has NOT yet been tested. P1g creates a generic, safe hypercall wrapper based directly on the stock helper, and tests four diagnostic variants:
- **G0**: Validates the generic wrapper with LV1 91 (repository read of `bus/4/dev/2/type`, optical ROM device type, expected rc=0, val=5). Expected to match stock helper.
- **G1**: Issues `lv1_hcall(170, 9, 0, 0, 0, 0)` (`open_device` with invalid bus 9, expected -17 `INVALID_PARAMETER`). Does not touch hardware.
- **G2**: Issues `lv1_hcall(171, 4, 2, 0, 0, 0)` (`close_device` on optical node without opening, expected -11 `NOT_OWNER`).
- **G3**: Issues `lv1_hcall(170, 4, 2, 0, 0, 0)` (REAL open of optical node, flags 0); if rc == 0, immediately issues `lv1_hcall(171, 4, 2, 0, 0, 0)`. Records both return codes.

---

## 2. Stock Helper vs. Generic Wrapper Instruction Diff

Verified against `local_only/stock.elf` (SHA-256 `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`).

The stock helper occupies `0x111eb8..0x111f6c` (45 instructions, 180 bytes, `0xB4` bytes).
The generic wrapper `lv1_hcall` occupies the exact same footprint (`0x4800..0x48B4`, 180 bytes) with `sc 0` positioned at the identical offset `0x4858` (+0x58).

### Side-by-Side Instruction Comparison Table

| Offset | Stock Address | Stock Word | Stock Instruction | Generic Word | Generic Instruction | Notes / Reason for Diff |
|---|---|---|---|---|---|---|
| +0x00 | `0x111eb8` | `7d800026` | `mfcr r12` | `7d800026` | `mfcr r12` | **IDENTICAL**: Save CR into r12 |
| +0x04 | `0x111ebc` | `78ab0020` | `rldicl r11,r5,0,32` | `60000000` | `ori r0,r0,0` | Replaced stock node1 lo32 extraction with nop |
| +0x08 | `0x111ec0` | `78a50022` | `rldicl r5,r5,32,32` | `60000000` | `ori r0,r0,0` | Replaced stock node1 hi32 extraction with nop |
| +0x0C | `0x111ec4` | `f821ff81` | `stdu r1,-128(r1)` | `f821ff81` | `stdu r1,-128(r1)` | **IDENTICAL**: Allocate 0x80 stack frame |
| +0x10 | `0x111ec8` | `fbc10070` | `std r30,112(r1)` | `fbc10070` | `std r30,112(r1)` | **IDENTICAL**: Save caller r30 at SP+0x70 |
| +0x14 | `0x111ecc` | `fbe10078` | `std r31,120(r1)` | `fbe10078` | `std r31,120(r1)` | **IDENTICAL**: Save caller r31 at SP+0x78 |
| +0x18 | `0x111ed0` | `7c7e1b78` | `or r30,r3,r3` | `3fc00093` | `lis r30,0x93` | Load mailbox hi16 for r30 output ptr |
| +0x1C | `0x111ed4` | `7c9f2378` | `or r31,r4,r4` | `3bde0f70` | `addi r30,r30,0x0f70` | r30 = `0x930F70` (`&S->raw_val1`) |
| +0x20 | `0x111ed8` | `7cc33378` | `or r3,r6,r6` | `3bfe0008` | `addi r31,r30,8` | r31 = `0x930F78` (`&S->raw_val2`) |
| +0x24 | `0x111edc` | `7ce63b78` | `or r6,r7,r7` | `7c6b1b78` | `or r11,r3,r3` | r11 = num (from incoming r3) |
| +0x28 | `0x111ee0` | `7d074378` | `or r7,r8,r8` | `7c832378` | `or r3,r4,r4` | r3 = a1 (from incoming r4) |
| +0x2C | `0x111ee4` | `91810088` | `stw r12,136(r1)` | `91810088` | `stw r12,136(r1)` | **IDENTICAL**: Save CR at SP+0x88 |
| +0x30 | `0x111ee8` | `7c0802a6` | `mfspr r0,LR` | `7c0802a6` | `mfspr r0,LR` | **IDENTICAL**: Read LR |
| +0x34 | `0x111eec` | `f8010090` | `std r0,144(r1)` | `f8010090` | `std r0,144(r1)` | **IDENTICAL**: Save LR at SP+0x90 |
| +0x38 | `0x111ef0` | `7d602838` | `and r0,r11,r5` | `7ca42b78` | `or r4,r5,r5` | r4 = a2 (from incoming r5) |
| +0x3C | `0x111ef4` | `2fa00000` | `cmpdi cr7,r0,0` | `7cc53378` | `or r5,r6,r6` | r5 = a3 (from incoming r6) |
| +0x40 | `0x111ef8` | `40de0068` | `bne cr7,0x111f60` | `7ce63b78` | `or r6,r7,r7` | r6 = a4 (from incoming r7) |
| +0x44 | `0x111efc` | `7d642b78` | `or r4,r11,r5` | `7d074378` | `or r7,r8,r8` | r7 = a5 (from incoming r8) |
| +0x48 | `0x111f00` | `7c651b78` | `or r5,r3,r3` | `60000000` | `ori r0,r0,0` | nop |
| +0x4C | `0x111f04` | `3960005b` | `li r11,91` | `60000000` | `ori r0,r0,0` | nop |
| +0x50 | `0x111f08` | `38600001` | `li r3,1` | `60000000` | `ori r0,r0,0` | nop |
| +0x54 | `0x111f0c` | `656b8000` | `oris r11,r11,0x8000` | `656b8000` | `oris r11,r11,0x8000` | **IDENTICAL**: Set HV call bit 63 |
| +0x58 | `0x111f10` | `44000002` | `sc 0` | `44000002` | `sc 0` | **IDENTICAL**: Issue hypercall |
| +0x5C | `0x111f14` | `2e230000` | `cmpdi cr4,r3,0` | `2e230000` | `cmpdi cr4,r3,0` | **IDENTICAL**: Check rc == 0 in cr4 |
| +0x60 | `0x111f18` | `39200000` | `li r9,0` | `39200000` | `li r9,0` | **IDENTICAL**: Default r9 = 0 |
| +0x64 | `0x111f1c` | `38000000` | `li r0,0` | `38000000` | `li r0,0` | **IDENTICAL**: Default r0 = 0 |
| +0x68 | `0x111f20` | `41920034` | `beq cr4,+0x34` | `41920034` | `beq cr4,+0x34` | **IDENTICAL**: Branch to +0x9C if rc == 0 |
| +0x6C | `0x111f24` | `2fa30000` | `cmpdi cr7,r3,0` | `2fa30000` | `cmpdi cr7,r3,0` | **IDENTICAL**: Compare rc with 0 in cr7 |
| +0x70 | `0x111f28` | `409e000c` | `bne cr7,+0x0C` | `409e000c` | `bne cr7,+0x0C` | **IDENTICAL**: Branch to +0x7C if rc != 0 |
| +0x74 | `0x111f2c` | `f81e0000` | `std r0,0(r30)` | `f81e0000` | `std r0,0(r30)` | **IDENTICAL**: Store val1 to `*r30` |
| +0x78 | `0x111f30` | `f93f0000` | `std r9,0(r31)` | `f93f0000` | `std r9,0(r31)` | **IDENTICAL**: Store val2 to `*r31` |
| +0x7C | `0x111f34` | `e8010090` | `ld r0,144(r1)` | `e8010090` | `ld r0,144(r1)` | **IDENTICAL**: Restore LR from SP+0x90 |
| +0x80 | `0x111f38` | `81810088` | `lwz r12,136(r1)` | `81810088` | `lwz r12,136(r1)` | **IDENTICAL**: Restore CR from SP+0x88 |
| +0x84 | `0x111f3c` | `ebc10070` | `ld r30,112(r1)` | `ebc10070` | `ld r30,112(r1)` | **IDENTICAL**: Restore caller r30 |
| +0x88 | `0x111f40` | `7c0803a6` | `mtspr LR,r0` | `7c0803a6` | `mtspr LR,r0` | **IDENTICAL**: Restore LR |
| +0x8C | `0x111f44` | `ebe10078` | `ld r31,120(r1)` | `ebe10078` | `ld r31,120(r1)` | **IDENTICAL**: Restore caller r31 |
| +0x90 | `0x111f48` | `7d908120` | `mtocrf 8,r12` | `7d908120` | `mtocrf 8,r12` | **IDENTICAL**: Restore cr4 |
| +0x94 | `0x111f4c` | `38210080` | `addi r1,r1,128` | `38210080` | `addi r1,r1,128` | **IDENTICAL**: Pop 0x80 stack frame |
| +0x98 | `0x111f50` | `4e800020` | `blr` | `4e800020` | `blr` | **IDENTICAL**: Return to caller |
| +0x9C | `0x111f54` | `7c802378` | `or r0,r4,r4` | `7c802378` | `or r0,r4,r4` | **IDENTICAL**: r0 = returned r4 |
| +0xA0 | `0x111f58` | `7ca92b78` | `or r9,r5,r5` | `7ca92b78` | `or r9,r5,r5` | **IDENTICAL**: r9 = returned r5 |
| +0xA4 | `0x111f5c` | `4bffffc8` | `b -0x38` | `4bffffc8` | `b -0x38` | **IDENTICAL**: Branch back to +0x6C |
| +0xA8 | `0x111f60` | `38600001` | `li r3,1` | `60000000` | `ori r0,r0,0` | Replaced stock panic with nop |
| +0xAC | `0x111f64` | `4bfffb19` | `bl 0x111a7c` | `60000000` | `ori r0,r0,0` | Replaced stock panic call with nop |
| +0xB0 | `0x111f68` | `60000000` | `ori r0,r0,0` | `60000000` | `ori r0,r0,0` | **IDENTICAL**: nop |

### Summary of Differences:
- **Total instructions**: 45 (180 bytes).
- **Identical instructions**: Exactly 29 out of 45 instructions (64.4%) match the stock helper byte-for-byte.
- **The entire epilogue and return path** (`+0x58..+0xA4`, 20 instructions, 80 bytes) is **100% byte-for-byte identical to stock**, including all internal branch displacements!
- **Changed instructions (16 total)**:
  - `+0x04..+0x08`: replaced node1 lo32/hi32 extraction with nops.
  - `+0x18..+0x20`: set `r30 = 0x930F70` (`&S->raw_val1`) and `r31 = 0x930F78` (`&S->raw_val2`).
  - `+0x24..+0x28`: move `r11 = num` (r3), `r3 = a1` (r4).
  - `+0x38..+0x44`: move `r4 = a2` (r5), `r5 = a3` (r6), `r6 = a4` (r7), `r7 = a5` (r8).
  - `+0x48..+0x50`: nops replacing stock fixed-number setup (`li r11, 91`, `li r3, 1`).
  - `+0xA8..+0xAC`: nops replacing unused panic path.

---

## 3. Register Discipline & ABI Compliance

- **Condition Register (CR)**:
  - Saved in `r12` at `+0x00` (`mfcr r12`) and stored at `0x88(r1)` (`+0x2C`).
  - `cr2` and `cr3` (non-volatile in PPC64 ELF ABI) are NEVER touched by any instruction in `lv1_hcall`.
  - `cr4` (non-volatile, used by internal branch `beq cr4, +0x34`) is restored from `0x88(r1)` via `mtocrf 8, r12` (`+0x90`).
  - Full preservation of `cr2`, `cr3`, and `cr4` across the call is verified by PC emulation.
- **Link Register (LR)**:
  - Read into `r0` at `+0x30` (`mfspr r0, LR`) and stored at `0x90(r1)` (`+0x34`).
  - Restored at `+0x7C` (`ld r0, 144(r1)`) and `+0x88` (`mtspr LR, r0`).
- **Non-Volatile Registers `r30` and `r31`**:
  - Saved at `112(r1)` and `120(r1)` before modification (`+0x10`, `+0x14`).
  - Used internally as output pointers pointing to `raw_val1` (`0x930F70`) and `raw_val2` (`0x930F78`) in the mailbox.
  - Restored at `+0x84` (`ld r30, 112(r1)`) and `+0x8C` (`ld r31, 120(r1)`).
- **Registers `r14..r29`**:
  - Completely untouched by `lv1_hcall`.
- **Stack Frame**:
  - Exactly 128 bytes (`0x80`), created by `stdu r1, -128(r1)` (`f821ff81`) at `+0x0C` and popped by `addi r1, r1, 128` (`+0x94`).
  - Meets all PPC64 ELF ABI requirements.

---

## 4. Mailbox Layout (`0x930F20..0x930F80`, 96 bytes)

```c
struct ProbeState {
    u32 status;            /* 0..3: bit 0: started, bit 1: done, bit 2: raw_att, bit 3: raw_ok, bit 4: close_att, bit 5: close_ok */
    u32 total_devices;     /* 4..7: total devices discovered across all buses */
    u32 rom_count;         /* 8..11: count of type 5 (ROM) devices */
    u32 hdd_found;         /* 12..15: 1 if type 0 (DISK) device found on bus 4 port 2 */
    u32 flags;             /* 16..19: probe flags */
    u32 total_hypercalls;  /* 20..23: count of hypercalls made */
    u32 first_err_rc;      /* 24..27: return code of first failed repository call */
    u32 match_status;      /* 28..31: 0: not run, 1: MATCH, 2: DIFF (used in G0) */

    u8 rom_bus_idx;        /* 32: bus index (0..15) of first ROM device */
    u8 rom_dev_idx;        /* 33: dev index (0..15) of first ROM device */
    u8 rom_port;           /* 34: port value of first ROM device (or 0xFF) */
    u8 storage_bus_idx;    /* 35: bus index that has bus_type == 5 (or 0xFF) */

    u8 hdd_bus_idx;        /* 36: bus index where HDD control was found */
    u8 hdd_dev_idx;        /* 37: dev index */
    u8 hdd_port;           /* 38: port value */
    u8 phat_match;         /* 39: bit 0: emu (bus type 5), bit 1: gxemu (bus 4) */

    s32 stock_rc;          /* 40..43: signed 32-bit rc from stock helper for target node */
    s32 raw_rc;            /* 44..47: primary hypercall return code (G0 clone rc, G1/G3 open rc, G2 close rc) */
    s32 close_rc;          /* 48..51: secondary close hypercall return code (used in G3) */
    u32 reserved;          /* 52..55: padding / reserved */

    u64 stock_val1;        /* 56..63: val1 from stock helper (expected: 5) */
    u64 rom_bus_id;        /* 64..71: 64-bit bus_id from repository (preserves P1a offset 64) */
    u64 rom_dev_id;        /* 72..79: 64-bit dev_id from repository (preserves P1a offset 72) */

    u64 raw_val1;          /* 80..87: val1 from lv1_hcall epilogue (0x930F70) */
    u64 raw_val2;          /* 88..95: val2 from lv1_hcall epilogue (0x930F78) */
};
```

---

## 5. Built Artifacts and Hashes

All builds are located strictly in `local_only/p1g/` (gitignored, never committed to git):

| Variant | ELF Path | ELF Size | ELF SHA-256 | SELF Path | SELF Size | SELF SHA-256 | Code Slot Usage |
|---|---|---:|---|---|---:|---|---|
| **G0** | `local_only/p1g/ps2_netemu_p1g_G0.elf` | 11,294,504 B | `f911700f7953a196abe5dea2e2c2555a46ed3ccbf96d190f59b7807d4181aa90` | `local_only/p1g/ps2_netemu_p1g_G0.self` | 2,543,920 B | `9f1732bd652a0dfb86a42a74d55fb5734383400886808fbd335e5564293878ae` | 2,720 B / 14,320 (19.0%) |
| **G1** | `local_only/p1g/ps2_netemu_p1g_G1.elf` | 11,228,968 B | `a4c3adc371dfa8c0e231c8aa0f03403221ad010484ea838de3635bca2abc72f4` | `local_only/p1g/ps2_netemu_p1g_G1.self` | 2,542,160 B | `e372815f5007ed784f16f0eee2db5eb7ed65f0a9aad35033a6affeeab446037e` | 2,192 B / 14,320 (15.3%) |
| **G2** | `local_only/p1g/ps2_netemu_p1g_G2.elf` | 11,228,968 B | `4aa6465a30582b630e94e47074e39a334ecf2cfda1e9f6bcfa248d2122d783ee` | `local_only/p1g/ps2_netemu_p1g_G2.self` | 2,542,160 B | `e3c39f709a71026d54040ea7a87b3b19cfacbf55e891fb630b618db9f293629b` | 2,192 B / 14,320 (15.3%) |
| **G3** | `local_only/p1g/ps2_netemu_p1g_G3.elf` | 11,228,968 B | `f1ff8a328617f111876efcf114d2a5a97483fcdff98ce222bddf4496d2cdf30f` | `local_only/p1g/ps2_netemu_p1g_G3.self` | 2,542,976 B | `3ef11f7aad437a436081fc6abf821d2cff7c0fc50a541cfb3bd978d5f8e13dba` | 2,384 B / 14,320 (16.6%) |

- **SELF Round-Trip Integrity**: All 4 decrypted roundtrip ELFs (`local_only/p1g/roundtrip_G0.elf` .. `_G3.elf`) via `selfdec.py` match their respective patched ELFs byte-for-byte exact.

---

## 6. Strict PC Validation Results (`netemu_p1g\validate_pc.py`)

All tests executed via pyghidra `EmulatorHelper` (PPC64 BE 64-bit):

1. **Register Preservation Test**:
   - Both `Stock Helper` (0x111eb8) and `Generic Wrapper` (0x4800) tested with marker values.
   - `cr2`, `cr3`, `cr4`, `LR`, `r30`, `r31`, `r14..r29`, and stack pointer `r1` verified **100% PRESERVED** across function calls!
2. **G0 Verification**:
   - Issues exactly ONE call via generic wrapper with `(num=0x5b, a1=1, a2=0x62757304, a3=KEY_DEV(2), a4=KEY_TYPE, a5=0)`.
   - Results: `rc=0`, `raw_val1=5` (ROM).
   - Labels:
     - Page A: `P1G-G0 DONE read(4,2) rc=SUCCESS v=5(ROM)`
     - Page B: `RC=00000000 (0) SUCCESS`
     - Page C: `P1G MATCH: CLONE==STOCK (RC=0 SUCCESS, V=5 ROM)`
     - Page D: `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`
   - Verified once-only execution across repeated menu open calls.
3. **G1 Verification**:
   - Issues exactly ONE call to LV1 170 (`open_device`) with args `(bus_id=9, dev_id=0, flags=0)`.
   - Zero calls to LV1 171.
   - Labels:
     - Page A: `P1G-G1 DONE open(9,0,0) rc=INVALID_PARAMETER`
     - Page B: `RC=FFFFFFEF (-17) INVALID_PARAMETER`
     - Page C: `P1G-G1 OP:INVALID_PARAMETER CL:--`
     - Page D: `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`
   - Verified once-only execution.
4. **G2 Verification**:
   - Issues exactly ONE call to LV1 171 (`close_device`) with args `(bus_id=4, dev_id=2)`.
   - Zero calls to LV1 170.
   - Labels:
     - Page A: `P1G-G2 DONE close(4,2) rc=NOT_OWNER/WRONG_STATE`
     - Page B: `RC=FFFFFFF5 (-11) NOT_OWNER`
     - Page C: `P1G-G2 OP:-- CL:NOT_OWNER/WRONG_STATE`
     - Page D: `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`
   - Verified once-only execution.
5. **G3 Verification**:
   - Success path (`rc=0` on open): issues exactly ONE call to LV1 170 `(4, 2, 0)` followed immediately by LV1 171 `(4, 2)`.
     - Page A: `P1G-G3 DONE open(4,2,0) rc=SUCCESS`
     - Page B: `RC=00000000 (0) SUCCESS`
     - Page C: `P1G-G3 OP:SUCCESS CL:SUCCESS`
     - Page D: `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`
   - Error paths (`rc=-4`, `rc=-6`, `rc=-9`, `rc=-17`): issues exactly ONE call to LV1 170; LV1 171 close is **NEVER** called!
   - Verified once-only execution.
6. **Exhaustive Index Bounds Fuzzing**:
   - Page A G0 (96 strings): all indices in `[0, 95]`.
   - Page A G1..G3 (12 strings): all indices in `[0, 11]`.
   - Page B All Variants (529 strings): all indices in `[0, 528]`.
   - Page C G0 (230 strings): all indices in `[0, 229]`.
   - Page C G3 (144 strings): all indices in `[0, 143]`.
   - Page D All Variants (4505 strings): all indices in `[0, 4504]`.
   - Zero out-of-bounds combinations.
7. **Strict Store & SC Audit (`tools/p1a_audit.py`)**:
   - Verified for all four ELFs. Exactly ONE `sc` instruction in changed executable ranges at `0x4858` (`18520`).
   - Store base registers: strictly `r1` (stack), `r22` (mailbox pointer `0x930F20`), `r30` (`0x930F70`), `r31` (`0x930F78`).
8. **Installer Script Syntax**:
   - `tools/install_netemu.ps1` and `tools/restore_netemu.ps1` syntax checked via PowerShell AST parser: 0 errors.
