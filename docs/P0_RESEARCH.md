# P0 research: optical access and PS2 launch

**Verdict — INFERRED:** a slim reading original PS2 DVD sectors is plausible: there is a concrete CECH-2101A ripping report and an existing LV1 optical-driver pattern. **UNKNOWN:** whether this owner's CECH-25xx reads the required sectors, whether PS2 CDs work, and whether netemu's LV1 partition can open the optical device. Neither a successful LV2 read nor unrestricted hypercall dispatch proves that partition's device access. Stock/Cobra netemu has no implemented optical backend in the sources examined; that is a software limitation, not evidence of an optical-hardware impossibility.

Research date: 2026-10-31. Labels follow `NETEMU_KNOWLEDGE.md`: **PROVEN** requires an actual local check or execution; **INFERRED** is a conclusion from inspected source; **CLAIMED** is an external statement; **UNKNOWN** remains untested. Source-code observations below are **INFERRED**, not console results. Addresses and control flow of the owner's ELF belong in `P0_STATIC_ANALYSIS.md`.

## What was checked locally

**PROVEN:** the five briefing files were read in the requested order. Public web browsing was available. No request was sent to the console; no disc, ISO, game, installer or PS3 application was accessed or run. Source pages were inspected through web access. Shell HTTPS access failed at connection establishment, including a browser-User-Agent `curl.exe` attempt against PSX-Place; this was not an observed HTTP 403. Some web pages were also unavailable or returned no readable body.

**PROVEN:** an existing public-source copy at `C:\Users\remus\ps3buzz-console\game_logger\sources\cobra_storage_ext.c` was read without editing it. Its launch logic agrees with the fetched Cobra source in the important respects described below, but its exact upstream revision was not established. No downloaded or copied Sony code was created for this research.

## Physical PS2 discs on slim models

**CLAIMED:** PSDevWiki describes netemu as “The only emulator not able to run physical media in any capacity”. The same page says the emulators run as LV1 guests after LV2 unloads. Its syscall documentation describes hypercalls dispatched through `0x800000XX`, a normal whitelist, and CFW patches allowing numbers 0–255. Guest syscall 18 is described as an ENCDEC decryption operation for selected emulator threads, using device 0 and command `0x88`; it is not identified as optical I/O. These are wiki descriptions, not measurements on the owner's console. [PSDevWiki, PS2 Emulation](https://www.psdevwiki.com/ps3/PS2_Emulation)

**CLAIMED:** Dogman1227 identifies a **CECH-2101A** in the January 2024 thread below. Initially PS2 ripping failed while PS3 ripping worked; in post #3 the author reports resolving PS1/PS2 ripping by switching from mmCM to normal multiMAN. This is a useful slim-model success report. It supplies neither a sector dump nor disc identifiers, and does not establish a separate PS2 CD test. Quote: “then, you can rip the ps1 and ps2 isos.” [PSX-Place, Read Error PS2 disc on multiMAN/PS1 ripping ridiculously slow](https://www.psx-place.com/threads/read-error-ps2-disc-on-multiman-ps1-ripping-ridiculously-slow.42632/)

**CLAIMED:** kozarovv's May 2017 announcement attributes a netemu modification to 3141card with “full hvcall support, and option to dump lv1 from inside netemu.” The thread also contains 3141card's report of temperature queries through the LV1 system-manager proxy. Neither claim demonstrates BD-device assignment or storage permissions. No linked emulator binary was downloaded. [PSX-Place, ps2_netemu now with full hvcall support & lv1 dumper by 3141card](https://www.psx-place.com/threads/ps2_netemu-now-with-full-hvcall-support-lv1-dumper-by-3141card.13912/)

**CLAIMED / limitation:** Predator0808's emulator-mod release thread documents fan/temperature/display work; no read-sector result for a PS2 optical backend was found in the inspected material. It supplies useful emulator-development context, not feasibility proof. [PSX-Place, emulators modded by Kozarovv](https://psx-place.com/threads/release-ps2_emu-gxemu-and-netemu-modded-by-kozarovv-fan-control-cell-rsx-temps-fps-indicator.47809/)

**UNKNOWN:** no primary result was found that provides raw read return codes, sense data and a verified PS2 PVD from a CECH-25xx on Evilnat 4.93. The owner probe must establish this. A statement that the XMB cannot launch a PS2 disc does not settle raw reading.

## Public LV1 interface: names, IDs and optical-driver pattern

**INFERRED from inspected declarations:** Linux names `170/0xaa` **lv1_open_device(bus_id, dev_id, flags)** and `171/0xab` **lv1_close_device(bus_id, dev_id)**. There are no separate `lv1_storage_open` / `lv1_storage_close` entries in this header. Relevant numbers are:

| Decimal / hex | Linux name | Inputs / outputs |
|---|---|---|
| 18 / 0x12 | construct_event_receive_port | 0 / 1 |
| 91 / 0x5b | read_repository_node | 5 / 2 |
| 170 / 0xaa | open_device | 3 / 0 |
| 171 / 0xab | close_device | 2 / 0 |
| 174 / 0xae | allocate_device_dma_region | 5 / 1 |
| 175 / 0xaf | free_device_dma_region | 3 / 0 |
| 176 / 0xb0 | map_device_dma_region | 6 / 0 |
| 177 / 0xb1 | unmap_device_dma_region | 4 / 0 |
| 197 / 0xc5 | connect_interrupt_event_receive_port | 4 / 0 |
| 245 / 0xf5 | storage_read | 6 / 1 |
| 246 / 0xf6 | storage_write | 6 / 1 |
| 248 / 0xf8 | storage_send_device_command | 6 / 1 |
| 249 / 0xf9 | storage_get_async_status | 1 / 2 |
| 254 / 0xfe | storage_check_async_status | 2 / 1 |
| 255 / 0xff | panic | 1 / 0 |

[Linux, arch/powerpc/include/asm/lv1call.h](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/include/asm/lv1call.h)

**INFERRED:** keep the namespaces separate. Linux's storage **bus type is 5**; storage **DISK device type is 0**, **ROM device type is 5**, and FLASH is 14. These are classification values, not the device identifier to pass to an open. The Linux platform's driver match IDs are another namespace again. [Linux, platform.h](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/platforms/ps3/platform.h)

**CLAIMED:** the wiki says generic open obtains bus/device IDs from repository nodes. It documents distinct failures for nonexistent device, busy device and invalid bus. This supports logging the exact signed return code; it does not justify hard-coding an LV2 storage ID as an LV1 ID. [PSDevWiki, HV Syscall Reference](https://www.psdevwiki.com/ps3/HV_Syscall_Reference)

**INFERRED:** Linux `ps3rom.c` implements BD/DVD/CD through two routes. READ(10) becomes `lv1_storage_read(dev_id, region_id, lba, count, 0, bounce_lpar, &tag)`; other SCSI packets use `lv1_storage_send_device_command` with device-command **1**. Its ATAPI structure contains a 32-byte packet area, packet length 12, transfer dimensions, direction/protocol, LPAR buffer address and argument length. Small inbound transfers use PIO; larger inbound transfers use DMA. Submission can return `LV1_DENIED_BY_POLICY`. Completion checks returned tag/status in the interrupt path. The host advertises one command at a time (`can_queue = 1`). This supplies an implementation pattern, not permission or PS2-media proof. [Linux, drivers/scsi/ps3rom.c](https://raw.githubusercontent.com/torvalds/linux/master/drivers/scsi/ps3rom.c)

**INFERRED:** `ps3stor_setup` opens the HV device, creates/connects an event receive port, installs an interrupt handler, then creates/maps a per-device DMA region for its bounce buffer. Alignment below 4 KiB is rejected. The helper probes accessible disk regions, while ROM is treated specially as accessible. Read/write and device-command helpers submit a tag then await completion. The synchronous helpers use an unbounded completion wait, which must not be copied as a timeout policy. A second device needs its own lifecycle/state and validated DMA mapping; sharing the HDD's mapping merely because the wrappers exist is unsupported by this source. [Linux, drivers/ps3/ps3stor_lib.c](https://raw.githubusercontent.com/torvalds/linux/master/drivers/ps3/ps3stor_lib.c)

## What might refuse access

**CLAIMED:** PSDevWiki's reverse-engineering notes describe per-region ACLs and authority-dependent filtering of storage commands. They distinguish physical storage, RBD and ENCDEC and show IDs varying by environment. The notes include a GET CONFIGURATION example and discuss storage request completion/status. Much of the analysis is for old firmware; it is not a reliable device-assignment dump for the owner's 4.93 netemu partition. [PSDevWiki, Hypervisor Reverse Engineering](https://www.psdevwiki.com/ps3/Hypervisor_Reverse_Engineering)

**INFERRED:** permission to execute a hypercall, device visibility, region access, command policy and actual media-read success are separate checks. An open succeeding is only the P1 milestone. A read may still fail because of readiness, addressing, buffer setup, disc condition or policy. **UNKNOWN:** exactly which authentication/media checks apply to original PS2 DVD and CD sectors on this console. Nothing inspected proves a requirement to send authentication or vendor commands for the requested read-only probe.

**INFERRED:** public LV2 homebrew code identifies the BD device as **`0x0101000000000006`**, opens via syscall 600, reads via 602, gets information via 609, sends device commands via 604 and executes ATAPI through 616. The LV2 ATAPI block is a distinct 56-byte structure; the Linux LV1 block cannot simply be passed to an LV2 syscall. The public header also includes authentication/reset helpers; those are outside this probe and must not be copied into its command list. [IRISMAN, include/storage.h](https://raw.githubusercontent.com/aldostools/IRISMAN/master/include/storage.h)

**INFERRED:** webMAN's BD-info implementation supplies another public ATAPI packet/block example. This is useful for the probe ABI, but a successful build is not a runtime validation. [webMAN MOD, scsi_info.h](https://raw.githubusercontent.com/aldostools/webMAN-MOD/master/include/feat/scsi_info.h)

**CLAIMED / relevance limit:** ps3-disc-dumper is a **PC** utility requiring a compatible Blu-ray drive and matching PS3 decryption key. Its requirements concern PS3 Blu-ray dumps and cannot establish PS2 read policy on a PS3 slim, or provide the netemu partition's device IDs. No decryption keys, game dumps or dumper executable were downloaded. [13xforever, ps3-disc-dumper](https://github.com/13xforever/ps3-disc-dumper)

## webMAN/Cobra launch chain and stub requirements

**INFERRED:** webMAN's PS2ISO branch chooses netemu, caches non-HDD PS2 images to HDD, and mounts via `mount_ps_disc_image`. With automatic game-fix lookup enabled and no adjacent config, it temporarily mounts, checks a game ID in the filename, otherwise lists `/dev_bdvd` for executable-style names to select a config. It then mounts/reuses the ISO and sends insertion events. This runs while LV2 exists; it provides no continued service after transition. A future marker ISO must therefore be a valid mountable filesystem, not an empty path token. This branch does not establish that webMAN itself always reads `SYSTEM.CNF`; its fallback is a directory scan. [webMAN MOD, mount_cobra.h, PS2 branch](https://raw.githubusercontent.com/aldostools/webMAN-MOD/master/include/mount/mount_cobra.h)

**INFERRED:** webMAN's mount entry point checks that `/dev_bdvd` appears, while its autoplay code asks XMB to launch the disc icon. It does not directly exec netemu with a normal process argument vector. **UNKNOWN:** all Sony VSH/game-extension reads before transition; those components were not dynamically traced. A real `SYSTEM.CNF`, directory records and a small legal owner-authored boot ELF remain sensible future stub candidates, but are not yet a proven minimal set. [webMAN MOD, mount.h](https://raw.githubusercontent.com/aldostools/webMAN-MOD/master/include/mount/mount.h)

**INFERRED:** Cobra's `mount_ps2_discfile` first reads `0xb0` bytes at image offset `0x8000`, checks the PVD and uses metadata there to classify CD/DVD; multi-track images take a CD path. At transition `build_netemu_params` writes `--COBRA--` markers into system-manager arguments and `/dev_hdd0/tmp/game/ps2bootparam.dat`. Preparation writes `/dev_hdd0/tmp/cfg.bin`: flag byte at 0, image path from byte 1, track count at `0x800` and descriptors at `0x801` for CD. Thus the ISO path is conveyed through Cobra configuration, not a webMAN background reader. A real-disc/netemu branch explicitly calls `fatal` with “Sorry, no optical disc support in ps2_netemu”. Optical authentication patches are skipped for netemu; comments associate them with recorded CD/DVD support in other emulators. Separately the source has a real-disc LV1 read wrapper in LV2 context. These describe the inspected historical Cobra tree, not guaranteed bytes of Evilnat 4.93. [Cobra 7.3 repository, 486/LITE/stage2/storage_ext.c](https://raw.githubusercontent.com/Joonie86/COBRA-7.3/master/486/LITE/stage2/storage_ext.c)

## Owner tests and evidence needed next

1. **UNKNOWN → test:** run the built read-only LV2 probe separately with an original PS2 DVD, PS2 CD, then a PS3 game baseline. Keep each complete log and the disc's title/type. The primary evidence is return codes, returned sector counts, PVD bytes, capacity/profile and any sense response.
2. **UNKNOWN → P1 candidate:** after static wrapper/argument validation, a label-only netemu build should enumerate relevant repository entries and attempt one optical open, record the exact return code, close only if opened, and leave stock game behavior intact. No automatic installer or console execution is part of P0.
3. **UNKNOWN → P2 candidate:** only after P1 establishes access, use a separately validated buffer/mapping and bounded command path to read sector 16 inside netemu. Compare the six bytes `01 43 44 30 30 31` and the full returned byte count. This is the first emulator-side read proof.

## Source access limits

**PROVEN:** `PS2_Emulation`, `HV_Syscall_Reference`, `Hypervisor_Reverse_Engineering`, the cited Linux sources, Cobra storage source, webMAN sources and the named PSX-Place reports were readable through web tools. `LV1_Functions`, `PS2_Netemu`, some guessed storage pages and several GitHub directory/history endpoints were unavailable; no content is attributed to those unread pages. Direct shell downloads were connection-blocked. Raw `master` URLs are mutable; no exact upstream commit pin was established. Retrieval date and function names above identify what was inspected. No public source was executed and no hardware behavior was verified during research.

**PROVEN (P0B follow-up):** owner probe results, error decoding and source-backed unlock candidates: [P0B_PS2_MEDIA_READ.md](P0B_PS2_MEDIA_READ.md).
