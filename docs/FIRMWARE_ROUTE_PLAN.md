# Firmware route: boot PS2 disc straight from the drive, 2026-11-22

Owner explicitly authorized the firmware route (direct-from-physical-drive) this
session, accepting the brick/power-off risk. **Implementation stays on live LV1
RAM patches (webMAN `peek.lv1`/`poke.lv1`, reboot-recoverable) — NOT `/dev_flash`
writes** (those risk a permanent brick needing a hardware flasher). Any actual
flash write is flagged and stopped for a separate explicit decision.

Goal: let the `PS2_NE_LPAR` netemu partition reach the optical drive, which stock
firmware forbids (see [DISC_READ_WALL.md](DISC_READ_WALL.md)). Four components;
A and B are LV1 RAM patches (secure module `sysmgr_ss`, loaded in the permanent
HV pool `0x100000..0x300000`, like the proven ss_server3 patcher). C and D are
netemu SELF patches (our proven pipeline + the console-proven owned buffer).

All INFERRED until a console test says otherwise. Each console test can power the
console off (Syscon cut). Recovery is armed: smart plug cut
(`C:\Users\remus\ps3_power_manager.py recover`) then owner presses power.

## Component A — restore PS2_NE_LPAR optical ability bit (CONFIRMED offline)

`sysmgr_ss` VA `0x8001e334`: `and r0,r0,r9` (`0x7c004838`) strips ability bit
`0x02000000` from `PS2_NE_LPAR` (constructor `0x8001e308`), which removes Port 10
(VUART 10 / auth `0x5005`) binding and optical repository auth → `lv1_storage_open`
returns `-4`/`-6`. Patch to `nop` (`0x60000000`) to preserve the bit.

- Unique signature (module `07c0bd2a`, official 4.93, matches console secure mods):
  8-byte `f97d0000 7c004838`. Poke the word at **sig+4** (`7c004838`) → `60000000`.

## Component B — power the BD PCI bridge for PS2_NE_LPAR (CONFIRMED offline)

`PS2_NE_LPAR` vtable `0x8003e220` method `+0xc0` is a stub `0x8001dad8`
(`li r3,1; blr`) that does nothing; `PS2_SW_LPAR`'s `+0xc0` calls `0x8001decc` to
power on the physical PCI bus / drive. P18 G3 CONFIRMED this unpowered bridge is
the P1b power-off cause. Patch the stub to tail-branch into the power-on routine:

- Unique signature: 16-byte `f8030060 4e800020 38600001 4e800020` (the `38600001`
  stub is at **offset+8**). Poke that `38600001` → `480003f4` (`b 0x8001decc`;
  displacement `+0x3f4` is PC-relative, so physical relocation is irrelevant).

Risk: `0x8001decc` is PS2_SW's power-on; running it in the PS2_NE context is
untested and may fault (recoverable power-off).

## Component C — optical IRQ handler in the netemu SELF (TO BUILD)

`ps2_netemu` wires interrupts only for HDD (IRQ 0x12) and VUART 2; the optical
drive uses IRQ 9/10. An unhandled drive interrupt hits the guest panic vector
`0xf58` (`li r3,0x11f; li r11,0xff; sc 1` = `lv1_panic(0x11f)` → power off).
`ps2_emu` wires IRQ 9 to handler `0x222cc`; netemu has none. Add an event-port /
IRQ handler so the drive interrupt is consumed, not fatal. Build via the proven
netemu patch pipeline.

## Component D — issue the optical read into the owned buffer (TO BUILD)

Console-proven owned buffer (OWNED_CONTROL): data region EA `0x80023500` / LPAR
`0x3b23500`. From the netemu partition, after A/B/C, call `lv1_storage_open(4,2,0)`
(HV 170), then `lv1_storage_read` (HV 245) of LBA 16 into the owned buffer, poll
completion (HV 248 / event), then snapshot the bytes (controller-free, same path
as owned_control). Success = sector 16 begins `\x01CD001` (ISO9660 PVD) = the
read-proof milestone (GOAL_AND_PLAN P2).

## Test sequence (first console attempt of the route)

1. Precreate snapshot file, backup+install the C/D probe netemu (proven installer).
2. Apply A + B live via `poke.lv1` (peek-verify stock first, verify patched).
3. Launch the Buzz carrier (or `/play.ps3` TDU) controller-free; recovery armed.
4. On clean return: FTP + decode snapshot (did open/read succeed? sector bytes?).
   On no-return (freeze/power-off): plug recover, notify owner, then iterate.
5. Restore stock netemu; A/B clear on reboot (RAM patches).

## Status

- A, B: **CONFIRMED offline** against module `07c0bd2a`; live bytes to be
  peek-verified before poking. Patcher: `tools/patch_sysmgr_optical.py`.
- C, D: not built. Heavy netemu build (extends `experiments/netemu_owned_control`).

## UPDATE: A/B located + stock-verified live (2026-11-22)

`tools/patch_sysmgr_optical.py --check` scanned `0x110000..0x1a0000` (535552 B
mapped, 3 runs) and found both sites uniquely, matching the offline module:
- A ability-bit: phys `0x119334` live `7c004838` [STOCK] (VA 0x8001e334).
- B bridge-power: phys `0x118ad8` live `38600001` [STOCK] (VA 0x8001dad8).
Physical base this boot: VA 0x80000000 -> phys 0xFB000 (contiguous here). The tool
locates by signature each run, so per-boot relocation is handled. `--apply` pokes
A->60000000 and B->480003f4; `--restore` reverts; reboot also clears (RAM only).
NOT yet applied: waits for the C/D netemu probe so there is something to test.

## CONSOLE RESULT: probe 1 (open-only) POWERED OFF — 2026-11-22 ~20:15

Applied A+B live (A 0x119334->60000000, B 0x118ad8->480003f4, both verified),
installed firmware_probe1 (sha 468544385d4e19da5fc656bfab5331a99f202f2225a55921dbbe540fab7b65e8),
launched Buzz carrier. Console powered OFF at ~24s (no XMB return). No snapshot
written (panic before shutdown path). Recovery: plug off 30s + on restored
standby (the 5s recover cycle was too short; 30s discharge works), owner pressed
power. Stock netemu restored + verified (bad3e45c); A+B cleared by the power cycle.

**Interpretation:** A (ability) + B (bridge power) alone do NOT make
lv1_open_device(4,2,0) survivable. Consistent with hypothesis #2: the optical
drive asserts IRQ 9/10, the netemu has no handler, so it hits the guest panic
vector 0xf58 -> lv1_panic(0x11f) -> Syscon power-off. (Cannot yet rule out that
B's power-on routine 0x8001decc faulted in the PS2_NE context.)

**Next: Component C** — install an optical IRQ 9/10 handler/event-port in the
netemu guest kernel (mirror ps2_emu's IRQ 9 -> 0x222cc) so the drive interrupt is
consumed, then re-run the open probe. If it then survives, the IRQ was the cause.
If it still powers off with C present, suspect B's power-on path and revisit.

Also PROVEN this session: plug off/on does NOT auto-boot (powerOnReset=0, and
enabling it is unproven on this Slim); recovery needs a >=30s AC discharge then a
manual power-button press (or BT wake, which is unreliable after an abrupt cut).

## ROOT CAUSE of the probe power-offs (2026-11-22, offline analysis)

The open-probe powered off the console even with bus=99 (which per P0I returns
-17 WITHOUT touching hardware). So the power-off is NOT the optical device, the
bridge power (B), or the IRQ (Component C) -- it is the **hypercall itself**.

Evidence from stock.elf + P0D:
- All 20 `sc 1` sites in the netemu are **panic stubs** (`li r11,255; sc1` =
  lv1_panic; r3 = panic code). The netemu makes NO raw device `sc 1` in its code.
- P0D: the netemu reaches LV1 through a guest->HV **forwarding bridge** (163
  sites, r11=0x80000000|n), not bare `sc 1`. The PHAT emus call LV1 directly but
  **wrap the `sc 1` in an LPAR-state switch**: `bl 0x2f38` (switch/disable LPAR
  state) -> `sc 1` -> `mtmsrd r28` (restore) (P0D optical-read path).
- Our probe did a **bare `li r11,170; sc 1`** with no state switch. A device
  hypercall issued from the wrong LPAR/MSR state faults -> guest exception ->
  a `li r11,255; sc1` panic stub -> lv1_panic -> Syscon power-off. This fires
  regardless of the bus/dev args, matching the bus=99 power-off.

**Correction:** Component A/B and C were not the blocker for the OPEN. The real
requirement is to issue the LV1 call the way the netemu/PHAT code does: with the
correct LPAR-state-switch wrapper (and likely the netemu's forwarding path), not
a bare `sc 1`. A bare injected hypercall at owned_startup is mis-issued.

**Next (offline, before any more console tests):** reverse-engineer the netemu's
own LV1-call wrapper (its equivalent of PHAT `bl 0x2f38 ... sc1 ... mtmsrd`), or
reuse an existing netemu hypercall trampoline, and call lv1_open_device/
lv1_storage_read THROUGH it. Do NOT fire more bare-`sc 1` probes: each one
panics and powers the console off, and plug recovery is unreliable.

## Recovery reliability note
The Tapo P115 plug (192.168.0.12) becomes unreachable after a console power-off
(repeated connect timeouts), so autonomous plug-cycle recovery is unreliable.
A >=30s plug-off discharge + manual power button (owner) is the reliable path.
