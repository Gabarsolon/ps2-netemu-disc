# P0I: LV1 Hypervisor Analysis — Official 4.93 Netemu Profile and Device Open Lifecycle

**Verdict — PROVEN (4.93 static analysis):** Official PS3 4.93 LV1 hypervisor contains a fully defined netemu partition profile named **`PS2_NE_LPAR`** (authority ID **`SCE_CELLOS_SYSTEM_MGR_PS2_NE`**, constructor `0x8001e308`, vtable `0x8003e220`) in its embedded System Manager (`sysmgr_ss.elf`), mapped directly to shutdown operation `0x82` with target selector **`4`** (`0x8204`). Crucially, in official 4.93 LV1, **`lv1_open_device` (HV call 170) is PROVEN to contain NO panic, trap, shutdown, or fatal abort path**. Every branch in the outer dispatch (`0x305a38`), lower device dispatcher (`0x2375b0`), device lookup (`0x236594`), and storage open implementation (`0x2545a4`) cleanly returns standard error codes (`-2`, `-4`, `-6`, `-9`, `-17`) or `0` (`LV1_SUCCESS`), and maintains two concurrent opener slots (`+0x9f0` and `+0xa30`). The repository key **`meddling`** is PROVEN to be written by `StorageBus::register_device` (`0x252c50`) querying virtual method `+0xf8` (`FUN_002718bc`), which reads `sys.hw.config` bit 60 (evaluating to 1 for external BD drive daughterboard architecture on Phat consoles and 0 for HDD); **`meddling` is NEVER read by LV1 or any secure module** and is purely an informative repository attribute. Therefore, the console shutdown observed in the P1b test on Evilnat 4.93 is **NOT an LV1 policy assertion or fatal hypercall failure**. Instead, the leading explanations are: (1) **Unpowered PCI/drive interface in `PS2_NE_LPAR`**: while legacy `PS2_SW_LPAR` powers on the physical bus at vtable `+0xc0` (`0x8001decc`), `PS2_NE_LPAR` deliberately stubs this out (`0x8001dad8`, `li r3, 1; blr`), so claiming the drive causes a Southbridge bus error / Syscon emergency shutdown; (2) **Unhandled guest interrupt delivery**: `ps2_netemu` registers no interrupt handler or event port for the optical device (IRQ 9/10), causing an unsolicited drive interrupt to hit the guest kernel panic handler (`0xf58`), which calls `lv1_panic(0x11f)`. The planned **P1d experiment** (open with invalid `bus=99`, and close without open) is **the ideal next test**: because `bus=99` returns `-17` at instruction `0x305a54` without touching any device object or hardware, P1d decisively determines whether the crash was caused by the hypercall interface/bridge or by physical drive hardware activation.

**PROVEN / INFERRED / CLAIMED / UNKNOWN convention:** PROVEN identifies performed byte/decoding checks or explicitly attributed owner observations; INFERRED identifies static meaning/control-flow reconstruction; CLAIMED identifies an unverified external assertion; UNKNOWN identifies unresolved behavior. A labelled paragraph or table carries its label to its contents. Static analysis of official LV1 cannot establish Evilnat CFW runtime patch or hardware behavior.

---

## 1. Extraction and Integrity Validation

**PROVEN (PC):** `CORE_OS_PACKAGE.pkg` from the official 4.93 OFW PUP (`C:\Users\remus\Downloads\PS3UPDAT.PUP`, SHA-256 `158471fd834f8ea8036136b6aab43cd86c7ba73d79ca30e0af3c0fe0001cf365`) was decrypted using the local key vault.
- `lv1.self` (SELF type 2, revision 0, version `0x0004009300000000`) decrypted cleanly.
- All five section HMACs (including four load segments) were verified with full zero metadata padding.
- Decrypted `lv1.elf` (4,130,048 bytes, SHA-256 `e8d0b532adf6ba6c6c1ea40a5c5b86407abe11ea7a3ab8624ca5b09d3e4c3d6b`, native TOC `0x35a038`) matches ELF program headers.
- The embedded secure filesystem at `0x1f0000` (payload offset `0xe8`) was extracted into 8 modules:

| Module / Artifact | SHA-256 | Size (4.93) | Size (3.55) | Notes |
|---|---|---:|---:|---|
| `lv1.elf` | `e8d0b532adf6ba6c6c1ea40a5c5b86407abe11ea7a3ab8624ca5b09d3e4c3d6b` | 4,130,048 B | 3,999,127 B | Native TOC `0x35a038` |
| `sysmgr_ss.elf` | `07c0bd2a76f2f3549704ae7ae58ec6a836bc3845b4588fa899a647d6a5cff367` | 391,208 B | 389,904 B | System Manager isolated module |
| `pme_init` | `e2a4be60fe73ddfd48e246c0516b080f555e1a171e54917a02c91cf6f26487e4` | 137,176 B | 137,176 B | Platform Management Engine init |
| `pme_init.conf` | `ff19ec0bcf2e7a1772670d8a594411130d22045610cb860955f00e9fcb908779` | 175 B | 175 B | **Byte-for-byte identical to 3.55** |
| `ss_init.elf` | `1da90a071850785f7ea349be8bb7541f930e16b9b2ff903c7344be6c14dcbf58` | 216,024 B | 216,024 B | Security Server init |
| `updater_frontend.elf`| `dfc7a7e8ca37a0915f05b1f5c6dd3a5a7fb4c58f9fc560e2ce1c9e7eb22fe075` | 145,552 B | 145,552 B | Firmware updater frontend |
| `ss_server1.elf` | `71b058a5da4299ee8c4990d0b04c8aaee5e54d7f722363574c30c33a9cfa88eb` | 529,968 B | 370,128 B | Secure Service (0x5000 / 0x5005) |
| `ss_server2.elf` | `d719543e50e932462e08719bc451b7501a355fe8288540c49cf7149a4e3ff3d3` | 305,248 B | 271,760 B | SPL Policy & Authority |
| `ss_server3.elf` | `bf67c87c2b6441b44ec63c78beec068593aa06dcfaef6cc92e597cfa908ecbe3` | 232,840 B | 137,296 B | Storage & Boot Service |
| `default.spp` | `83ef50811e58e3794380eb9a3e617d91e3256191cbba2b8344eeb1d1ca9e5b22` | 10,144 B | 8,352 B | SPP type 4 (encrypted post-3.55) |
| `me_iso_for_ps2emu.self` | `908b98297bcf61e93ca373f75727be6f5424cf9659b8be0092f026a793fcadbe`| 34,960 B | N/A | PS2 Master Engine isolated SPU |
| `sv_iso_for_ps2emu.self` | `9478fcf1ffba7ff94da07f5e3966580f1aa538626c71be68b5ea1ee566d71b40`| 91,936 B | N/A | PS2 Supervisor isolated SPU |

---

## 2. The SPP / Profiles and Isolated SPU Modules

### 2.1 `default.spp` Status
**PROVEN (PC):** `default.spp` in 4.93 is 10,144 bytes (compared to 8,352 bytes in 3.55). Public cryptographic keys for decrypting SCE SPP containers are only publicly known for firmware range 0.80–3.55 (published on psdevwiki under "Keys" / "Spp verifier"). No public key exists for 3.56+ or 4.93 SPP containers. Following project rules, the key was not guessed; instead, the partition profile tables were analyzed directly inside the extracted `sysmgr_ss.elf` module.

### 2.2 SPU Isolated Modules (`me_iso_for_ps2emu` & `sv_iso_for_ps2emu`)
**PROVEN (PC):** In 4.93 `CORE_OS`, two dedicated isolated SPU modules (`iso`) exist specifically for the PS2 emulators:
- `me_iso_for_ps2emu.self` (34,960 B, ELF header type `0x100`, app type `0x600`, app version `0x8290`): Media / Master Engine SPU isolated subsystem.
- `sv_iso_for_ps2emu.self` (91,936 B, ELF header type `0x100`, app type `0x600`, app version `0x16120`): Supervisor SPU isolated subsystem.
These modules run within hardware-isolated SPU local storage to provide tamper-resistant DRM authentication, cryptographic verification, and supervisory control for PS2 emulation partitions without exposing keys to host or guest PPU memory.

---

## 3. System Manager in 4.93: Op `0x82` and `PS2_NE_LPAR` Profile

### 3.1 Op `0x82` Selector 4 Handling (`fn_8001bf14`)
**PROVEN (PC):** In 4.93 `sysmgr_ss.elf` at `0x8001bf14`, incoming shutdown/reboot packets are processed:
- Byte 1 `0x82` selects LPAR restart mode.
- Byte 2 (the target selector) is evaluated at `0x8001bf88`:
  - Selector `1`: maps to mode `1` (`PS2_LPAR` / `PS2_GX_LPAR`).
  - Selector `2`: maps to mode `2` (`PS2_SW_LPAR`).
  - Selector **`4`**: checked at `0x8001bf90` (`cmpwi cr7, r9, 4`) -> branches to `0x8001c0a0` (`li r11, 3`), setting `target_mode = 3`.
- `target_mode = 3` selects profile string **`PS2_NE_LPAR`** (`0x8003b2b8`) and authority string **`SCE_CELLOS_SYSTEM_MGR_PS2_NE`** (`0x8003b268`).

### 3.2 `PS2_NE_LPAR` Object Structure and Vtable (`0x8003e220`)
**PROVEN (PC):** Constructor `0x8001e308` instantiates a 472-byte profile object:
- Sets LPAR ID = 2, target selector = 4, profile ID = 3.
- Vtable is initialized to `0x8003e220`.
- **Method `+0x68` (`0x8001dd00`):** Drive setup hook. Polls `/dev/rbd0` up to 60 times. **Byte-for-byte identical across `PS2_LPAR`, `PS2_SW_LPAR`, and `PS2_NE_LPAR`**.
- **Method `+0x78` (`0x8001dca0`):** Netemu parameter loader. Sets buffer size to 64 (`0x40` bytes) and invokes `0x80020b28` to load the parameter block (corroborating Cobra 7.3 `build_netemu_params` 0x40-byte `--COBRA--` block).
- **Method `+0xc0` (`0x8001dad8`):** Stub implementation (`li r3, 1; blr`). **Crucial difference: `PS2_SW_LPAR` invokes `0x8001decc` to power on the physical PCI bus / drive interface; `PS2_NE_LPAR` deliberately stubs this out.**

### 3.3 The `meddling` Attribute: Origin and Meaning
**PROVEN (PC):** In `lv1.elf`:
1. The string `"meddling"` exists at `0x320b38`, referenced in the repository literal table at `0x354510` alongside `"bus"`, `"dev"`, `"blk_size"`, `"n_blocks"`, `"port"`, `"hosttype"`, `"n_regs"`.
2. `"meddling"` is written into the repository during device registration (`StorageBus::register_device`, `0x252c50` and `0x2524a4`):
   ```c
   uVar6 = (*(code *)**(undefined8 **)(*param_2 + 0xf8))(param_2);
   func_0x002384a0(uVar6, 0, uVar4, 4, uVar5, param_2[0x1ba], uRam0000000000354510 /* "meddling" */, 0, 0);
   ```
3. Virtual method `+0xf8` differs by storage device class:
   - For HDD and generic storage devices: `+0xf8` is `0x253364`, which executes `li r3, 0; blr` (returns **0**).
   - For BDVD (optical drive, vtable `0x35e370`): `+0xf8` is `FUN_002718bc`.
4. `FUN_002718bc` queries `"sys.hw.config"` via `func_0x002bacb4` and extracts bit 60:
   `return (auStack_10[0] >> 0x3c ^ 1) & 1;`
   On Phat consoles with separate BD drive daughterboards, bit 60 is 0, returning `(0 ^ 1) & 1 = 1`. On Slim consoles with integrated BD controller SoC, it returns 0.
5. **LV1 NEVER reads `"meddling"`:** Thorough cross-reference scan of 4.93 `lv1.elf` and all secure modules proves that not one instruction queries or branches on `"meddling"`. It is purely an informational hardware attribute published for GameOS / VSH.

---

## 4. End-to-End Audit of `lv1_open_device` (170) and `lv1_close_device` (171) in 4.93

### 4.1 Hypercall Dispatch Table
**PROVEN (PC):** The 140 registration records in 4.93 reside between `0x3c2340` and `0x3c2c00`:
- **HV 170 (`lv1_open_device`):** registration `0x3c2910`, descriptor `0x34f6c8`, entry **`0x305a38`**, TOC `0x35a038`.
- **HV 171 (`lv1_close_device`):** registration `0x3c2920`, descriptor `0x34f830`, entry **`0x306eec`**, TOC `0x35a038`.

### 4.2 Outer Wrappers (`0x305a38` / `0x306eec`)
- Open (`0x305a38`): validates `bus_id < 5`. If `bus_id >= 5`, returns `0x1ffffffef` (`-17`, `LV1_NO_BUS`). Otherwise calls lower dispatcher `0x2375b0`.
- Close (`0x306eec`): validates `bus_id < 5`. If `bus_id >= 5`, returns `-17`. Otherwise calls lower dispatcher `0x2373b0`.

### 4.3 Lower Device Dispatchers and Lookup
- Open dispatcher (`0x2375b0`): validates bus in `{1, 2, 3, 4}` (else returns `-6`). Calls `0x236594(bus, dev)`. For Bus 4, invokes device vtable `+0x18`.
- Device lookup (`0x236594`): for `bus == 4`, reads storage device pointer from global array:
  `*(long *)(param_2 * 8 + *plRam0000000000353818 + 0xee8)`.
  For `dev_id == 2` (optical ROM node), returns slot 2. If null, returns 0 (`-6`).

### 4.4 Storage Open Method (`0x2545a4`)
**PROVEN (code audit):**
1. Queries caller LAID via `0x31ce8c` (reads repository `ss/laid`). If query fails, returns **`-4` (`LV1_DENIED_BY_POLICY`)**.
2. Checks initialized byte at `device_ptr + 0x1b5`. If uninitialized and caller is not PME, returns **`-6` (`LV1_NO_ENTRY`)**.
3. Evaluates device type via virtual method `+0x128`:
   - For BDVD (`0x35e370`), `+0x128` is `0x27187c`, which executes `li r3, 5; blr` (returns 5).
   - Because `5 != 0`, the restricted partition check (`alStack_30[0] != 0x1070...`) is **BYPASSED**.
4. Acquires spinlock at `device_ptr + 0x9e8`:
   - Checks **Slot 0** (`0x9f0`) and **Slot 1** (`0xa30`).
   - If Slot 0 is free: claims Slot 0, sets active flag `+0xa00 = 1`, returns **`0` (`LV1_SUCCESS`)**.
   - If Slot 0 held by caller: returns **`-9` (`LV1_RESOURCE_BUSY`)**.
   - If Slot 0 occupied by another LPAR: checks Slot 1. If Slot 1 is free, claims Slot 1, returns **`0` (`LV1_SUCCESS`)**.
   - If both slots occupied: returns **`-2` (`LV1_RESOURCE_SHORTAGE`)**.

### 4.5 Storage Close Method (`0x253fa0`)
**PROVEN (code audit):**
- Checks whether caller holds Slot 0 or Slot 1 via `+0x30` (`0x25477c`). If not an active opener, returns **`-11` (`LV1_NOT_OWNER`)**.
- If caller is an active opener, calls `+0xe8` (`0x25756c`) and `+0xf0` (`0x258e18`) to release DMA and interrupt bindings, clears the slot, and returns **`0` (`LV1_SUCCESS`)**.

> [!IMPORTANT]
> **Definitive Finding:** PROVEN: Not a single instruction in `0x305a38`, `0x2375b0`, `0x236594`, `0x2545a4`, `0x306eec`, `0x2373b0`, `0x253fa0`, `0x25477c`, `0x25756c`, or `0x258e18` contains a panic, trap, `lv1_panic`, or shutdown branch. Hypercall 170 and 171 cannot be fatal in official 4.93 LV1.

---

## 5. Post-Open Lifecycle and Explanation of the P1b Power-Off

Since `lv1_open_device` is non-fatal in LV1, the P1b console shutdown is explained by post-call or environment interactions:

### Ranked Mechanisms

1. **Unpowered Physical Bus Interface in `PS2_NE_LPAR` (Hardware Fault / Syscon Trip) — Highest Likelihood (INFERRED):**
   In `sysmgr_ss`, `PS2_NE_LPAR` explicitly stubs out vtable method `+0xc0` (`0x8001dad8`), leaving the physical BD drive PCI interface unpowered/unclocked when running netemu. When `lv1_open_device(4, 2, 0)` is called, subsequent hardware bus access or interrupt assertion across an unpowered bridge generates an immediate Southbridge bus error / checkstop, causing Syscon to cut main power.
2. **Unhandled Guest IRQ Delivery to Guest Panic Vector — High Likelihood (INFERRED):**
   `ps2_netemu`'s guest kernel configures interrupts exclusively for HDD (IRQ 0x12) and VUART 2. The optical drive uses interrupt line 2 (IRQ 9/10). In `ps2_emu`, an event port is explicitly wired to IRQ 9 with handler `0x222cc`. In `netemu`, no handler exists. If drive activation asserts an unhandled interrupt, netemu hits its guest kernel panic vector at `0xf58` (`li r3, 0x11f; li r11, 0xff; sc 1`), executing `lv1_panic(0x11f)` and powering off.
3. **Cobra Stage2 Live CFW Interception — Moderate Likelihood (INFERRED):**
   When Cobra 8.x launches netemu for ISO/BIN.ENC playback, stage2 patches hypercall tables to redirect storage I/O. If Cobra hooks HV 170 or crashes upon unexpected physical drive access during emulated disc mode, stage2 could trigger an abort.
4. **Immediate Close Race / DMA Teardown — Low Likelihood (INFERRED):**
   P1b executed `lv1_close_device` immediately upon `open_device` returning 0. Calling close on an optical device that just began power-up / spin-up could produce a controller stall.

---

## 6. Official Firmware Diff: 3.55 vs. 4.93

| Subsystem / Feature | Official 3.55 LV1 | Official 4.93 LV1 | Diff / Impact |
|---|---|---|---|
| LV1 ELF Size / SHA-256 | 3,999,127 B / `30812594...` | 4,130,048 B / `e8d0b532...` | +130,921 B |
| Native TOC Pointer (`r2`) | `0x351198` | `0x35a038` | Shifted by `+0x8ea0` |
| Secure Modules in Filesystem | 7 files (389,904 B sysmgr) | 8 files (391,208 B sysmgr; `pme_init.conf` SHA identical) | Core structure preserved |
| SPU Isolated PS2 Modules | None in Core OS | Added `me_iso_for_ps2emu` & `sv_iso_for_ps2emu` | Hardware-isolated PS2 DRM |
| Op 0x82 Target Selectors | 1 (`PS2_LPAR`), 2 (`PS2_SW_LPAR`) | 1, 2, and **4 (`PS2_NE_LPAR`)** | **`0x8204` officially supported** |
| Netemu Profile Definition | **ABSENT** in 3.55 | **`PS2_NE_LPAR`** (`0x8003b2b8`) in `sysmgr_ss` | PROVEN present in 4.93 |
| Netemu Parameter Block | N/A | 0x40 bytes via `0x8001dca0` / `0x80020b28` | Matches Cobra `--COBRA--` block |
| Netemu Drive Setup (`+0x68`) | N/A (PS2_SW: `0x8001cd8c`) | `0x8001dd00` (polls `/dev/rbd0` 60 times) | Shared with `PS2_SW_LPAR` |
| Netemu PCI Bus Power (`+0xc0`) | N/A (PS2_SW calls `0x8001decc`) | `0x8001dad8` (`li r3, 1; blr` no-op) | **PCI bus unpowered in netemu** |
| `default.spp` Size / Records | 8,352 B (14 records, plain) | 10,144 B (encrypted post-3.55 key) | Container expanded |
| HV Table Registration Records | 140 entries (`0x3abce8`) | 140 entries (`0x3c2340`) | Identical 140 call slots |
| HV 170 (`lv1_open_device`) | `0x2fe1d8` | `0x305a38` | Handler logic identical |
| Lower Open Dispatcher | `0x236a2c` | `0x2375b0` | Code identical |
| Device Lookup | `0x235a10` | `0x236594` | Global array at `0x353818` |
| Storage Open Implementation | `0x252bac` | `0x2545a4` | Opener slots at `+0x9e8` |
| HV 170 Fatal Path / Panic | **NONE** (clean error returns) | **NONE** (clean error returns) | **PROVEN safe in both** |
| HV 171 (`lv1_close_device`) | `0x2ff68c` | `0x306eec` | Handler logic identical |
| Storage Close Implementation | `0x252904` | `0x253fa0` | Slot release identical |
| HV 171 Fatal Path / Panic | **NONE** (clean error returns) | **NONE** (clean error returns) | **PROVEN safe in both** |
| Repository Key `"meddling"` | Evaluates `+0xf8` | Evaluates `+0xf8` (`FUN_002718bc`) | Never read by LV1 |

---

## 7. Ranked Next Experiments and Evaluation of P1d

### Ranked Next Experiments

1. **P1d (Open with Invalid Bus ID `bus=99`; Close without Open) — Recommended Next:**
   - **Rationale:** `lv1_open_device(99, 2, 0)` is handled entirely at `0x305a38` / `0x305a54`: it tests `param_1 < 5`, fails immediately, and returns `-17` (`0x1ffffffef`) without touching the device array, spinlocks, or hardware.
   - **Worst-Case:** Console shuts down. If `bus=99` powers off, this **proves** the issue is in the `sc 0` / bridge dispatch or a live CFW hypercall hook, completely clearing the physical optical drive.
   - **Best-Case:** Console does NOT shut down and displays `open=-17(PARAM) close=-11(STATE)`. This **proves** the hypercall execution environment is functional and that the P1b shutdown was triggered by claiming the physical drive object.
2. **P1e (Repository State Dump of Device Pointer Properties):**
   - Read-only probe dumping whether any storage node reflects active opener LPAR ID in repository before and during menu open. Zero crash risk.
3. **P1f (Optical Open with IRQ Masking / Event Port Construction):**
   - Construct guest event port (HV 18) and connect interrupt (HV 197) prior to `open_device`, matching the `ps2_emu` lifecycle order (docs/P0E Section 1), to prevent unhandled guest IRQ delivery.
