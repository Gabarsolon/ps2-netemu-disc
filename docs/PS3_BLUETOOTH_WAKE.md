# PS3 Bluetooth wake — standby works; abrupt AC recovery unresolved

## Result and owner commands

- **PROVEN:** a later abrupt AC cut while the PS3 was still on at XMB did not
  recover by Bluetooth. The plug was off for five seconds, restored/verified on,
  and the dongle got a successful ACL, but the PS3 stayed red with no webMAN.
  The owner also tried the real paired DS3, disconnected from PC USB, and it did
  not wake the console in that state. This differs from the clean-shutdown test.
- **UNKNOWN:** whether that state is caused by lost wake configuration, power
  sequencing, an intentional policy, or another console-side condition.
  Unattended recovery after a true hard cut is not yet solved.
- **PROVEN, 2026-11-22:** the external Barrot dongle woke the PS3 from normal
  standby. Console boot was confirmed by webMAN returning online.
- **PROVEN:** the complete recovery sequence also passed: clean XMB shutdown,
  P115 AC off for five seconds, AC on verified, ten-second wait, Bluetooth wake,
  then webMAN online.
- **PROVEN:** stock ps2_netemu.self remains restored. Receipt:
  local_only/restore_stock_20261122_120327_892.json.
- **PROVEN (software):** the owner's existing manager now routes wake through
  the verified backend. Its user commands were parse-checked; the hardware
  sequence was exercised through the guarded internal test.

PowerShell, wake from standby:

    python C:\Users\remus\ps3_power_manager.py wake

Explicit smart-plug recovery followed by wake:

    python C:\Users\remus\ps3_power_manager.py recover

Read-only power status:

    python C:\Users\remus\ps3_power_manager.py status

The repository frontend is also available directly:

    python C:\Users\remus\ps2-netemu-disc\tools\ps3_bt_power.py wake

**PROVEN:** recover is an explicit command. There is no automatic power-cycle
watchdog. A healthy PS2 session can make webMAN unavailable, so HTTP availability
is not used to decide whether the emulator has frozen. The recovery command
verifies the P115 and the actual Bluetooth backend before any console power
change, then attempts a clean shutdown before the requested AC cycle.

## Proven wake sequence

1. **PROVEN:** select only external USB 0A12:0001, read manufacturer 2279
   (Barrot), and require the captured original adapter address.
2. **PROVEN:** set the paired DS3 address through Barrot opcode FC80/subcommand 5,
   RAM only. Standard HCI Reset 0C03 activates it. Verify both standard and vendor
   address reads.
3. **PROVEN:** write Class of Device 000508 with HCI Write_Class_of_Device 0C24;
   verify its readback before paging.
4. **PROVEN:** send HCI Create Connection to the captured console address with
   packet type CC18, page-scan repetition R2, no clock hint, role switch allowed.
   Await matching Connection Complete, then hold the successful link three seconds.
5. **PROVEN:** clear this attempt's connection, restore the original address,
   reset and verify it, and restore/verify the original device class.
6. **PROVEN:** success is reported only after webMAN returns online. Command
   acceptance and an ACL connection alone are insufficient proof of wake.

**PROVEN:** an ACL with the correct address but generic device class and immediate
disconnect did not wake this console; its power LED stayed red. The tested
controller-class/held-link sequence did wake it. **UNKNOWN:** whether class or
hold duration alone is sufficient; no further isolation is needed for this fix.

**PROVEN:** no Bluetooth HID reports, PS-button emulation, controller pairing
writes, or console firmware changes were needed for the working wake sequence.
The unused HID prototype remains an experiment, not the owner-facing route.

## Hardware identity and local setup

| Item | Verified identity |
|---|---|
| External dongle | 0A12:0001, Barrot BR8051A01, manufacturer 2279 |
| Original dongle address | 04:7F:0E:0C:E5:80 |
| Paired DS3 | 04:76:6E:8B:47:E4 |
| Console Bluetooth address | 78:DD:08:8D:37:F4 |
| Console LAN address | 192.168.0.169 |
| Tapo P115 LAN address | 192.168.0.13 |
| Original radio class | 000000 |

- **PROVEN:** controller F2/F5 USB reports supplied the two pairing addresses.
  The real controller also woke this PS3. Its normal HidUsb driver was restored.
- **PROVEN:** the P115 moved from 192.168.0.12 to 192.168.0.13. Authentication and
  power-on status were verified; only the saved IP was changed in the private
  Tapo configuration. Credentials were not printed or copied into repository code.
- **PROVEN:** WSL2 was already installed. Isolated Ubuntu 24.04 was imported as
  PS3-Bluetooth under local_only/wsl/PS3-Bluetooth. Its image checksum matched the
  official Ubuntu SHA256SUMS. Python/PyUSB/libusb are installed inside it.
- **PROVEN:** official usbipd-win 5.3.0 installed with valid signature and release
  checksum; installer exit 0, no PC reboot. Only the external dongle is force-shared.
- **PROVEN:** returning this clone repeatedly to Windows caused Code 10/43 and
  descriptor failures, requiring physical reconnection. It now stays assigned to
  the Linux backend; wake calls do not detach, unbind, or change Windows drivers.
- **PROVEN:** a hidden, tracked WSL keeper keeps the backend alive. The frontend
  verifies/reuses its own PID/start time and never stops another process.
- **PROVEN:** the usbipd firewall rule created by this setup is restricted to the
  WSL virtual Ethernet interface and its local subnet. Fresh backend TCP access
  was verified; the frontend needs no firewall changes per wake.
- **PROVEN (implementation):** wake access has an exclusive OS-held lock.
  Workers and separate recovery have deadlines. Linux USB ownership stays with
  this backend; its raw worker leaves the selected HCI interface unbound from
  btusb to avoid this clone's kernel initialization problem.

## Files and evidence

- tools/ps3_bt_power.py: concise Windows command, private logs, backend/USB checks.
- tools/start_ps3_bt_backend.ps1: hidden keeper with PID and start-time verification.
- tools/ps3_bt_linux.py: captured identities, standard reset, class, held page,
  restoration and actual boot confirmation.
- local_only/ps3_bt_pairing.json: captured USB reports and validated addresses.
- local_only/ps3_bt_radio_state.json: original class for recovery.
- local_only/bt_usb_class_wake_20261122.log: successful standby wake.
- local_only/bt_plug_recovery_test_20261122.log: successful full AC recovery.
- local_only/bt_final_radio_recovery_20261122.log: original address/class verified.
- local_only/backups/: original manager/config and pre-restoration emulator backups.

**PROVEN:** 56 offline protocol/cleanup tests passed, including class verification
before paging, held connection settings, ignored writes, failed activation and
restoration, malformed events, USB ownership cleanup, and actual packet fixtures.
Five Windows frontend mock checks and two additional preflight tests (including
success/failure/timeout subcases) passed. User command/helper syntax
was checked, including Windows PowerShell 5 parsing.

**UNKNOWN / not tested:** an intentionally frozen emulator, PC reboot/resume,
and console firmware/hardware other than this owner's setup. The recovery test
used a clean shutdown before AC removal; no game or emulator was launched for it.

Earlier diagnostic history is retained privately under local_only.

## Why the earlier approaches failed

- **PROVEN:** USB IDs labelled CSR hid a Barrot chip. CSR BCCMD was the wrong
  vendor command family.
- **PROVEN:** guessed neighbouring Ethernet addresses were replaced with the
  actual console address read from the paired controller.
- **PROVEN:** Windows WinUSB/libusbK replacement produced Code 10.
- **PROVEN:** native Windows vendor IOCTL allowed Barrot RAM reads/writes but
  rejected the standard address-read route. Barrot's documented type-4 vendor
  reset returned HCI status 12 on this A01 chip.
- **PROVEN:** direct Linux USB access accepted the standard HCI reset and address
  reads. Kernel btusb/raw-socket initialization still timed out on this clone;
  the working route uses PyUSB directly.
- **PROVEN:** correct source address plus bare HCI acceptance still left the
  console in standby. Device class and holding the link completed the tested fix.

## Primary implementation references

- [GIMX controller class and Sixaxis connection](https://github.com/matlo/GIMX/blob/master/core/connectors/sixaxis.c)
- [WakePS3's tested GIMX-based approach](https://github.com/Vegz78/WakePS3)
- [Barrot RAM address commands](https://github.com/tryger/barrot-tools/blob/main/src/barrot_tools/brt_hci_spec/brt_hci_spec.py)
- [Upstream connection packet fields](https://github.com/FreeTHX/pywakepsx-on-bt/blob/main/pywakepsx_on_bt/hci.py)
- [Microsoft USB passthrough guide](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)

## Owner-test launcher fix

- **PROVEN:** the owner's first recover command stopped before power changes.
  WSL's default shell stripped backslashes from the Windows worker path passed
  to wslpath. The hardware and keeper were already available.
- **PROVEN:** the frontend now uses WSL --exec for both path conversion and
  worker execution, and supplies the Windows path in forward-slash form.
  Three regression checks cover spaces, literal shell characters and recovery.
- **PROVEN:** the actual frontend prepare() passed after this fix, including
  path conversion, Linux worker execution and original address/class recovery.
  No console shutdown or smart-plug power change was made for this check.

## Abrupt power-cut test and software leads

- **PROVEN:** no shutdown endpoint was called in the hard-cut test. XMB was
  checked immediately before relay off, relay off was read back, and webMAN
  disappeared while AC was cut. Relay on was restored and verified in finally.
- **PROVEN:** original dongle address and class were independently recovered.
  Receipt: local_only/bt_hard_cut_20261122T122935Z.json.
  Log: local_only/logs/bt_wake_20261122T123000.168045Z_35944.log.
- **PROVEN (owner):** console stayed red; the real DS3 PS button also failed.
- **INFERRED:** the limitation now includes the console's wake state, because
  a genuine controller fails too. The exact mechanism is still UNKNOWN.
- **PROVEN (source):** Evilnat's xRegistry interface includes
  loadRegistryPowerOnReset(), selector 0x38. Sony-authored Linux PS3 system-manager
  code defines PS3_SM_WAKE_P_O_R (0x80000000). **UNKNOWN:** whether this offers a
  usable AC-restore auto-boot setting on this CECH-25xx/CFW combination.
- **PROVEN (Sony documentation):** Control for HDMI supports TV-remote power-on
  on CECH-2000 and later. **UNKNOWN:** whether it works in this abrupt-cut state
  with the owner's connected display.
- No console setting, Syscon firmware, or additional flash file was modified.

Primary leads:
- https://github.com/xXEvilnatXx/xai_plugin/blob/main/xai_plugin/xRegistry.h
- https://github.com/torvalds/linux/blob/master/drivers/ps3/ps3-sys-manager.c
- https://manuals.playstation.net/document/en/ps3/current/settings/ctrlhdmi.html

## Read-only power-setting inspection after hard-cut recovery

- **PROVEN (owner):** the front power button returned the console to XMB.
- **PROVEN (read-only console inspection):** firmware reports 4.93 CEX,
  Cobra 8.5. A local private copy of /dev_flash2/etc/xRegistry.sys was read;
  no console registry or firmware write was performed.
- **PROVEN:** powerOnReset=0, hdmiControl=0, hdmiControlEx=0,
  wolDex=0, powerOnDiscBoot=0, bootMode=PS3. The offline parser followed
  webMAN MOD's record layout and validated 518 records, printing only this
  allow-list. Private receipt: local_only/bt_power_settings_readonly.json.
- **UNKNOWN:** enabling powerOnReset would affect this retail CEX Slim or
  survive an abrupt AC cut. A registry entry and an OtherOS wake-source bit
  do not prove that feature works on this model. No setting was changed.
- **UNKNOWN:** exact reason Bluetooth wake failed after the abrupt cut.
  Coordinated shutdown code programs wake sources in Sony's Linux driver;
  this is evidence that shutdown configuration matters, not proof of a
  deliberate GameOS forced-shutdown lockout.
- Clean-shutdown recovery remains proven; recovery from a running console
  losing AC remains unresolved. No further hard-cut experiment was run.

Read-only parser reference:
https://github.com/aldostools/webMAN-MOD/blob/master/include/feat/xregistry.h

## Authorized PowerOnReset enablement

- **PROVEN:** owner explicitly requested powerOnReset On. Saved and verified
  a fresh private registry backup before changing the exact key through
  /xmb.ps3$xregistry(/setting/system/powerOnReset)=1.
- **PROVEN:** exact-key HTTP readback and independent FTP registry read both
  report 1. All 518 setting records were compared; only this setting VALUE
  changed. Three metadata bytes also changed in autoPowerOffEx, whose value
  stayed identical. No automatic rollback or additional write was attempted.
- **PROVEN (source):** webMAN's numeric handler routes ID 0x38 to a user/browser
  setting. It was NOT used. Its enabled DEBUG_XREGISTRY exact-path handler
  writes the named registry field directly; VSH cached state is UNKNOWN.
- **UNKNOWN:** whether a clean reboot is needed for VSH to consume the disk
  setting, whether CEX honors it, and whether abrupt AC recovery will work.
  No reboot, shutdown, smart-plug switch, or firmware flash was performed.
- Backup: local_only/backups/xRegistry_before_powerOnReset_20261122T124633.003011Z.sys
- Receipt: local_only/bt_poweronreset_20261122T124633.json
- Rollback, if requested: same exact-key endpoint with =0, then read back.

## Persistence check and alternatives

- **PROVEN (owner):** a later smart-plug off/on did not automatically boot.
- **PROVEN (read-only, 2026-11-22 12:54:16 UTC):** exact-key HTTP readback
  and an independent fresh FTP registry copy both report powerOnReset=1;
  518 records validated. The stored flag did not revert. The actual reason
  for no automatic startup remains **UNKNOWN**. No further setting changed.
  Receipt: local_only/bt_poweronreset_persistence_20261122T125416Z.json.
- **PROVEN (owner):** video goes through an HDMI splitter to a USB capture
  device on the PC. Their CEC capabilities are **UNKNOWN**.
- **PROVEN (source):** Sony documents HDMI remote power-on for CECH-2000+.
  gkoh/pico-cec supports transmitting CEC frames through a USB serial CLI.
  **UNKNOWN:** wake after abrupt AC loss on this PS3. An adapter on the PS3
  side of a CEC-blocking splitter could avoid relying on splitter passthrough.
- **PROVEN (source):** SwitchBot publishes local BLE press commands for its
  Bot. **UNKNOWN:** physical mounting compatibility with this PS3. A servo
  or suitable ready-made pusher would automate the manually proven button.
- **UNKNOWN:** exact front-panel circuit for an isolated relay/contact mod;
  no contact wiring or GPIO connection should be assumed from the model alone.
- Owner-requested agyp remus web research started read-only, using
  local_only/ps3_ac_wake_research_prompt.txt. No console experiments requested.

Research review outcome:
- **PROVEN:** agyp remus completed successfully and used web-search tools.
  Its local report was annotated with substantial corrections: its cited Sony
  page does not contain its alleged quotation, and its universal Syscon wake
  lockout, authenticated-pairing, capacitor, wiring and reliability assertions
  exceed the evidence. Its Linux WOL mask was also wrong (actual 0x00000400).
- **UNKNOWN:** no confirmed software fix for the tested abrupt-cut state has
  been identified; this does not prove that software fixes are impossible.
- **CLAIMED (reverse-engineering source):** the Syscon firmware research page
  describes persistent wake-source configuration in NVS for a CECHA00 CXR
  reference image. **UNKNOWN:** relevance to this CECH-25xx Syscon revision.
  No Syscon writes, mode changes, or pin assumptions were attempted.
  https://www.psdevwiki.com/ps3/Syscon_Firmware_Reverse_Engineering
- Annotated external report: local_only/ps3_ac_wake_agy_research.md.
- Task receipt: local_only/ps3_ac_wake_research_task.json.

## Hardware choices and owner recovery instructions

- **PROVEN (owner):** a Raspberry Pi Pico is already available; no CEC or
  servo add-on has been bought or demonstrated here. USB serial control is
  sufficient for a Pico build; Wi-Fi is not required.
- **INFERRED:** an externally mounted positional micro servo could automate
  the proven manual power button. It needs an appropriate supply, mounting,
  calibrated travel and reliable release. Mechanical reliability is untested.
- **PROVEN (source):** Pico-CEC lists a WP-905 male/female HDMI passthrough
  breakout and a USB-connected Pico-class board. Its current firmware needs
  configuration/adaptation for the exact board. Wires/headers, a data USB
  cable and possibly soldering are needed. The interface would be upstream
  of the splitter so its CEC connection reaches the PS3 directly.
- **ESTIMATE:** roughly EUR 5-10 extra for breakout and wires, before shipping,
  reusing the Pico/cable. This is not a verified delivered price. The project's
  January 2026 BOM lists its breakout at AUD 4.30; the live AliExpress price
  could not be verified. Earlier claims that a servo is always cheapest were
  not justified; total parts, mounting, supply and shipping determine that.
- **PROVEN (source, price checked during discussion):** Pulse-Eight's ready-made
  P8-USBCECv1 was listed at USD 47.55, before delivery/taxes, with short HDMI
  and USB cables. It is an alternative to building a Pico interface.
- **UNKNOWN:** whether CEC can wake this PS3 following the tested abrupt cut.
  HDMI wiring/voltage compatibility must be checked before connecting a Pico;
  do not assume all HDMI signals tolerate direct GPIO connection.
- **PROVEN (owner authorization):** resume sustained physical-disc netemu
  testing with TDU inserted. If a test demonstrably hard-freezes the console,
  cut and restore the plug once, notify the owner, then wait for them to press
  the physical power button. Do not infer a freeze solely from offline webMAN
  while a healthy PS2 partition runs. No further questions requested.

Hardware sources:
- https://github.com/gkoh/pico-cec
- https://www.aliexpress.com/item/1005004791079117.html
- https://www.adafruit.com/product/169
- https://www.pulse-eight.com/p/104/usb-hdmi-cec-adapter

Sources:
- https://manuals.playstation.net/document/en/ps3/current/settings/ctrlhdmi.html
- https://manuals.playstation.net/document/en/ps3/current/settings/remotestart.html
- https://github.com/gkoh/pico-cec/wiki/Command-Line-Interface-Guide
- https://github.com/OpenWonderLabs/SwitchBotAPI-BLE/blob/latest/devicetypes/bot.md

## Full controller experiment, 2026-11-22

- **PROVEN (console transcript):** the external dongle can negotiate both
  Bluetooth HID channels (PSM 0x11 and 0x13) with this PS3 from normal standby.
  The PS3 then disconnects with HCI reason 0x14 before sending any HID setup
  request. No accepted PS, direction, or face-button input has been demonstrated.
  It is **not yet a working substitute for the Pico controller bridge**.
- **PROVEN (offline):** the neutral 50-byte DS3 input report matches GIMX's
  packed default and Bluetooth status bytes exactly. Seven ACL/L2CAP/button
  checks, two controller frontend cleanup checks, the six existing HID checks,
  and five power frontend checks passed. This establishes packet/state
  behavior on the PC, not console input acceptance.
- **PROVEN (comparison):** an isolated Bumble 0.0.236 stack reached the same
  configured-channels/no-HID/disconnect boundary. The timestamped private H4
  trace places channel readiness at about 10.26 seconds and disconnect at
  11.49 seconds after stack initialization in that run. Local-name setup and an
  initial PS press did not fix the rejection. **UNKNOWN:** its underlying cause.
- **PROVEN (read-only registry):** the captured real controller address remains
  listed in `/setting/pad/bdaddr`. No pairing record or link key was changed.
- **PROVEN (control):** a page using the dongle's unchanged original MAC and
  controller class was rejected with status 0x0D. A subsequent use of the proven
  temporary-controller-address wake path brought webMAN online. This supports
  an identity-dependent difference; the exact transmitted address has still
  not been independently observed by another receiver.
- **PROVEN (cleanup):** test workers restored/read back the original MAC,
  device class, and (where changed) local name. USB ownership stays in the
  isolated Linux backend. No smart-plug cycle or console flash write was made
  during these controller tests.

Implementation: `tools/ps3_bt_controller.py` is a bounded experimental diagnostic,
not a validated everyday controller command. Private comparison code, packet
traces, registry-presence receipt, and the independent review are under
`local_only/`. Relevant logs: `bt_controller_20261122T143001Z.log`,
`bt_bumble_20261122T143930Z.log`, and the original-address control
`bt_bumble_20261122T144752Z.log`, all in `local_only/logs/`.

Primary references: [GIMX Sixaxis implementation](https://github.com/matlo/GIMX/blob/e44a1cc9823939165d3d92418e9d679c66496ee1/core/connectors/sixaxis.c),
[Bumble](https://github.com/google/bumble), and
[Bluetooth controller error definitions](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-61/out/en/architecture%2C-change-history%2C-and-conventions/controller-error-codes.html).

## Working Bluetooth DS3 controller, 2026-11-24

- **PROVEN (console + capture card):** the external dongle now works as a full
  DS3 controller. On the PS3 "Set the time and date" screen, a bounded test
  pressed Up and the day changed 01 -> 02; an interactive session then sent
  Down, Right, Up x3 and the date showed exactly 01/04. Frames:
  `local_only/bt_ctl_before.png`, `bt_ctl_after2.png`, `bt_ctl_after3.png`.
- **Root cause 1 (PROVEN):** after HCI Reset the dongle's Default Link Policy
  is 0, so it refused the PS3's role-switch request. The PS3 must be piconet
  master and dropped the link with reason 0x14. Writing Default Link Policy
  0x0005 (role switch + sniff, HCI 0x080F) before paging fixed it: the log
  shows ROLE CHANGE (dongle -> slave), then the PS3's HID setup, then a sniff
  MODE CHANGE (interval 18 slots). BlueZ (GIMX's stack) enables this by default,
  which is why GIMX never hit it.
- **Root cause 2 (PROVEN):** the PS3 re-requested GET_REPORT 0xF2 forever while
  we answered 16 data bytes (the USB capture was read with a 17-byte buffer).
  Appending GIMX's 17th byte (0x09) let the handshake continue.
- **PROVEN handshake order on this console:** GET feature 01, GET F2, SET EF
  (byte6 a0), GET EF, SET EF (b0), GET EF, GET F8, SET output 01, GET F7,
  SET F4 `42 0a 00 00` (enable), then output reports (LEDs) at ~60 Hz on the
  interrupt channel while our 100 Hz input reports are accepted.
- Tools: `tools/ps3_bt_controller.py --serve` (stdin commands
  `PRESS <btn> [ms] | DOWN/UP <btn> | STICK <L|R> x y | RELEASE | QUIT`, up to
  6 h, identity restored on exit) and `tools/ps3_bt_pad.py` (Python API with the
  same methods as `pico-ds3-bridge/python/ps3_controller.py`; CLI
  `python tools/ps3_bt_pad.py press up 300` or `... shell`). `--link-policy 0`
  reproduces the old failure.
- Backend notes from this session: the dongle had moved to a new USB port
  (busid 8-3), so it needed `usbipd bind --force` again; the usbipd firewall
  rule was bound to the previous WSL vEthernet GUID and was re-pointed to
  `vEthernet (WSL (Hyper-V firewall))`; a "Device in error state" attach was
  cleared by `pnputil /restart-device` on the parent hub (VID_05E3 PID_0610),
  no physical replug.
- **UNKNOWN:** behavior inside PS2 emulation (netemu) and in games; whether the
  session survives the console going to standby (expected: link drops; the
  wake path still works only after a clean shutdown).
- Consequence: the Pico is no longer needed as the DS3 bridge and can be
  powered from the PC to drive the power-button servo (docs/SERVO_POWER_BUTTON.md).
- **Fragility found later the same day (PROVEN):** a CLI session that sent one
  press and QUIT immediately after channel setup (while the PS3 was still in
  its HID setup) left the dongle unresponsive (`No reply to HCI 0x1001`). After
  usbip re-attach, the WSL kernel's `btusb` driver bound to the dongle, sent its
  own init and wedged it (`Controller not accepting commands anymore: ncmd = 0`).
  A libusb reset then made it stop enumerating entirely; hub restarts did not
  recover it. **Needs a physical unplug/replug** (then `usbipd bind --busid
  <new> --force` if the port changed, and `usbipd attach --wsl`).
- Fixes applied (not yet re-tested live because the dongle is wedged):
  `READY` is now printed only after the PS3's SET F4 enable (or 4 s), commands
  are ignored before that, and a session ends with HCI Disconnect + wait for
  Disconnection Complete before the identity restore resets the radio.
  `btusb` is blacklisted and unloaded in the dedicated `PS3-Bluetooth` WSL
  distro (`/etc/modprobe.d/ps3-no-btusb.conf`). `tools/ps3_bt_pad.py` now logs
  all worker output to `local_only/logs/bt_pad_*.log`.
