# Research Report: External USB Optical (DVD/BD) Drive for PS2 Netemu on PS3 Slim

**Target Context:** PS3 Slim CECH-25xx, CFW Evilnat 4.93 + Cobra, webMAN MOD 1.47.48.  
**Project Goal:** Run PS2 discs directly from an optical drive using `ps2_netemu.self` without copying to HDD.  
**Question Investigated:** Would attaching an external USB optical (DVD/BD) drive bypass the internal BD drive's LV1/daughterboard authentication and make reading PS2 discs easier?

---

## Short Verdict

> [!CAUTION]
> **Practical Verdict: DO NOT buy an external USB optical drive for this goal.**  
> An external USB optical drive does **not** make playing PS2 discs on a PS3 Slim easier. In fact, it replaces an LV1 hypervisor permissions problem with a significantly harder, double-layered driver problem.

### Key Reasons:
1. **GameOS / CFW is completely blind to USB optical drives:** Neither stock PS3 firmware, CFW Evilnat, Cobra, nor webMAN MOD contains a USB Mass Storage ATAPI/MMC driver (Class 0x08, Subclass 0x02/0x08). If you plug a USB DVD/BD drive into the PS3, GameOS ignores it entirely. It does not appear in `/dev_usb*`, `/dev_bdvd`, or the XMB.
2. **GameOS ceases to exist during PS2 execution:** Even if a driver or mount redirect existed in GameOS/LV2 (e.g., via Cobra or webMAN), **LV2 is completely shut down and unloaded from RAM** when a PS2 game starts. The PS3 hypervisor (LV1) constructs a fresh, isolated guest partition to execute `ps2_netemu.self`. All LV2 drivers, mounts, and syscall hooks vanish.
3. **`ps2_netemu` has no USB Mass Storage or Bulk Transport stack:** While `ps2_netemu` has a built-in USB host controller driver, it is wired **exclusively for USB HID input devices** (controllers, steering wheels, Buzz buzzers via Control and Interrupt-In endpoints). It has **zero** USB Mass Storage Class (0x08) code, **zero** Bulk-Only Transport (BOT) pipeline, and **zero** SCSI/MMC command formatting. Writing a full USB BOT engine + SCSI reader from scratch in PPC64 assembly/C inside `ps2_netemu`'s constrained ~14 KB payload slot is vastly more complex than communicating with the internal drive.
4. **The internal drive is already an ATAPI/SCSI block device on LV1:** The console's internal BD drive is physically connected to the Southbridge and interfaced directly through LV1 hypercalls (`lv1_storage_open`, `lv1_storage_read`, `lv1_storage_send_device_command`). Tackling the internal drive via LV1 hypercalls remains the only architecturally viable path.

---

## Detailed Evidence & Answers to Research Questions

### 1. Visibility of USB Optical Drives in PS3 Firmware & Homebrew

* **Stock GameOS / LV2 Kernel:**
  * **[PROVEN]** The PS3 LV2 USB mass storage driver (`sys_usbd` + storage Logical Device Driver) binds strictly to **USB Mass Storage Class (`bInterfaceClass = 0x08`)**, **Subclass `0x06` (SCSI transparent command set / Reduced Block Commands)** using **Bulk-Only Transport (`bInterfaceProtocol = 0x50`)**. It expects block devices formatted with an MBR partition table and FAT32 file system using 512-byte or 4096-byte logical sectors (Sources: RPCS3 `sys_storage.cpp` / `sys_usbd.cpp`; PSDevWiki `LV2_Functions_and_Syscalls`).
  * **[PROVEN]** USB optical drives (CD/DVD/BD) implement **Subclass `0x02` (SFF-8020i / ATAPI)**, **Subclass `0x05` (SFF-8070i)**, or **Subclass `0x08` (MMC-5)** with 2048-byte sector geometry and ISO9660/UDF disc structures. Sony's LV2 kernel has no LDD driver for these subclasses.
  * **[CLAIMED / PROVEN]** When a standard USB optical drive is plugged into a PS3 running stock firmware or CFW, the drive receives power (spins up if bus-powered or self-powered), but GameOS does not mount it. No device node is created under `/dev_usb*`, and no disc icon appears in the XMB under Game, Video, or Music (Sources: PSX-Place community testing, threads on USB DVD drives).

* **CFW / Cobra / webMAN MOD / Evilnat:**
  * **[PROVEN]** Neither Cobra CFW payload nor webMAN MOD implements a USB optical drive driver.
  * **[PROVEN]** Cobra's storage subsystem (`storage_ext.c`) intercepts LV2 storage system calls (`sys_storage_*`) to redirect the internal `/dev_bdvd` node to raw sector maps of ISO images stored on `/dev_hdd0` or `/dev_usb*` (using `rawseciso` or `netiso`). It contains no USB host controller stack and no USB BOT/ATAPI client (Source: GitHub `xXEvilnatXx/Cobra-PS3`, `Joonie86/Cobra-7.00` `stage2/storage_ext.c`).
  * **[PROVEN]** webMAN MOD scans `/dev_usb000` through `/dev_usb007` for FAT32 filesystem structures, and delegates NTFS/exFAT scanning to `prepISO` (which uses user-space block parsers). webMAN MOD has no interface for USB optical drives (Source: GitHub `aldostools/webMAN-MOD`).

* **Linux on PS3 (OtherOS / OtherOS++):**
  * **[PROVEN]** In Linux running under OtherOS/OtherOS++, the standard Linux kernel USB stack (`ehci-hcd`, `ohci-hcd`), `usb-storage`, and SCSI CD-ROM driver (`sr_mod`) are present.
  * **[PROVEN]** Under PS3 Linux, external USB optical drives **are** recognized and bound as standard SCSI CD-ROM devices (e.g., `/dev/sr0`) (Source: Linux kernel `drivers/scsi/ps3rom.c`, PS3 Linux documentation).
  * **[PROVEN]** However, OtherOS runs in its own hypervisor partition (LPAR). Linux drivers run inside the Linux guest and have no presence in GameOS or `ps2_netemu`.

* **Hardware Exceptions: "TV Compatibility Mode" / USB Flash Drive Emulation:**
  * **[CLAIMED / PROVEN]** Certain portable external DVD writers (e.g., LG GP60/GP65 series with "TV Connectivity", Lite-On eBAU108 with "TV Mode") feature a bridge chip mode toggled by holding the drive's eject button for 2–3 seconds while the tray is open.
  * **[PROVEN]** In TV Mode, the drive's bridge firmware emulates a standard USB flash drive (Class 0x08, Subclass 0x06, 512-byte sectors) and presents media files (MP3, MP4, JPEG) stored on data discs via an emulated FAT32 filesystem so smart TVs can browse them.
  * **[PROVEN]** TV Mode does **not** provide raw optical LBA access (2048-byte sector SCSI reads), does not support encrypted commercial movie DVDs, and cannot run or present PS2 game disc structures (Sources: Hitachi-LG Data Storage manuals; PSX-Place ODD experiments).

* **Known Projects Clarification:**
  * **"Cobra USB":** Was a hardware DRM / security dongle released in 2011 to unlock Cobra CFW features; it was never an optical drive (PROVEN: PSDevWiki).
  * **"Cobra ODE" / "3k3y" / "E3 ODE":** Were hardware Optical Drive Emulators spliced directly into the internal SATA/PATA ribbon cable between the PS3 motherboard and the Blu-ray daughterboard. They emulated the internal BD drive over SATA, not via USB (PROVEN: PSDevWiki).
  * **"USB BD drive on PS3":** In the RPCS3 and PC dumping communities, specific external USB Blu-ray drives (such as LG BP50NB40 flashed with LibreDrive) are used on **PCs** to dump PS3 discs via Disc Dumper / 3K3Y tools. They are not plugged into or used by PS3 consoles (PROVEN: RPCS3 Quickstart Guide).
  * **"PS2 USB Disc Loaders":** On original PS2 hardware, Open PS2 Loader (OPL) only loads from USB mass storage (FAT32/exFAT ISO files). The PS2's USB 1.1 ports (12 Mbps / 1.5 MB/s) were slower than a 1x CD-ROM, and no USB optical drive loader exists for PS2 (PROVEN: OPL project documentation).

---

### 2. Device Visibility, Mount Points, and the PS2 Launch Boundary

* **Device Mapping in GameOS:**
  * **[PROVEN]** An external USB optical drive does **not** appear as `/dev_usbXXX` (because the LV2 mass storage driver rejects non-Subclass-0x06 descriptors) and does **not** appear as `/dev_bdvd` (which is hardwired to the internal BD drive interface).
  * **[INFERRED]** Even if a developer wrote a custom LV2 kernel extension registering a USB Logical Device Driver via `sys_usbd_register_ldd` for Subclass 0x02, it would only exist as an arbitrary custom kernel node inside LV2.

* **Mounting as `/dev_bdvd` via Cobra / webMAN MOD:**
  * **[PROVEN]** Cobra's virtual disc mounting redirects `/dev_bdvd` storage requests to an ISO file by patching LV2 system call dispatchers (`sys_storage_open`, `sys_storage_read`). Cobra has no mechanism to redirect `/dev_bdvd` to a USB device.
  * **[PROVEN]** webMAN MOD's command `/mount.ps2/<path>` mounts an extracted PS2 folder to `/dev_ps2disc`. This was created specifically for PS3 *SingStar* to import songs from PS2 *SingStar* discs. It is a GameOS userspace mount for a native PS3 title; it is not a PS2 emulator launcher (Source: GitHub `aldostools/webMAN-MOD` Wiki, "Web Commands").

* **The PS2 Launch Boundary (The Fatal Architecture Barrier):**
  * **[PROVEN]** On a PS3 Slim, when a PS2 game is launched, **GameOS (LV2) is terminated and completely unloaded from memory**.
  * **[PROVEN]** The PS3 hypervisor (LV1) constructs an independent, isolated Logical Partition (LPAR) for the PS2 guest environment and boots `ps2_netemu.self`.
  * **[PROVEN]** All LV2 drivers, mount points (`/dev_bdvd`, `/dev_usb*`), Cobra hooks, and webMAN MOD plugins cease to exist before `ps2_netemu.self` executes its first instruction.
  * **[PROVEN in Buzz! Bridge]** Even GameOS filesystem redirects such as webMAN's `/remap.ps3` for `ps2_netemu.self` are ignored because the hypervisor loads the emulator binary directly from flash storage without going through LV2 (Source: `docs/NETEMU_KNOWLEDGE.md`, Stage 1-4 console tests).

---

### 3. BD Drive Authentication vs. USB & PS2 Disc Protection

* **Does a USB drive skip PS3 BD-drive authentication?**
  * **[PROVEN] YES, at the console hardware/hypervisor level.**
  * The PS3's internal BD drive security involves:
    1. Cryptographic pairing between the drive daughterboard (Renesas controller) and the motherboard via keys in EID (EID4 / `eid_root_key`).
    2. Mutual authentication handshakes enforced by the Security Server (`ss_server`).
    3. Hardware physical checks for BD-ROM media (BCA, PIC, ROM-Mark, wobble groove).
  * USB storage connects to the Southbridge USB Host Controller (OHCI/EHCI). It does not interface with the BD drive controller, requires no daughterboard handshake, and has no `ss_server` pairing.

* **Does `ps2_netemu` require PS2 disc authentication?**
  * **[PROVEN] NO. `ps2_netemu.self` contains zero disc authentication routines.**
  * **Why:** Sony created `ps2_netemu` exclusively for **"PS2 Classics"** distributed digitally via the PlayStation Store (PSN). In official releases, the game is delivered as an encrypted package (`ISO.BIN.ENC`) stored on the internal hard drive (`/dev_hdd0/game/.../USRDIR/ISO.BIN.ENC`).
  * The emulator was engineered with **no physical disc interface**, **no Mechacon wobble-groove checking code**, and **no SCEx handshake routines**.
  * Cobra CFW patches `ps2_netemu` in flash (at address `0x3940` / `0x3CFC`) so that instead of decrypting `ISO.BIN.ENC` via the VME crypto engine, it reads raw 2048-byte sectors directly from an unencrypted `.iso` file on the HDD.
  * **[PROVEN in Buzz! Bridge]** The emulator's file read interface expects only standard 2048-byte sector responses via `open`, `stat` (reporting file size), and `read(fd, offset, buffer, size)`. Any backend that provides 2048-byte sector data satisfies the emulator (Source: `docs/NETEMU_KNOWLEDGE.md`).

* **Physical PS2 Discs in a PC USB Optical Drive:**
  * **[PROVEN]** Genuine PS2 DVD-ROM discs use standard DVD physical layouts formatted with ISO9660 or UDF filesystems. Any generic PC optical drive can read their 2048-byte sectors over USB using standard SCSI `READ(10)` commands without requiring proprietary authentication or decryption keys (which is why tools like ImgBurn or `dd` can dump PS2 discs on any PC).
  * (Note: PS2 CD-ROM titles use CD-ROM XA Mode 2 Form 1, which also returns 2048 user bytes per sector via standard MMC commands).
  * The PS2's original anti-piracy check was executed exclusively by the physical Mechacon chip inside real PS2 consoles. Because `ps2_netemu` is a pure software emulator, it has no Mechacon check to satisfy.

---

### 4. How `ps2_netemu` Reads Images and the USB Replacement Problem

* **How `ps2_netemu` reads game data on PS3 Slim:**
  * **[PROVEN]** Stock `ps2_netemu` opens `ISO.BIN.ENC` on `/dev_hdd0` using its own built-in UFS filesystem reader (`raw_read` at `0x1ED5CC`, `open` at `0x1ECC5C`, `stat` at `0x1EC760`), reading via LV1 storage hypercalls (`lv1_storage_open`, `lv1_storage_read`) directed at the internal HDD.
  * **[PROVEN]** Under Cobra CFW, Cobra's injected payload hooks entry points at `0x135F70` / `0x136FF4` (`open`), `0x135FAC` (`stat`), and `0x3CFC` (`read dispatcher`). These hooks route sector requests directly through the UFS reader to `/dev_hdd0/PS2ISO/*.iso` (Source: `docs/NETEMU_KNOWLEDGE.md`).

* **`cdvd_send_atapi_command` and Low-Level Device Commands:**
  * **[PROVEN]** In early backwards-compatible PS3 models (CECHA/B/C/E) running `ps2_emu.self` or `ps2_gxemu.self`, the emulator retained a hardware CDVD bridge that sent ATAPI packet commands to the internal BD drive via LV1 hypercalls (`lv1_storage_send_device_command` hypercall 202 / `0xCA`, and `lv1_storage_read` hypercall 200 / `0xC8`) (Sources: PSDevWiki `PS2_Emulation`; Linux kernel `drivers/scsi/ps3rom.c`).
  * **[PROVEN]** In `ps2_netemu.self`, **Sony completely removed all physical CDVD hardware drive and ATAPI code**. `ps2_netemu` emulates the PS2's `cdvdman.irx` / `cdvd.irx` IOP module in guest software, translating guest `sceCdRead` and `sceCdSeek` calls into simple synchronous host file reads: `read(fd, lba * 2048, buffer, count * 2048)`.

* **Could a USB optical drive replace the UFS reader?**
  * **[INFERRED]** In theory, if a backend can supply `open`, `stat`, and `read(fd, offset, buffer, size)` returning 2048-byte sector data, the emulator's read dispatcher will accept it.
  * **[PROVEN / INFERRED] In practice, writing a USB optical driver inside `ps2_netemu` is an enormous barrier:**
    1. **Driver absent:** `ps2_netemu` contains a USB host stack, but it is implemented **strictly for HID devices** (DualShock controllers, steering wheels, Buzz buzzers). It exposes an internal HID manager (`0x24389a8`), control transfer submission (`0x5F08C`), and interrupt-in completion handlers (`0xD15CC`).
    2. **Missing Bulk Transport:** USB Mass Storage / ATAPI requires **Bulk-Only Transport (BOT)** endpoints (Bulk-In and Bulk-Out with `xfer_type = 2`). `ps2_netemu` has no BOT state machine, no Command Block Wrapper (CBW) / Command Status Wrapper (CSW) handling, and no SCSI command builder (`INQUIRY`, `READ CAPACITY (10)`, `READ (10)`).
    3. **Severe Code Slot Limits:** The available payload reservation inside `ps2_netemu` is approximately 14,320 bytes (`0x4800..0x7FF0`). The Buzz! Bridge payload already uses 14,304 bytes. Implementing a full USB BOT stack and SCSI parser in that space is practically impossible without major architectural restructuring of the ELF load segments.
    4. **Comparison to Internal Drive:** The console's internal BD drive does not require a USB host controller stack, BOT protocol, or external cabling. It is already directly wired to the hypervisor as an LV1 storage block device.

---

### 5. Practical Verdict & Drive Models / Chipsets

* **Should the owner buy a USB optical drive for this goal?**
  * **NO.** It is a dead end. An external USB drive does not bypass any obstacle on the PS3 Slim; instead, it introduces an entire operating system's worth of missing USB Mass Storage and SCSI driver infrastructure into an environment (`ps2_netemu`) that has neither the code nor the memory space to support it.
  * **The correct path forward remains Plan A (the internal BD drive):**
    * The internal drive is physically integrated into the console.
    * It speaks SCSI/ATAPI natively to the Southbridge.
    * It is accessed via existing LV1 hypercalls (`lv1_storage_open`, `lv1_storage_read`, `lv1_storage_send_device_command`).
    * The primary question for Plan A is simply whether the PS2 partition's LV1 resource list allows opening the BD storage device ID (Phase P0 / P1 in `docs/GOAL_AND_PLAN.md`).

* **Drive Models and Chipset Evaluation:**
  | Category | Models / Chipsets | Behavior on PS3 | Viable for PS2 Netemu? |
  | :--- | :--- | :--- | :--- |
  | **Standard External USB DVD/BD Writers** | Generic USB 2.0/3.0 external drives (Hitachi-LG, Lite-On, ASUS, Pioneer, Samsung) | Ignored by GameOS (subclass 0x02 not bound). Ignored by `ps2_netemu` (no BOT driver). | **NO** |
  | **"TV Connectivity Mode" Drives** | LG GP60NB50, GP65NB60; Lite-On eBAU108 (MediaTek MT1862/MT1887 bridges) | Emulates FAT32 flash drive for media playback on TVs; does not provide raw LBA access or game disc reading. | **NO** |
  | **Flashed PC Blu-ray Drives** | LG WH16NS40, BP50NB40; ASUS BW-16D1HT (MediaTek MT1959, LibreDrive firmware) | Functions on **PC only** (Windows/Linux with Disc Dumper / RPCS3). Unrecognized if plugged into PS3. | **NO** |

---

## Primary Sources & References

1. **Linux Kernel Upstream - PS3 Storage & ROM Drivers:**
   * [`drivers/scsi/ps3rom.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/scsi/ps3rom.c) — PS3 BD/DVD/CD-ROM driver interfacing with the LV1 hypervisor.
   * [`drivers/ps3/ps3stor_lib.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/ps3/ps3stor_lib.c) — `ps3stor_send_command` sending `lv1_storage_send_device_command`.
   * [`arch/powerpc/platforms/ps3/system-bus.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/powerpc/platforms/ps3/system-bus.c) — LV1 storage hypercalls (`lv1_storage_open` 198, `lv1_storage_read` 200, `lv1_storage_send_device_command` 202).

2. **PSDevWiki Documentation:**
   * [PSDevWiki: PS2 Emulation](https://www.psdevwiki.com/ps3/PS2_Emulation) — Breakdown of `ps2_emu`, `ps2_gxemu`, `ps2_softemu`, and `ps2_netemu`.
   * [PSDevWiki: LV2 Functions and Syscalls](https://www.psdevwiki.com/ps3/LV2_Functions_and_Syscalls) — Storage syscalls 600 (`sys_storage_open`), 602 (`sys_storage_read`), 604 (`sys_storage_send_device_command`).
   * [PSDevWiki: PS2 Classics Emulator Compatibility List](https://www.psdevwiki.com/ps3/PS2_Classics_Emulator_Compatibility_List) — Background on PS2 Classics software emulation containerization.

3. **Open-Source CFW & Homebrew Repositories:**
   * [Evilnat / Cobra-PS3](https://github.com/xXEvilnatXx/Cobra-PS3) — Cobra payload `storage_ext.c` virtual optical disc mounting and SCSI command handling.
   * [Joonie86 / Cobra-7.00](https://github.com/Joonie86/Cobra-7.00) — `stage2/storage_ext.c` and `ps2emu_stage2`.
   * [aldostools / webMAN-MOD](https://github.com/aldostools/webMAN-MOD) — `/mount.ps2` implementation and ISO mounting architecture.
   * [RPCS3 / rpcs3](https://github.com/rpcs3/rpcs3) — `rpcs3/Emu/Cell/lv2/lv2.cpp` and `sys_storage.cpp` low-level LV2 storage syscall emulation.

4. **USB Specifications:**
   * USB Implementers Forum: *Universal Serial Bus Mass Storage Class Specification Overview* (Revision 1.4) — Class `0x08`, Subclass `0x02` (SFF-8020i), Subclass `0x06` (SCSI Transparent), Protocol `0x50` (Bulk-Only Transport).
