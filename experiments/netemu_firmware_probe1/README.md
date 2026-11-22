Firmware-route probe 1 — optical OPEN survivability test
========================================================

TEST BUILD, not fail-open by design. Extends netemu_owned_control with a single
LV1 optical-drive OPEN from the netemu partition, to answer: do the external
sysmgr_ss A+B RAM patches make `lv1_open_device(4,2,0)` SURVIVE instead of
powering the console off (the PROVEN P1b behavior)? See docs/FIRMWARE_ROUTE_PLAN.md.

## What it does
After the console-proven owned 8192-byte block is obtained in `owned_startup`
(cold-start epoch, IRQs restored), exactly once:
  oret = lv1_open_device(4, 2, 0);          // HV 170, bus 4 dev 2 = optical ROM
  cret = (oret>=0) ? lv1_close_device(4,2)  // HV 171
                   : 0xd1ed;
  probe_store(owned, oret, cret);           // free owned-block slots L_OPEN/L_CLOSE/L_PMARK
The controller-free auto-return + OWNSEC1 snapshot path is unchanged; the snapshot
now also carries open_ret (sec[62]) and close_ret (sec[63]).

NO DMA, NO sector read, NO device command. This only tests the OPEN claim.

## Hypercall stubs (build.py)
Leaf stubs, args in r3.. per the C ABI, return in r3:
  lv1_open_device  @ 0x4c60 : li r11,170 ; sc 1 ; blr  (396000aa 44000022 4e800020)
  lv1_close_device @ 0x4c78 : li r11,171 ; sc 1 ; blr  (396000ab 44000022 4e800020)
Linker symbols added at those slot addresses; IR/assembly audits and the JVM
validator extended to recognize the two stubs (validator models the HV return,
default 0; sites 0x4c60/0x4c78).

## Build / validate (offline, no console)
  python -B experiments/netemu_firmware_probe1/build.py
  python -B -u experiments/netemu_firmware_probe1/validate_pc.py --allow-jvm
Artifacts in local_only/firmware_probe1/ (gitignored). SELF:
ps2_netemu_firmware_probe1.self.

## Console test (operator)
1. Precreate /dev_hdd0/tmp/netemu_owned_snapshot.bin = 65536 zero bytes (FTP).
2. Apply A+B:  python tools/patch_sysmgr_optical.py --apply   (verify STOCK->PATCHED)
3. Backup+install the probe SELF via tools/install_netemu.ps1.
4. Launch the Buzz carrier controller-free (webMAN play.ps3). Recovery armed:
   if no XMB return within ~180 s => power-off/freeze: cut smart plug
   (ps3_power_manager.py recover), notify owner, then iterate.
5. On clean return: FTP + decode the snapshot
   (decode_snapshot.py) -> read probe_open_ret / probe_close_ret.
6. tools/patch_sysmgr_optical.py --restore ; restore stock netemu. A+B also
   clear on reboot (RAM only).

## Reading the result
- SURVIVED + probe_open_ret == 0x0  : OPEN succeeded, bridge powered (B worked),
  ability granted (A worked). Big step. Next: Component C (optical IRQ handler)
  + D (lv1_storage_read LBA 16 into the owned buffer).
- SURVIVED + probe_open_ret negative : open reached LV1 but was denied
  (e.g. -4 policy, -6 no-entry) -> A/ability or device-state issue; iterate A.
- NO snapshot / power-off           : open still fatal -> an optical IRQ fired
  (need Component C) or B insufficient. Recover and add C.

## Risk (honest)
INFERRED throughout. Opening the live drive may still power the console off
(IRQ panic, or B running PS2_SW's power-on in the PS2_NE context may fault).
This build is NOT fail-open: with A+B absent it WILL power off on launch, so it
is installed only for the single test and stock is restored immediately after.
