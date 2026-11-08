# Phase 15: Cobra LV2 Kernel Hook & Position-Independent Trampoline

**2026-11-09 audit:** the direct-disc launches ended in black screens with
all-zero logs. Netemu entry, hypercall success, LV1 patch persistence,
authentication, and sector reads remain unproven. See
[P15_RESUME_AUDIT.md](P15_RESUME_AUDIT.md) for evidence and patcher fixes.
The flow and rationale below describe the proposed mechanism.

## 1. Problem Statement & Background

When attempting to launch physical optical retail PS2 discs directly from the XMB disc icon (`PlayStation®2 Format Disc`) on PS3 Slim consoles running Evilnat 4.93 CEX Cobra 8.5:

1. **Cobra Stage2 Hard Panic**:  
   In Cobra CFW (`storage_ext_cobra7.c`, line 2573), the function `shutdown_copy_params_patched` intercepts `sys_sm_shutdown(0x8204)` (the shutdown code for booting into `ps2_netemu`). It contains an explicit hard panic for physical optical discs:
   ```c
   if (disc_emulation == EMU_OFF && (effective_disctype == DEVICE_TYPE_PS2_CD || effective_disctype == DEVICE_TYPE_PS2_DVD)) {
       fatal("Sorry, no optical disc support in ps2_netemu\n");
   }
   ```
   In compiled machine code (`stage2.cex` loaded at `0x00520000` in LV2 RAM), `fatal()` was compiled at `0x005308C4` as:
   ```text
   0x005308C0: 41 9D 06 C8    bgt cr7, 0x00530F88
   0x005308C4: 48 00 00 00    b 0x005308C4          ; infinite branch to self (hard hang)
   ```
   This immediately froze the console on optical disc launch before `ps2_netemu` could even be initialized.

2. **LV1 RAM Reset Across Partition Reboot**:  
   XMB-applied patches were observed stock after reboot. Their state during
   netemu execution and the precise reset point have not been measured.

3. **Hypercall Restrictions in Guest LPAR**:  
   Guest probes for `HVSC 182` (`lv1_peekd`) and `HVSC 183` (`lv1_poked`)
   returned `-6` / `LV1_NO_ENTRY`. Applying patches during LV2 shutdown is the
   proposed alternative; its success and persistence still need evidence.

---

## 2. Cobra Stage2 Execution Flow

Disassembly of `shutdown_copy_params_patched` in decrypted Cobra `stage2.cex`:

```text
0x005308AC: ld   r9, -0x7708(r2)    ; effective_disctype pointer
0x005308B0: lwz  r9, 0(r9)          ; load effective_disctype
0x005308B4: addis r9, r9, -1
0x005308B8: addi r9, r9, 0x00A0     ; test PS2_CD (0x10060) or PS2_DVD (0x10061)
0x005308BC: cmplwi cr7, r9, 1
0x005308C0: bgt  cr7, 0x00530F88    ; if not PS2 disc, exit cleanly
0x005308C4: b    0x005308C4         ; [STOCK HOOK POINT] fatal() infinite loop!
0x005308C8: addi r0, r9, -2         ; (ISO emulation path)
0x005308CC: cmplwi cr7, r0, 1
0x005308D0: bgt  cr7, 0x00530F88
0x005308D4: std  r2, 0x28(r1)       ; [RESUME TARGET] build_netemu_params begins
0x005308D8: ld   r26, -0x7580(r2)   ; build_netemu_params OPD
...
```

Right after the check, if execution bypasses the panic and jumps to `0x005308D4`:
- Cobra sets `prepare_ps2emu = 1`.
- Calls `build_netemu_params`, formatting `argp` with `--COBRA--` and writing `/dev_hdd0/tmp/game/ps2bootparam.dat`.
- Since `disc_emulation == EMU_OFF`, Cobra deletes `/dev_hdd0/tmp/game/ps2emu.dat` (so netemu does not expect an ISO file).
- Returns `0` to LV2 shutdown handler to launch `ps2_netemu`.

---

## 3. Position-Independent Kernel Trampoline Design

To avoid modifying flash or kernel binaries permanently, an executable trampoline is injected into unused zero-alignment space at `0x0053BD00` in Cobra's resident RAM.

### 3.1 Kernel DSI Exception Prevention (PIC Addressing)
In 64-bit PowerPC on Cell OS LV2, accessing absolute 32-bit addresses without the kernel effective address prefix (`0x80000000`) causes a kernel Data Storage Interrupt (DSI page fault / panic) because user-space segment registers are unmapped during shutdown.

The trampoline solves this by using position-independent code (`bl +4` followed by `mflr r12`), capturing the exact 64-bit runtime kernel virtual pointer into `r12`.

### 3.2 Machine Code & Register Layout

```text
Address     Opcode            Disassembly                     Description
-------------------------------------------------------------------------------------------------
0x0053BD00: 48 00 00 05       bl   0x0053BD04                 ; LR = runtime EA of 0x0053BD04
0x0053BD04: 7D 88 02 A6       mflr r12                        ; r12 = 0x0053BD04 (Kernel EA)
0x0053BD08: E8 6C 00 7C       ld   r3, 0x7C(r12)              ; r3 = 0x00713210 (FW check addr)
0x0053BD0C: E8 8C 00 84       ld   r4, 0x84(r12)              ; r4 = 0x48000164e92296c0 (patch)
0x0053BD10: 39 60 00 B7       li   r11, 183                   ; HVSC 183 (lv1_poked)
0x0053BD14: 44 00 00 22       sc   1                          ; Execute hypercall
0x0053BD18: 48 00 00 05       bl   0x0053BD1C                 ; Refresh LR
0x0053BD1C: 7D 88 02 A6       mflr r12                        ; r12 = 0x0053BD1C (Kernel EA)
0x0053BD20: E8 6C 00 74       ld   r3, 0x74(r12)              ; r3 = 0x00714710 (Profile addr)
0x0053BD24: E8 8C 00 7C       ld   r4, 0x7C(r12)              ; r4 = 0x4800001c7fc3f378 (patch)
0x0053BD28: 39 60 00 B7       li   r11, 183                   ; HVSC 183 (lv1_poked)
0x0053BD2C: 44 00 00 22       sc   1                          ; Execute hypercall
0x0053BD30: 4B FF 4B A4       b    0x005308D4                 ; Resume Cobra build_netemu_params
0x0053BD34: 60 00 00 00       nop                             ; Alignment padding
```

### 3.3 Constant Data Table at `0x0053BD80`
```text
0x0053BD80: 00 00 00 00 00 71 32 10    ; ss_server1 Drive FW check physical address
0x0053BD88: 48 00 01 64 E9 22 96 C0    ; b 0x8001F374 + ld r9, -0x6940(r2)
0x0053BD90: 00 00 00 00 00 71 47 10    ; ss_server1 Disc profile check physical address
0x0053BD98: 48 00 00 1C 7F C3 F3 78    ; b 0x8002072C + mr r3, r30
```

### 3.4 Hook Activation at `0x005308C0`
```text
Stock: 41 9D 06 C8 48 00 00 00    ; bgt +6c8; b 0x005308c4 (fatal infinite loop)
Patch: 41 9D 06 C8 48 00 B4 3C    ; bgt +6c8; b 0x0053bd00 (branch to trampoline)
```

---

## 4. Automation and Tooling

- [`tools/patch_cobra_netemu_disc.py`](file:///C:/Users/remus/ps2-netemu-disc/tools/patch_cobra_netemu_disc.py):
  - `--apply`: Installs the constant data table, writes the PIC trampoline, hooks Cobra, and verifies state.
  - `--check`: Reads Cobra stage2 RAM and reports `ACTIVE`, `STOCK`, or `ERROR`.
  - `--revert`: Restores stock `b 0x005308c4` and zeroes trampoline RAM.
- [`pico-ds3-bridge/python/ps3_controller.py`](file:///C:/Users/remus/ps2-netemu-disc/pico-ds3-bridge/python/ps3_controller.py):
  - Hardware UART controller emulation via Raspberry Pi Pico 2.
  - Synchronous command parser discarding unsolicited debug logs.
  - Automates XMB game launch and netemu exit sequences.
- [`tools/capture_obs.py`](file:///C:/Users/remus/ps2-netemu-disc/tools/capture_obs.py):
  - Captures OBS virtual canvas for visual diagnostics and screen verification.
