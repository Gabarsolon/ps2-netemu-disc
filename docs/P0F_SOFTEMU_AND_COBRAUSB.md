# P0F: ps2_softemu leads, console ps2emu listing, CobraUSB source

Labels: PROVEN / INFERRED / CLAIMED / UNKNOWN.

## Console listing (PROVEN, read-only FTP, 2026-10-31)
`/dev_flash/ps2emu/` on the owner's CECH-25xx / Evilnat 4.93 holds: `ps2gxemu_stage2.bin` (11264), `ps2hwemu_stage2.bin` (11408), `ps2_emu.self` (1770208), `ps2_gxemu.self` (1981120), `ps2_netemu.self`. No `ps2_softemu.self` and no softemu stage2 (INFERRED: removed from 4.x firmware, consistent with the video below). The netemu on the console was our P1b no-open ablation at that moment (size 2554192). ps2_emu / ps2_gxemu need the PS2 hardware chips, so they cannot run on a slim (INFERRED).

## Video transcript (owner's `Testing out Sony's Forgotten PS2 Software Emulator on PS3.srt`, CLAIMED)
- ps2_softemu (software emulator that predates netemu) recognizes PHYSICAL PS2 discs; a patched softemu 4.01 was run on a slim downgraded to firmware 3.55 with Cobra; PAL discs on a PAL console played, some games playable; configs only fix freezes.
- Limits: no virtual memory cards, region locked, no burned discs, no XMB button (power off to quit). A small app recognizes the disc and starts it.
- Not verified by us. The owner's pasted "four emulators" table is an unverified summary and contradicts some proven facts.

## Joonie86/CobraUSB (public source, 2014; read via gh; files copied to local_only/cobrausb/ for reading)
- `USB/ps2emu/include/ps2emu/symbols.h` lists symbols for PS2HWEMU, PS2GXEMU and PS2SOFTEMU (firmware 3.41 / 3.55 ...). For SOFTEMU (3.41): `cdvd_send_atapi_command_symbol 0x88C88`, `cdvd_send_device_command_symbol 0x88B9C`, `ps2_disc_auth_symbol 0x8B2BC`, UFS read/open/close/fstat, TOC `0x5C8C00`. GXEMU has the same family plus `cdvd_read_symbol`. The netemu has none of the ATAPI/device-command/disc-auth symbols (agy report, CLAIMED; consistent with our static work).
- `USB/ps2emu/include/ps2emu/cdvd.h`: media type codes `0xFF70` PS3 DVD, `0xFF71` PS3 BD, `0xFF60` PS2 CD, `0xFF61` PS2 DVD, `0xFF50` PSX CD (the values our probe saw: PS3 BD disc profile `FF71`); `STORAGE_COMMAND_ATAPI 0x01`, `GET_DEVICE_SIZE 0x10`, `GET_DEVICE_TYPE 0x11`.
- `USB/lv1/src/stor.c`: the LV1 storage wrapper uses `STOR_BUS_ID 4` and the device id as `dev` index (`bus 4`, `dev <id>`), reads `blk_size` from the repository, maps a DMA region and calls `lv1_storage_read` + `lv1_storage_check_async_status`, without calling `open_device` in that wrapper. Consistent with our repository finding (storage bus index 4, ids equal indexes).
- `USB/ps2emu_stage1.5/loader/` has Makefiles and loader keys for `gxemu`, `hwemu` and `softemu`: Cobra's way of loading payloads into the PS2 emulator files (same idea as our build).
- Every ps2 emulator including softemu has a `ps2_disc_auth` function: the emulator itself authenticates the disc (INFERRED from the symbol).

## vLaunchSELF (psx-place resource, CLAIMED from the pasted page)
A PSL1GHT file browser that launches ELF/SELF files from LV2. The PS2 emulators are LV1 partitions, not LV2 processes, so this does not start them (INFERRED).

## What would help
1. `ps2_softemu.self` (4.01, unpatched preferred) in `local_only/`: how a non-BC (slim) emulator opens the drive, auth sequence, which partition type.
2. Open question the softemu could settle: is the drive assigned to the partition that runs softemu (parameter `0x8202`) but not to the netemu partition (`0x8204`)? (UNKNOWN)

## ps2_softemu obtained (2026-10-31)
- Source: owner's official 3.55 `PS3UPDAT.PUP` (`C:\Users\remus\Downloads\3.55-OFW-PS3UPDAT.PUP`, sha256 `334e60a4ef5843a688c1c6aebf0951c3259429233c7a5aca5a24f0edad78a192`, version.txt `3.55`). Unpacked with `tools/pup_extract.py` (PUP entry 0x300 tar -> `dev_flash_NNN` SCE type 3 files decrypted with the public SCEPKG ERK/RIV constants from RPCS3). Extracted files and ELFs stay in `local_only/fw355/` (never git).
- PROVEN (PC): `dev_flash/ps2emu/ps2_softemu.self` md5 `f95cc406bf1b4ec44481bae1195ca94c` (the checksum a forum paste quoted for the 3.55 file), size 2058104; also `ps2_emu.self` (md5 `89c71599...`) and `ps2_gxemu.self` (md5 `81037e5c...`). `selfdec.py` decrypts all three (LV2-type SELF, version 0x0003005500000000) to ELF.
- PROVEN (PC): the decrypted softemu ELF has LV1 248 (`device command`) `sc` sites at 0x88c0c and 0x88d54, inside the functions CobraUSB names `cdvd_send_device_command_symbol` (0x88B9C) and `cdvd_send_atapi_command_symbol` (0x88C88) for softemu, and LV1 170 (open_device) sites at 0x88814 and 0x8e08c, LV1 171 at 0x8c94c / 0x67d00. So the CobraUSB 3.55 symbol table matches this binary.
