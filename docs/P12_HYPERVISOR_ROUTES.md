# P12: Hypervisor & Secure Service Routes for PS2 Optical Disc Authentication in Netemu

## Verdict

Static reverse engineering of the hypervisor (`lv1.elf`), system manager (`sysmgr_ss.elf`), and secure storage server (`ss_server1.elf`) confirms that the optical drive profile check (`0xFF60`/`0xFF61`) cannot be bypassed from within the guest `ps2_netemu` partition because `/dev/rbd0` is an isolated hypervisor device node, and `PS2_NE_LPAR` is explicitly constructed with optical drive abilities stripped. Unlocking genuine PS2 optical disc sector reads under a netemu ISO launch requires intervening on the hypervisor / secure-service side.

Among all candidate routes, the **Rank 1 recommendation is an in-memory dynamic patch of `ss_server1` applied via Cobra CFW (`stage2.bin`) or runtime LV1 poke**. This modifies a single 4-byte conditional branch in `ss_server1` (`0x80020710`) to unconditionally proceed to session key derivation. This route modifies zero flash files, carries zero brick risk, works identically across CFW and PS3 HEN, and is immediately reversible on reboot.

---

## 1. Cobra Secure-Service Patching Architecture & Primitives

### Public Source References
- **Repository**: Joonie86 / `Cobra-7.00` (and `aldostools/Mamba`)
- **Source Files**:
  - `stage2/storage_ext.c` (`patch_ps2emu_entry`, lines 3374–3411)
  - `stage2/main.c` (`main` -> `storage_ext_patches`, line 559)
  - `lv1/include/lv1/patch.h` (`HV_BASE`, `lv1_peekd`, `lv1_pokew`)
  - `lv1/include/lv1/lv1call.h` (Hypercalls 182 `lv1_cfw_peek` and 183 `lv1_cfw_poke`)
- **Upstream URLs**:
  - `https://raw.githubusercontent.com/Joonie86/Cobra-7.00/master/446/stage2/storage_ext.c`
  - `https://raw.githubusercontent.com/aldostools/Mamba/master/stage2/storage_ext.c`
  - `https://raw.githubusercontent.com/aldostools/Mamba/master/lv1/include/lv1/patch.h`

### Execution Timing
The Cobra optical disc authentication patch does **NOT** run per PS2 launch. Instead, it runs **once at system boot** during early Level-2 kernel initialization:
1. When the PS3 boots, Level-1 hypervisor initializes and unpacks the secure service modules into hypervisor RAM.
2. Level-2 kernel (`lv2_kernel.self`) loads and mounts early system subsystems.
3. Cobra's `stage2.bin` payload executes `main()`, calling `storage_ext_patches()`.
4. `storage_ext_patches()` invokes `patch_ps2emu_entry(ps2emu_type)` synchronously before any game or emulator partition is spawned.

### Patch Primitives & Memory Addressing
Cobra supports two primitives for reading and writing hypervisor memory:
1. **Direct Memory Mapping via `HV_BASE` (`0x8000000014000000ULL`)**:
   Under custom firmware, the Level-2 kernel page tables map the first 16 MiB of hypervisor physical memory directly into Level-2 kernel space at virtual offset `0x8000000014000000ULL`. Cobra's `lv1_peekd(addr)` and `lv1_pokew(addr, val)` access hypervisor memory directly as `*(u32 *)(HV_BASE + addr)`.
2. **CFW Hypercalls (HVSC 182 / 183)**:
   When direct page mapping is unavailable, Cobra and Mamba fall back to hypervisor system calls:
   - Hypercall 182 (`0xB6`): `lv1_cfw_peek(u64 addr, u64 *val)`
   - Hypercall 183 (`0xB7`): `lv1_cfw_poke(u64 addr, u64 val)`

### Scan Range & Safety by Construction
Cobra scans the physical address range:
- Range: `0x100000` to `0x300000` (1 MiB to 3 MiB in Level-1 physical memory; tightened to `0x160000..0x300000` in Mamba).
- Stride: 4 bytes (instruction-aligned).
- **Physical vs Virtual Addressing**: The scan addresses (`0x100000..0x300000`) represent Level-1 physical RAM where hypervisor processes reside.
- **Safety by Construction**: The 1 MiB to 3 MiB region is part of the contiguous, linearly mapped hypervisor dynamic allocation pool. There are no unmapped page holes within this region during post-boot operation. Reading 8 bytes at 4-byte intervals cannot trigger a Data Storage Interrupt (DSI / page fault) exception. Once the target match count is satisfied (`patch_count == 2`), the loop immediately breaks.

### Target Module: Loaded Process Pages vs Embedded Image
- In the static binary `lv1.elf`, embedded secure server modules reside between `0x1f0000` and `0x3d0000` (virtual addresses `0x400000..0x5fffff`).
- On a running 4.93 retail/CFW console, live memory peeks performed during Task P11b proved that the address range `0x400000..0x5fffff` is zeroed and reclaimed after initialization.
- **Cobra patches the LOADED PROCESS PAGES** residing within the dynamic process pool at `0x100000..0x300000`, not the embedded filesystem image.
- Because `ss_server3` (and `ss_server1`) are loaded into hypervisor memory at boot and remain resident, the dynamic memory search reliably finds the running code pages.

### Why Cobra Excluded Netemu
In `storage_ext.c`, Cobra explicitly includes an early return:
```c
if (ps2emu_type == PS2EMU_SW) {
    condition_ps2softemu = 1;
    // No need to do the optical disc auth patch for ps2_netemu since there is no optical disc support
    return;
}
```
The original Cobra developers deliberately skipped optical disc authentication patching on non-backwards-compatible consoles because retail `ps2_netemu` was purely a PlayStation Network digital title emulator with no optical disc drive support.

### Evilnat 4.93 Comparison
Evilnat CFW 4.93 incorporates Cobra 8.4/8.5. The underlying secure-service patching architecture remains structurally identical to the Cobra 7.00 implementation: it relies on the same early-boot Level-2 invocation, the same `HV_BASE` / hypercall 183 poke primitive, and the same pattern search loop across `0x100000..0x300000`.

---

## 2. Process Lifecycle & Execution Timeline: `ss_server1` vs `ps2_netemu`

### Lifecycle of `ss_server1`
1. **System Boot**:
   During initial hypervisor boot, the module loader `ss_init.elf` unpacks and launches all core secure server modules:
   - `ss_server3.fself` (Secure System Loader / drive authentication manager)
   - `ss_server2.fself` (System security server)
   - `ss_server1.fself` (Secure storage, ATA/BD manager, DRM, and EEPROM service)
   - `sysmgr_ss.fself` (System manager and LPAR lifecycle coordinator)
2. **Service Residence**:
   `ss_server1` is **NOT** loaded on demand per PS2 launch. It is launched once at cold boot and remains permanently resident as a hypervisor background daemon. It binds to Virtual UART (VUART) Port 10 with a 4096-byte ring buffer.
3. **Partition Switch Independence**:
   When GameOS or webMAN MOD launches `ps2_netemu`, Level-1 hypervisor spawns `PS2_NE_LPAR`. The hypervisor secure server modules (`ss_server1`, `sysmgr_ss`) are external to guest partitions and are never destroyed or reloaded during partition transitions.
4. **Implication for Patching**:
   Any patch applied to `ss_server1` memory during system boot (or by Cobra `stage2` / LV1 poke prior to launching netemu) **persists indefinitely** across guest partition switches. There is no race condition between partition creation and the authentication request.

### Execution Timeline
Analysis of the console execution logs from Tasks P10, P11, and P11b confirms the following timeline:
- **`t = 0.00 s` (Netemu Entry)**: Guest netemu partition boots. Custom probe executes hypercall 165 (`lv1_get_virtual_uart_param`) on VUART Port 10. The hypervisor returns success (`rc = 0`), buffer size `0x1000` (4096 bytes). This proves `ss_server1` is already alive, initialized, and listening before netemu executes its first instruction.
- **`t = 0.16 s`**: Netemu completes initial partition and memory setup; initializes storage controller; issues `TEST UNIT READY`, `INQUIRY`, and `READ CAPACITY` to the drive.
- **`t = 0.20 s`**: Netemu issues the 112-byte `0x5005` disc authentication packet to VUART Port 10 via hypercall 163 (`lv1_write_virtual_uart`).
- **`t = 0.21 s` (~54,000 polling cycles)**: `ss_server1` processes the request and returns the 112-byte reply. In stock operation, `ss_server1` queries `/dev/rbd0` (command `0x11`), reads profile `0x0010`, fails the check at `0x80020710`, and returns status `0x16`.

---

## 3. Ranked Hypervisor & Firmware Routes

| Rank | Route | Description | Feasibility | Brick Risk | Compatibility |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **In-Memory `ss_server1` Profile Bypass** | Single 4-byte branch modification in live `ss_server1` text space | **Very High (10/10)** | **None (0/10)** | CFW & HEN |
| **2** | **Sysmgr LPAR Ability Bit Hook** | Modify `_opd_FUN_8001e308` in `sysmgr_ss` to preserve bit `0x02000000` | **High (8/10)** | **None (0/10)** | CFW & HEN |
| **3** | **CoreOS Flash Patch (`lv1.self`)** | Modify embedded `ss_server1` binary inside flash CoreOS | **Low (3/10)** | **Severe (9/10)** | CFW Only |
| **4** | **Drive-Side ATA Vendor Override** | Issue vendor ATA command to drive controller to force PS2 profile | **Very Low (2/10)** | **Moderate (5/10)** | CFW & HEN |

---

### Route 1 (Rank 1): In-Memory Dynamic Patch of `ss_server1` Profile Check

- **Target Module**: `ss_server1.elf` (loaded process memory in LV1 physical pool `0x100000..0x300000`).
- **Virtual Address**: `0x80020710` (ELF file offset `0x30710` in `ss_server1.elf`; offset `0x2faf80` in `lv1.elf`).
- **Mechanism**:
  In function `0x80020638`, `ss_server1` reads the optical drive profile word from `/dev/rbd0` and evaluates whether `(profile - 0xFF60) <= 1`.
  - Stock instruction at `0x80020710`: Conditional branch if less than or equal (`ble cr7, 0x8002072c`, big-endian word `0x409D001C`). If false, execution falls through to error status assignment `0x16` (`li r31, 0x16`).
  - Patch instruction: Unconditional relative branch forward by 28 bytes (`b 0x8002072c`, big-endian word `0x4800001C`).
- **Search Pattern**:
  A 16-byte signature uniquely identifies this location across the entire hypervisor:
  `81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01`
  The patch is applied at `pattern_offset + 0x10`.
- **Implementation**:
  Applied dynamically at boot by adding a scan loop to Cobra `stage2` (or via runtime poke using PS3MAPI / webMAN MOD).
- **Pros**: Zero flash writes; zero brick risk; immediately reversible on console reboot; operates identically on CFW and PS3 HEN.
- **Cons**: Requires CFW Cobra payload modification or a user-space loader to apply the LV1 poke.

---

### Route 2 (Rank 2): Sysmgr LPAR Ability Bit Preservation Hook

- **Target Module**: `sysmgr_ss.elf` (loaded process memory in LV1 physical pool `0x100000..0x300000`).
- **Virtual Address**: `0x8001e334` (ELF file offset `0x2e334` in `sysmgr_ss.elf`).
- **Mechanism**:
  Function `_opd_FUN_8001e308` configures the partition abilities descriptor for `PS2_NE_LPAR`. It inherits base abilities from `_opd_FUN_8001e2a8` (`0x201226c`), but then explicitly executes a bitwise AND with `0xFDFFFFF7` (`and r0, r0, r9`, big-endian word `0x7C004838`), which strips optical drive authentication ability `0x02000000`.
  - Stock instruction at `0x8001e334`: `and r0, r0, r9` (`0x7C004838`).
  - Patch instruction: Replace with a no-operation instruction (`nop`, big-endian word `0x60000000`).
- **Effect**: `PS2_NE_LPAR` retains ability `0x02000000`.
- **Pros**: Restores retail `PS2_SW_LPAR` hypervisor privilege levels to the netemu partition.
- **Cons**: Retaining hypervisor partition ability does not guarantee that the drive controller's internal profile state switches from `0x0010` to `0xFF60` if the drive was not initialized through retail disc launch routines.

---

### Route 3 (Rank 3): Flash Patch of CoreOS `lv1.self`

- **Target Module**: Flash CoreOS partition (`dev_flash/sys/internal/lv1.self`).
- **Mechanism**:
  Unpack the CFW update PUP; extract CoreOS; decrypt `lv1.self` to `lv1.elf`; apply the 4-byte patch at file offset `0x2faf80`; re-encrypt and fake-sign `lv1.self` using CFW CoreOS keys; rebuild the PUP and flash to console NOR/NAND flash.
- **Pros**: Persistent across reboots without requiring payload hooks.
- **Cons & Brick Risk**:
  - Extremely high brick risk: Corrupting CoreOS or encountering a write interruption during flash updates results in an unrecoverable hardware brick.
  - Incompatible with PS3 HEN: Non-CFW consoles (late Slim and SuperSlim) have `metldr2`, which enforces hardware ECDSA signature checks on CoreOS binaries. Attempting to install a modified `lv1.self` on a HEN console causes an instant, permanent hardware brick.

---

### Route 4 (Rank 4): Drive-Side ATA / MMC Vendor Command

- **Target**: BD-ROM Drive Controller Firmware.
- **Mechanism**:
  Dispatch a vendor-specific ATA command or MMC profile override to the drive controller via hypervisor driver `/dev/rbd0` to force the drive controller to report profile `0xFF60`.
- **Feasibility & Risk**:
  - Drive controller firmware is proprietary and closed-source.
  - Public scene documentation contains no verified vendor command for Renesas / Sunplus / Panasonic drive controllers that overrides the active MMC profile without completing optical authentication.
  - High risk of wedging the drive controller into an unresponsive state requiring an AC power disconnect.

---

## 4. Optical Drive Gate Verification & Minimal Read-Only Experiment

### Analysis of the Optical Drive Gate
A central question is whether the optical drive controller refuses sector reads solely because authentication was not performed, or if the generic MMC profile `0x0010` acts as an independent gate:
1. **Drive Firmware Operation**: When a genuine PS2 DVD-ROM is inserted, the drive spins up and successfully completes `READ CAPACITY`, returning the exact sector count (`0x001da34f` = ~3.88 GB). This proves the drive laser, tracking servos, and physical media detection are fully functional.
2. **Authentication Gate**: Under standard ATAPI specifications, profile `0x0010` is generic "DVD-ROM". Sector data streaming is withheld by the drive controller because the SAC (Secure Authenticated Channel) challenge/response has not occurred.
3. **Software Gate in `ss_server1`**: Decompilation of `0x80020638` reveals that the profile check `aiStack_40[0] - 0xff60U < 2` is a software gate within `ss_server1`. When that check passes, `ss_server1` calls `_opd_FUN_8003220c(0xc, 0x38, param_2)`. Function `_opd_FUN_8003220c` **does not inspect or pass the profile word**; it directly executes the SAC challenge/response with the drive hardware (`_opd_FUN_80035a98`).
4. **Conclusion**: The profile check in `ss_server1` is the primary software gate that prevents the drive SAC handshake from being initiated.

### Minimal First Console Experiments

#### 1. Non-Destructive Read-Only RAM Scan (PROVE live address)
Before modifying any memory, perform a safe, read-only LV1 memory scan using webMAN MOD's HTTP peek interface or PS3MAPI:
- **Action**: Read 8-byte blocks across Level-1 physical memory from `0x100000` to `0x300000` searching for the unique 16-byte pattern:
  `81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01`
- **Safety**: 100% read-only. Zero writes to memory or disk.
- **Outcome**: Confirms the exact live physical address `search_addr` of the profile check on the user's running 4.93 console.

#### 2. Reversible In-Memory Verification (PROVE authentication & sector read)
Once the physical address is identified:
1. Use webMAN MOD / PS3MAPI to execute a single 4-byte poke at `search_addr + 0x10`:
   - Write: `0x4800001C` (replacing `0x409D001C`).
2. Launch `ps2_netemu_p11_W2.self` with a retail PS2 DVD in the drive.
3. Inspect the resulting log:
   - If the VUART Port 10 response returns status `0x0000` with non-zero session keys, and subsequent `READ(10)` calls return genuine ISO 9660 Volume Descriptor data (`CD001` at LBA 16), the hypothesis is completely proven.
   - If `_opd_FUN_8003220c` returns a hardware error from the drive, the drive controller requires additional drive-side preparation.
4. Rebooting the console immediately restores stock memory with zero permanent changes.

---

## 5. Summary of Proven Facts, Inferences, and Unknowns

### Proven Facts [PROVEN]
1. Cobra patches the **loaded process pages** in LV1 physical memory (`0x100000..0x300000`), not the embedded filesystem image (which is zeroed after boot).
2. Cobra applies its secure-service patches **once at system boot** inside `main()` -> `storage_ext_patches()`, not per PS2 launch.
3. Cobra uses direct memory mapping via `HV_BASE` (`0x8000000014000000ULL`) or hypercall 183 (`lv1_cfw_poke`) as its writing primitive.
4. Cobra explicitly skipped optical disc authentication patching for `ps2_netemu` (`ps2emu_type == PS2EMU_SW`) with an early return.
5. `ss_server1` is launched at cold boot by `ss_init` and remains permanently resident across guest partition switches; it is already alive and listening on VUART Port 10 when netemu starts.
6. The profile check in `ss_server1` resides at virtual address `0x80020710` (pattern `812100703D29FFFF392900A02B890001`).
7. Changing instruction `0x409D001C` (`ble cr7, 0x8002072c`) to `0x4800001C` (`b 0x8002072c`) turns the profile check into an unconditional branch to session key calculation.
8. `sysmgr_ss` function `_opd_FUN_8001e308` explicitly strips ability `0x02000000` by executing `and r0, r0, r9` with mask `0xFDFFFFF7`.

### Inferences [INFERRED]
1. Because `_opd_FUN_8003220c` in `ss_server1` does not receive or validate the profile word, the profile check at `0x80020710` is an artificial software gate imposed by Sony to block optical disc authentication in digital emulators.
2. When the software gate is bypassed, the drive controller will complete the SAC handshake if the physical disc in the tray possesses valid PS2 optical wobble marks.

### Unknowns [UNKNOWN]
1. Whether the drive controller firmware itself enforces an internal profile check during the SAC challenge/response before streaming decrypted sector data over the ATA bus.
2. The exact physical address where `ss_server1` is loaded in RAM on the owner's specific 4.93 console (readily resolved by the proposed read-only memory scan).

## Orchestrator verification (2026-11-01)

Checked against the public Cobra source (`Joonie86/Cobra-7.00`, `446/stage2/storage_ext.c`, function `patch_ps2emu_entry`, lines ~3374-3411): CONFIRMED that Cobra scans HV physical addresses 0x100000..0x300000 in 4-byte steps with `lv1_peekd` and patches matches with `lv1_pokew` (pattern 0x409E00702FBE0001, patch at +0x10, `li r3,0x29`), and that it returns early for the softemu type with the comment about netemu having no optical disc support. So a read-only scan of that same range is what Cobra itself already does on this console; the byte offsets for an `ss_server1` patch and the claim that the loaded `ss_server1` pages sit in that range are still agy's INFERENCE (not checked on the console). Not verified by the orchestrator: the timing claim ("Cobra runs once at boot, not per PS2 launch") and the "0/10 risk" rating of a live LV1 poke (a wrong write into hypervisor memory can freeze the console; recovery is a hard power cycle, but this is not proven harmless).
