# Starter prompt for a new chat

Open this repository and paste:

```
Continue the physical PS2-disc project in C:\Users\remus\ps2-netemu-disc.
Goal: boot and play the owner's inserted TDU disc through ps2_netemu on the
PS3 Slim CECH-25xx, Evilnat 4.93 CEX/Cobra 8.5, 192.168.0.169, without copying
the game to HDD. A Buzz! Schools Quiz ISO is only a diagnostic carrier.

Read AGENTS.md, docs/NETEMU_KNOWLEDGE.md, docs/GOAL_AND_PLAN.md, and
docs/OPEN_QUESTIONS.md first. Then read docs/P16_CONSOLE_RESULT.md,
docs/P17_VUART_ROUTING.md, docs/AUTOMATIC_RETURN_CONTROL.md,
docs/AUTOMATIC_SNAPSHOT_CONTROL.md and
docs/PS3_BLUETOOTH_WAKE.md. Historical P8/P9/P18 diagnosis overclaims have
review annotations; preserve measurements while distinguishing hypotheses.

Latest evidence, 2026-11-22:
- PROVEN: GameOS reads the physical TDU filesystem, SLES_544.66. Inside
  netemu, small PIO metadata arrived but sector data remained A5 prefill;
  P16 authentication returned 0x16/flags0. Physical-disc boot is UNKNOWN.
- PROVEN: 27 root netemu directories moved intact under experiments/;
  paths and validators were updated. Later controls also live there.
- PROVEN offline: experiments/netemu_disc had a stat-buffer overwrite
  and a hidden virtual read-return defect; both were reproduced and fixed.
  The full unfinished backend has NOT been installed in this follow-up.
- PROVEN: one experiments/netemu_autoreturn Buzz carrier run returned
  cleanly to XMB without controller input or plug action. It adds no
  optical commands. Stock was restored and read-back verified afterward.
  Last verified stock SHA256:
  bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a.
- PROVEN: a subsequent snapshot control retrieved a fresh HDD diagnostic
  record and returned cleanly to XMB; stock was restored and verified again.
  Its canonical compiled PPC validator passed 62 cases. No physical read.
- PROVEN offline: exact 4.93 ROM parser accepts the existing 64-byte ATAPI
  command. Missing Linux arglen is not a demonstrated defect. Call 174,
  not post-176 raw output, supplies the allocated DMA bus base.
- PROVEN offline: CPU84000000 selects VSID7 and mapper74000000; these are
  representations of one translation. LV1 rebuilds WIMG. Stock read-only
  call95 can reveal final low-R attributes, but not full physical identity
  or currently installed hardware SLB state. Live values remain UNKNOWN.
- PROVEN: normal-standby Bluetooth wake works. Full controller HID input
  remains unaccepted with both handwritten and Bumble stacks; it cannot
  yet replace Pico control. Leave the dongle assigned to isolated Linux.

Continue with owned staging-memory and safe automatic diagnostic logging,
not speculative command/auth/cache changes. Do not move the blocking P16
menu probe into native refresh. The durable snapshot candidate and owned
heap CPU-to-LPAR review are tracked in private local_only/*_task.json
receipts. Inspect those and the actual current installed hash before any
new launch; their results may be newer than this dated note. One Ghidra
JVM at a time, -Xmx3G, pyghidra only; check who owns it before starting.

The owner authorized continued implementation and console tests without
repeated confirmation in the ongoing session. Only ps2_netemu.self may
be flashed, strictly through tools/install_netemu.ps1 with PC and HDD
backups, read-back hash verification, and dev_blind unmounted in finally.
No other flash files. Preserve original games/discs and existing dirty work.
Sony-derived files stay private in ignored local_only/. No pushes/releases.

If a demonstrable hard freeze occurs: cut and restore smart-plug power
once, notify the owner, then wait for them to press the physical power
button. Offline webMAN during healthy PS2 mode is not a freeze. Direct
PS3 USB3 Video HDMI capture is allowed; desktop screenshots/input are not.
Do not kill unrelated agents/processes or touch the internal MediaTek radio.
Never print smart-plug credentials. Follow any newer owner instructions.

Keep answers short, communicate progress, and continue toward actual
physical-disc boot. Do not call an offline build or carrier loading screen
proof that TDU has booted from the drive.
```
