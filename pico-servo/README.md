# pico-servo: PS3 power-button pusher

A Raspberry Pi Pico 2 H running MicroPython drives one SG90 servo that
presses the PS3 front power button. The PC sends line commands over USB serial.
Full background and decisions: `docs/SERVO_POWER_BUTTON.md`.

Status 2026-11-24: code written, **not yet run on hardware** (servos arriving).

## Wiring (no soldering)

| Servo wire | Pico 2 H pin |
|---|---|
| brown | 38 (GND) |
| red | 40 (VBUS, 5 V) |
| orange | 20 (GP15) |

Use male-female Dupont wires: male end into the servo plug, female end onto the
Pico pin. The Pico's own micro-USB cable goes to the **PC** (not the PS3), so
the Pico and servo stay powered when the PS3 is off.

## Flash (one time)

1. Download MicroPython for **RPI_PICO2** (`.uf2`) from
   https://micropython.org/download/RPI_PICO2/
2. Hold BOOTSEL on the Pico, plug it into the PC, release: a drive appears.
   Copy the `.uf2` onto it; the Pico reboots into MicroPython.
3. `pip install mpremote`, then from this folder:
   `mpremote cp main.py :main.py` and `mpremote reset`.

This replaces the DS3 bridge firmware. The PS3 controller role is now covered
by the Bluetooth dongle (`tools/ps3_bt_pad.py`). To go back, flash
`pico-ds3-bridge/firmware/pico_ds3_serial.uf2` the same way.

## Calibrate

Mount the servo (lying flat on a heavy block, arm swinging horizontally into
the button, soft tip, away from the eject button). Then:

```
python tools/ps3_power_button.py angle 90     # find a rest angle just clear of the button
python tools/ps3_power_button.py angle 70     # find the angle that clicks the button
python tools/ps3_power_button.py set rest 90
python tools/ps3_power_button.py set press 70
python tools/ps3_power_button.py rest
```

Pick the press angle that just clicks the button, not further: the servo should
not stall against the case.

## Use

```
python tools/ps3_power_button.py status        # console state + calibration
python tools/ps3_power_button.py on            # only if the console looks OFF
python tools/ps3_power_button.py off --yes     # 10 s force-off hold
python tools/ps3_power_button.py recover --yes # off, then on, then wait for webMAN
```
