# ps2-netemu-disc

Goal: play a PS2 disc straight from the PS3 slim's disc drive through the CFW `ps2_netemu.self`, with no copy to the HDD.

**Status: research and diagnostic builds on the real console.** The patched netemu can already open the optical drive, map DMA and run ATAPI commands (it reads the real disc size) from inside the PS2 partition. It cannot read sector data yet. Nothing playable exists. Every result is written up in `docs/` (labels PROVEN / INFERRED / CLAIMED / UNKNOWN).

Built on what the [Buzz! Bridge](https://github.com/Gabarsolon/buzz-bridge) project learned about patching `ps2_netemu.self`.

<!-- progress:start -->
## Progress

![Project progress 32%](docs/progress.svg)

**Overall: about 32%** (effort-weighted estimate; the real risk is not evenly spread).

| Stage | Weight | Done |
|---|---:|---|
| Patch / install / test pipeline and durable HDD log | 10% | `██████████` 100% |
| Netemu partition talks to the drive (open, DMA map, ATAPI commands) | 20% | `██████████` 95% |
| Level 1: read sector 16 (ISO9660 signature) | 10% | `████░░░░░░` 35% |
| Disc authentication (likely required for any data read) | 15% | `░░░░░░░░░░` 0% |
| Level 2: emulator disc layer reads from the drive (boot) | 25% | `░░░░░░░░░░` 0% |
| Level 3: playable (read-ahead, CD/DVD, dual layer) | 10% | `░░░░░░░░░░` 0% |
| Level 4: usable (app, stub ISO, configs, no-disc messages) | 10% | `░░░░░░░░░░` 0% |

_Last update: 2026-11-01. ATAPI reads (PIO and DMA) of sector data return success with no data on both the PS2 DVD and a PS3 control disc: the drive/hypervisor most likely withholds media data until the disc authentication is done (the secure service softemu calls). Next: how to reach that service from the netemu partition._
<!-- progress:end -->

The progress block above is generated: edit `docs/progress.json` (or run `python -I tools/update_progress.py --note "..." --set "Level 1=50"`) after every iteration, then commit and push.

## Read in this order

1. `CLAUDE.md`: rules and workflow (also for any AI helper)
2. `docs/NETEMU_KNOWLEDGE.md`: what we know about the emulator file
3. `docs/GOAL_AND_PLAN.md`: phases and fallback routes
4. `docs/OPEN_QUESTIONS.md`: what must be settled first
5. `docs/TOOLING_AND_WORKFLOW.md`: how to analyze, build, validate, test
6. `docs/NEW_CHAT_PROMPT.md`: starter prompt for a fresh chat

## Layout

- `reference/`: working Buzz! netemu build, test and installer sources (templates)
- `tools/`: `install_netemu.ps1`, `restore_netemu.ps1` (any build, hash-verified, backups)
- `local_only/`: stock/modified SELFs, ELFs, logs (gitignored; Sony-derived files never go in git)

Own console, own discs, CFW only. No game data or firmware files are included.
