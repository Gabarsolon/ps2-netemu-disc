# P1a plan: can the netemu partition SEE the optical drive? (repository lookup only)

Labels: PROVEN / INFERRED / UNKNOWN as elsewhere. Nothing here is built or tested yet.

## Question
Does the LV1 repository, as seen from the ps2_netemu partition, contain an optical (ROM, device type 5) storage device node? This is read-only: LV1 call 91 (`lv1_get_repository_node_value`) only. No `open_device` (170), no storage read, no drive command. If the node is absent, the whole in-emulator route is dead without CFW/LV1 changes (Plan C), and we learn it with almost no risk.

## Why this is the right first step (INFERRED from P0 / P0D)
- Netemu already enumerates its HDD this way: `0x12be04` init, key encoder `0x111f6c`, repository helper `0x111eb8` (LV1 91 at `0x111f10`), enumerator `0x114ea4(bus_index=4, dev_index=0, info, type=0, port=2)` which reads `bus/dev/id/type/port/blk_size/n_blocks/n_regs`.
- The phat emulators (`ps2_emu` `fn_00022138` = LV1 248 wrapper at `0x221f8`) do the same repository lookup with a different type selector. Their exact selectors are in `docs/P0D_PHAT_EMU_ANALYSIS.md` (verify them, do not trust the flash-model write-up blindly).
- Linux reference (CLAIMED/INFERRED): storage bus type 5, DISK device type 0, ROM device type 5, FLASH 14. LV2's BD id `0x0101000000000006` is an LV2 id, not necessarily the LV1 bus/dev id.

## Design
1. **When to run:** once, lazily, the first time the PS-button menu row hook (`0x270FFC`, label `Debug Information` at `0x304EC0`) is exercised after boot (flag in the RW mailbox says "done"). Avoids startup timing issues; the repository is long since initialized by then. Bounded: at most 16 bus indexes x 16 device indexes.
2. **What it does (only these LV1 calls: 91):** for bus index 0..15 and device index 0..15, read `bus/N/dev/M/type` (+ `id`, `port`, `bus` ids) through the existing helper (`0x111eb8`) or a direct wrapper copy; record for each hit the device type; for every device with type 5 (and also record types 0, 14 hits for comparison) store bus_id, dev_id, port, blk_size, n_blocks if readable. All return codes recorded.
3. **Where results live:** RW mailbox `0x930F20..0x930F80` (proven RW), or an arena from allocator `0xB9848` like the Buzz build. Never write outside proven RW ranges (store audit on PC).
4. **How we read it:** labels, as in the Buzz work: immutable strings chosen by RW state, pages selected by `selected & 3`. Pages: (A) summary: `P1A DONE n=<devices> rom=<count>`, (B) first ROM device: bus_id/dev_id/port bytes `B3=7F` style, (C) HDD comparison (known-good: type 0 found), (D) error codes of failed lookups.
5. **Fail-open:** if any expected original word at a hook site differs, do nothing and let stock behavior run. The probe must never loop unbounded, never block, never touch game behavior.
6. **Control:** the HDD device must be found the same way as a sanity check (if our own enumeration cannot find the HDD, the probe is wrong, not the console).

## Worst cases
- A wrong hypercall argument/number returns an LV1 error code (harmless) or, rarely, panics the partition (PS3 powers off or reboots to XMB). Mitigation: only call number 91 with the exact calling sequence the stock code uses; PC emulation of the real code before shipping.
- A store into read-only memory powers the PS3 off (PROVEN rule): store-target audit.
- Bad file: restore with `tools/restore_netemu.ps1` (works without the emulator running; no console restart needed).

## Deliverables of the build task
`netemu/` (copied pipeline from `reference/buzz-netemu-build/`, adapted), the probe payload source, PC test results (emulation with a fake repository returning (a) an optical node, (b) no optical node, (c) errors; store audit; SELF round trip), the built SELF in `local_only/p1a/` (never git), `docs/P1A_RESULT_TEMPLATE.md` (how to read the labels), and the exact owner test steps. Nothing is installed by us: the owner runs `tools/install_netemu.ps1` and `tools/restore_netemu.ps1` (parse-check only).

## Owner test (after a build exists)
Install, start any PS2 game from webMAN, open the PS-button menu, open the `Debug Information` row, photograph pages A-D (I read them over adb), restore. One pass, then hand back.
