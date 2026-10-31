# P1b result (console test, 2026-10-31)

Static follow-up: [P0E optical-open analysis](P0E_OPTICAL_OPEN_ANALYSIS.md) verifies both phat paths, bridge initialization, ranked causes, and exact read-only P1c repository keys.

Build `local_only/p1b/ps2_netemu_p1b.self` (sha256 `b49e86f2738af08177207be4d1cfe8253139f0ec292a033dc4065d2e6eba2ee8`): repository scan (LV1 91) plus ONE `lv1_open_device` (170) on the optical node, close (171) if it succeeded.

## Observation

- **PROVEN (owner):** after installing P1b and pressing the PS button to open the in-game menu, the PS3 shut itself down. No label was seen.
- The P1a build (same hook, same repository scan, no open) ran the same menu hook on the same console without problems (PROVEN).

## Interpretation

- **INFERRED, not proven:** the `open_device` call is the likely cause (LV1 treating an open of a device this partition may not own as a fatal violation for the partition, powering the console off). The shutdown therefore does not yet answer "denied"; it could also be a bug in how we call it.
- **UNKNOWN alternatives:** (a) a label-table index outside the extended read-only data, producing a fault (the P1b read-only extension is 0x74E930..0x7BB590, about 445 KB; P1a's was about 125 KB), (b) a defect in the new scan or mailbox code that the PC emulation did not reproduce. Stores were audited as stack/mailbox only.

## Next: ablation

Same build with the open/close turned off (compile-time flag), everything else identical (same layout, same tables, same wrappers present but never called). Menu works: the open call is the cause. Still shuts down: the cause is elsewhere. Also exhaustive bounds check of every label-table index over all possible mailbox values.

## Ablation result (console, 2026-10-31)

Build `local_only/p1b_noopen/ps2_netemu_p1b_noopen.self` (sha256 `2cf25e816d128193f4e6e2c530192c5e0e425fa739fe706e2ad4055aa8a71cee`), identical to P1b except that open/close are never called. Label as reported by the owner (no disc inserted):

`p1b done rom=1 open=off close=- rom b=04 d=02 p=0 id=4/2 hdd b=4 d=3 p=2 ph=both op:skip cl:-- rp:-6(fa)`

- **PROVEN (console, one trial each):** the menu works with the open disabled and the console shuts down with it enabled. The only difference between the two builds is the `lv1_open_device` (170) call, so that call is what powers the console off. The oversized-table, `stb` and bounds suspects are cleared by this.
- **PROVEN:** repository ids of the optical node are bus id 4 / device id 2 (bus idx 4, dev idx 2, port 0); the real HDD control is bus 4, dev 3, port 2 (the earlier bus-0 control hit was a different type-0 device).
- **INFERRED (static, bridge at 0xc50..0xca0):** the netemu's guest `sc 0` bridge only checks the call number (< 0x100) and a per-number privilege byte, with no argument filtering, then issues `sc 1`. So the shutdown most likely comes from LV1, not from the bridge. UNKNOWN whether LV1 treats the open as a fatal policy violation for this partition, or the open succeeded and something after it (event/interrupt, unhandled device state) killed the partition.
- Consequence: `lv1_open_device` on the optical node, called the way the stock HDD init calls it for the HDD (flags 0), is not usable from this partition as is.

## Next (options)

1. P1c, read-only: dump every repository field of the optical node and of the HDD node (type, id, port, `meddling`, `blk_size`, `n_blocks`, `n_regs`, interrupts, regions, any other fields) and compare; look for a flag that explains ownership. Same risk as P1a (repository reads only).
2. Static: how ps2_emu / ps2_gxemu call `open_device` on the optical device (flags, preceding calls, what the guest kernel sets up for them) and what differs from the netemu partition.
3. Plan B: external USB DVD drive through the emulator's USB stack, or a CFW/LV1-side change (plan C).
