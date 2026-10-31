# ps2-netemu-disc

Goal: play a PS2 disc straight from the PS3 slim's disc drive through the CFW `ps2_netemu.self`, with no copy to the HDD.

**Status: research and planning. Nothing is built.** It is not known yet whether the slim's drive can read PS2 media or whether the emulator's partition may talk to the drive. See `docs/OPEN_QUESTIONS.md`.

Built on what the [Buzz! Bridge](https://github.com/Gabarsolon/buzz-bridge) project learned about patching `ps2_netemu.self`.

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
