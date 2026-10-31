# Starter prompt for a new chat

Start Claude Code in `C:\Users\remus\ps2-netemu-disc` (so CLAUDE.md loads) and paste:

```
New project: make the PS3 slim's PS2 emulator (ps2_netemu.self, CFW Evilnat 4.93 + Cobra) play a PS2 disc straight from the disc drive, no copy to the HDD.

This repo was set up from the Buzz! Bridge project, where we already patched ps2_netemu.self (four real buzzers + lamps, v1.3.0) and proved the whole hook/build/sign/install/test pipeline on my console.

Read, in order: CLAUDE.md, docs/NETEMU_KNOWLEDGE.md, docs/GOAL_AND_PLAN.md, docs/OPEN_QUESTIONS.md, docs/TOOLING_AND_WORKFLOW.md. Follow CLAUDE.md rules (never run installers or write to the PS3 yourself, never touch my ISOs, Sony files stay in local_only/, ask before risky experiments, test once then hand over).

Key fact: while a PS2 game runs, LV2 (Cobra/webMAN) is gone; the emulator is an LV1 guest, so it must read the drive itself. First goal is P0: find out if this is possible at all.
1. pyghidra on the stock netemu: LV1 hypercall sites, how the UFS reader opens the HDD, any optical/drive references, how the CDVD layer uses the file size and sector reads.
2. Plan a PS3 homebrew probe (PS3DK) that reads sector 16 + media info from the drive with a PS2 disc inserted.
3. Research proven patterns (Linux ps3rom, webMAN MOD, Cobra, psdevwiki, psx-place) before inventing anything; use Codex/agy for heavy work as described in CLAUDE.md.

Start by telling me what you will do for P0 and what you need from me (e.g. the stock netemu read over FTP, a PS2 disc for the probe). Short answers please.
```
