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
owner's PS3 slim (role switch enabled, 17-byte F2 report); also in PS2 games.

Reconnect: the PS3 tells controllers to disconnect (SET F4 42 08) when entering
or leaving the PS2 emulator AND when powering off - indistinguishable. Paging a
PS3 that is off wakes it, so auto-reconnect only happens once webMAN HTTP has
been up for a while (back at XMB). Otherwise a PS press reconnects, like a DS3.
"""
from __future__ import annotations

import queue
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

TOOL = Path(__file__).resolve().with_name('ps3_bt_controller.py')
HOST = '192.168.0.169'


def http_up(timeout=2):
    try:
        urllib.request.urlopen(f'http://{HOST}/', timeout=timeout)
        return True
    except Exception:
        return False


class PS3BtPad:
    STABLE_S = 10   # webMAN must be up this long before an automatic reconnect
    SETTLE_S = 15   # and at least this long after the disconnect

    def __init__(self, seconds=3600, connect_timeout=45, verbose=False, auto_reconnect=True):
        self.seconds, self.verbose, self.auto_reconnect = seconds, verbose, auto_reconnect
        self.lines = queue.Queue()      # OK/ERR replies + INFO lines for callers
        self.proc = None
        self.connected = False
        self.closing = False
        self.ended = None
        self.reconnect_now = threading.Event()
        self._last_error = None
        if not self._start_session(connect_timeout):
            raise RuntimeError('Bluetooth pad failed: ' + (self._last_error or 'did not become READY'))
        if auto_reconnect:
            threading.Thread(target=self._supervise, daemon=True).start()

    # ---- session management -------------------------------------------------
    def _start_session(self, connect_timeout):
        self._last_error = None
        self.ready = threading.Event()
        self.ended = threading.Event()
        self.proc = subprocess.Popen(
            [sys.executable, str(TOOL), '--serve', '--seconds', str(self.seconds)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1)
        threading.Thread(target=self._pump, args=(self.proc, self.ready, self.ended),
                         daemon=True).start()
        if not self.ready.wait(connect_timeout) or self.ended.is_set():
            self._stop_proc()
            return False
        self.connected = True
        return True

    def _pump(self, proc, ready, ended):
        logs = TOOL.parents[1] / 'local_only' / 'logs'
        logs.mkdir(parents=True, exist_ok=True)
        log = (logs / time.strftime('bt_pad_%Y%m%dT%H%M%S.log')).open('a', encoding='utf-8')
        for line in proc.stdout:
            line = line.rstrip('\r\n')
            log.write(line + '\n')
            log.flush()
            if self.verbose:
                print('[pad]', line, flush=True)
            if line == 'READY':
                ready.set()
            elif line.startswith('STOP:'):
                self._last_error = line
                if self.connected:
                    self.lines.put('INFO disconnected by console: ' + line[5:].strip())
            elif line.startswith(('OK', 'ERR')):
                self.lines.put(line)
        log.close()
        self.connected = False
        ended.set()

    def _supervise(self):
        while not self.closing:
            self.ended.wait()
            if self.closing:
                return
            self._stop_proc()
            self.lines.put('INFO DISCONNECTED - auto-reconnect when back at XMB; '
                           'press PS (Esc/P) to reconnect now')
            lost_at, up_since = time.monotonic(), None
            while not self.closing:
                if self.reconnect_now.wait(3):
                    self.reconnect_now.clear()
                    if self.closing:
                        return
                    reason = 'PS pressed'
                else:
                    now = time.monotonic()
                    up_since = (up_since or now) if http_up() else None
                    if not (up_since and now - up_since >= self.STABLE_S
                            and now - lost_at >= self.SETTLE_S):
                        continue
                    reason = 'XMB is back'
                self.lines.put(f'INFO reconnecting ({reason})...')
                if self._start_session(45):
                    self.lines.put('INFO RECONNECTED')
                    break
                self.lines.put('INFO reconnect failed: ' + (self._last_error or 'not READY')
                               + ' - will retry')
                self.reconnect_now.clear()
                up_since = None
                time.sleep(5)

    def _stop_proc(self):
        proc = self.proc
        if proc is None or proc.poll() is not None:
            return
        try:
            proc.stdin.write('QUIT\n')
            proc.stdin.flush()
            proc.stdin.close()
        except (OSError, ValueError):
            pass
        try:
            proc.wait(timeout=60)  # worker restores the dongle identity first
        except subprocess.TimeoutExpired:
            proc.terminate()

    # ---- commands -----------------------------------------------------------
    @staticmethod
    def _is_ps(cmd):
        words = cmd.upper().split()
        return bool(words) and (words[0] == 'PS' or
                                (words[0] in ('DOWN', 'PRESS') and len(words) > 1 and words[1] == 'PS'))

    def write_line(self, cmd):
        """Fire-and-forget command; never raises. Used by the keyboard remote."""
        cmd = cmd.strip()
        if not cmd:
            return
        if not self.connected:
            if self._is_ps(cmd):
                self.reconnect_now.set()
            return
        try:
            self.proc.stdin.write(cmd + '\n')
            self.proc.stdin.flush()
        except (OSError, ValueError):
            self.connected = False

    def _next(self, timeout):
        try:
            return self.lines.get(timeout=max(0.01, timeout))
        except queue.Empty:
            return None

    def send_cmd(self, cmd, timeout=2.0):
        if not self.connected:
            if self._is_ps(cmd):
                self.reconnect_now.set()
            raise RuntimeError('Bluetooth pad disconnected (reconnecting)')
        self.write_line(cmd)
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
        self.closing = True
        self.reconnect_now.set()
        if self.ended is not None:
            self.ended.set()
        self._stop_proc()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class SerialShim:
    """pyserial-like object so pico-ds3-bridge scripts can drive the BT pad."""

    def __init__(self, pad):
        self.pad = pad
        self.buffer = []

    def write(self, data):
        for line in data.decode('utf-8', 'ignore').replace('\r', '').split('\n'):
            self.pad.write_line(line)
        return len(data)

    def _drain(self):
        while True:
            try:
                line = self.pad.lines.get_nowait()
            except queue.Empty:
                return
            if line is not None:
                self.buffer.append(line)

    @property
    def in_waiting(self):
        self._drain()
        return len(self.buffer)

    def readline(self):
        self._drain()
        return (self.buffer.pop(0) + '\n').encode() if self.buffer else b''

    def reset_input_buffer(self):
        self._drain()
        self.buffer.clear()

    def close(self):
        self.pad.close()


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    shell = args[0] == 'shell'
    with PS3BtPad(seconds=21600 if shell else 300, auto_reconnect=shell) as pad:
        if shell:
            print('READY. Commands: PRESS <btn> [ms] | DOWN/UP <btn> | STICK <L|R> x y | RELEASE | QUIT')
            for line in sys.stdin:
                if line.strip().upper() == 'QUIT':
                    break
                if line.strip():
                    try:
                        print(pad.send_cmd(line.strip()))
                    except RuntimeError as exc:
                        print(exc)
        else:
            print(pad.send_cmd(' '.join(args)))
            if args[0].upper() == 'PRESS':
                time.sleep((int(args[2]) if len(args) > 2 else 120) / 1000 + 0.1)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
