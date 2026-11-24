"""PS3 controller over the external Bluetooth dongle (no Pico needed).

Same API as pico-ds3-bridge/python/ps3_controller.py:

    from ps3_bt_pad import PS3BtPad
    pad = PS3BtPad()            # connects; PS3 must be on (XMB or game)
    pad.press('cross')
    pad.down('ps'); time.sleep(2); pad.up('ps')
    pad.stick('L', 128, 0)
    pad.close()

CLI: python tools/ps3_bt_pad.py press up 300   |   python tools/ps3_bt_pad.py shell

Runs tools/ps3_bt_controller.py --serve (WSL raw-HCI backend), which spoofs the
paired DS3 address on the dongle for the session and restores it on exit.
PROVEN 2026-11-24: full DS3 HID handshake + accepted D-pad input on the
owner's PS3 slim (role switch enabled, 17-byte F2 report).
"""
from __future__ import annotations

import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

TOOL = Path(__file__).resolve().with_name('ps3_bt_controller.py')


class PS3BtPad:
    def __init__(self, seconds=3600, connect_timeout=45, verbose=False):
        self.verbose = verbose
        self.proc = subprocess.Popen(
            [sys.executable, str(TOOL), '--serve', '--seconds', str(seconds)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1)
        self.lines = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()
        deadline = time.monotonic() + connect_timeout
        while time.monotonic() < deadline:
            line = self._next(deadline - time.monotonic())
            if line is None:
                break
            if line == 'READY':
                return
            if line.startswith('STOP:') or line.startswith('Controller diagnostic log'):
                self.close()
                raise RuntimeError('Bluetooth pad failed: ' + line)
        self.close()
        raise RuntimeError('Bluetooth pad did not become READY')

    def _pump(self):
        for line in self.proc.stdout:
            line = line.rstrip('\r\n')
            if self.verbose:
                print('[pad]', line, flush=True)
            if line.startswith(('READY', 'OK', 'ERR', 'STOP:', 'SESSION END', 'Controller diagnostic log')):
                self.lines.put(line)
        self.lines.put(None)

    def _next(self, timeout):
        try:
            return self.lines.get(timeout=max(0.01, timeout))
        except queue.Empty:
            return None

    def send_cmd(self, cmd, timeout=2.0):
        if self.proc.poll() is not None:
            raise RuntimeError('Bluetooth pad session has ended')
        self.proc.stdin.write(cmd + '\n')
        self.proc.stdin.flush()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            line = self._next(deadline - time.monotonic())
            if line is None:
                break
            if line.startswith(('OK', 'ERR')):
                return line
        raise RuntimeError(f'No reply to {cmd!r}')

    def press(self, button, duration_ms=120):
        reply = self.send_cmd(f'PRESS {button} {duration_ms}')
        time.sleep(duration_ms / 1000 + 0.03)
        return reply

    def down(self, button):
        return self.send_cmd(f'DOWN {button}')

    def up(self, button):
        return self.send_cmd(f'UP {button}')

    def stick(self, which, x, y):
        return self.send_cmd(f'STICK {which} {x} {y}')

    def ps_button(self, duration_ms=300):
        return self.press('ps', duration_ms)

    def hold_ps_button(self, duration_ms=2000):
        return self.press('ps', duration_ms)

    def release_all(self):
        return self.send_cmd('RELEASE')

    def close(self):
        if self.proc.poll() is None:
            try:
                self.proc.stdin.write('QUIT\n')
                self.proc.stdin.flush()
                self.proc.stdin.close()
            except OSError:
                pass
            try:
                self.proc.wait(timeout=60)  # worker restores the dongle identity first
            except subprocess.TimeoutExpired:
                self.proc.terminate()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    with PS3BtPad(seconds=21600 if args[0] == 'shell' else 300) as pad:
        if args[0] == 'shell':
            print('READY. Commands: PRESS <btn> [ms] | DOWN/UP <btn> | STICK <L|R> x y | RELEASE | QUIT')
            for line in sys.stdin:
                if line.strip().upper() == 'QUIT':
                    break
                if line.strip():
                    try:
                        print(pad.send_cmd(line.strip()))
                    except RuntimeError as exc:
                        print(exc)
                        break
        else:
            print(pad.send_cmd(' '.join(args)))
            if args[0].upper() == 'PRESS':
                time.sleep((int(args[2]) if len(args) > 2 else 120) / 1000 + 0.1)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
