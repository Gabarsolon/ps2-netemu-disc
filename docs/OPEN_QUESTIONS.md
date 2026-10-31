# Open questions (ranked by what they unlock)

All UNKNOWN until settled. For each: why it matters, how to settle it, who/what does it.

## R1. Does the slim's drive read PS2 media at the sector level? (blocks everything)
- PS2 discs are ordinary CD-ROM or DVD-ROM (single or dual layer) media with PS2-specific markers. The PS3 XMB does not play them on a slim, but that may be software policy and not a drive limit.
- Settle: PS3DK homebrew probe on the PS3 (LV2): `sys_storage_open(BD device)` then `sys_storage_read` of sector 16 and a GET CONFIGURATION / READ CAPACITY, with a PS2 DVD and a PS2 CD inserted. Log return codes. Also try webMAN's `/dev_bdvd` view with a PS2 disc. Compare with a PS3 game disc to see the baseline.
- Research: PS3 Linux `ps3rom`, disc dumper tools, forum reports about PS2 discs in slim drives.

## R2. Can the emulator's partition open the drive through LV1? (blocks the in-emulator reader)
- LV1 hands a partition only the devices in its resource list. The emulator already uses LV1 storage for the HDD (its UFS reader). Whether a BD device id is in its list is unknown.
- Settle: pyghidra analysis of how the UFS reader opens the HDD (hypercall numbers, device id source, repository/resource lookup), then a label-only netemu probe (P1) that attempts the open and shows the return code.
- Related claim (kozarovv, psx-place): the "Memory Dumper Mod" netemu can use all hypervisor calls: shows the partition may issue arbitrary hypercalls; it does not prove it may open the drive.

## R3. How does the emulator model the CD/DVD drive? (shapes the backend)
- Where does it take sector size, media type (CD vs DVD), total size, layer break, and the "disc present / tray" state? Does it need TOC/CDDA info? How does it react to a failed or slow read (retry, error to the guest, hang)?
- Settle: trace the CDVD emulation code from the read layer up (callers of `0x3CFC` read, `0x1ED5CC`; the `stat` size users); PPC64 emulation harness (`reference/buzz-netemu-build/gh_harness.py`) with fake read callbacks of various lengths and delays.

## R4. How long can a read block? (read-ahead design)
- PS2 games stream; a DVD seek is ~100-200 ms. If the emulator's read call is synchronous and its thread also runs emulation, a slow read stalls the game.
- Settle: measure on the PC harness how the emulator behaves with delayed reads (is the reader on its own thread?), then design a read-ahead cache in the 1,792-byte-style allocator arena (size it much larger; check the pool limits at `0x934980` / `0x24565b8`).

## R5. Launch flow (stub ISO)
- webMAN starts the emulator for a mounted ISO path; it may read SYSTEM.CNF from the image for the game id or `.CONFIG` lookup before launch. A stub must satisfy whatever LV2 reads.
- Settle: inspect what webMAN MOD does for PS2 ISO launch (source: github.com/aldostools/webMAN-MOD, `mount.h`/ps2 sections) and what the emulator receives (the path string and where). Prototype with a tiny stub ISO that already contains a valid SYSTEM.CNF.

## R6. Disc-specific details
- Dual-layer: logical addressing is linear across layers for READ(10); confirm with a DVD-9 and what the emulator expects as the size.
- CD-ROM mode 2: user data should come back as 2048 bytes; confirm with a CD game. Audio tracks (CDDA) in games.
- Anti-copy checks on original discs vs dumped ISOs: the emulator was built for ISOs, so likely fine; confirm with several titles (Buzz! Schools Quiz original disc is available to the owner? ask).

## R7. Error handling and safety
- Every drive command needs a hard timeout and a bail-out. What does the emulator do if the disc is removed mid-game? Must not hang the console. Test the unplug/eject cases on the PC harness first, then the console.

## R8. Plan B feasibility: USB DVD drive through the emulator's USB stack
- Does the emulator's USB layer support bulk endpoints and can our payload add a mass-storage reader? We have used control transfers (`0x5F08C -> 0x85538`, submit boundary `0x83060`) and interrupt-in completions (`D19AC`, `D15CC`); bulk is untouched.
- Settle after R1/R2 if they fail: analysis of the USB submit API and the PC harness.

## R9. CFW-side options (Plan C)
- Could a CFW change give the PS2 partition the BD device at PS2 launch? Look at how the CFW (Evilnat/Cobra) already patches the PS2 launch path (the Cobra payload is embedded in the emulator, which suggests the CFW works by patching the emulator file itself). Probably out of scope.

## R10. Where is the existing knowledge outside this repo?
- psdevwiki "PS2 Emulation" and "PS2 Netemu" pages; kozarovv's and 3141card's posts on psx-place (netemu patches, hypervisor access); Predator0808's emulator-mods thread; the Cobra source (COBRA-7-3 on GitHub, `ps2` and `storage` sections); PS3 Linux sources (ps3-storage, ps3rom). Note psx-place blocks automated fetches (HTTP 403), but `curl -A "<browser UA>"` worked for fccid.io and may work elsewhere; the user can paste pages.
