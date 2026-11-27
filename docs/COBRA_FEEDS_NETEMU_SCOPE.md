# Scope: get PS2 disc sectors into the netemu, 2026-11-27

After probes 7q-7u proved the netemu partition can issue ATAPI commands and read
drive **metadata** (GET CONFIGURATION=DVD-ROM, READ CAPACITY=real capacity) but
**READ(10) returns SUCCESS + 0 bytes** (the PS2-disc content gate,
docs/FIRMWARE_ROUTE_READ_CORRECTION.md), this scopes how to actually get disc
content to the emulator.

## Why READ(10) returns no content (root cause)

P0F_SOFTEMU_AND_COBRAUSB.md + CobraUSB symbols: **every PS2 emulator has a
`ps2_disc_auth` function, EXCEPT the netemu has none of the ATAPI /
device-command / disc-auth symbols.** softemu (3.55) symbols:
- `cdvd_send_device_command` 0x88B9C
- `cdvd_send_atapi_command` 0x88C88
- `ps2_disc_auth` 0x8B2BC
- UFS read/open/close/fstat, TOC

The drive serves metadata but withholds user-sector content until a PS2-specific
**disc authentication** handshake runs. The netemu never performs it (no such
code), so READ(10) silently returns 0 bytes. softemu DOES perform it and reads
physical PS2 discs (owner's video: softemu 4.01 on a slim played physical PAL
discs).

## Two routes to feed sectors

### Route A (RECOMMENDED): port softemu's disc-auth into the netemu probe
The netemu probe (firmware_probe1) already sends ATAPI via
`lv1_send_device_command` and gets metadata back. The ONLY missing piece is the
auth command sequence the drive expects before READ(10). softemu's
`ps2_disc_auth` (0x8B2BC) + `cdvd_send_atapi_command` (0x88C88) contain exactly
that sequence (CDBs / challenge-response). Reverse them from the decrypted ELF
(`local_only/fw355/out/ps2_softemu.elf`), replay the same CDBs from the netemu
probe before READ(10), then re-test whether READ(10) delivers content. This is
the direct "straight from the drive" path and keeps all work inside the netemu
partition (no LV2/Cobra dependency during PS2 mode).

### Route B: external sector source (Cobra / HDD / network)
"Cobra-feeds-netemu" literally (Cobra serving `/dev_bdvd` to netemu during play)
is blocked: at PS2 launch LV2/GameOS is torn down for `PS2_NE_LPAR`, so Cobra is
not running to serve reads; in PS2 mode only HDD and network are reachable
(DISC_READ_WALL.md). The non-firmware fallback is to stage the disc to an
HDD/network ISO and launch that through the netemu's proven UFS file path
(`0x1ed5cc`) / dispatcher `0x1359d4` (context byte +0x32 picks UFS vs Cobra
container) — but that is a copy, against the "straight from drive" goal. Keep as
fallback only.

## Plan (executing)

1. Decompile softemu `ps2_disc_auth` (0x8B2BC), `cdvd_send_atapi_command`
   (0x88C88), `cdvd_send_device_command` (0x88B9C), reply reader (0x8AE28).
   -> `local_only/softemu_auth_decomp.txt`.
2. Extract the exact ATAPI auth CDB sequence and any challenge-response /
   key handling.
3. Port the sequence into a new probe (7v) issued via the proven
   `run_atapi` before READ(10).
4. Console-test: does READ(10) then return real sector content (byte0=0x01
   "CD001" at LBA 16)? Verify with the LBA-variance + buffer-leftover controls
   learned in 7t/7u.
