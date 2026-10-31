# P0E: optical open from the PS2 partitions

**Verdict — INFERRED:** the strongest remaining explanation is an LV1-side difference in optical-device ownership, access policy, or launch-time device state for the netemu LPAR. **PROVEN (owner):** enabling the P1b optical-open path powers off the CECH-25xx; disabling it works. **PROVEN (PC decoding):** the phat optical opens use the same repository-ID namespace and **r5=0**, and both open **before** constructing their optical event port. There is no optical PCI-claim, MMIO setup, or event-port-before-open prerequisite in either traced path. The bridge also initializes its privilege bytes to allow both guest privilege states. **UNKNOWN:** the actual fatal instruction and LV1 decision: the available evidence cannot distinguish a fatal open from a successful open followed by a fatal event, close, or other subsequent action. Recommend the read-only P1c repository comparison below; do not repeat P1b unchanged.

Evidence convention: **PROVEN** means owner observation or a performed PC byte/decoding check; **INFERRED** means static control/data-flow interpretation; **CLAIMED** means an external assertion not independently established here; **UNKNOWN** means unresolved. A paragraph/table introduced with a label inherits that label unless a cell explicitly overrides it. No hardware behavior is proved by disassembly.

**PROVEN (PC):** fresh decoding used `tools/p0e_ghidra.py`, pyghidra/Ghidra 12.1.3, JDK 21, `-Xmx3G`, one JVM/program at a time. Projects, raw listings and the complete annotated pseudo-C are under `local_only/analysis/p0e/`; no Sony listing/decompilation is reproduced here. `tools/p0e_inspect.py` reads the ELFs, displays raw instruction words beside Ghidra text, resolves TOC constants, and verifies the open-site opcodes. The three inputs matched:

| Input | SHA-256 — PROVEN (PC) |
|---|---|
| stock netemu | `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3` |
| community ps2_emu | `3af1ba14806df8d71b277682dec4c60e20c9552a73b6612439c0d0e701981252` |
| community ps2_gxemu | `365769d75cb05c4c48602eb163e54593669834ede253d7c5d26e59795edde36c` |

**PROVEN (PC validation):** `python tools/p0e_checks.py` passed the three full hashes, independent executable-segment scan for all 16 constant-170 sites (12 phat plus four netemu), immediate r5=0 anchors, and the bridge initializer/panic and HDD no-op-helper words; results are retained in `local_only/analysis/p0e/checks.json`. The three analysis tools also passed Python compilation. Public sources were inspected through web retrieval; local socket retrieval was denied by the workspace sandbox, and no network restriction was bypassed.

**UNKNOWN:** equivalence of the community files to untouched Sony releases, and the owner's running LV1 to the public Cobra source. Findings below apply to these hashes. **PROVEN (work performed):** no console/LAN/phone contact, console writes, installers, game/emulator launches, process termination, or git mutations were performed.

## 1. How the phat emulators open optical

### All constant LV1 170 sites

**PROVEN (PC):** all twelve supplied sites are `sc 1` with locally established r11=170 and **r5=0**. **INFERRED:** their classifications and arguments are as follows. `B`/`D` are repository indexes; the LV1 arguments are values read from the `id` fields, never the selector numbers themselves. This covers all constant-170 sites in the independently scanned executable segments; **UNKNOWN:** arbitrary dynamically computed hypercall numbers.

| ELF | Open site / containing init | Selection producing `(r3=bus_id,r4=dev_id)` | Classification |
|---|---|---|---|
| emu | `0x1d4a0` / `0x1d400` | scanner `0x1d954(1,1,0xffffffff820e104d,...)`; PCI identity match | PCI platform device; exact hardware role UNKNOWN |
| emu | **`0x22524` / `0x22460`** | **bus type 5, device type 5**; actual IDs through `0x1dd14`/`0x1dd90` | **Optical ROM** |
| emu | `0x26a94` / `0x26988` | bus type 4, device type 3 | Network driver, corroborated by following LV1 191 and network-family calls |
| emu | `0x28e84` / `0x28da8` | bus type 4, device type 4; repeated enumeration excludes previous packed device key | Other controller, not ROM; P0D's optical/PATA association is unsupported |
| emu | `0x42f14` / `0x42e58` | bus type 5, device type 0 | HDD |
| emu | `0xfbcdc` / `0xfbc28` | bus type 5, device type 14 | Flash |
| gxemu | `0x41494` / `0x413a8` | bus index 1, type 4, start index 0; enumerator `0x4199c` | Other controller, not ROM |
| gxemu | `0x56c74` / `0x56a6c` | bus index 2, type 1; PCI identity `0x81ff104d`; selected matching instance | PCI platform device, not ROM |
| gxemu | `0x6b884` / `0x6b6d8` | bus index 4, type 0, start 0, end all-ones | HDD |
| gxemu | **`0x8d600` / `0x8d510`** | **bus index 4, device type 5**, start 0, end all-ones | **Optical ROM** |
| gxemu | `0x92ad8` / `0x92a50` | bus index 1, type 3 | Network driver; following LV1 191 corroborates |
| gxemu | `0x95fb0` / `0x95f3c` | scanner `0x98244(5,14,0,...)` | Flash |

**INFERRED:** emu optical discovery does **not** filter port 0. Its scanner `0x1d954` searches bus indexes 0..255 by bus **type**, reads `num_dev`, and searches device **type**. For non-PCI types, its third argument is an excluded *packed device key*, not a port. Passing 0 excludes no normal `dev/D` key. It returns packed bus/device keys; `0x1dd54` and `0x1ddd0` issue LV1 91 to obtain the final IDs. Neither ID is a file descriptor returned by open: LV1 170 returns status only. Context `0x502898+0` is bus ID, `+8` device ID, `+0x10` event port, `+0x18` buffer LPAR address, `+0x20` CPU address, `+0x28` DMA base. P0D's context layout and “device fd” interpretation were wrong.

**INFERRED:** gxemu reads `bus/4/id` at call `0x8d584`, obtains `info.id` from enumerator `0x4199c(4,5,0,info,~0)`, and stores that ID at `0x8d5c8`. Its second argument is device type, third start index, fifth end index; it has **no port-filter argument**. It requires exactly one interrupt (`info+0x1c`, checked at `0x8d5d8`), and later a readable port (`info+0x38 != -1`), without comparing the port to 0. `0x420f8`, called twice, is a dump-shaped no-op/finite counter loop; it makes no hypercall or device registration.

**PROVEN (owner):** P1b found the ROM at B=4,D=2 with ID values 4/2, type 5, port 0. **INFERRED:** this matches both phat selectors. Their actual runtime numeric IDs on phat hardware are **UNKNOWN**; do not describe the binaries as hardcoding `(4,2)`.

### Optical lifecycle, in order

**INFERRED reconstruction:** the complete pseudo-C, including scanner branches, packet submission, completion and shutdown, is in `local_only/analysis/p0e/optical_lifecycle.pseudo.c`. The following are ordered address summaries, not copied source. Checked failure branches are not a transactional rollback: emu commonly returns failure with already acquired resources; gxemu retries missing enumeration and panics on other setup failures.

| Order | ps2_emu optical init `0x22460` |
|---|---|
| 1 | Clear context; find storage/ROM at `0x224b0`; read final bus/device IDs at `0x224f4`/`0x22508`. Only repository reads precede this device's open. |
| 2 | **170 `(bus_id,dev_id,0)` at `0x22524`.** |
| 3 | **18** construct port at `0x22538`; **197** `(bus,dev,event_port,interrupt_id=0)` at `0x22568`; **28** `(irq_plug=9,event_port)` at `0x22584`. The last argument of 197 is an interrupt ID, not general flags. |
| 4 | Install handler/mask bit with guest-kernel helper `0x3a24` at `0x225a0`; descriptor `0x4c54d0` leads to handler `0x222cc`. This helper changes local tables/mask state, not LV1 device ownership. |
| 5 | Buffer: partition memory base from leaf `0x44c4` plus `0x100000` for LPAR address; CPU address `0x30100000`. **174** `(bus,dev,0x100000,page_exp=20,flags=0)` at `0x225d8`. **176** maps that LPAR buffer, returned DMA base, size `0x100000`, flags **`0xe000000000000800`**, at `0x22610`. |
| 6 | Packet helper `0x22138` issues **248** at `0x221f8`. Init first sends MODE SENSE(10), page `0x1a`, allocation `0x14`, at `0x2267c`; saves two timer values if successful. Then attempts MODE SELECT(10), PF=1, page `0x1a`, zero timers/control bits, at `0x22780`, even if MODE SENSE failed. This is device-state modification, not an open-only example. |
| 7 | Store callback descriptor `0x4c5500` (entry `0x223a0`) through `0x1ee1c` at `0x22788`, return success. The leaf stores it at local state `0x500d68+0x28`; its broader role is UNKNOWN. |

**INFERRED:** packet submission uses `(dev_id,command=1,packet,0x40,data_buffer,byte_count)`; it masks/restores MSR.EE around submission, saves the tag, and waits for guest event `0x4000` (`sc 0` at `0x22260`). Optical interrupt handler `0x222cc` uses **254** `(dev_id,expected_tag)` at `0x222f4`, stores status and signals that event. **PROVEN (PC):** it is 254, not 249 in this handler. **INFERRED:** `0x4000` is an event mask, not successful LV1 status or a decrementer constant. A successful submission can wait without the retry count providing a completion deadline. Linux names 248/249/254 consistently with these argument counts. [Linux LV1 ABI](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/include/asm/lv1call.h).

**INFERRED:** emu shutdown **`0x227ac`** restores the saved page-`0x1a` timer settings using MODE SELECT at `0x228ac`, then **177** unmap `(bus,dev,dma,0x100000)` at `0x228c4`, **175** free at `0x228d8`, **171** close `(bus,dev)` at `0x228e8`. There is no explicit 198/29/19 event disconnect/destruction in this routine. **UNKNOWN:** additional partition-wide cleanup of those resources.

| Order | ps2_gxemu optical init |
|---|---|
| 1 | Caller `0x8b2a0` sets size **1 MiB** at `0x8b2c0`, allocates the LPAR/CPU buffer through `0x40fdc` at `0x8b2c8`, creates local disc/worker state through `0x8f73c`, then calls `0x8d510` at `0x8b2d8`. These steps contain no optical open or PCI configuration. |
| 2 | Read bus ID, enumerate ROM, require one interrupt, as above. **170 `(bus_id,dev_id,0)` at `0x8d600`.** |
| 3 | Retain/validate repository port. **174** `(bus,dev,0x100000,20,0)` at `0x8d63c`; **176** `(bus,dev,buffer_lpar,dma,0x100000,0xe000000000000800)` at `0x8d670`. |
| 4 | **18** at `0x8d680`; **197** `(bus,dev,event_port,info.intr[0].id)` at `0x8d6a8`; **28** `(irq_plug=10,event_port)` at `0x8d6c0`. |
| 5 | Register handler via `0x4f810` at `0x8d6d4`; descriptor `0x64f440` points to `0x8d7d4`. Return. No MODE SENSE/SELECT in this initializer. |

**INFERRED:** gxemu packet helper `0x8da80` issues **248** command 1 at `0x8db4c`, then waits for guest event `0x800`; an alternative command-0 submission is at `0x8da04`. Handler `0x8d7d4` polls **249** at `0x8d82c`, matches the pending tag, handles no-entry, acknowledges with **27** at `0x8d8a0`, and signals/defer-signals `0x800`. These are later driver operations, not pre-open requirements.

**PROVEN (PC):** gxemu has just three locally constant 171 sites: `0x6bbcc` (HDD), `0x914e8` (network), `0x96054` (flash). **INFERRED:** none closes the optical globals; the optical-adjacent `0x8d74c` is a return stub. **UNKNOWN:** an indirect/common partition-wide optical teardown. A gxemu optical “unmap/free/close identical to emu” cannot be supplied honestly; P0D's symmetry assumption is false. The pseudo-C explicitly retains that missing close as UNKNOWN.

### PCI, MMIO and the kernel boundary

**PROVEN (PC) / INFERRED meaning:** the `0x146` sequence is **178 read PCI configuration**, then **179 write PCI configuration** at offset **4**, width **4**, value **`0x146`**, and offset **12**, width **4**, value **0**. These are register arguments, not stores into a command buffer. The emu scanner executes it only when device type is 1 or 2 (`0x1dae4`, `0x1db4c`); ROM type 5 branches past it to `0x1dc7c`. Netemu scanner `0x1e9ba0` has the same conditional PCI branch; its existence does not make it an HDD/ROM prerequisite. Gxemu's separate platform init reads PCI at `0x56b70`, writes at `0x56c18`/`0x56c44`, then opens a **bus-2/type-1** device, not ROM. [HV PCI ABI](https://www.psdevwiki.com/ps3/HV_Syscall_Reference#lv1_read_pci_config).

**INFERRED:** **neither traced optical lifecycle issues 172 or writes MMIO registers**. Emu `0x1d504` maps MMIO for its distinct bus-type-1/type-1 platform device, with later DMA/platform setup in `0x1d544`; gxemu has other platform/MMIO drivers as well. Those paths must not be spliced into ROM init. **UNKNOWN:** broader hardware dependencies of the external PCI device, especially on phat/devkit configurations; no traced optical-specific claim or registration is supplied by it.

**INFERRED:** all phat LV1 calls above execute with direct `sc 1` in the PPU partition's own privileged native code. Early platform enumeration/setup belongs to its kernel/platform portion; optical init, command submission and callbacks belong to its native driver/emulator portion in that same privileged address space. The IRQ dispatcher, local handler registration, interrupt masking and event wait/signal machinery are guest-kernel services. Their `sc 0` event operations are not forwarded LV1 calls. This is separate from emulated PS2 IOP/EE code. Netemu's native driver instead reaches LV1 through the guest-kernel bridge. A phat open does not return a kernel-owned fd to an unprivileged optical frontend.

**INFERRED, call ownership:** E's common repository helpers `0x1d954`/`0x1dd14`/`0x1dd90` and G's `0x40160`/`0x4199c` issue 91 inside shared platform services. The optical driver bodies themselves issue 170/18/197/28/174/176, and their command/IRQ bodies issue 248/254 (E) or 248/249/27 (G). The distinct early PCI/platform opens are not optical opens performed on their behalf. No extra kernel-only optical grant call was identified.

## 2. What netemu is missing, and what is already present

**INFERRED, instruction checked:** stock HDD init `0x12be04` does this:

| Stage | Netemu evidence |
|---|---|
| Before lookup | Clear driver state, set invalid tag/status; check startup mode through `0x111db4`. No device-open authorization call. |
| Repository | `bus/4/id` via `0x111eb8` at `0x12beb0`; `0x114ea4(4,0,info,type=0,port=2)` at `0x12bed8`, with ten delayed retries if missing. |
| Lookup to open | Call **`0x114dc8` at `0x12bf6c`, which is only `blr`**; load `info+8` as device ID, preserve the previously read bus ID, set r5=0. No other LV1 call or device registration intervenes. |
| Open/event | **170 at `0x12bf8c`**, **18 at `0x12bfa0`**, **197 `(bus,dev,port,interrupt_id=0)` at `0x12bfd0`**, **28 `(0x12,port)` at `0x12bfec`**. |
| Memory | Allocate 1 MiB driver buffer; **174 `(bus,dev,0x80000,12,0)` at `0x12c03c`**; helper `0x160fc` maps it with **176 at `0x16134`**, size `0x80000`, flags `0xe000000000000800`. No 172 or 178/179. |
| Ready to read | Return/enable driver and cache state. Read helper `0x12b5fc` submits **245 at `0x12b674`**, `(dev_id,region_id=1,lba,sectors,flags=0,buffer_lpar)`; waits for event `0x2000`. Handler `0x12b320` uses **27 at `0x12b33c`**, **249 at `0x12b350`**, saves tag/status, signals the event. No successful-submission completion deadline is visible. |
| Shutdown | HDD cleanup includes dirty-cache writes; then **177/175/171 at `0x12d5e4`/`0x12d5fc`/`0x12d610`**. It is unsuitable as an optical probe or generic close helper. |

**INFERRED:** generic startup calls the HDD initializer at `0x18cc4`. The kernel's event/IRQ machinery already exists by then; the HDD completion handler is part of that established native driver arrangement. Its port connects only the HDD device/interrupt. Having that port present during the later menu hook does not connect the ROM node to a handler. A second active storage driver needs its own port, IRQ registration, DMA ownership, tag/status and event state; none of those is a demonstrated **pre-open** permission mechanism.

**PROVEN (PC) / INFERRED:** the bridge has more context checking than “call number plus one byte” might suggest, but no argument filtering:

- `0xc50` removes the high call marker; `0xc64` bounds the number below 256.
- `0xc6c..0xc74` selects a 256-byte bank using USPRG0 bit `0x40000000`, then indexes by hypercall number. `0xc78..0xc84` compares the byte against saved MSR.PR. A rejected privilege check reaches `0xf58`, **LV1 panic 255 with code `0x11f`** at `0xf60`; it does not return a permission error.
- Crucially, initializer **`0x10550`**, called at `0x16f38` and `0x175e0`, fills **all 256 entries in the selected bank with 2**. The byte store is `0x10590`: base `0x1c30 + bank + index + 0x750 + 0xc`, i.e. `0x238c + bank + index`. `0x10834` contains the same reset-to-2 loop, called at `0x11cac`.
- Thus both PR=0 and PR=1 pass with the initialized value 2, including number 170; no per-device or per-software-thread restriction appears here. `0xc88..0xc9c` restores argument registers before `sc 1` at `0xca0`; r5 is preserved. The P1b leaf at `0x4820` is `li/oris/sc0/return`, with no TOC access or argument rearrangement.

**UNKNOWN:** corruption or later modification of the live table/context on the owner's trial. The ELF's zero-filled low state is not the initialized runtime table and must not be read as “170 forbidden.” **INFERRED:** the menu-vs-init thread explanation is now weak: bank/PR selection exists, but stock initialization grants both states. No evidence supports a special “menu thread may not call 170” rule. No register-return observation proves that the bridge reached LV1 on the failing trial, so absolute exoneration would still overstate the evidence.

**INFERRED comparison:** phat emu adds ROM selection, IRQ 9/event `0x4000`, a 1 MiB/1 MiB-page DMA mapping, optical command handling, power-condition MODE SENSE/SELECT and restoration. Gxemu adds ROM selection, repository-derived interrupt ID, IRQ 10/event `0x800`, its own buffer/worker and DMA-before-event order. Netemu HDD instead uses type 0/port 2, IRQ `0x12`/event `0x2000`, 512 KiB DMA with 4 KiB pages, fixed storage region 1 and HDD caches/writeback. Its generic sc0 bridge and partition memory mapper are additional layers, not missing ROM permissions. **UNKNOWN:** the optical LPAR grant and launch profile; repository visibility is not evidence of either.

## 3. Ranked explanations and discriminating experiments

### Public-source cross-check

**PROVEN (source inspection) / INFERRED comparison:** Linux `ps3_open_hv_device` sends storage ROM/disk/flash through `lv1_open_device(bus_id,dev_id,0)`; the special shared-open counters are for USB IDs 1/1 and 1/2. Failure is handled as an error. [Linux system bus](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/platforms/ps3/system-bus.c). Linux storage setup **opens first**, then sets up event reception/IRQ, then DMA. It does not pre-register an optical device with a separate grant call. [Linux storage setup](https://raw.githubusercontent.com/torvalds/linux/master/drivers/ps3/ps3stor_lib.c). Its event helper constructs a port, binds the CPU IRQ, then connects the device's repository interrupt ID; this differs from the phat connection order without implying a pre-open requirement. [Linux interrupts](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/platforms/ps3/interrupt.c).

**PROVEN (source inspection):** Cobra 8.5/4.93 `get_ps2emu_type` selects HW/GX/SW from hardware configuration. `patch_ps2emu_entry`, lines 3547..3592, **returns for SW/netemu**. For HW/GX it scans LV1 `0x160000..0x300000` for two instruction signatures and replaces the instruction at match+`0x10` with `li r3,0x29`. **CLAIMED (source comments/wiki):** these substitute optical authentication/reset behavior; comments say additional emulator patches are needed for recordable discs. **INFERRED:** this inspected routine does not patch LV1 170's dispatcher, change repository IDs, connect IRQs, or assign ROM to netemu. **UNKNOWN:** other patches present in the owner's LV1 and whether a different launch/profile/auth path contributes to the shutdown. Copying these two instructions into LV1 is not a supported experiment here. [Cobra source](https://github.com/xXEvilnatXx/Cobra-PS3/blob/main/8.5/4.93/EVILNAT/PEX/SRC/stage2/storage_ext.c#L3547), [wiki attribution to ss_storage service 0x5004](https://www.psdevwiki.com/ps3/PS2_Emulation#Cobra_core).

| Rank — INFERRED | Evidence for | Evidence against / limit |
|---|---|---|
| **1: (a) LV1 ownership/policy or incompatible launch/device state** | Owner's open-enabled/off ablation; same valid ID namespace and flags as phat; no missing pre-open API in the working patterns. Netemu takes a distinct optical-less launch path. | **UNKNOWN:** no owner's LV1 disassembly, assignment/ACL record, panic reason or return trace. Linux normally expects an error from denied/failed opens; fatal-on-unassigned is **not PROVEN**, and is not documented as a general rule by the inspected reference. |
| **2: (b) successful open followed by fatal event/state transition** | P1b installs no optical receive port/handler. No observed return does not locate the failure within open. | Both phats and Linux deliberately open before constructing the optical port. Merely lacking a port at the instant of open is therefore weak as a general explanation. **UNKNOWN:** stale routing, pending unsolicited events, and the immediate-close path. |
| **3: (d) bridge/context** | Bridge rejection itself can panic; menu and bootstrap are different contexts, and live state was not captured. | Initializers set every privilege byte to 2, admitting both PR values; no device arguments or software-thread identity are tested. Leaf ABI matches stock. **UNKNOWN:** trial-specific corruption. |
| **4: (c) wrong IDs** | A selector/index substitution can generally be disastrous. | **PROVEN (owner):** IDs were actually read as 4/2. **INFERRED:** P1b stores repository outputs at mailbox +64/+72 and passes those; stock and phats read the same `id` nodes. Index and ID happen to agree here. No LV2 long device identifier is involved. |
| **5: (e) different open flags needed** | Possible firmware/device-specific semantics are UNKNOWN. | **PROVEN (PC):** both ROM opens, all other ten phat opens and stock HDD open use r5=0. Linux also uses 0. No evidence supports a nonzero optical flag or trying flag values. |

**UNKNOWN:** P1b's successful-return branch would immediately store the result and issue 171. The ablation identifies the open-enabled lifecycle as the trigger, not an instruction-level LV1 crash location. Do not infer “LV1 returned denied,” “open definitely never returned,” or “an unhandled interrupt definitely occurred” from the missing label.

### Experiments: proposals only, none executed or built here

1. **Recommended — read-only P1c. INFERRED diagnostic value:** dump both values and return codes for the exact keys in section 4, separately for B=4,D=2 and B=4,D=3; retain full 64-bit IDs. Compare interrupt type/ID, port, `meddling`, geometry, region count and region tuples. This can expose an ID/interrupt assumption and characterize the device, but cannot prove its assignment to the current LPAR. Use the existing bounded LV1-91 wrapper; do not call the stock fatal-on-missing-key helpers. **Worst case:** an implementation/memory fault powers off the partition/console; it issues no drive command or LV1 device-state write. Missing keys must remain ordinary logged errors.
2. **Optional later controlled open — UNKNOWN outcome:** if the owner elects another risky trial, place a one-shot probe in the stock init context **after the HDD's 18/197/28 setup has succeeded**, with separate state and an already constructed optical port, validated unused IRQ plug, installed handler and matching mask. Open only the independently verified ROM IDs with flags 0; on success connect 197 using the ROM's actual interrupt ID. Observe a returned-status phase before a separately staged close. No DMA, MMIO, PCI writes, storage reads/writes, MODE SELECT, reset or authentication calls. **Worst case:** the same immediate console power-off; no intentional media write or persistent configuration change. An unattached pre-created port cannot catch device events before 197, so this does **not** eliminate the immediate-event window. Startup success versus menu failure favors timing/context; a failure still cannot separate policy from an immediate state/event failure without LV1-side evidence. A post-open phase followed by failure at connect/close would relocate the cause.

**INFERRED:** no read-only repository experiment can fully distinguish (a) from an event occurring inside/just after open. Preconnecting 197 to an unopened device is not established by these sources, so it is not proposed. Do not open the already-active HDD, vary flags, borrow its IRQ/DMA context, or copy the phat PCI/MODE SELECT sequence as a diagnostic.

## 4. Exact repository fields for P1c

**INFERRED, strings/register construction checked:** names below are four 64-bit fields supplied to LV1 91 with repository partition argument **1**, not slash-separated ASCII. Define `K(s,i) = BE64(s padded with zero bytes to 8) OR i`, with the index confined to zero padding. For the first field, `F("bus",B) = 0x0000000062757300 + B`; subsequent `K("dev",D) = 0x6465760000000000 + D`. Netemu encoder `0x111f6c` rejects names longer than eight bytes or indexes overlapping text; wrapper `0x111eb8` folds the first encoded field's high/low 32-bit halves together (`0x111ebc..0x111efc`). Gxemu uses encoder `0x40208`/wrapper `0x40160`; emu builds first-field `bus` and subsequent fields directly in registers. Example node `bus/4/dev/2/id` is `(0x62757304,0x6465760000000002,0x6964000000000000,0)`. The partition argument 1 is the PME repository selector; it does not mean the ROM is granted to LPAR 1 or to netemu.

**INFERRED:** table notation `b/d/x` means `F(bus,B),K(dev,D),K(x,0),0`; `intr/I` and `reg/R` pack their integer indexes into their own fields. E=ps2_emu, G=ps2_gxemu, N=netemu. Addresses name the repository call instruction (or call into the shared LV1-91 wrapper). “No” is scoped to the inspected enumeration paths, not every possible dynamically constructed query.

| Key path / four-field scheme | Meaning of returned values | Phat reader / address | Does netemu read it? / address | Status |
|---|---|---|---|---|
| `bus/B/id` = `F(bus,B),K(id,0),0,0` | Final LV1 bus ID, v1 | E `0x1da5c`, `0x1dd54`; G optical `0x8d584` | Yes, HDD `0x12beb0`; bus walker `0x115618` | INFERRED |
| `bus/B/type` | Bus type, v1 | E scanner `0x1da20`; G bus walker `0x42220` (not needed by fixed-bus optical selection) | Yes, `0x115688` | INFERRED |
| `bus/B/num_dev` | Device count, v1 | E `0x1da94`; G bus walker `0x42274` | Yes, `0x1156d4` | INFERRED |
| `bus/B/dev/D/id` = `b/d/id` | Final LV1 device ID, v1 | E `0x1ddd0`; G `0x41af0` | Yes, `0x114fa8` | INFERRED |
| `bus/B/dev/D/type` | Device type, v1; ROM=5 | E `0x1db1c`; G `0x41b50` | Yes, `0x11500c` | INFERRED |
| `bus/B/dev/D/port` | Storage port, v1 | E helper `0x1de48`, **not called by optical init**; G `0x41cf0` | Yes, filter `0x115074`, final read `0x1153cc` | INFERRED |
| `bus/B/dev/D/pci_bus` | PCI bus number, v1 | E `0x1db6c`, **PCI types only**; G `0x41bc8` | Yes, `0x11510c` | INFERRED |
| `bus/B/dev/D/pci_dev` | PCI device number, v1 | E `0x1dba0`, **PCI types only**; G `0x41c20` | Yes, `0x115164` | INFERRED |
| `bus/B/dev/D/pci_fun` | PCI function, v1; **exact spelling is `pci_fun`** | E `0x1dbd4`, **PCI types only**; G `0x41c78` | Yes, `0x1151bc` | INFERRED |
| `bus/B/dev/D/meddling` | Raw device attribute v1; ownership meaning UNKNOWN | G `0x41d48`; E ROM scanner does not read it | Yes, `0x115424` | INFERRED / UNKNOWN meaning |
| `bus/B/dev/D/blk_size` | Block size, v1 | G `0x41da0`; E ROM scanner does not read it | Yes, `0x11547c` | INFERRED |
| `bus/B/dev/D/n_blocks` | Block count, v1 | G `0x41df8`; E ROM scanner does not read it | Yes, `0x1154d4` | INFERRED |
| `bus/B/dev/D/n_regs` | **Storage-region count**, v1; not the MMIO-register count | G `0x41e50`; E ROM scanner does not read it | Yes, `0x11552c` | INFERRED, Linux corroboration |
| `bus/B/dev/D/intr/I` = `F(bus,B),K(dev,D),K(intr,I),0` | **v1 interrupt type, v2 interrupt ID**. No `type`/`id` suffix | G `0x41ebc`; E helper `0x1ded0`, not called by this optical init | Yes, `0x115244`; indexes 0..15 until failed lookup | INFERRED |
| `bus/B/dev/D/reg/R/type` = `F(bus,B),K(dev,D),K(reg,R),K(type,0)` | MMIO register type, v1 | G `0x41f6c`; E helper `0x1dfa4`, not optical init | Yes, `0x11536c`; bounded 0..15 | INFERRED |
| `bus/B/dev/D/reg/R/data` = previous with `K(data,0)` | **v1 register address, v2 length** | G `0x41fe0`; E `0x1df68`, not optical init | Yes, `0x1152cc`; bounded 0..15 | INFERRED |
| `bus/B/dev/D/region/J/id` = `F(bus,B),K(dev,D),K(region,J),K(id,0)` | Storage region ID, v1 | No in the traced ROM enumerators | No in `0x114ea4`; **Linux** `ps3_repository_read_stor_dev_region_id` | INFERRED public schema |
| `bus/B/dev/D/region/J/start` = same with `K(start,0)` | Region start sector, v1 | No in traced paths | No in `0x114ea4`; **Linux** `ps3_repository_read_stor_dev_region_start` | INFERRED public schema |
| `bus/B/dev/D/region/J/size` = same with `K(size,0)` | Region size in sectors, v1 | No in traced paths | No in `0x114ea4`; **Linux** `ps3_repository_read_stor_dev_region_size` | INFERRED public schema |
| `bus/B/dev/D/region/J/access_right` | No validated field or packing | No reader identified | No reader identified; absent from inspected Linux repository implementation | **UNKNOWN; do not invent/pack this literal** |

**PROVEN (PC):** the exact N string pointers are `bus=0x300960`, `dev=0x3009f0`, `id=0x300388`, `type=0x3009f8`, `port=0x300a00`, `pci_bus=0x300a08`, `pci_dev=0x300a10`, `pci_fun=0x300a18`, `intr=0x300a20`, `reg=0x300a28`, `data=0x300628`, `meddling=0x300a30`, `blk_size=0x300a40`, `n_blocks=0x300a50`, `n_regs=0x300a60`, `num_dev=0x300a68`. G's corresponding strings are `0x531678..0x531708`; TOC slots `0x670750..0x6707c8`. E uses packed constants such as `intr=0x696e747200000000`, `reg=0x7265670000000000`, `data=0x6461746100000000`. The raw byte search found no null-terminated `region`, `start`, or `access_right` literal in these three ELFs; absence alone does not exclude constructed constants.

**INFERRED public additions:** Linux documents region `id`, `start`, `size`, the first-field packing and the paired interrupt/register results. These are additions for P1c, **not findings that the phat optical paths already read region ACLs**. Keep those public-source inferences distinct from the binary-reader addresses. [Linux repository implementation](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/platforms/ps3/repository.c).

**UNKNOWN:** a repository storage-region ACL key. `access_right` is 12 characters, longer than this eight-byte component format, and is not read by the inspected code. Silently truncating it to eight bytes would query a different, unsupported name. No `intr/N/id`, `intr/N/type`, `reg/N/start`, or `reg/N/size` lookup was found in these readers either; use the actual paired values above. **INFERRED:** dump at most 16 interrupt/register entries and a bounded number of regions (record count and truncation if greater), using region **indexes** to fetch region **IDs**, preserving both v1/v2 and each error. The ROM can legitimately lack geometry/regions with no disc; do not turn missing entries into a fatal assertion or proof of denied ownership.

### Corrections to P0D that affect this decision

**INFERRED, independently rechecked:** do not reuse P0D's device-fd/context layout, optical 172 mapping, unconditional 178/179 claim, buffer interpretation of `0x146`, port interpretation of the scanner's third argument, `pci_func` spelling, gxemu symmetry, or `0x4000`-as-success/decrementer explanation. Those claims were contradicted or unsupported by the instructions. **UNKNOWN:** physical-disc readability and any complete phat-to-slim backend transplant; P0E does not establish either.
