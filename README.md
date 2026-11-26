# ps2-netemu-disc

Goal: play a PS2 disc straight from the PS3 slim's disc drive through the CFW `ps2_netemu.self`, with no copy to the HDD.

**Status: research and diagnostic builds on the real console.** The patched netemu can already open the optical drive, map DMA and run ATAPI commands (it reads the real disc size) from inside the PS2 partition. It cannot read sector data yet. Nothing playable exists. Every result is written up in `docs/` (labels PROVEN / INFERRED / CLAIMED / UNKNOWN).

Built on what the [Buzz! Bridge](https://github.com/Gabarsolon/buzz-bridge) project learned about patching `ps2_netemu.self`.

<!-- progress:start -->
## Progress

![Project progress 40%](docs/progress.svg)

**Overall: about 40%** (effort-weighted estimate; the real risk is not evenly spread).

| Stage | Weight | Done |
|---|---:|---|
| Patch / install / test pipeline and durable HDD log | 10% | `██████████` 100% |
| Netemu partition talks to the drive (open, DMA map, ATAPI commands) | 20% | `██████████` 99.8% |
| Level 1: read sector 16 (ISO9660 signature) | 10% | `████████░░` 80.0% |
| Disc authentication (likely required for any data read) | 15% | `██░░░░░░░░` 15.0% |
| Level 2: emulator disc layer reads from the drive (boot) | 25% | `░░░░░░░░░░` 0% |
| Level 3: playable (read-ahead, CD/DVD, dual layer) | 10% | `░░░░░░░░░░` 0% |
| Level 4: usable (app, stub ISO, configs, no-disc messages) | 10% | `░░░░░░░░░░` 0% |

_Last update: 2026-11-26. 2026-11-26 probe 7d/7e: the FULL optical read chain runs on console and SURVIVES (open(4,2,0)=0 -&gt; allocate_device_dma_region(174)=0xc0000000 -&gt; map_device_dma_region(176) -&gt; storage_read(245) -&gt; poll get_async_status(249)), all forwarded sc0, no patch A. BLOCKER: map(176) returns -17 = LV1_ILLEGAL_PARAMETER_VALUE (size 0x100000 ruled out in 7e). Cause: the DMA target buffer must be PAGE-ALIGNED (0x1000) guest-physical, but the 8KB owned block (base 0x80022440, unaligned) cannot host a page-aligned 2KB+ buffer clear of the integrity-checked command/data patterns that gate snapshot delivery. FIX (probe 7f): dedicated page-aligned DMA buffer -- enlarge the owned allocation (N 0x2000-&gt;0x4000, DMA page at (alloc+0x2000)&amp;~0xfff, past the patterns) or a separate page-aligned region. map(176) arg order proven: r3=bus,r4=dev,r5=lpar_addr(page-aligned),r6=dma_region,r7=size,r8=flags 0xe000000000000800._
<!-- progress:end -->

The progress block above is generated: edit `docs/progress.json` (or run `python -I tools/update_progress.py --note "..." --set "Level 1=50"`) after every iteration, then commit and push.

## Read in this order

1. `AGENTS.md`: rules and workflow (also for any AI helper)
2. `docs/NETEMU_KNOWLEDGE.md`: what we know about the emulator file
3. `docs/GOAL_AND_PLAN.md`: phases and fallback routes
4. `docs/OPEN_QUESTIONS.md`: what must be settled first
5. `docs/TOOLING_AND_WORKFLOW.md`: how to analyze, build, validate, test
6. `docs/NEW_CHAT_PROMPT.md`: starter prompt for a fresh chat

## Layout

- `experiments/`: all netemu build variants, keeping their original names
  (`netemu`, `netemu_p16`, `netemu_disc`, and earlier diagnostics).
- `reference/`: working Buzz! netemu build, test and installer sources (templates)
- `tools/`: `install_netemu.ps1`, `restore_netemu.ps1` (any build, hash-verified, backups)
- `local_only/`: stock/modified SELFs, ELFs, logs (gitignored; Sony-derived files never go in git)

On 2026-11-22 the 27 root netemu directories moved under `experiments/`.
Historical commands in older notes need that prefix, for example
`python experiments/netemu_p16/build.py`. Build and validation scripts were
updated for the new location. No experiment contents were discarded.

## Current work and console power

Resume the physical-disc investigation with the owner's inserted TDU disc
(`SLES_544.66`, PAL). Boot from the physical drive remains **UNKNOWN**.
The prior Buzz ISO is a diagnostic carrier/control, not evidence of disc boot.
Read the P16/P17 evidence before accepting P18's stronger authentication claims.

The Bluetooth backend, smart-plug tests, PowerOnReset change, hardware wake
options, and research corrections are recorded in
[PS3_BLUETOOTH_WAKE.md](docs/PS3_BLUETOOTH_WAKE.md).
A controller-free Buzz carrier returned cleanly to XMB in one test; see
[AUTOMATIC_RETURN_CONTROL.md](docs/AUTOMATIC_RETURN_CONTROL.md). This
does not establish physical-disc boot or recovery from a hung worker.
A subsequent control retrieved a fresh HDD snapshot and returned cleanly; see
[AUTOMATIC_SNAPSHOT_CONTROL.md](docs/AUTOMATIC_SNAPSHOT_CONTROL.md).
Normal-standby Bluetooth wake works; abrupt-cut wake does not work in the
tested state. The saved PowerOnReset flag remains 1, without demonstrated
automatic startup. A confirmed hard freeze may be recovered by one smart-plug
power cycle; the owner then presses the PS3's physical power button.

Own console, own discs, CFW only. No game data or firmware files are included.
