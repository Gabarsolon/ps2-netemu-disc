import serial
import time

class PS3Controller:
    """Python interface to control PS3 via Raspberry Pi Pico 2 & CP2102 Serial Bridge."""

    def __init__(self, port="COM9", baudrate=115200, timeout=0.2):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(0.1)
        self.ser.reset_input_buffer()

    def send_cmd(self, cmd, timeout=1.5):
        self.ser.reset_input_buffer()
        line = cmd.strip() + "\r\n"
        self.ser.write(line.encode("utf-8"))
        start = time.time()
        while time.time() - start < timeout:
            raw = self.ser.readline()
            if not raw:
                continue
            resp = raw.decode("utf-8", errors="ignore").strip()
            if resp.startswith("OK") or resp.startswith("ERR") or resp.startswith("STATUS"):
                return resp
        return ""

    def press(self, button, duration_ms=100):
        """Tap a button (CROSS, CIRCLE, SQUARE, TRIANGLE, UP, DOWN, LEFT, RIGHT, L1, R1, L2, R2, START, SELECT, PS)."""
        duration_ms = max(20, int(duration_ms))
        response = self.send_cmd(f"PRESS {button} {duration_ms}")
        # Firmware acknowledges when the timed press starts. Wait until it
        # finishes so close() cannot cancel it with an immediate RELEASE.
        if response.startswith("OK PRESS "):
            time.sleep(duration_ms / 1000.0)
        return response

    def down(self, button):
        """Hold a button down."""
        return self.send_cmd(f"DOWN {button}")

    def up(self, button):
        """Release a held button."""
        return self.send_cmd(f"UP {button}")

    def stick(self, which, x, y):
        """Set analog stick. which: 'L' or 'R', x: 0-255, y: 0-255 (128 is center)."""
        return self.send_cmd(f"STICK {which} {x} {y}")

    def ps_button(self, duration_ms=300):
        """Tap the PlayStation (Home) button."""
        return self.press("PS", duration_ms)

    def hold_ps_button(self, duration_ms=2000):
        """Hold the PS (Home) button (brings up In-Game / Turn Off Console menu)."""
        return self.press("PS", duration_ms)

    def release_all(self):
        """Release all buttons and center all analog sticks."""
        return self.send_cmd("RELEASE")

    def get_status(self):
        """Get connection and controller state from Pico."""
        return self.send_cmd("STATUS")

    def close(self):
        self.release_all()
        self.ser.close()

if __name__ == "__main__":
    import sys
    print("Testing PS3 Controller Interface on COM9...")
    try:
        ctl = PS3Controller("COM9")
        print("Connected!")
        print("Status:", ctl.get_status())
        print("Tapping CROSS button...")
        print(ctl.press("CROSS", 100))
        ctl.close()
        print("Test passed.")
    except Exception as e:
        print("Error:", e)
