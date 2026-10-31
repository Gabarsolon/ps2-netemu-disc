# PS2 Disc Probe (P0C v3, build only)

**PROVEN (PC):** PS3DK v0.26.0 compiles and links v3 with CMake/Ninja and `-Wall -Wextra -Werror`; generated SFO and finalized PKG checks pass. **PROVEN (owner's logs/photos):** PS3 BD reads work; the PS2 DVD fails sector/file reads before and after the manager-mode switch, although multiMAN displays SYSTEM.CNF and the subsequent profile changes to DVD-ROM. **UNKNOWN:** modern multiMAN's exact read path, v3 hardware behavior and netemu access. Nothing was sent, installed or run on the console during this task. See [P0C source findings and limits](../docs/P0C_MULTIMAN_EXPERIMENT.md#source-findings); forbidden preparation was not implemented.

**PROVEN (source/PC):** v3 retains v2's fixed append-only log and run markers, adding stage markers and a launch selector. Earlier runs, including incomplete ones, remain in that same file. Prefixes are console uptime, not calendar timestamps. There is no settings file. **UNKNOWN:** recovery from a kernel-wide hang remains outside the userspace watchdog's guarantee.

**PROVEN (PC), current package:** `local_only/ps3probe/PS2DiscProbe.pkg`, 148368 bytes; SHA256 `4f0c398fd7fda49429c46ad01d19e6cd98eb6350709df69330735e1baa8eb646`. The build refreshes `SHA256SUMS.txt` and `package_manifest.json`, including v3 stage/deadline/flag information; a future rebuild can have a different hash.

Build from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\ps3probe\build_ps3.ps1
```

All output, temporary files, signing output, package staging, `SHA256SUMS.txt`, and `package_manifest.json` are under `local_only\ps3probe\`. The app is `local_only\ps3probe\PS2DiscProbe.pkg`, title ID `PS2DP0001`. Its only packaged files are our EBOOT, PARAM.SFO, and generated icon; it contains no Sony firmware or game data. Python needs PyCryptodome for the existing Buzz package acceptance checker.

## Exact owner test

**UNKNOWN → owner test (never performed by this task):**

1. Copy the package above to USB and install manually using XMB Package Manager. Start from a normal fresh boot, no virtual ISO mounted, with the same original **PS2 DVD** inserted and settled. Record firmware/Cobra variant if known, disc title, manager version and whether a virtual image or `/dev_ps2disc` mapping existed. Keep this disc inserted for the comparison; do not launch/copy/mount/eject it between runs.
2. Launch **PS2 Disc Probe**. Leave **ALL** selected and press Cross, or wait 10 seconds. Wait for `Finished: log ready`, then Triangle/Circle to exit. Save the cumulative `/dev_hdd0/tmp/ps2disc_probe.log` with your existing FTP client as `v3-before-managers.log`; do not delete/truncate the console log. Record the latest `RUN BEGIN` uptime/selection and any missing stage/end marker.
3. Start **plain mmCM** without switching mode. Try viewing `/dev_bdvd/SYSTEM.CNF`, record whether the real 55-byte text appears, exit to XMB without launching/copying/mounting/ejecting, and run v3 **ALL** again. Save the entire cumulative log as `v3-after-mmcm.log`.
4. In mmCM choose **Switch to multiman mode - restart mmCM into standard CFW mode**. View the same file, record result, exit identically, then run v3 **ALL**. Save as `v3-after-multiman.log`. Report if mmCM already opens in standard mode or the order differs; these histories are not interchangeable.
5. Send the full cumulative log and the three mode/viewer results. Compare `file read` path/rc/bytes, `v3 READ` rc/count/bytes/PVD, and baseline `current_profile`. A real profile with failing reads is still a useful result. If a run times out, preserve the last `BEGIN`; optionally repeat only its stage using Left/Right at launch then Cross. Choices: **1 files**, **2 fresh/aligned storage**, **3 v2 baseline**, **ALL**. Up/Down scrolls after starting; Triangle/Circle exits. App lifetime is at most 60 seconds unless the kernel itself hangs.

**UNKNOWN → optional follow-up:** repeat ALL without revisiting a manager, then after a normal reboot to test transient-state persistence. Only after these comparisons, repeat separately with PS2 CD, PS1 CD and PS3 baseline if needed; no raw CD/subchannel copying is implemented. **INFERRED worst case:** read/driver or whole-console hang requiring restart and an incomplete log. Manager steps may also change patches/authentication/mount state/settings. Probe deadlines cannot cure a kernel-wide hang.

**UNKNOWN:** a failed read can mean policy, authentication, media format, access permissions, or a drive issue. Keep the raw codes; do not infer a cause from failure alone. `PVD lba16 signature_01_CD001=MATCH` after a full 2048-byte sector read is the useful positive result. This app never authenticates the drive/disc or changes firmware settings to turn a failure into a success.

## What it requests

**PROVEN (source), new v3 stages:**

- **1 files:** O_RDONLY open/read/close of `/dev_bdvd/SYSTEM.CNF`, then `/dev_ps2disc/SYSTEM.CNF`, requesting 64 bytes into a 128-byte-aligned buffer. Missing paths are logged. It never mounts or remaps anything; `/dev_ps2disc` may represent an existing folder mapping and is not physical-disc proof.
- **2 storage:** require successful device info, 2048-byte sector size and capacity >=18. Open BD fresh for each request; read LBA16 count1 then count2 with a static 64 KiB-aligned 64 KiB buffer. Arguments are **600 `(BD,0,&fd,0)`**, **602 `(fd,0,16,count,buffer,&u32_nread,0)`**, then **601 `(fd)`**. Exact rc, returned sectors/bytes, requested count, pointer/alignment and read elapsed time are logged. Each count is attempted once. No flags other than zero are used.
- **3 baseline:** the following v2 survey is retained; its sampled file buffer is now explicitly 128-byte aligned. ALL runs 1,2,3 in that order. Each stage has a fixed 15-second deadline; every I/O/log operation has five seconds, independently of the 60-second process guard.

**PROVEN (source), retained baseline:**

- Information for known LV2 device IDs: optical `0x0101000000000006`, HDD `...0007`, USB slots 0 and 1. Each result code and successful 64-byte device-info block is logged. This is a bounded known-ID survey, not exhaustive device enumeration; only the optical device is opened.
- Optical open with mode/flags zero; one-sector storage reads at LBA 16, 0, and 17. Full reads log 64 bytes; LBA 16 checks the six bytes `01 43 44 30 30 31`. READ CAPACITY(10) adds a last-LBA read if its block size is 2048. A reported non-2048 sector size skips these reads. If device-info fails, the default 2048 assumption is logged in the read line; the DMA destination is conservatively 64 KiB.
- Standard read/status ATAPI packets through `sys_storage_execute_device_command` (616), command 1: INQUIRY (36 bytes), TEST UNIT READY (no data), GET CONFIGURATION (32 bytes and current-profile decode), READ CAPACITY(10) (8 bytes), READ DISC STRUCTURE (DVD physical format 0/layer 0, 32 bytes). It records syscall rc and the opaque auxiliary output without asserting its meaning. On a failing command it requests standard REQUEST SENSE (18 bytes), logs the raw bytes, and decodes recognized fixed/descriptor sense formats. The DVD physical command can legitimately fail on CD or BD media.
- `/dev_bdvd` stat, read-only open, directory listing/stat, and the first 64 bytes of one regular file found in a bounded breadth-first search (up to 8 directories, 24 entries per directory, 32 entries overall). No files from the disc are copied to HDD.

**PROVEN (source inspection):** there are no storage writes, data-out packets, vendor/authentication packets, start/stop/eject, speed changes, medium-lock commands, firmware operations, mounts, network code, or installers in the app. Only `/dev_hdd0/tmp/ps2disc_probe.log` is written by the running app; it may create `/dev_hdd0/tmp` if absent. Every log line attempts fsync. Logging failure is displayed and does not stop other checks.

## SDK and ABI limits

**PROVEN (local headers):** the installed SDK's `ppu/include/lv2/syscalls.h` declares numeric `SYSCALL_STORAGE_*` constants and `sys/lv2_syscall.h` supplies generic syscall adapters, but it has no typed storage API/header. `storage_abi.h` adapts independently written argument passing to those SDK constants, using these primary public ABI references inspected on 2026-10-31:

**INFERRED (v3 rationale):** IRISMAN's ordinary storage wrapper accepts a variable sector count with final flags0; its CD-identification caller uses one sector. v3's counts1/2 are conservative ordinary transfer sizes, not a source-discovered PS2 unlock. Its stronger alignment is an experimental over-alignment, not a proven LV2 requirement. The sources do not justify equating Cobra's internal LV1 region0/flag2 read with LV2 602 flag2. No direct LV1, new ATAPI data-read packet, Cobra read opcode, decrypt/auth/reset helper or patch was added. Exact source functions, quotes, retrieval gaps and ranked experiments are in [P0C](../docs/P0C_MULTIMAN_EXPERIMENT.md#source-findings).

- [IRISMAN include/storage.h](https://github.com/aldostools/IRISMAN/blob/master/include/storage.h), specifically BD ID, the 56-byte packet, device-info field offsets, and syscall argument order for 600/601/602/609/616. [Raw source](https://raw.githubusercontent.com/aldostools/IRISMAN/master/include/storage.h). The published code is GPL-2.0-or-later; the small adapters here express ABI facts, rather than copying the full header or its control/authentication functions. `master` is mutable; an exact revision could not be retrieved through the available web cache, so no commit hash is claimed.
- [webMAN MOD scsi_info.h](https://github.com/aldostools/webMAN-MOD/blob/master/include/feat/scsi_info.h) independently shows the same packet layout and INQUIRY approach. It uses syscall 604 with seven arguments; this probe uses the explicit execute (616) variant from IRISMAN instead of guessing the auxiliary output for 604.
- [Linux ps3rom.c](https://github.com/torvalds/linux/blob/v6.12/drivers/scsi/ps3rom.c) documents packet length 12, non-data/PIO-in protocols, read direction, and a 2048-byte optical block size. Its LV1 packet includes extra DMA-address fields: that different LV1 struct is deliberately not passed to LV2 here.
- [Linux cdrom.c](https://github.com/torvalds/linux/blob/v6.12/drivers/cdrom/cdrom.c) supplies the standard GET CONFIGURATION current-profile and DVD physical descriptor field layouts; [scsi_proto.h](https://github.com/torvalds/linux/blob/v6.12/include/scsi/scsi_proto.h) supplies standard opcodes. No Linux implementation is linked into the probe.

**UNKNOWN / skipped:** `sys_storage_get_device_config` (610) has no SDK typed declaration. The [wiki syscall list](https://www.psdevwiki.com/ps3/LV2_Functions_and_Syscalls) gives a device/buffer signature with a question mark; [RPCS3's implementation](https://github.com/RPCS3/rpcs3/blob/master/rpcs3/Emu/Cell/lv2/sys_storage.cpp) instead takes two output count pointers. The probe logs this omission and uses known-ID device-info calls. It does not invent a signature, enumerate with an unverified report-devices ABI, or issue syscall 610 with the BD ID as a pointer.

## Time bounds and validation

**PROVEN (source inspection), console behavior UNKNOWN:** an independent high-priority guard has an absolute 60-second deadline that is never reset, including the launch selector. Each stage has an independent 15-second absolute deadline that logging cannot extend. Storage, file and log operations run only on a worker with a five-second operation deadline; GPU waits have two-second bounds. On expiry the guard requests exit, then calls `sysProcessExit` without taking file/libc/RSX locks or joining the blocked worker. Triangle/Circle requests cooperative cleanup; process termination reclaims a handle if a call remains blocked. A userspace guard cannot guarantee recovery from a kernel-wide hang or make an uninterruptible syscall cancellable. A timeout ends this run; later stages are not attempted. The fsynced `BEGIN` line identifies the pending call.

**PROVEN (PC):** normal CMake/Ninja build, NPDRM generation, SFO validation, finalized PKG header/digest/decrypted member validation, and PowerShell parser checks. **UNKNOWN:** controller/display/drive behavior on this console; no native executable was run. The framebuffer/font/video/pad/guard patterns were adapted from the owner's MIT Buzz app under `C:\Users\remus\ps3buzz-console\buzzbridge_app\ps3\plugin\autoload` (read-only). `ui_layout.c/.h` and `pkg_inspect.py` retain that template's text implementation. See `THIRD_PARTY.md` for provenance.
