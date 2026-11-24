"""Keyboard remote for the PS3 over the Bluetooth dongle (no Pico needed).

Same window and keys as pico-ds3-bridge/python/ps3_keyboard_remote.py:
  Arrows = D-pad, WASD = left stick, Enter/K/X = Cross, Backspace/L/C = Circle,
  J/Z = Square, I/V = Triangle, Q/E = L1/R1, 1/2 = L2/R2,
  Space = Start, Tab = Select, Esc/P = PS (tap = XMB, hold = quit/power menu).

The PS3 must be on (XMB or a game). Connecting takes ~5-10 s.
Run:  python tools/ps3_bt_keyboard_remote.py   (or double-click ps3_bt_remote.bat)
"""
import runpy
import sys
from pathlib import Path

REMOTE = Path(__file__).resolve().parents[1] / 'pico-ds3-bridge' / 'python' / 'ps3_keyboard_remote.py'

if __name__ == '__main__':
    sys.argv = [str(REMOTE), '--bt']
    runpy.run_path(str(REMOTE), run_name='__main__')
