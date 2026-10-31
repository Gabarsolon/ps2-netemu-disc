# P0H: LV1 Hypervisor Analysis — PS2 LPAR Profiles and Device Open Lifecycle

**Follow-up (Official 4.93 LV1 Analysis):** See [P0I LV1 4.93 Analysis](P0I_LV1_493_ANALYSIS.md) for official 4.93 netemu profile (`PS2_NE_LPAR` / `0x8204`), `lv1_open_device` (170) fatal-path audit, `meddling` attribute resolution, and 3.55 vs 4.93 diff.

**Verdict — INFERRED (3.55 static analysis):** Official 3.55 LV1 contains **no netemu profile** in its decrypted `default.spp` policy container (14 records) nor in its embedded System Manager (`sysmgr_ss`). The legacy system manager only supports shutdown operation `0x82` with target selectors **1** (`PS2_LPAR` / `PS2_GX_LPAR`) and **2** (`PS2_SW_LPAR`); target selector **4** (`0x8204`, netemu) is unhandled in 3.55 and was introduced in later firmware. In 3.55, **`lv1_open_device` (HV call 170) is PROVEN never to panic, power off, or destroy an LPAR on a non-owned, denied, or busy device**. Every branch in the outer dispatch (`0x2fe1d8`), lower device lookup (`0x236a2c`), and storage open implementation (`0x252bac`) returns an ordinary integer error code (`-2`, `-4`, `-6`, `-9`, `-17`). Furthermore, 3.55's storage layer maintains **two concurrent opener slots** per device, so an open of an already-opened drive is not automatically fatal or an exclusive-ownership conflict. Therefore, the console shutdown observed in the P1b test on Evilnat 4.93 is most plausibly explained by either: (1) **Open succeeded, followed by a fatal guest or drive state transition** (unsolicited drive event/interrupt delivered to netemu's unconfigured IRQ vectors, or immediate close/event race), or (2) **A new fatal hypervisor policy assertion introduced in later LV1 (4.93)** specifically for the `0x8204` netemu LPAR. Static analysis of 3.55 LV1 cannot prove 4.93 or console behavior.

**PROVEN / INFERRED / CLAIMED / UNKNOWN convention:** PROVEN identifies performed byte/decoding checks or explicitly attributed owner observations; INFERRED identifies static meaning/control-flow reconstruction; CLAIMED identifies an unverified external assertion; UNKNOWN identifies unresolved behavior. A labelled paragraph or table carries its label to its contents. Static analysis does not establish successful hardware execution.

---

## 1. Extraction and Integrity Validation

**PROVEN (PC):** `CORE_OS_PACKAGE.pkg` from the official 3.55 OFW PUP (`C:\Users\remus\Downloads\3.55-OFW-PS3UPDAT.PUP`, SHA-256 `334e60a4ef5843a688c1c6aebf0951c3259429233c7a5aca5a24f0edad78a192`) was decrypted using the public SCEPKG ERK/RIV. Its file table contains 24 entries (`lv0`, `lv1ldr`, `lv2ldr`, `isoldr`, `appldr`, `lv1.self`, `lv2_kernel.self`, etc.).

**PROVEN (PC):** `lv1.self` (SELF type 2, revision 0, version `0x0003005500000000`) decrypted cleanly using the local key vault. All five section HMACs (including four load segments) were verified with full zero metadata padding. Decrypted segments exactly match the ELF program headers.

| Artifact | Location | SHA-256 | Size | Notes |
|---|---|---|---:|---|
| `lv1.elf` | `local_only/fw355/out/lv1.elf` | `3081259451b6243c8d4903fb44112d84a688586d90aef2e35847fe8ec0e12760` | 3,999,127 B | Native TOC `0x351198` |
| `lv2_kernel.elf` | `local_only/fw355/out/lv2_kernel.elf` | `ebbf6f6b0f19c8f9ee6fffa5cf0f15855f30894fe954d048ea6c757c3e5d0a61` | 4,960,656 B | Core OS kernel |
| `sysmgr_ss.elf` | `local_only/analysis/p0h/modules/sysmgr_ss.elf` | `4b2583fcba7c0a3486323508d3f6785e1274717e41a91da20b60f8b2af7adaf5` | 389,904 B | System Manager isolated module |
| `ss_server1.elf` | `local_only/analysis/p0h/modules/ss_server1.elf` | `cde8b5e94894e81238e7b78db3be181fa1e7f350c2fe9218acc604e1b9bbd847` | 370,128 B | Secure Service (0x5000 / 0x5005) |
| `ss_server2.elf` | `local_only/analysis/p0h/modules/ss_server2.elf` | `7a324eea5e641d12384bc8da1a7e3b3eb5f30a39ff63c3146d926eea517e1b8f` | 271,760 B | SPL Policy & Authority |
| `ss_server3.elf` | `local_only/analysis/p0h/modules/ss_server3.elf` | `33ef1f0c5a2cbe7d08ba5f79ea123a669bc019f2010bf1f62c0fa0f5ce252a1d` | 137,296 B | Storage & Boot Service |
| `default.spp` | `local_only/analysis/p0h/default.spp.plain` | `4fc59655b3e3e79a87e1fbf38e738034afa33136d400bda923f85273ef394aae` | 8,352 B | Decrypted SPP policy (14 records) |

---

## 2. Hypercall Table Dispatch and Architecture

**INFERRED (instructions checked):** Boot code builds the 256-entry hypercall table from 140 numbered static registration records stored between `0x3abce8` and `0x3ac598`. Each record contains hypercall number, registration structure pointer, descriptor pointer, handler address, and privilege requirement bit.

**PROVEN (PC):** Hypercall dispatch addresses verified against CobraUSB `lv1call.h` and Linux `lv1call.h`:

| Number | Registration | Descriptor | Handler | Description |
|---|---|---|---|---|
| **91** | Dynamic / tree | Dynamic | `0x2e4700` | `lv1_get_repository_node_value` |
| **162** | `0x3ac038` | `0x340de0` | `0x2eca40` | `lv1_read_virtual_uart` |
| **163** | `0x3ac048` | `0x340cf0` | `0x2eb298` | `lv1_write_virtual_uart` |
| **164** | `0x3ac058` | `0x340db0` | `0x2ec8a4` | `lv1_set_virtual_uart_param` |
| **165** | `0x3ac068` | `0x340d68` | `0x2ec20c` | `lv1_get_virtual_uart_param` |
| **166** | `0x3ac078` | `0x340cd8` | `0x2eafb4` | `lv1_configure_virtual_uart_irq` |
| **170** | `0x3ac2b8` | `0x3468b8` | `0x2fe1d8` | **`lv1_open_device`** |
| **171** | `0x3ac2c8` | `0x346a20` | `0x2ff68c` | **`lv1_close_device`** |
| **197** | `0x3ac378` | `0x346918` | `0x2fe490` | `lv1_connect_interrupt_event` |
| **245** | `0x3ac448` | `0x346d98` | `0x301328` | `lv1_storage_read` |
| **246** | `0x3ac458` | `0x346d80` | `0x3011a8` | `lv1_storage_write` |
| **248** | `0x3ac468` | `0x346e40` | `0x301c84` | `lv1_send_device_command` |
| **249** | `0x3ac478` | `0x346e28` | `0x301b4c` | `lv1_get_async_status` |

---

## 3. End-to-End Analysis of `lv1_open_device` (170) and `lv1_close_device` (171)

### 3.1 Outer Wrapper (`0x2fe1d8`)
- Parameter 1: `bus_id`, Parameter 2: `dev_id`, Parameter 3: `flags`.
- Validates `bus_id < 5`. If `bus_id >= 5`, immediately returns `-17` (`0x1ffffffef`, `LV1_NO_BUS`).
- Obtains caller LPAR ID/structure from the current thread pointer in `r13`: `*(undefined8 *)(*(long *)(r13 - 0x67e8) + 0x50)`.
- Dispatches to shared device open layer `_opd_FUN_00236a2c(caller_lpar, bus_id, dev_id, flags)`.

### 3.2 Lower Device Dispatcher (`0x236a2c`) and Lookup (`0x235a10`)
- Bus validation: checks `1 < (bus_id - 1) && bus_id != 4 && bus_id != 3`. If `bus_id == 0`, returns `-6` (`0x1fffffffa`, `LV1_NO_ENTRY`).
- Calls device lookup helper `_opd_FUN_00235a10(bus_id, dev_id)`.
- Storage Bus Lookup (`bus == 4`):
  ```c
  if (param_1 == 4) {
      if (param_2 < 7) {
          return *(long *)(param_2 * 8 + *plRam000000000034a708 + 0xee8);
      }
      if (param_2 == 0xffffffffffffffff) {
          return *plRam000000000034a708;
      }
      return 0;
  }
  ```
  If `dev_id == 2` (optical ROM node), looks up slot 2 in storage device array at offset `+0xee8`. If `dev_id >= 7`, returns `NULL`.
- If device pointer is `NULL`, returns `-6` (`0x2fffffffa`, `LV1_NO_ENTRY`).
- For storage bus 4, invokes the device's C++ virtual method at vtable offset **`+0x18`**:
  `(*(code *)**(undefined8 **)(*plVar4 + 0x18))(plVar4, caller_lpar, flags)`.

### 3.3 Storage Device Open Virtual Method (`0x252bac`)
**PROVEN (decompilation checked):** All storage device classes (HDD, BD/DVD ROM) inherit from a common base class whose vtable entry `+0x18` is `_opd_FUN_00252bac`:
1. **LPAR LAID Policy Query:** Calls `_opd_FUN_003153a0(caller_lpar, &laid)`.
   - Queries repository for `ss.laid` under caller's partition.
   - For LPAR 1 (GameOS), defaults to `0x1070000001000001` (`SCE_CELLOS_PME`).
   - If repository query fails, returns **`-4` (`LV1_DENIED_BY_POLICY`)**.
2. **Device Readiness Check:** Inspects `device_ptr[0x1a5]` (device initialized byte).
   - If device is not ready (`0`) and caller LAID is not `0x1070000001000001`, returns **`-6` (`LV1_NO_ENTRY`)**.
3. **Partition Policy Constraint:**
   - If `device_ptr[0x12]->field_0x930 == 0`, calls virtual method `+0x128` (`0x2b3a40`).
   - If return value is 0 (restricted partition access), requires caller LAID to match either `0x1070000002000001` (`PS3_LPAR` / GameOS) or `0x1070000001000001` (`SCE_CELLOS_PME`).
   - If caller LAID does not match (e.g. `0x1020000003000001` PS2 LPAR), returns **`-4` (`LV1_DENIED_BY_POLICY`)**.
4. **Two Opener Slots (Spinlock Protected at `device_ptr + 0x9e8`):**
   - **Slot 0:** LPAR ID at `+0x9f0` (`0x13e*8`), flags at `+0x9f8` (`0x13f*8`), active byte at `+0xa00` (`0x140*8`).
   - **Slot 1:** LPAR ID at `+0xa30` (`0x146*8`), flags at `+0xa38` (`0x147*8`), active byte at `+0xa40` (`0x148*8`).
   - **Allocation logic:**
     - If Slot 0 is inactive: claims Slot 0, records caller LPAR ID and flags, marks active, returns **`0` (`LV1_SUCCESS`)**.
     - Else if Slot 0 was already opened by this caller LPAR: returns **`-9` (`LV1_RESOURCE_BUSY` / `LV1_ALREADY_OPEN`)**.
     - Else (Slot 0 occupied by another LPAR, e.g. GameOS):
       - If Slot 1 is inactive: claims Slot 1, records caller LPAR ID and flags, marks active, returns **`0` (`LV1_SUCCESS`)**.
       - Else (both slots full): if caller already opened Slot 1, returns **`-9`**; else returns **`-2` (`LV1_RESOURCE_SHORTAGE`)**.

### 3.4 Complete Error Summary for HV Call 170
**PROVEN (code audit):** Every possible return value of `lv1_open_device`:
- `0` (`LV1_SUCCESS`) — device successfully claimed in Slot 0 or Slot 1.
- `-2` (`LV1_RESOURCE_SHORTAGE`) — both opener slots already occupied by other LPARs.
- `-4` (`LV1_DENIED_BY_POLICY`) — caller LAID not permitted by repository policy record.
- `-6` (`LV1_NO_ENTRY`) — bus 0, invalid `dev_id`, device not present, or device not ready.
- `-9` (`LV1_RESOURCE_BUSY`) — caller LPAR already has this device opened in Slot 0 or Slot 1.
- `-17` (`LV1_NO_BUS`) — `bus_id >= 5`.

> [!IMPORTANT]
> **Definitive Finding:** NOT ONE instruction in `0x2fe1d8`, `0x236a2c`, `0x235a10`, `0x252bac`, or `0x3153a0` invokes `panic`, `lv1_panic`, shutdown, power-off, trap, or LPAR termination. In 3.55 LV1, attempting to open a device that is non-owned, denied by policy, uninitialized, or already open returns an ordinary clean error code.

### 3.5 Close Handler (`lv1_close_device`, 171)
- Outer wrapper `0x2ff68c`: validates `bus_id < 5` (else `-17`), dispatches `_opd_FUN_0023682c`.
- Lower dispatcher `0x23682c`: looks up device via `_opd_FUN_00235a10`. If null, returns `-6`.
- Calls device virtual method at vtable offset **`+0x20`** (`_opd_FUN_00252904`).
- `_opd_FUN_00252904`: checks active opener ownership via `_opd_FUN_0025368c`. If caller is not in Slot 0 or Slot 1, returns `-11` (`LV1_NOT_OWNER`).
- If caller is an active opener, calls vtable `+0xe8` (`0x254c04`) and `+0xf0` (`0x255c9c` / `0x2557d8`).
- `0x2557d8`: clears the caller's opener slot, releases associated DMA mappings and interrupt bindings, returns **`0` (`LV1_SUCCESS`)**.

---

## 4. Partition Profile Construction and Launch Selection in System Manager

### 4.1 Absence of Netemu Profile in 3.55 Policy Container (`default.spp`)
**PROVEN (PC):** Decrypted `default.spp` contains 14 policy records. Only three PS2 emulator profiles exist:
- **`PS2_LPAR`** (record 3, offset `0x530`): LAID `0x1020000003000001`, path `/local_sys0/ps2emu/ps2_emu.self`.
- **`PS2_GX_LPAR`** (record 4, offset `0x7b8`): LAID `0x1020000003000001`, path `/local_sys0/ps2emu/ps2_gxemu.self`.
- **`PS2_SW_LPAR`** (record 5, offset `0xa40`): LAID `0x1020000003000001`, path `/local_sys0/ps2emu/ps2_softemu.self`.
- **GameOS `PS3_LPAR`** (record 2, offset `0x2a8`): LAID `0x1070000002000001`, path `/flh/os/lv2_kernel.self`.

**PROVEN:** All three legacy PS2 profiles share the exact same LPAR authority ID (`0x1020000003000001`). No `netemu` string, `ps2_netemu.self` path, or 4th PS2 profile exists anywhere in 3.55 `default.spp` or LV1 modules.

### 4.2 Shutdown Operation `0x82` and Profile Selection (`sysmgr_ss`)
**INFERRED (instructions checked):** `sysmgr_ss` decodes incoming shutdown command packets in `fn_8001b45c.c`:
- Parameter byte `param_1[1] == 0x82` selects LPAR restart mode.
- Parameter byte `param_1[2]` is the target selector:
  - **Selector `1`:** checks capability bit `0x4` (EE+GS hardware). If present, sets op `0x82`, target `1` (`PS2_LPAR` / `PS2_GX_LPAR`).
  - **Selector `2`:** checks capability bit `0x8` (software emulation). If present, sets op `0x82`, target `2` (`PS2_SW_LPAR`).
  - **Selector `> 2` (including 4):** falls through with NO ACTION (returns 0 without updating target).
- In VSH / LV2 syscall 379: the 16-bit word `0x8202` represents Operation `0x82` / Selector `0x02`.
- In CFW 4.93: `0x8204` represents Operation `0x82` / Selector `0x04`, which is new to post-3.55 firmware.

### 4.3 Hardware Compatibility Mapping (`fn_8001c1f8.c`)
During profile construction, `sysmgr_ss` matches profile records against hardware capability registers:
- `_opd_FUN_8001d9dc()` checks for full EE+GS hardware (CECHA/CECHB) -> selects `PS2_LPAR`.
- `_opd_FUN_8001da04()` checks for GS-only hardware (CECHC/CECHE) -> selects `PS2_GX_LPAR`.
- If neither is present -> falls back to `PS2_SW_LPAR` (`SCE_CELLOS_SYSTEM_MGR_PS2_SW`).

**PROVEN:** All three PS2 profiles instantiate LPAR ID 2 (`fn_8001d34c.c`: `param_1[1] = 2`) with resource grant flags `0x1226c` (compared to GameOS LPAR ID 1 with flags `0x3bf7ee`).

### 4.4 Optical Drive Lifecycle and Handover
**INFERRED (instructions checked):**
- **Drive Setup Before Launch (`fn_8001cd8c.c`):** PS2 profiles use virtual method `+0x68` (`0x8001cd8c`). This invokes `_opd_FUN_8001f48c()`, which opens `/dev/rbd0` in a retry loop (up to 60 attempts) to ensure the physical BD drive is online and ready before starting the guest LPAR. (In GameOS `PS3_LPAR`, `+0x68` is a no-op stub `0x8001cc88`).
- **Drive Reset on Teardown (`fn_8001c5b4.c`):** During partition shutdown/reset, `_opd_FUN_80025a40()` issues `reset bd drive...` and calls `_opd_FUN_800182f0(4, 2)` (Bus 4, Dev 2) to reset drive hardware state.

---

## 5. Secure Service `0x5000` / Operation `0x5005` Analysis

### 5.1 Service Registration in `ss_server1`
**PROVEN (bytes checked):** In `ss_server1` at `0x8001bb3c`:
- `li r4, 0x5005` (Operation `0x5005`)
- `li r5, 0x5000` (Service `0x5000`)
- `bl 0x8000055c` (registers service descriptor `0x80055c28`)
- Vtable `0x80055c28` contains the op handlers:
  - `+0x00`: `_opd_FUN_8001c818` (response writer: copies `0x38` bytes of auth/key data)
  - `+0x08`: `_opd_FUN_8001c290` (request reader)
  - `+0x30`: `_opd_FUN_8001c884` (buffer base query)

### 5.2 Virtual UART 10 Routing and SPL Authorization
**INFERRED:**
- Incoming requests from Virtual UART 10 are routed to `ss_server1` through internal port mapping table `port_id_table` (`_opd_FUN_80039d0c`).
- Authorization is enforced by `_opd_FUN_8000b800` in `ss_server2` (the Secure Partition Loader / Policy manager):
  ```c
  if (*caller_laid == *service_laid) {
      return 1; // Authorized
  }
  ```
  It validates the caller's LAID against the service's permitted LAID list.
- In softemu's request (docs/P0G Section 3), offset `+0x30` provides `0x1020000401000001`. The service verifies that the caller has PS2 authority (`0x1020` vendor prefix).
- In 3.55 LV1, VUART 10 is configured for PS2 LPARs during launch. In stock netemu on 4.93, only VUART 2 (`sysmgr`) is configured in the repository by default; VUART 10 is unconfigured.

---

## 6. Comparison: Legacy Profiles vs. Netemu Partition Repository

| Property | Legacy PS2 Profiles (3.55) | Netemu Partition (Evilnat 4.93 Console) |
|---|---|---|
| Launch Shutdown Op | `0x8202` (Op `0x82`, Selector `0x02`) | `0x8204` (Op `0x82`, Selector `0x04`) |
| Launch Parameter Block | `0x4f0` bytes | `0x40` bytes (Cobra `--COBRA--` block) |
| LPAR ID | `2` (`param_1[1] = 2`) | `2` (or modern dynamic guest ID) |
| SPP Policy Record | Present (`PS2_SW_LPAR`, LAID `0x1020000003000001`) | **ABSENT in 3.55**; added in post-3.56+ SPP |
| Repository Optical Node | Bus 4, Dev 2, Type 5, Port 0 | Bus 4, Dev 2, Type 5, Port 0 (PROVEN, P1a/P1b) |
| `lv1_open_device(4,2,0)` | Succeeds (claims Slot 0 or 1, returns 0) | **Powers off console** (PROVEN, P1b) |
| VUART 10 (Auth `0x5005`) | Configured and active | Not in repository by default (only VUART 2) |
| Pre-Launch Drive Setup | `/dev/rbd0` probed (up to 60 retries) | UNKNOWN (Cobra skips optical handover) |

---

## 7. Analysis of the P1b Power-Off and Ranked Hypotheses

In P1b, calling `lv1_open_device(4, 2, 0)` from the netemu partition on Evilnat 4.93 immediately powered off the console. Ablation confirmed that with the `open` call disabled, the menu hook runs normally without shutdown.

Because 3.55 LV1 **never panics on `lv1_open_device` failure** (it returns clean error codes `-2`, `-4`, `-6`, `-9`, `-17`), the power-off cannot be explained by standard 3.55 hypervisor denial logic.

### Ranked Hypotheses:

1. **Open Succeeded, Followed by Unhandled Drive Event / Interrupt in Guest (Rank 1 — Most Plausible):**
   - In 3.55 LV1, opening a storage device sets slot ownership and connects device state. If optical open succeeded in 4.93 (e.g. taking Slot 1 while GameOS had Slot 0), the drive hardware transitioned to active state and raised a status change / tray / media interrupt.
   - Netemu's exception vector `0xc00` / `0x900` or IRQ dispatch in P1b was not configured for optical IRQ plug 11. An unhandled guest interrupt or unexpected register save into unmapped/read-only memory causes an immediate hardware checkstop / power-off.
   - In P1b, `open` was immediately followed by `close` without draining status tags or acknowledging events. A race between device open state transition and guest execution could trigger the fault.

2. **4.93 LV1 Introduces Strict Sandbox Panics for Netemu LPAR (Rank 2):**
   - 3.55 had no `0x8204` netemu profile. When Sony added `ps2_netemu.self` for PS2 Classics on OFW 3.56/4.xx, they created a new restricted LPAR profile designed strictly for encrypted ISO images from HDD.
   - If modern LV1 contains an explicit security assertion that panics/terminates the partition if the netemu LPAR attempts to claim physical optical storage hardware (to prevent disc authentication bypasses), `lv1_open_device` could reach an `lv1_panic` path that does not exist in 3.55.

3. **Hypercall ABI / Register Trampoline Violation in Guest Hook (Rank 3 — Weaker):**
   - Stock netemu routes hypercalls through a dynamic bridge at `0xc50..0xca0` using `r11 = 0x80000000 | n`.
   - If the return path from hypercall 170 corrupted `r2` (TOC), `r1` (stack), or MSR state before returning to the caller, the subsequent instruction would checkstop the PPU.

---

## 8. Requirements for Analyzing OFW / Evilnat 4.93 LV1

To confirm whether 4.93 LV1 contains a panic in `open_device` or an updated `0x8204` policy record:
1. **Inputs Needed:** An official or Evilnat 4.93 PUP file (e.g. `PS3UPDAT.PUP` 4.93).
2. **Extraction Pipeline:**
   - Run `tools/pup_extract.py` to extract `update_files.tar` and decrypt `CORE_OS_PACKAGE.pkg` using public SCEPKG keys.
   - Unpack CORE_OS container to extract `lv1.self`.
3. **Decryption Requirement:**
   - 4.93 `lv1.self` uses SELF type 2, version `0x0004093000000000`.
   - The local key vault (`dl\key_vault.cpp` / `dl\keys.h`) must contain the revision key for 4.93 LV1.
   - Once present, `tools/p0h_extract.py` will decrypt `lv1.self` to `lv1_493.elf` and extract its embedded SPP and SS modules for direct side-by-side diffing against 3.55.

---

## 9. Ranked Next Experiments

1. **Read-Only P1c2 Repository Probe (Rank 1 — Lowest Risk):**
   - Run the already-built, read-only P1c2 probe (LV1 91 only) to compare all fields of the Optical node (`bus 4, dev 2`) against HDD (`bus 4, dev 3`).
   - Specifically check if Optical has an assigned interrupt plug in the repository or returns `-6 NO_ENTRY`.
   - **Worst case:** harmless freeze/reboot if display memory index is exceeded; no device state mutation.

2. **Durable Return Diagnostic Before Close (Rank 2 — Medium Risk):**
   - Modify the open test so that it attempts `lv1_open_device(4, 2, 0)` and immediately writes the returned `r3` error code to a persistent mailbox / SRAM / display buffer *without calling close* and *with interrupts masked (`MSR.EE = 0`)*.
   - This separates Hypothesis 1 (open returned cleanly, fault happened during close/IRQ) from Hypothesis 2 (open itself is fatal).
   - **Worst case:** console powers off; recovery via standard safe mode / restore script.

3. **VUART 2 vs VUART 10 Auth Inquiry (Rank 3 — Medium Risk):**
   - Send service inquiry `0x5000` / `0x5005` over VUART 2 (which netemu already has opened to sysmgr) to see if the system manager acts as a proxy, or attempt `lv1_set_virtual_uart_param` on port 10 to test port permission.
   - **Worst case:** `-6` or `-4` returned; worst case guest freeze.

4. **CFW / Cobra Stage2 Launch Profile Patch (Rank 4 — High Risk):**
   - In Cobra stage2 `storage_ext.c`, modify `shutdown_copy_params_patched` to investigate whether launching netemu with legacy profile `0x8202` (or granting the optical device in `build_netemu_params`) grants device ownership.
   - Requires CFW build/install expertise; must be fail-open.
   - **Worst case:** failed PS2 game launch, black screen requiring hard power cycle.

---

## 10. Summary of Files Produced in P0H

- `local_only/fw355/out/lv1.elf`: Decrypted 3.55 Hypervisor ELF (HMAC verified).
- `local_only/analysis/p0h/default.spp.plain`: Decrypted SPP policy records (14 entries).
- `local_only/analysis/p0h/modules/`: Extracted embedded secure modules (`sysmgr_ss.elf`, `ss_server1.elf`, `ss_server2.elf`, `ss_server3.elf`, `ss_init.elf`).
- `local_only/analysis/p0h/hvcall_registrations.json`: 140 hypercall registration records.
- `local_only/analysis/p0h/lv1/`: Decompiled C and ASM listings for `lv1_open_device` (`0x2fe1d8`, `0x236a2c`, `0x252bac`), `lv1_close_device` (`0x2ff68c`, `0x23682c`, `0x252904`), and VUART handlers.
- `local_only/analysis/p0h/sysmgr_ss/`: Decompiled C and ASM listings for LPAR profile construction and BD drive setup/reset routines.
- `local_only/analysis/p0h/ss_server1/` & `ss_server2/`: Decompiled C and ASM listings for Service `0x5000` / Op `0x5005` registration and SPL LAID authorization.
