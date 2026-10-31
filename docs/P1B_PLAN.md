# P1b plan: is the netemu partition ALLOWED to open the optical device? (open + close only)

Labels: PROVEN / INFERRED / UNKNOWN. Nothing here is built or tested yet.

## Question
P1a (PROVEN, console): the repository seen from the ps2_netemu partition has an optical node (type 5) at bus index 4, device index 2, port 0, on the same storage bus index (4) as the netemu's HDD. Visible is not permitted. P1b answers: does `lv1_open_device(bus_id, dev_id, flags=0)` (LV1 call 170) on that node succeed from this partition? If yes the partition owns the drive and the in-emulator reader is feasible; if `LV1_DENIED_BY_POLICY` / `NO_PRIVILEGE` / `ACCESS_VIOLATION`, the route needs LV1/CFW changes (or plan B).

## Design (extends the P1a build; P1a stays reproducible, build in a NEW dir)
1. Copy `netemu/` to `netemu_p1b/`; output `local_only/p1b/ps2_netemu_p1b.self`. Start from the STOCK file again (not from P1a).
2. Same lazy once-only trigger as P1a (first PS-button menu row hook after boot), same bounded repository scan (LV1 91 only), same mailbox `0x930F20..0x930F80`.
3. After the scan: if exactly >= 1 ROM device was found, take the 64-bit bus id and device id read from the repository for the FIRST ROM device (the P1a probe already reads `bus/b/id` and `bus/b/dev/d/id`; use exactly those values, do not construct ids) and issue ONE `open_device` (170) with flags 0 through the stock guest-to-LV1 wrapper that the netemu's own HDD init uses (call site near `0x12bf8c`; verify in the stock ELF, find the wrapper function for r11=0xaa, use its exact calling sequence). Record the raw return code (signed 64 and low 32 bits). If rc == 0: ONE `close_device` (171) through the stock wrapper (call near `0x12d610`, verify), record its rc. Never retry. Never call any other LV1 number (only 91, 170, 171). No event port, no DMA, no interrupt, no storage read, no device command.
4. HDD control done right: also record the netemu's own HDD the way stock finds it (bus index 4, first type-0 device with port 2: scan bus 4 only for type 0 and port 2) so page C shows the real HDD (expected: bus 4, dev 0, port 2), to prove the lookup is valid. Do NOT open the HDD (stock already owns it).
5. Show the 64-bit bus id and dev id of the optical node on the labels (byte pages, `B3=7F` style or hex nibbles), plus the open rc and close rc: pages: A summary (`P1B DONE rom=<n> open=<ok/denied/err> close=<ok/-/err>`), B optical node idx/port and ids, C HDD control, D raw rc values (open, close, first repository error).
6. Fail-open: any expected original word mismatch aborts the build; at run time on any inconsistency do nothing.

## Worst cases
- `open_device` on a device the partition does not own returns an error code (harmless, the expected "no" answer).
- If it succeeds and `close` is skipped/fails the device stays claimed until the partition ends (PS2 game exit); bounded impact (PS2 mode only; the XMB/LV2 reclaims the drive on return).
- A hung or panicking hypercall powers off or reboots the console. Mitigation: only the exact stock calling sequences; PC emulation of the real code with fake return codes; strict store audit (stores only into the mailbox or stack).
- Restore with `tools/restore_netemu.ps1`.

## Owner test
Install with `tools/install_netemu.ps1 -File local_only/p1b/ps2_netemu_p1b.self -Force`; start any PS2 ISO from webMAN; PS-button menu; `Debug Information` row; photograph pages A-D; restore.
