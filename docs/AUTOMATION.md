# Unattended console test loop (2026-11-25)

How an agent runs a netemu console test end to end with no owner action:
launch, watch, read the screen, press buttons, and recover from a freeze or
power-off. Details and evidence: [PS3_BLUETOOTH_WAKE.md](PS3_BLUETOOTH_WAKE.md)
(sc 377 auto-boot, Bluetooth pad), [AUTOMATIC_SNAPSHOT_CONTROL.md](AUTOMATIC_SNAPSHOT_CONTROL.md)
(auto-return netemu builds).

## Pieces

| Job | Tool | Status |
|---|---|---|
| Console state | `python tools/ps3_auto.py state` (webMAN HTTP, XMB flag, plug on/off, watts) | PROVEN 2026-11-25 (XMB = 73-74 W) |
| Screen | `python tools/ps3_auto.py grab [out.png]` (capture card, unmutes + regrabs if black) | PROVEN grab at XMB; SD unmute path PROVEN in ps3-240p 2026-11-24 |
| Buttons | `python tools/ps3_bt_pad.py press <btn> [ms]` or `... shell`; Python `PS3BtPad` | PROVEN at XMB and in a PS2 game 2026-11-24 |
| Launch an ISO | `GET http://192.168.0.169/play.ps3/dev_hdd0/PS2ISO/<iso>` or `tools/run_test.py` | PROVEN |
| Auto-exit PS2 | auto-return netemu builds (reason byte 2 after 20 s) | PROVEN carrier runs, ~75 s to XMB |
| Recover | `python tools/ps3_auto.py recover` (30 s AC cut, waits for auto-boot, else servo press) | auto-boot PROVEN 3/3 hard cuts from XMB via autoexec.bat; servo step PROVEN alone 2026-11-26, full fallback path only dry-run |
| Power button | `python tools/ps3_power_button.py on` (Pico servo, [SERVO_POWER_BUTTON.md](SERVO_POWER_BUTTON.md)) | PROVEN boot from standby 2026-11-26 |
| Install netemu | `tools/install_netemu.ps1 -File <self> -Force` (backup + hash readback) | PROVEN |

Fixed facts: PS3 `192.168.0.169`; Tapo P115 at the IP in the private config
(`C:\Users\remus\ps3_power_manager.py` / its JSON, currently `192.168.0.12`;
never print credentials); capture card DirectShow name `USB3 Video`, HID
`345f:2131`; stock netemu SHA256 `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`.

## Recovery (autoboot DISABLED by owner 2026-11-27)

The owner disabled the autoboot plugin: `/dev_hdd0/autoexec.bat` (which ran
`/syscall.ps3?377|1` at every boot to re-arm `PS3_SM_WAKE_P_O_R`) is **removed**.
AC restore after a cut therefore does **not** boot the console on its own
anymore. Recovery is now: AC cut to force-off a frozen console, then the Pico
servo presses the power button.

**Panic recovery needs a DOUBLE press (owner-reported 2026-11-27):** after a
kernel panic a single power-button press does not boot the console; press the
button **2 times**. `ps3_auto.py servo_press()` does this (two `PRESS 300`, ~1 s
apart).

Historical (while autoexec was present, PROVEN 3/3): the sc 377 re-arm made AC
restore auto-boot (webMAN up ~18 s after AC on). That path is now disabled.

**PROVEN once (2026-11-26):** the auto-boot also happens after a clean webMAN
`/shutdown.ps3` followed by a `recover` cut (webMAN up 18 s after AC on). A
clean shutdown therefore does not exercise the servo step.

**Exception (PROVEN by sysmgr_ss disassembly, 2026-11-25):** a panic shutdown
overwrites the wake source and wipes `PS3_SM_WAKE_P_O_R`, so after a panic AC
restore does not boot the console. Only the power button does. The servo
fallback below covers this.

## Automatic power recovery

One command, no owner action:

```
python tools/ps3_auto.py recover
```

| Step | Action | If it works | If not |
|---|---|---|---|
| 0 | webMAN still answers | refuse, exit 1 (`--force` to override) | continue |
| 1 | Smart plug off 30 s, then on (force-off) | continue | AC on not verified: exit 2 |
| 2 | Wait 180 s for auto-boot (now disabled, so expect none) | exit 0 | continue |
| 3 | Servo presses the power button **twice** (panic needs 2) | wait 180 s, exit 0 | exit 3 |

Step 3 presses only if all of these hold: the plug is readable and on, it draws
less than 15 W, and webMAN does not answer. A press on a running console turns
it off, so any doubt means no press (exit 3). It presses twice (a panic needs a
double press); a cut on a running console is already prevented by the plug/HTTP
guard, so the double press lands only on a provably-off console.

Force-off is always the smart plug (owner decision 2026-11-26), never a long
hold of the button.

Needs, for step 3: the Pico on PC USB with `pico-servo/main.py`, the servo
mounted at the button, calibration `rest=0 press=45`, and no `servo_jog.py`
running (it holds the serial port). Check with
`python tools/ps3_power_button.py status`.

Exit 2 or 3: notify the owner.

## The loop

1. **Preflight.** `ps3_auto.py state` must show `http=up xmb=True plug=on`.
   Wait >= 15 s after webMAN first answers (autoexec must have run).
2. **Prepare.** Offline build + audit. For firmware-route builds, apply live LV1
   patches (`python -I tools/patch_sysmgr_optical.py --apply`, verify
   STOCK->PATCHED); precreate snapshot files by FTP as the build README says.
3. **Install** the test SELF with the installer.
4. **Launch** via webMAN `play.ps3` (record the time). `grab` a frame at
   ~6, 20, 45, 75 s for evidence.
5. **Watch.** Poll HTTP every 5 s and `state` every 15-30 s. HTTP going down
   in PS2 mode is NORMAL (no network in the emulator). Never use FTP for
   liveness.
6. **Classify** (first match wins):
   - HTTP back: clean return. FTP the snapshot/log, decode.
   - HTTP down and watts low (well below ~70 W; exact standby wattage not yet
     recorded, write it down the first time) or plug says `off`: console
     powered off (panic). Go to 7.
   - Auto-return build, HTTP still down 180 s after launch, watts high:
     `grab` twice 10 s apart. Same frame or black after unmute: hung. Go to 7.
   - Normal build (no auto-return): exit with the pad, PS, CROSS, LEFT, CROSS
     (2 s after PS, 1.2 s between the rest; this is run_test.py's default).
     No XMB within 60 s of that and the screen does not change: hung. Go to 7.
7. **Recover.** `python tools/ps3_auto.py recover` (add `--force` only when
   webMAN still answers but the console is clearly wrong). Exit 0 = booted
   (by itself or by the servo). Exit 3 = not booted even after the servo step:
   notify the owner. Exit 2 = plug did not confirm on: notify the owner. The
   plug can be unreachable for a while after a console power-off; the tool
   retries. See "Automatic power recovery" above.
8. **After any recovery or test:** live LV1 patches are gone (RAM only).
   A build that is not fail-open (any optical probe) must be replaced by the
   stock netemu **before any further PS2 launch**: run the installer with the
   stock SELF and check the hash above. Then back to 1.

## Pad notes

- The PS3 drops the pad when entering/leaving the PS2 emulator and when it
  powers off. In `shell` mode it reconnects by itself once XMB is back; a PS
  press also reconnects. Paging a powered-off PS3 wakes it.
- Wait for `READY` before sending; never QUIT during the PS3's HID setup.
  That once wedged the dongle (needs a physical replug, then
  `usbipd bind --busid <new> --force` and `usbipd attach --wsl`).
- Only one program can own the dongle (pad, keyboard remote, wake).

## Capture notes

- One program at a time on the card: close OBS / `capture_view.py` before `grab`.
- SD/low-line modes (PS2 480i/480p/240p) can come out black: the card's
  firmware sets a mute bit on every mode change. `grab` clears it once and
  regrabs. For a long run keep `python capture_unmute.py --watch` running
  from `C:\Users\remus\ps3-240p\tools` (it imports `capture_input_status.py`
  from there). Volatile HID RAM write only.
- SD frames sit 1:1 in the top-left of the 1080p buffer: crop 720x480 (480p),
  720x576 (576p), 1440x240 (240p). A dark XMB frame (mean ~9) is the dimmed
  screensaver, not mute.

## Not proven yet

- A cut during the first seconds of boot, before autoexec.bat runs: the flag
  is not armed, so it would stay off (`recover` then tries the servo).
- The whole `recover` run ending in the servo step. PROVEN separately on
  2026-11-26: `servo_press()` after a webMAN shutdown booted the console
  (webMAN up 13 s after the press); the branch logic was dry-run with fakes
  (6/6). A servo press after a real panic is still untested.
- A real hung emulator recovered by this loop (only clean XMB cuts tested).
- Standby wattage threshold (record it).
- Launching the inserted physical disc via webMAN instead of the XMB disc icon.

## Next console test queued (firmware route)

`experiments/netemu_firmware_probe1/src/owned.c` already carries the bus-99
probe (`lv1_open_device(99,2,0)`, expect `-17`, no hardware touched), edited
2026-11-24 but **not rebuilt** (SELF in `local_only/firmware_probe1/` is from
2026-11-22, bus 4). Rebuild + validate, apply A+B, install, launch the Buzz
carrier, run the loop. Survives with `open_ret = 0x1ffffffef`: bare `sc 1`
is fine once A authorizes, move to Component C. Powers off: the hypercall
mechanism/wrapper is the problem. See [FIRMWARE_ROUTE_PLAN.md](FIRMWARE_ROUTE_PLAN.md).
