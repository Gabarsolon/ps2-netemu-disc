# What we know about `ps2_netemu.self` (from the Buzz! Bridge project)

Labels: **PROVEN** = confirmed on the owner's real console or by running the real code on the PC; **INFERRED** = read from the binary / strong evidence but not exercised; **CLAIMED** = a forum/wiki says so; **UNKNOWN**.

Base file: Evilnat 4.93 `/dev_flash/ps2emu/ps2_netemu.self`, SELF sha256 `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`, decrypted ELF sha256 `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`. It is the "debug-menu" variant: the PS-button menu shows a `Debug Information` row. Kozarovv says the emulator code has not changed since firmware 4.78 (CLAIMED), but only this exact hash was ever patched.

## What the emulator is

- psdevwiki (CLAIMED): the PS2 emulators are not normal Game OS programs but guest systems on LV1; LV2 (the normal PS3 OS, with Cobra/HEN/webMAN hooks) is unloaded before the emulator loads. Consequences we saw (PROVEN): webMAN's `/remap.ps3` path redirect of `ps2_netemu.self` is ignored; the stock file in flash is what runs. HEN's payload does not survive into PS2 mode, so patches must live in the file in flash (CFW only).
- `ps2_netemu` is the software PS2 emulator used by the slim consoles (no PS2 hardware). psdevwiki: "the only emulator not able to run physical discs"; for ISOs the CFW "hacked it to use decrypted ISO files" (this lives inside the file: see the Cobra payload below).
- It has its own storage/USB/HID stacks (it runs in its own partition): its own **UFS** reader for the PS3 HDD (`raw_read` at `0x1ed5cc`), its own HID stack for USB devices (host input path, manager pointer at `0x24389a8`).

## Memory rules at runtime (PROVEN by hardware: stores into RO power the PS3 off)

- `[0, 0x300000)` text = read-only, `[0x300000, 0x800000)` data = read-only, RW from `0x800000`.
- Proven RW mailbox: `[0x930F20, 0x930F80)` (96 bytes, our `struct State`: status, fd, start, iso_size, length, stride, skip, epoch, produced, timestamp, owner, generation, reverse_arena, queue[8]).
- Native allocator `0xB9848` `(size, 3, 0)` returns RW memory owned by us (we allocate one 1792-byte arena at startup; checked against the pool `0x934980` / `0x24565b8`). All other persistent state lives there.
- Label strings are immutable (RO data we add); labels are chosen by RW loads (never by formatting into memory).
- A **code slot** exists for payload code: the Cobra payload sits at `0x3940` (cap `0x46B0`); our reservation is `0x4800..0x7FF0` = 14,320 bytes. S4L3 uses 14,304: it is nearly full. More code needs space (compile out diagnostics, or move code into an extended segment: the build already extends the RO load segment to hold ~1 MB of immutable data at `0x74E930`; extending executable space would be new work).
- Native helper entry points we call (via a trampoline table at `0x4A00..0x4F40`): `native_alloc 0xB9848`, `native_lock 0xBA24C` (HID manager critical section, `manager+0x30`), `native_unlock 0xB9074`, `native_set_report 0x5F08C` (host USB SET_REPORT output), `native_clock 0xB9CD0` (timebase, 79.8 MHz), original handlers for the pad/HID paths.

## The disc/file read layer (Stage 1 of the Buzz! work, PROVEN on hardware)

This is the layer most relevant to the new project. We hooked it to substitute a game's USB module at runtime:

- Hooks (patched words, expected originals): `entry_read` at `0x3CFC` (original `4E800421`, the Cobra read dispatcher), `entry_open` at `0x135F70` and `0x136FF4` (branch to Cobra open at `0x3960`), `entry_stat` at `0x135FAC` (Cobra stat `0x39B0`). `raw_read` = `0x1ED5CC` is the UFS read `(fd, offset, buffer, size)` returning bytes read (0x1ecc5c opens, 0x1ec760 stats). Our `s1_open/s1_stat/s1_read` recognize the ISO the emulator is mounting (exact SYSTEM.CNF + USBD + IOPRP authentication, fail-open) and serve bytes from our own memory for the substituted file, passing everything else through unchanged.
- The emulator asks this layer for **2048-byte sectors of an ISO file** (ISO9660 parse by us: `bb_patch.py` and `iso_patch.c` show a bounded ISO9660 reader). So a disc backend must look like a file: `open` returns an fd, `stat` returns a size (the size matters: the emulator uses it, including for dual-layer layout), `read(fd, off, buf, n)` returns bytes.
- The disc read must never block the emulator forever and must return exactly the length asked (short reads were handled as errors).
- Test hardware facts: ISO launched from webMAN with plain `.iso` in `/dev_hdd0/PS2ISO` on CFW (Cobra); `.CONFIG` next to it is optional.

## How patches are built and installed (PROVEN pipeline, reuse it)

1. Decrypt the stock SELF (`reference/buzz-netemu-build/selfdec.py`, keys from the public `key_vault.cpp`; not copied here: `C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp`), get the ELF.
2. `build.py` compiles our C payload for PPC64 (`clang --target=powerpc64-unknown-linux-gnu -mcpu=970 -mabi=elfv2 -mno-altivec -mno-vsx -msoft-float -ffreestanding -fno-pic -Oz`), links it with `ld.lld` into the code slot with the trampoline table, patches the entry points, extends the RO segment (PHDR1 filesz/memsz, last RO section size) to hold immutable data, rewrites the ELF headers and section table, and repacks the SELF through the original metadata (keys/IVs kept, section HMACs and whole-ELF SHA-1 recomputed, ECDSA field zero: valid only because CFW does not check it). The result reproduces byte for byte (`selfdec` round trip exact).
3. Validate on the PC before the console: PPC64 emulation of the real final code with stock-derived objects (`gh_run.py` + `gh_harness.py` + tests: pyghidra `EmulatorHelper`, original handlers run unchanged, OS calls modeled), store-target audit (no store outside proven RW; `gh_store_scan.py` and the compiled-IR audit), SELF/HMAC round trip, installer parse. Code size must stay under 14,320 bytes.
4. Install with the PowerShell/bash scripts in `reference/installer-scripts/` (hash allow-list, backup to PC and to `/dev_hdd0/buzzbridge/netemu_backup/`, mount `dev_blind`, upload, read back and compare, unmount in `finally`). No console restart is needed. Restore script ready first.
5. Console diagnostics without logs: the `Debug Information` row of the PS-button menu is replaced by a label chosen from an immutable string table by sticky flags in RW memory (pages selected by the highlighted menu row, `selected & 3`). Hook: `0x270FFC` (menu row selector), marker string at `0x304EC0` (`Debug Information\0`). The owner photographs the TV (or films it) and we read the flags with the phone over adb. This is how every hypothesis in the Buzz work was tested on hardware. It is slow but reliable; byte labels (`B3=7F`) were used to read raw data.
6. Guest (PS2 IOP) side: we also embed an IOP module (our virtual USB dongle, `bbusbd`) that the emulator serves in place of the game's USBD; talks to native code through a private 21-byte command-0x42 poll on SIO2 (a frame shape proven to be safe on this emulator). SIO2 frame shapes other than the standard pad lengths froze the console once or twice (cause never proven): only use frame shapes proven on hardware.

## Native pad/HID facts (PROVEN unless marked)

- Host pad refresh runs every 16 ms in the native event loop `BAD80` (calls `BAF10 -> BC168`, no lock held), reading each host device through `D0BAC -> CF71C -> registered provider`. Guest pad polls arrive via SIO2 PIO pump `126B18 -> 12825C` (command `0x42` at `127B70`), served from a cache filled by `BC168` and read by `BC838`.
- Buzz dongle: the emulator turns a USB HID device into **one** pad using 12-byte records `VID,PID,map` at `0x939234..` (Buzz records `054C:1000` at `0x93963C` and `054C:0002` at `0x939648`, map `0x30C340`): 12 buttons only; usages 13..20 are dropped. This is why only two handsets work in stock and why we patched the emulator.
- HID worker input events enter at `D15CC(T, request)` (T+0x40 = the physical interface, VID/PID at +0x16/+0x18; request: buffer, T, status, count). Our hooks sit there.

## Console facts

- CECH-25xx slim (no PS2 hardware), CFW Evilnat 4.93 Cobra, `192.168.0.169`, webMAN MOD 1.47.48 with FTP and web server; `dev_blind` via `http://host/dev_blind?1` and `?0`.
- ISOs live in `/dev_hdd0/PS2ISO` (40-odd files; plain `.iso`, some with `.CONFIG`). Images over 2 GiB exist (libc `stat` drops them in homebrew: use `sysLv2FsStat`).
- The PS3 app (`BuzzBridge.pkg`) is built with PS3DK (PSL1GHT-like) + CMake; GCM video output with a software framebuffer; useful as a template for any PS3 homebrew probe we need (video init, pads, log file, watchdog).

## What does NOT work (do not retry)

- webMAN/Cobra path redirect of `ps2_netemu.self` (`/remap.ps3?src=...&to=...`): ignored, PS2 mode loads the file from flash.
- `.CONFIG` files cannot change emulator internals (guest-side patches and per-game flags only).
- HEN cannot replace the file and loses its payload in PS2 mode (CLAIMED + consistent with the redirect failure on CFW).
- Anything touching SIO2 with new frame shapes: untrustworthy (two unexplained freezes).
- Long idle in our PS3 app once froze the whole console (not understood; heartbeat log added in v1.3.0).

## Where the Buzz! work lives

- Final netemu build tree: `C:\Users\remus\ps3buzz-console\raw_capture_debug11` (build.py, src, tests, package, REPORT.md; earlier stages `raw_capture_debug2..10`, `netemu_stage1..4` in an older scratchpad that may be gone).
- Installer/restore scripts: `C:\Users\remus\buzz-pad-bridge\netemu\` and `reference/installer-scripts/`.
- PS3 app: `C:\Users\remus\ps3buzz-console\buzzbridge_app` (REPORT.md has every decision, test and limit).
- Release: https://github.com/Gabarsolon/buzz-bridge/releases/tag/v1.3.0.
