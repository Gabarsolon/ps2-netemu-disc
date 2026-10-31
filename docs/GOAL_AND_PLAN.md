# Goal and plan

## Goal

Put a PS2 disc in the slim PS3's drive, start it, and the modified `ps2_netemu` plays it **straight from the disc**, with no copy to the HDD. CFW only (Evilnat 4.93 + Cobra on a CECH-25xx slim, no PS2 hardware).

Success levels:

1. **Read proof:** from inside the emulator, read sector 16 of the inserted disc and show it (the ISO9660 volume descriptor `\x01CD001`) on the debug label.
2. **Boot:** a real PS2 disc boots to its title screen from the drive.
3. **Playable:** a full game session with no stutter worse than from an HDD image (needs read-ahead).
4. **Usable:** a one-step launch from the XMB or the PS3 app, a clear message with no disc or an unreadable one, safe eject.

## Starting point (what the Buzz! Bridge work gives us, all PROVEN)

- We can patch, rebuild, sign, install and restore `ps2_netemu.self`, and test on the real console with label diagnostics (`docs/NETEMU_KNOWLEDGE.md`).
- The emulator reads images through a small file layer that we have already hooked (`open` / `stat` / `read` returning 2048-byte sector data). A disc backend can sit exactly there.
- It has its own storage stack (a UFS reader for the HDD) that works without the normal PS3 OS. What the disc needs from that stack is the open question.

## The hard part (and why this is not just a hook)

When a PS2 game runs, the normal PS3 OS (LV2, where Cobra, webMAN and the drive drivers live) is **not loaded**. The emulator runs as its own guest system on LV1. So the disc has to be read **by the emulator's own code**, talking to the drive through LV1, the way the emulator already talks to the HDD. Nothing in LV2 can help once the game runs.

Open feasibility questions (details in `OPEN_QUESTIONS.md`):

- Can the slim's drive read PS2 CD/DVD media at the sector level at all? (UNKNOWN; the XMB refuses PS2 discs, but that may be a software policy.)
- Is the drive visible to the emulator's partition? LV1 gives each partition only the devices its configuration lists. (UNKNOWN; the emulator already uses LV1 storage for the HDD, and a kozarovv note says the "Memory Dumper" modded emulator can use all hypervisor calls, CLAIMED.)
- If not visible, can a CFW (LV2-side) change give the PS2 partition the drive? (UNKNOWN, riskier, a CFW-developer-level task.)

## Phases

Each phase ends with an exact test for the owner; do not skip ahead.

**P0, no emulator changes, safe: find out whether it is possible.**
- Static analysis (pyghidra) of the stock netemu: find every LV1 hypercall site (`sc` with the LV1 convention), the storage open/read path used by the UFS reader at `0x1ED5CC`, the device identifiers it opens, and what it does with them. Also look for any existing drive/optical references. Output: where a second device could be opened, and which hypercalls (`lv1_storage_open`, `lv1_storage_read`, `lv1_storage_send_device_command`, ...) the file already contains wrappers for.
- A tiny PS3 homebrew probe (PS3DK, template: the PS3 app in `C:\Users\remus\ps3buzz-console\buzzbridge_app`) that, with a PS2 disc inserted, tries to read sector 16 and the media info from the drive through LV2 (`sys_storage_open` on the BD device, `sys_storage_read` / device command), and logs the result codes. This answers "does the drive read PS2 media at all", independent of the emulator. Source patterns to copy: ps3dev wiki, PSL1GHT, PS3 disc dumper homebrew; do not invent.
- Research (agy/Codex): how PS3 Linux (`ps3rom`, `ps3stor`), `ps3-disc-dumper`-style tools and webMAN talk to the drive; what the drive refuses (media type, authentication); whether any report exists of PS2 discs readable on a slim.

**P1, label-only emulator probe: can the emulator's partition open the drive?**
- A netemu build (fail-open, like the Buzz builds) that tries the LV1 storage open for the drive's device id once at startup and shows the return code on the `Debug Information` label. No reads yet if opening fails; no change to game behavior either way.

**P2, read proof:** read sector 16 and the media size through the LV1 path, compare to the PVD signature, show it on the label.

**P3, disc backend:** serve the emulator's `open/stat/read` from the drive for a marker image, with:
- a read-ahead cache in allocator-owned RAM (PS2 games stream; a drive seek is ~100+ ms and the emulator's read is synchronous: check how long the emulator tolerates a blocked read),
- correct `stat` size (READ CAPACITY; dual-layer discs read linearly by LBA),
- strict bounds and a timeout on every drive command (a hung drive must not hang the console), automatic fallback to "disc not readable" instead of a hang.

**P4, launch flow and UX:** the emulator is started by webMAN from a mounted ISO path, so use a small **stub ISO** (placed once in `/dev_hdd0/PS2ISO`, recognized by hash/name) as the "disc" marker: when the emulator opens it, our hook routes reads to the real drive. Add a "Play PS2 disc" entry to the Buzz!-Bridge-style PS3 app (or webMAN) that starts it. Messages for no disc / bad disc / eject.

**P5, polish and release:** installer/restore scripts (reuse `reference/installer-scripts`), docs, honest tested / untested list per game and per disc type (CD vs DVD, single vs dual layer).

## Alternative routes if P1 says no

- **B, USB DVD drive:** the emulator has its own USB host stack (it already drives our Buzz dongle, including SET_REPORT through `0x5F08C`). A bulk-only mass-storage class reader inside the emulator (SCSI READ(10)) for an external USB DVD drive might avoid the LV1 device-assignment problem. Uses much more of the USB layer than we have touched; the drive would be external, not the PS3's own. Also check whether PS2 discs read fine in a plain PC DVD drive (they should).
- **C, CFW-side change** so the PS2 partition is given the drive (an LV2/LV1 repository change at PS2 launch). Highest effort and risk; needs expertise in the CFW's launch path; only after A and B are ruled out.
- **D, fast dump to HDD** (the thing the owner does not want): out of scope, but a diagnostic fallback for comparing behavior.

## Risks

- Writing the emulator file is low risk (restore works, no restart needed); a wrong LV1 hypercall from our code is the new risk (could hang or reboot the console). Every drive call needs a bounded timeout and a plan to bail out; start with read-only, open-only probes.
- Legal: owner's own discs, a patched Sony firmware file never goes into git; releasing it is the owner's decision per release.
- Scope: PS2 disc formats vary (CD-ROM mode 2, DVD-5/9, CDDA audio tracks, copy-protection games). Expect a long tail.
