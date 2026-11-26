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
| Netemu partition talks to the drive (open, DMA map, ATAPI commands) | 20% | `██████████` 99.5% |
| Level 1: read sector 16 (ISO9660 signature) | 10% | `████████░░` 80.0% |
| Disc authentication (likely required for any data read) | 15% | `██░░░░░░░░` 15.0% |
| Level 2: emulator disc layer reads from the drive (boot) | 25% | `░░░░░░░░░░` 0% |
| Level 3: playable (read-ahead, CD/DVD, dual layer) | 10% | `░░░░░░░░░░` 0% |
| Level 4: usable (app, stub ISO, configs, no-disc messages) | 10% | `░░░░░░░░░░` 0% |

_Last update: 2026-11-26. 2026-11-26 CONSOLE BREAKTHROUGH (6 probes, all survived, all via netemu's FORWARDED guest-sc bridge li r11,N; oris r11,r11,0x8000; sc 0 -- NO patch A needed): (4) forwarded bridge dispatches from the injected payload and returns the true LV1 value with no A. (5) open_device(4,2,0) on the REAL optical returns 0 (SUCCESS). (6) construct_event_receive_port(18)-&gt;port 38 + connect_interrupt_event_receive_port(197)=0: optical interrupts route to a guest event port. (7a) repository enumerator (FUN_001e9ba0) finds the storage bus (bus 4). (7b) optical dev_id=2, flash dev_id=4: the optical is a DISTINCT repository storage node on the storage bus. So the optical reads via storage_read(245) (forwarded, no A) like flash -- NOT ATAPI send_device_command(248) (direct sc1, needs A). Full read ABI traced (245-&gt;poll 249-&gt;copy; DMA via 174/176 flags 0xe000000000000800). Next: probe 7c = actual storage_read of LBA 16. Stock netemu restored after every probe._
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
