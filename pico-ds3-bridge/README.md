# Pico 2 DualShock 3 Serial Bridge

A high-performance hardware bridge and PC remote control system for the **PlayStation 3** using a **Raspberry Pi Pico 2 (RP2350)** and a **CP2102 USB-to-UART TTL module**.

Enables complete remote control of a PS3 from a PC over serial (COM port) with **sub-millisecond latency**, supporting PC keyboard play, custom Python automation, macros, and autonomous AI gaming with video capture cards.

---

## Architecture Overview

```
+--------------------------------------------------------------------+
|                              PC                                    |
|                                                                    |
|  [ps3_keyboard_remote.py]  OR  [AI Agent / Python Script]          |
|                       |                                            |
|                       v                                            |
|             [CP2102 USB-UART Bridge] (COM9)                        |
+--------------------------------------------------------------------+
                           |   |   |
                   TXD/RXD |   |   | GND (3.3V Logic, NO power wire!)
                           v   v   v
+--------------------------------------------------------------------+
|                    Raspberry Pi Pico 2 (RP2350)                    |
|                                                                    |
|   Hardware UART0 (GP0/GP1 @ 115200 baud) <-> Command Parser        |
|                                 |                                  |
|                                 v                                  |
|   Genuine DualShock 3 Emulation Stack (054C:0268, Raw-Wire EP0)    |
|                                 |                                  |
|   Native Micro-USB Port (100 Hz HID Interrupt IN/OUT)              |
+--------------------------------------------------------------------+
                                  |
                                  | USB Cable
                                  v
+--------------------------------------------------------------------+
|                         PlayStation 3                              |
|       (Recognized as genuine Sony DualShock 3 / Player 1)          |
+--------------------------------------------------------------------+
```

---

## Hardware & Wiring

### Connections

| CP2102 Pin | Wire Color | Pico 2 Pin | Pico Pin # | Function |
| :--- | :--- | :--- | :--- | :--- |
| **TXD** | Yellow | **GP1** | Pin 2 | UART0 RX (receives commands from PC) |
| **RXD** | Green | **GP0** | Pin 1 | UART0 TX (sends responses/logs to PC) |
| **GND** | Black | **GND** | Pin 3 | Common Ground Reference |
| **5V / 3V3** | *None* | *None* | *None* | **DO NOT CONNECT!** |

> [!WARNING]
> **Power Isolation**: Never connect the `5V` or `3V3` pins between the CP2102 and the Pico.
> * The **Pico 2** is powered exclusively by the **PS3** via its micro-USB cable.
> * The **CP2102** is powered exclusively by the **PC** via its USB port.
> * Connecting the voltage pins can cause ground loops or voltage contention between the PC and PS3 power supplies.

---

## Technical Details: DualShock 3 Emulation on RP2350

### 1. USB Descriptors
* **VID / PID**: `0x054C` / `0x0268` (Official Sony DualShock 3)
* **Device Descriptor**: `bcdDevice` 0x0100, `bMaxPacketSize0` = 64, 1 Configuration.
* **Configuration Descriptor**: 41 bytes, 1 HID Interface (Interface 0), Interrupt IN EP `0x81` (64 bytes, 1ms polling), Interrupt OUT EP `0x02` (64 bytes, 1ms polling).
* **Report Descriptor**: 148 bytes (authentic native Sixaxis / DualShock 3 descriptor).

### 2. The TinyUSB Feature Report Bug & Raw-Wire Fix
On genuine PS3 hardware, the console sends control transfers to Endpoint 0 requesting specific Feature Reports to authenticate and initialize the controller:
* `GET_REPORT (0x01)`: 64-byte capabilities (starts with `00 01...`)
* `GET_REPORT (0xF2)`: 64-byte device MAC & firmware version (starts with `F2 FF FF...`)
* `GET_REPORT (0xEF)`: 64-byte calibration & gyro data (starts with `00 EF...`)
* `GET_REPORT (0xF5)`: 64-byte host Bluetooth pairing address
* `SET_REPORT (0xF4)`: Activation packet (`42 0C 00 00`), enabling active input streaming.

**The Bug**: Standard TinyUSB's default HID implementation (`hid_device.c`) automatically prepends the requested `report_id` to the front of every feature buffer. This caused `0xF2` to be transmitted as `F2 F2 FF...` and `0x01` as `01 01 04...`. The PS3 rejected these malformed headers and refused to activate the controller.

**The Solution (`usb_hooks.c`)**:
We intercept EP0 feature requests before TinyUSB's generic HID handler via `modec_hid_feature_request()` and service them directly through `tud_control_xfer()` with the exact byte layout required by the PS3. This results in immediate handshake completion (`streaming=1`).

### 3. The PS Button State Latch Fix
* **The Symptom**: D-Pad and face buttons worked immediately, but the PS button (tapping or holding) did nothing.
* **The Root Cause**:
  * An empty stub for `tud_hid_report_complete_cb` in `usb_descriptors.c` discarded report transmission acknowledgments.
  * In `ds3.c`, an initial 1.5-second boot pulse used `ps_pending = true` to auto-pair Player 1 on the PS3. Because the ACK callback was never dispatched, `ps_pending` was never cleared and remained `true` forever.
  * As a result, `report[3] |= 0x01` was sent in every 100 Hz USB packet indefinitely. Because the PS button was permanently high from second 1.5 onward, the PS3 never saw a transition (0 -> 1 -> 0) and ignored all subsequent taps or holds.
* **The Resolution**:
  1. Connected `tud_hid_report_complete_cb` in `main.c` directly to `ds3_input_acked((report[4] & 1) != 0)`.
  2. Added an explicit time-expiry safeguard to `ds3_ps_value()` in `ds3.c` ensuring `ps_pending` drops to `false` once the 250ms boot pulse elapses.
  3. Decoupled serial commands (`DOWN PS`, `UP PS`, `PRESS PS <ms>`) to directly manipulate `current_ps` and `ps_release_time`, preventing collision with internal state machine timers.
  4. Added UART telemetry messages `[DS3] PS BUTTON PRESSED` and `[DS3] PS BUTTON RELEASED` to confirm exact wire transitions.

---

## Serial Control Protocol

* **Port**: Virtual COM Port assigned to CP2102 (e.g. `COM9`)
* **Baud Rate**: `115200`
* **Format**: 8 Data bits, No Parity, 1 Stop bit (8N1)
* **Line Ending**: `\r\n` or `\n`

### Supported Commands

| Command | Arguments | Description | Example |
| :--- | :--- | :--- | :--- |
| `PRESS` | `<BTN> [HOLD_MS]` | Press a button and auto-release after duration (default 120ms). | `PRESS CROSS 150` |
| `DOWN` | `<BTN>` | Hold a button down indefinitely (for long-presses). | `DOWN PS` |
| `UP` | `<BTN>` | Release a held button. | `UP PS` |
| `STICK` | `<L\|R> <X> <Y>` | Set analog stick (0=Up/Left, 128=Center, 255=Down/Right). | `STICK L 128 0` |
| `PS` | *None* | Shortcut to tap the PS (Home) button. | `PS` |
| `RELEASE` | *None* | Release all buttons and center all analog sticks. | `RELEASE` |
| `STATUS` | *None* | Query live USB mount, streaming status, and active inputs. | `STATUS` |

### Supported Button Identifiers (Case-Insensitive)
* **Face Buttons**: `CROSS` (or `X`), `CIRCLE` (or `O`), `SQUARE` (or `SQ`), `TRIANGLE` (or `TRI`)
* **D-Pad**: `UP`, `DOWN`, `LEFT`, `RIGHT`
* **Shoulders**: `L1`, `R1`, `L2`, `R2`
* **Thumbsticks**: `L3`, `R3`
* **System**: `START`, `SELECT`, `PS`

---

## Long-Pressing Functionality

Long-press behavior is fully supported at the hardware level:

1. **In `ps3_keyboard_remote.py`**:
   * Holding down the **Escape** or **P** key on your PC keyboard sends `DOWN PS`.
   * The Pico maintains `report[3] |= 0x01` in every 100 Hz USB report sent to the PS3.
   * Releasing the key triggers `UP PS`.
   * Holding the key for 1–2 seconds brings up the PS3 in-game quit / power-off system menu.

2. **In Python Code**:
   ```python
   from ps3_controller import PS3Controller
   import time

   ctl = PS3Controller("COM9")

   # Method 1: Timed long press
   ctl.press("PS", duration_ms=2000)

   # Method 2: Explicit hold and release
   ctl.down("PS")
   time.sleep(2.0)
   ctl.up("PS")
   ```

---

## Software Tools

### 1. Interactive Keyboard Remote (`python/ps3_keyboard_remote.py`)
A low-latency Pygame HUD for real-time play:
```powershell
python python/ps3_keyboard_remote.py
```

#### Controls:
* **D-Pad**: Arrow Keys
* **Left Analog Stick**: `W` / `A` / `S` / `D`
* **Cross (X)**: `Enter`, `K`, or `X`
* **Circle (O)**: `Backspace`, `L`, or `C`
* **Square ([ ])**: `J` or `Z`
* **Triangle (/\\)**: `I` or `V`
* **L1 / R1**: `Q` / `E`
* **L2 / R2**: `1` / `2`
* **Start / Select**: `Space` / `Tab`
* **PS (Home) Button**: `Escape` or `P` (Tap for XMB, Hold for Power/Quit Menu)

### 2. Python Controller API (`python/ps3_controller.py`)
Clean Python library for automating games or building AI agents:
```python
from ps3_controller import PS3Controller

ctl = PS3Controller("COM9")

# Navigate XMB
ctl.press("UP")
ctl.press("DOWN")
ctl.press("CROSS")

# Analog stick control
ctl.stick("L", 128, 0)    # Full Forward
ctl.stick("L", 128, 128)  # Center

ctl.close()
```

### 3. Auto-Flasher (`python/flash_ds3.py`)
Watches for the Pico in BOOTSEL mode and flashes the firmware automatically:
```powershell
python python/flash_ds3.py
```

---

## Directory Structure

```
pico-ds3-bridge/
├── README.md                      # This documentation
├── firmware/
│   ├── CMakeLists.txt             # Ninja/CMake build definition
│   ├── tusb_config.h              # TinyUSB device configuration (64-byte EP0)
│   ├── usb_descriptors.c          # Clean 148-byte DS3 descriptor & strings
│   ├── usb_hooks.c                # Raw-wire feature transfer handler
│   ├── usb_trace.h                # Feature request interface
│   ├── ds3.c / ds3.h              # DS3 feature generators (F2/01/EF/F4/F5)
│   ├── main.c                     # UART parser + 100 Hz USB HID task
│   └── pico_ds3_serial.uf2        # Precompiled binary ready to flash
└── python/
    ├── ps3_controller.py          # Python driver library
    ├── ps3_keyboard_remote.py     # Real-time keyboard remote GUI
    └── flash_ds3.py               # Auto-flasher tool
```
