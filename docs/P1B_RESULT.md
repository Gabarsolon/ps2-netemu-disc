# P1b result (console test, 2026-10-31)

Build `local_only/p1b/ps2_netemu_p1b.self` (sha256 `b49e86f2738af08177207be4d1cfe8253139f0ec292a033dc4065d2e6eba2ee8`): repository scan (LV1 91) plus ONE `lv1_open_device` (170) on the optical node, close (171) if it succeeded.

## Observation

- **PROVEN (owner):** after installing P1b and pressing the PS button to open the in-game menu, the PS3 shut itself down. No label was seen.
- The P1a build (same hook, same repository scan, no open) ran the same menu hook on the same console without problems (PROVEN).

## Interpretation

- **INFERRED, not proven:** the `open_device` call is the likely cause (LV1 treating an open of a device this partition may not own as a fatal violation for the partition, powering the console off). The shutdown therefore does not yet answer "denied"; it could also be a bug in how we call it.
- **UNKNOWN alternatives:** (a) a label-table index outside the extended read-only data, producing a fault (the P1b read-only extension is 0x74E930..0x7BB590, about 445 KB; P1a's was about 125 KB), (b) a defect in the new scan or mailbox code that the PC emulation did not reproduce. Stores were audited as stack/mailbox only.

## Next: ablation

Same build with the open/close turned off (compile-time flag), everything else identical (same layout, same tables, same wrappers present but never called). Menu works: the open call is the cause. Still shuts down: the cause is elsewhere. Also exhaustive bounds check of every label-table index over all possible mailbox values.
