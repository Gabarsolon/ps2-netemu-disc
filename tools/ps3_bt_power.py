"""Windows PS3 Bluetooth wake frontend; never switches the smart plug.

PROVEN on the owner's console: the isolated Linux raw-USB worker can wake it.
Exit zero from that worker means console boot was verified, not just HCI success.
The external radio stays force-shared and attached to WSL after every attempt.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from ps3_bt_wake import webman_status

ROOT = Path(__file__).resolve().parents[1]
DISTRO = 'PS3-Bluetooth'
USBIPD = Path(r'C:\Program Files\usbipd-win\usbipd.exe')
KEEPER = ROOT / 'local_only' / 'bt_wsl_keeper.json'
START_HELPER = ROOT / 'tools' / 'start_ps3_bt_backend.ps1'
WORKER = ROOT / 'tools' / 'ps3_bt_linux.py'


class BackendError(RuntimeError):
    pass


def _decode(data):
    if isinstance(data, str):
        return data
    if b'\x00' in data:
        return data.decode('utf-16', errors='replace')
    return data.decode('utf-8-sig', errors='replace')


def _run(command, log, *, timeout, capture=False):
    """Run only our own bounded child; keep protocol details in the private log."""
    log.write(('COMMAND ' + subprocess.list2cmdline([str(x) for x in command]) + '\n').encode())
    log.flush()
    try:
        result = subprocess.run([str(x) for x in command], stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE if capture else log,
                                stderr=log if capture else subprocess.STDOUT,
                                timeout=timeout, check=False,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired as exc:
        log.write(('TIMEOUT after ' + str(timeout) + ' seconds\n').encode())
        log.flush()
        raise BackendError('Backend command exceeded its deadline') from exc
    if capture and result.stdout:
        log.write(result.stdout)
    log.write(('EXIT ' + str(result.returncode) + '\n').encode())
    log.flush()
    return result


def _selected_radio(state):
    devices = state.get('Devices')
    if not isinstance(devices, list):
        raise BackendError('usbipd returned an unexpected device list')
    matches = [d for d in devices if d.get('BusId') and
               re.match(r'^USB\\VID_0A12&PID_0001\\', d.get('InstanceId', ''), re.I)]
    if len(matches) != 1:
        raise BackendError('Expected exactly one present external 0A12:0001 dongle')
    radio = matches[0]
    guid = radio.get('PersistedGuid')
    if radio.get('IsForced') is not True or not guid or str(guid).strip('{}0-') == '':
        raise BackendError('External dongle must already be force-shared; no driver changes attempted')
    if not re.fullmatch(r'\d+-\d+', radio['BusId']):
        raise BackendError('usbipd returned an invalid bus identifier')
    return radio


def _usb_state(log):
    result = _run([USBIPD, 'state'], log, timeout=10, capture=True)
    if result.returncode:
        raise BackendError('Could not inspect usbipd state')
    try:
        return json.loads(_decode(result.stdout))
    except (ValueError, TypeError) as exc:
        raise BackendError('Could not decode usbipd state') from exc


def ensure_backend(log):
    """Keep our isolated WSL alive and attach only the already-shared radio."""
    powershell = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'WindowsPowerShell' / 'v1.0' / 'powershell.exe'
    result = _run([powershell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                   '-File', START_HELPER, '-ReceiptPath', KEEPER], log, timeout=15)
    if result.returncode:
        raise BackendError('Could not start the isolated Bluetooth backend')
    radio = _selected_radio(_usb_state(log))
    if not radio.get('ClientIPAddress'):
        result = _run([USBIPD, 'attach', '--wsl', '--busid', radio['BusId']], log, timeout=20)
        if result.returncode:
            raise BackendError('Could not attach the external dongle to WSL')
        after = _selected_radio(_usb_state(log))
        if (after['BusId'], after['InstanceId']) != (radio['BusId'], radio['InstanceId']) or not after.get('ClientIPAddress'):
            raise BackendError('External dongle attachment did not verify')


def _linux_worker_path(log):
    result = _run(['wsl.exe', '-d', DISTRO, '-u', 'root', '--exec', 'wslpath', '-u', WORKER.as_posix()],
                  log, timeout=10, capture=True)
    path = _decode(result.stdout).strip()
    if result.returncode or not path.startswith('/') or '\n' in path or '\r' in path:
        raise BackendError('Could not resolve the Linux worker path')
    return path


def _worker(path, mode, log):
    seconds, outer = (85, 95) if mode == '--wake' else (15, 20)
    return _run(['wsl.exe', '-d', DISTRO, '-u', 'root', '--exec', 'timeout',
                 '--signal=TERM', '--kill-after=2s', str(seconds) + 's',
                 'python3', '-B', path, mode], log, timeout=outer).returncode


@contextmanager
def _exclusive_radio():
    # An OS-held byte lock releases even if this frontend exits unexpectedly.
    import msvcrt
    with (ROOT / 'local_only' / 'bt_wake.lock').open('a+b') as lock:
        if lock.seek(0, os.SEEK_END) == 0:
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise BackendError('Another Bluetooth wake attempt is already running') from exc
        try:
            yield
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def wake() -> bool:
    """Wake and verify the PS3, restoring radio identity in a separate worker."""
    if webman_status()[0]:
        print('PS3 is already online.', flush=True)
        return True
    logs = ROOT / 'local_only' / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    log_path = logs / ('bt_wake_' + stamp + '_' + str(os.getpid()) + '.log')
    success = False
    with log_path.open('xb') as log:
        try:
            if sys.platform != 'win32':
                raise BackendError('Use this frontend from Windows')
            with _exclusive_radio():
                ensure_backend(log)
                worker_path = _linux_worker_path(log)
                try:
                    success = _worker(worker_path, '--wake', log) == 0
                finally:
                    try:
                        restored = _worker(worker_path, '--restore-only', log) == 0
                    except (BackendError, OSError) as exc:
                        restored = False
                        log.write(('RESTORE ERROR ' + str(exc) + '\n').encode())
                    if not restored:
                        success = False
                        log.write(b'RESTORE FAILED: radio identity recovery needs attention\n')
        except (BackendError, OSError, ValueError) as exc:
            success = False
            log.write(('ERROR ' + str(exc) + '\n').encode())
    if success:
        print('PS3 is online. Bluetooth dongle remains attached to WSL.', flush=True)
    else:
        print('Bluetooth wake did not complete. Log: ' + str(log_path), flush=True)
    return success


def prepare() -> bool:
    """Verify the attached raw-USB backend before any caller changes AC power.

    This only starts/reuses our backend and restores/checks radio identity. It
    does not contact the console, invoke wake, or alter USB driver ownership.
    """
    logs = ROOT / 'local_only' / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    log_path = logs / ('bt_prepare_' + stamp + '_' + str(os.getpid()) + '.log')
    success = False
    with log_path.open('xb') as log:
        try:
            if sys.platform != 'win32':
                raise BackendError('Use this frontend from Windows')
            with _exclusive_radio():
                ensure_backend(log)
                worker_path = _linux_worker_path(log)
                success = _worker(worker_path, '--restore-only', log) == 0
        except (BackendError, OSError, ValueError) as exc:
            log.write(('ERROR ' + str(exc) + '\n').encode())
    if not success:
        print('Bluetooth backend preflight failed. Log: ' + str(log_path), flush=True)
    return success


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('wake', 'status'))
    args = parser.parse_args()
    if args.command == 'status':
        online = webman_status()[0]
        print('PS3 online.' if online else 'PS3 offline or unreachable.')
        return 0 if online else 1
    return 0 if wake() else 1


if __name__ == '__main__':
    raise SystemExit(main())
