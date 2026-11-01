# P12-Scan Result: Read-Only LV1 Memory Scan (0x100000..0x300000)

**Date**: 2026-11-01  
**Target**: `http://192.168.0.169/peek.lv1?<hexaddr>`  
**Script**: [`tools/p12_scan_ss1.py`](file:///C:/Users/remus/ps2-netemu-disc/tools/p12_scan_ss1.py) (run via `python -I`)  
**Raw Log**: [`local_only/p12_scan_ss1.log`](file:///C:/Users/remus/ps2-netemu-disc/local_only/p12_scan_ss1.log)  

---

## 1. Executive Summary

A non-destructive, read-only memory scan of Level-1 hypervisor physical address space from `0x100000` to `0x300000` (2 MiB) was successfully executed against the console via webMAN MOD's HTTP `peek.lv1` interface.

- **Total Requests**: 4,229 / 4,229 successful (100% completion).
- **Network Errors / Retries**: 0.
- **HTML Parse Errors**: 0.
- **Scan Duration**: 803.37 seconds (~13.4 minutes, average rate 5.3 requests/second).
- **Aborted**: False.

### Pattern Matches
1. **`ss_server1` Profile-Check Pattern** (`81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01`):  
   **0 MATCHES** found within `0x100000..0x300000`.
2. **`ss_server3` Cobra Pattern** (`40 9E 00 70 2F BE 00 01`):  
   **EXACTLY 1 MATCH** found at physical address **`0x00165B44`**.  
   Instruction at `+0x10` (`0x00165B54`): `0x38600002` (`li r3, 2` = **STOCK / UNPATCHED**).

---

## 2. Detailed Findings

### A. Validation of `ss_server3` in Physical Memory [PROVEN]
- In the static binary [`ss_server3.elf`](file:///C:/Users/remus/ps2-netemu-disc/local_only/analysis/p0i/modules/ss_server3.elf), Cobra's search signature `0x409E00702FBE0001` is located at file offset `0x10B44`.
- The live scan identified this exact 8-byte signature at hypervisor physical address `0x00165B44`.
- Computing base address:
  $$\text{Base Address} = \text{0x00165B44} - \text{0x10B44} = \text{0x00155000}$$
- This proves that `ss_server3` is resident in hypervisor dynamic memory starting at physical address **`0x00155000`**.
- The 4 bytes at `match + 0x10` (`0x00165B54`) read `38 60 00 02` (`li r3, 2`).
- This confirms that on this console (CECH-2504B running Evilnat 4.93 CFW), Cobra did **not** patch `ss_server3` at boot, matching the public Cobra source code where `patch_ps2emu_entry()` executes an early return for `PS2EMU_SW`.

### B. Refutation of `ss_server1` in `0x100000..0x300000` [PROVEN]
- In the static binary [`ss_server1.elf`](file:///C:/Users/remus/ps2-netemu-disc/local_only/analysis/p0i/modules/ss_server1.elf), the profile validation routine contains the unique 16-byte pattern `81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01` at file offset `0x30700`.
- The scan covered every byte from `0x100000` to `0x300000` with 16-byte overlapping windows.
- Zero occurrences of this pattern exist in the entire 2 MiB range `0x100000..0x300000`.
- **Verdict**: The prior inference that `ss_server1` sits alongside `ss_server3` in the `0x100000..0x300000` physical address pool is **REFUTED** on the running console.

---

## 3. Analysis: Why `ss_server1` Was Not Found in `0x100000..0x300000`

### 1. Cumulative Memory Footprint of Hypervisor Modules [PROVEN]
The Level-1 hypervisor contains seven embedded secure service modules:
- `pme_init.elf`: 137,176 bytes (~134 KB)
- `sysmgr_ss.elf`: 391,208 bytes (~382 KB)
- `ss_init.elf`: 216,024 bytes (~211 KB)
- `updater_frontend.elf`: 145,552 bytes (~142 KB)
- `ss_server1.elf`: 529,968 bytes (~518 KB)
- `ss_server2.elf`: 305,248 bytes (~298 KB)
- `ss_server3.elf`: 232,840 bytes (~227 KB)
- **Total Module Payload**: 1,958,016 bytes (~1.91 MiB, exclusive of BSS and heap allocations).

### 2. Allocation Layout [INFERRED]
- Hypervisor kernel code, page tables, and early structures occupy `0x000000..0x154FFF`.
- `ss_server3` is allocated at `0x155000` (occupying up to `~0x190000`).
- If `ss_server1` (the largest single module at 530 KB) is loaded toward the end of the module sequence (or in a separate upper pool), its physical allocation lies above `0x300000` (e.g. `0x300000..0x600000`).
- Cobra itself only ever scanned `0x100000..0x300000` because `ss_server3` was its sole target. Cobra never searched for or patched `ss_server1`.

---

## 4. Status of Deliverables & Next Steps

### Patch Procedure Status
Under Rule 4 of the task specification:
> *"If a unique verified match is found, additionally write docs\P12_PATCH_PROCEDURE.md..."*

Because zero matches were detected for `ss_server1` in `0x100000..0x300000`, **no patch procedure can be formulated for this address range**. Applying an LV1 memory poke to an unverified or estimated address carries severe freeze/crash risks and is strictly prohibited.

---

## 5. Classification of Findings

- **[PROVEN]**:
  - webMAN MOD `peek.lv1` is completely stable for high-volume read-only sequential memory auditing (4,229 requests completed without error).
  - `ss_server3` is mapped at base physical address `0x00155000`, and its authentication routine at `0x00165B44` remains in stock unpatched state (`38600002`).
  - The profile check of `ss_server1` is **not present** anywhere in Level-1 physical memory between `0x100000` and `0x300000`.
- **[INFERRED]**:
  - `ss_server1` is allocated in physical hypervisor memory above `0x300000`, or its pages are mapped into an isolated address space that is not active while in GameOS/XMB.
- **[UNKNOWN]**:
  - The exact physical address of `ss_server1` on a running 4.93 console.
