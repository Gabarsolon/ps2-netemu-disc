# Servo power-button pusher (automatic PS3 power-on/off)

Status 2026-11-26: built, mounted, power-on PROVEN.
Labels: PROVEN / INFERRED / UNKNOWN / ESTIMATE, as in the rest of the docs.

## As built (2026-11-26)

- Pico 2 H on PC USB, MicroPython v1.29.0, `pico-servo/main.py`.
- One SG90 (only one arrived from the 2-pack), taped in place. Wiring as below.
- Calibration: `rest=0` (neutral), `press=45`. Slow movement, 20 ms per degree.
- **PROVEN:** `python tools/ps3_power_button.py on` booted the console from
  standby.
- **Owner decision:** the servo only powers on. Force-off is the Wi-Fi smart
  plug. The 10 s hold (`off`, `recover` in `ps3_power_button.py`) was never
  tested; do not use it.
- Automatic use: `python tools/ps3_auto.py recover`, see
  [AUTOMATION.md](AUTOMATION.md) "Automatic power recovery".
- Calibrate from the keyboard: `python tools/servo_jog.py` (quit it afterwards,
  it holds the serial port).

The sections below are the planning record from before the build.

## Goal

Let a PC script power the PS3 on and force it off unattended after a hard
freeze or self power-off, without the owner pressing the button.

## Why a button pusher

- **PROVEN** (docs/PS3_BLUETOOTH_WAKE.md): after an abrupt smart-plug AC cut
  the console sits in red standby and cannot be woken by the Bluetooth dongle
  or a genuine DS3 PS button. Only the physical front power button worked.
- **PROVEN:** powerOnReset=1 did not auto-boot on AC restore.
- **UNKNOWN:** HDMI-CEC wake after an abrupt cut. CEC is also off on the console
  (hdmiControl=0), and the HDMI splitter may block it. Rejected for now.
- **INFERRED / commonly documented:** holding the front power button ~10 s (until
  the second beep) force-shuts a frozen PS3. If it works during our freezes,
  the smart-plug cut (and its broken wake state + 30 s discharge) is avoided.
  The button is read by Syscon, not the frozen Cell. UNKNOWN on this console.

## Options evaluated (ranked)

1. **Servo on the front button** (chosen): no console opening, uses the proven
   physical path, one servo does both press (on) and hold (force off).
2. Optocoupler/relay across the button contacts: most reliable, but needs the
   PS3 opened and soldered. Button-board pinout for CECH-25xx UNKNOWN.
3. SwitchBot Bot: off-the-shelf BLE pusher, but fixed short press (10 s hold
   UNKNOWN), bulky for the small button next to eject, needs a spare BT adapter.
4. Solenoid: needs a driver and a separate 5-12 V supply, no gain over a servo.
5. HDMI-CEC (pico-cec / Pulse-Eight): no evidence it wakes the PS3 in this state.
6. Syscon UART: needs opening + soldering, auth issues. Not pursued.

Background research report (subagent, 2026-11-24) found no PS3-specific servo
project; similar servo-on-button builds warn about: the servo lifting itself
instead of pressing (needs rigid mount), brownouts on Raspberry Pi (Linux SBC)
boards, and jitter on weak supplies.

## Parts (eMAG, ordered 2026-11-24)

| Part | Price | Purpose |
|---|---|---|
| Set 2x SG90 servo, 180 deg (OMGift) | 24.67 lei | actuator + spare |
| Scotch-Fix 3M interior mounting tape 19 mm x 1.5 m | 19.37 lei | mounting |
| Dupont wires male-female, 40 pcs, 40 cm (Led Bazar) | 7.89 lei + 19.99 delivery | servo plug to Pico pins |
| Dupont wires male-male, 40 pcs, 30 cm (Led Bazar) | 5.20 lei | spare / breadboard |
| Breadboard 830 + jumper wires + MB102 5V/3.3V supply module | 24.66 lei | prototyping; MB102 can power the servo separately |

Not ordered (yet): second Pico, Schottky diode (diode route). The owner
already has a USB A male-male cable, so the OTG route can be tried with the
OTG Y-cable borrowed from their TV box (it stays in use there otherwise).

Already owned and used: Raspberry Pi Pico 2 H (headers soldered), Ugreen
micro-USB data cable, female-female Dupont wires, glasses nose pads / temple
sleeves (soft tip for the servo arm), OTG Y-cable (micro-B male + micro-B female
power inject + USB-A female), Chucai GM-114 USB screw-terminal adapters.

Decisions:
- **SG90, not the "MG90S 360" listing:** 360-degree servos are continuous-rotation
  (speed only, no position) and cannot press repeatably. Positional 180 deg needed.
- **SG90 vs MG90S:** SG90 torque ~1.2-1.8 kgf*cm; with a ~1 cm arm >1 kgf. A small
  tactile button typically needs ~0.2-0.3 kgf (ESTIMATE; PS3 button force UNKNOWN).
  Plastic gears are fine for a few presses a day. Firmware must not stall the
  servo against the button (press to contact, then cut PWM).
- **No capacitor:** Pico 2's buck-boost regulator runs from VSYS 1.8-5.5 V, so a
  USB dip from servo start does not reset it (the brownout reports were for a
  Raspberry Pi SBC). A cap on VSYS would not help the servo, and 3300 uF on USB
  far exceeds the 10 uF USB inrush limit. Fallback if the servo jitters: power it
  from a separate phone charger through the Chucai screw-terminal adapter (VBUS
  and GND terminals), with GND common to the Pico.
- **Geko silicone bumpers dropped:** the owner's glasses nose pads / temple
  sleeves serve as the soft tip.

## Wiring (servo to Pico 2 H)

| Servo wire | Pico pin | Signal |
|---|---|---|
| brown | 38 | GND |
| red | 40 | VBUS (5 V) |
| orange | 20 | GP15 (PWM, 50 Hz) |

Pins are numbered in a U: 1-20 down one side from the USB end, 21-40 back up
the other side, so 38 and 40 sit next to the USB connector.
Never plug the stock servo connector onto pins 38-39-40: the signal wire would
land on VBUS. Without male-female wires, the alternative is to re-pin the
servo housing (brown, empty, red on 38-39-40; orange crimp alone on pin 20,
taped) or to use paper-clip/solid-wire pins between female-female wires.

## Mounting

- Lay the servo flat on a heavy wood block (tape, or small screws through the
  servo ears) so the arm swings horizontally into the button. The reaction
  force then loads the tape in shear. Do not tape the servo on top of the PS3
  pointing down; that peels the tape.
- Short horn (<= 2 cm), soft tip, aim away from the adjacent eject button.
- Clean glossy surfaces with alcohol before taping. Calibrate angle before
  final fixing.

## Update 2026-11-24: Pico power problem solved

The external Bluetooth dongle now works as a full DS3 controller
(docs/PS3_BLUETOOTH_WAKE.md, "Working Bluetooth DS3 controller"; API
`tools/ps3_bt_pad.py`). The Pico is therefore free: unplug it from the PS3,
plug it into the PC, and use it only for the servo (power from PC USB, alive
while the PS3 is off). No second Pico, OTG cable or diode needed. The section
below is kept for history.

Code ready (not run on hardware yet): `pico-servo/main.py` (MicroPython
firmware: PRESS/HOLD/ANGLE/SET/REST/STATUS over USB serial, calibration in
`cal.json`, PWM released when idle) and `tools/ps3_power_button.py` (PC side:
`status`, `on` only when the console looks OFF, `off --yes`, `recover --yes`,
calibration helpers). Flash and calibration steps: `pico-servo/README.md`.
Note 2026-11-24: the Tapo plug did not answer at .12/.13 or anywhere on
192.168.0.0/24 during this session; the tool then reports state UNKNOWN and
`on` refuses to press unless webMAN is down AND the plug reads < 15 W.

## Open problem: Pico power (historical)

- **PROVEN** (pico-ds3-bridge/README.md): the only Pico runs the DS3 USB
  emulator and is powered by the PS3 USB port. PS3 USB ports are unpowered when
  the console is off (INFERRED, well known), so the Pico dies exactly when the
  servo is needed.
- Firmware can do both jobs (add `SERVO PRESS` / `SERVO HOLD <ms>` commands to
  the existing UART protocol over the CP2102); the problem is power only.

Options:
1. **Second Pico dedicated to the servo** (most certain): powered from the PC
   over its own USB, MicroPython, DS3 setup untouched. Pico 2 H ~44.60 lei on
   eMAG; needs a second micro-USB data cable.
2. **One Pico via the owned OTG Y-cable** (owner's choice to try first):
   ```
   PS3 USB port -- USB A male-male cable (VBUS taped, PS3 end) --> OTG USB-A female
                                                                   OTG micro-B male --> Pico
   PC / charger -- micro-USB cable -------------------------------> OTG micro-B female (power)
   ```
   Needs a USB A male-male cable (not owned yet, ~10 lei). VBUS on the PS3 end
   must be isolated, otherwise charger 5 V back-feeds the PS3 port. UNKNOWN:
   the cable's internal VBUS routing (check with a multimeter first) and
   whether the DS3 emulation re-enumerates when the PS3 boots while the Pico
   was already powered.
3. Single Pico with CP2102 5 V into VSYS through a Schottky diode (1N5819):
   works electrically but needs a diode and an extra junction for the servo red
   wire. Not chosen.

Bluetooth DS3 emulation through the dongle (which would free the Pico):
**PROVEN not working yet** (docs/PS3_BLUETOOTH_WAKE.md, 2026-11-22). Both HID
channels open, then the PS3 drops the link (HCI reason 0x14) before any HID
setup. Wake works only because it needs just a page from the paired address
with controller class, no HID session. GIMX implements DS3-over-Bluetooth for
PS3 and is the reference to copy if this is retried; the dongle is a Barrot
chip behind CSR USB IDs, so compatibility is UNKNOWN.

## Software plan

- Pico: `press` (short, power on), `hold <ms>` (~10 s, force off), angle
  calibration, PWM off when idle (no stall current, no jitter).
- PC: check console state first (webMAN HTTP + Tapo P115 wattage). A press on a
  running PS3 shuts it down, so press only when state is known.
- Recovery order after a freeze: smart-plug cut (>= 30 s, force off) -> wait ->
  press (on). **After a kernel panic, press TWICE** (owner-reported 2026-11-27: a
  single press does not boot a panic-standby console; two `PRESS 300`, ~1 s apart).
  Autoboot (sc 377 autoexec) was disabled by the owner 2026-11-27, so AC restore
  no longer boots on its own -> the servo double-press is the recovery.

## On arrival

1. Test both servos sweep ~0-160 deg (listing has no description; 14-day return).
2. Try the OTG single-Pico route (needs the A-A cable) or order the second Pico.
3. Calibrate press angle on the real button, then hook into the recovery loop.

## Sources

- https://www.supercheats.com/playstation-3/how-to/how-to-force-shutdown-the-ps3
- https://support.rockstargames.com/en-US/articles/6ckWtZTyjuGlkQwnKbQUCP/basic-troubleshooting-for-the-playstation-3-console
- https://hackaday.io/project/182243 (servo-on-button failure modes)
- https://docs.micropython.org/en/latest/library/machine.PWM.html (RP2350 PWM)
- https://www.ifixit.com/Teardown/PlayStation-3-Slim/1121/3 (button layout)
- https://github.com/OpenWonderLabs/SwitchBotAPI-BLE/blob/latest/devicetypes/bot.md
- https://github.com/gkoh/pico-cec
