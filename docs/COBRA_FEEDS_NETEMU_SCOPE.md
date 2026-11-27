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

## Decompile findings (softemu 3.55, local_only/softemu_auth_decomp.txt + _callers.txt)

- `ps2_disc_auth` (0x8B2BC) builds an internal CDVD message (magic `0xface`,
  type `0x5000`/`0x5005`, params at +0x38/+0x39/+0x40) and enqueues it via
  `FUN_00042c74(10, block, 0x70)`. `0x42c74` is a tiny `syscall(1)` enqueue loop,
  NOT the ATAPI itself.
- Caller `FUN_0022130c` is the **PS2 disc auth** logic: `ps2_disc_auth(handle, 0,
  arg, 0x4b)` -> command **0x4b**. It then reads a reply whose status byte (+0x38)
  bits 4/2/1 flag which **16-byte key regions** (+0x40/+0x50/+0x60) the drive
  returned, byte-reverses 8-byte chunks, and **XOR-descrambles 5 bytes of each
  key region with a TBLr (time-base) derived byte**. This is a **cryptographic
  disc-key exchange**, i.e. the PS2 copy-protection auth.
- `cdvd_send_atapi_command` (0x88C88) / `cdvd_send_device_command` (0x88B9C) are
  the transport (LV1 `syscall(1)` send + `syscall(0)` poll, LV1 248 class). The
  auth (0x4b) does NOT go through a raw 248 ATAPI CDB; it is the softemu's
  internal CDVD command processed by a worker that talks to LV1 / **ss_server3
  secure module** (which holds the disc keys; the ss_server3 "PS2 Drive Auth"
  sites 0x165B54/0x165CD0 found in LV1 are this).

## Why the netemu can't just replay it (PROVEN + INFERRED)

- Metadata ATAPI commands via LV1 248 WORK from the netemu partition (INQUIRY,
  GET CONFIGURATION=DVD, READ CAPACITY) — PROVEN (7r-7u).
- READ(10) media content is withheld (SUCCESS + 0 bytes) because no PS2 disc
  auth was performed — PROVEN (7u). ss_server3 being STOCK does not help: the
  netemu never TRIGGERS the auth (7s/7u with A+B stock identical).
- The auth is a secure key exchange done by ss_server3, not a replayable raw
  ATAPI CDB. INFERRED: the netemu cannot perform it without the softemu's CDVD
  auth subsystem and/or the secure module's keys.

## Options (honest)

- **A. Reproduce the LV1 secure disc-auth call from the netemu** — requires
  finding the exact LV1 hypercall the softemu worker issues for command 0x4b and
  whether it needs secure-module keys. Deep; possibly blocked by key access.
- **B. Run ps2_softemu itself** (it already auths + reads physical PS2 discs) —
  hurdle: the obtained softemu is 3.55-signed; the console is 4.93. Version /
  signature acceptance under Cobra is UNKNOWN.
- **C. Stage disc -> HDD ISO, launch via netemu's proven UFS path** — works but
  is a copy, against the "straight from drive" goal. Fallback only.

## Most tractable next experiment

Trace the softemu CDVD **worker** that dequeues the `0xface` message and
dispatches command 0x4b, to find the exact LV1 hypercall + whether it reaches a
replayable storage op or a secure-key op. That single answer decides whether
option A is feasible. (Targets: who reads globals -0x5858 / -0x5848 / -0x5830;
the worker thread entry.)
