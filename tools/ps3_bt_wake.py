"""Wake the PS3 through the external Barrot dongle; never toggles AC power.

Requires administrator rights and local_only/ps3_bt_pairing.json from verified
USB pairing reports. The dongle uses its original BTHUSB driver. Its temporary
RAM address change is verified and restored in finally; a separate recovery
worker also runs if a native call exceeds the deadline.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

from ps3_bt_probe import ProbeError, ds3_pairing, mac
from ps3_bt_windows_probe import radio_session

ROOT = Path(__file__).resolve().parents[1]
PAIRING = ROOT / 'local_only' / 'ps3_bt_pairing.json'
PS3_HOST = '192.168.0.169'


def mac_bytes(value):
    parts = value.split(':')
    if len(parts) != 6 or any(len(p) != 2 for p in parts):
        raise ProbeError('Expected a six-byte Bluetooth address')
    try:
        result = bytes(int(p, 16) for p in parts)
    except ValueError as exc:
        raise ProbeError('Invalid Bluetooth address') from exc
    mac(result)
    return result[::-1]


def load_pairing():
    pair = json.loads(PAIRING.read_text(encoding='utf-8'))
    captured = ds3_pairing(bytes.fromhex(pair['report_f2']), bytes.fromhex(pair['report_f5']))
    for key in ('controller_mac', 'console_mac'):
        if captured[key] != pair[key]:
            raise ProbeError('Pairing file disagrees with captured USB reports')
    if len({pair[k] for k in ('adapter_mac', 'controller_mac', 'console_mac')}) != 3:
        raise ProbeError('Adapter, controller and console addresses must differ')
    for key in ('adapter_mac', 'controller_mac', 'console_mac'):
        mac_bytes(pair[key])
    return pair


def spoof_and_page(query, pair, page, *, activate=None):
    original = mac_bytes(pair['adapter_mac'])
    controller = mac_bytes(pair['controller_mac'])
    if query(5) != original:
        raise ProbeError('Dongle address differs from the expected original; wake not attempted')
    attempted = False
    try:
        attempted = True
        query(5, address=controller)
        if query(5) != controller:
            raise ProbeError('RAM address change did not verify; wake not attempted')
        if activate is not None:
            activate()
            if query(5) != controller:
                raise ProbeError('HCI reset did not retain the temporary address; no page requested')
        page(pair['adapter_mac'], pair['console_mac'])
    finally:
        if attempted:
            if query(5) != original:
                query(5, address=original)
            if activate is not None:
                activate()
            if query(5) != original:
                raise ProbeError('Dongle address restoration did not verify; unplug/replug the dongle')
            print('PROVEN: original dongle address restored.', flush=True)


def page_console(local_mac, console_mac):
    # RFCOMM connection establishment causes the Windows Bluetooth stack to page
    # the specified BR/EDR address. PS3 need not offer an RFCOMM service to wake.
    # A timeout/refusal is never interpreted as proof that the PS3 woke up.
    stream = socket.socket(getattr(socket, 'AF_BLUETOOTH', 32), socket.SOCK_STREAM,
                           getattr(socket, 'BTPROTO_RFCOMM', 3))
    try:
        stream.settimeout(6)
        stream.bind((local_mac, 0))
        print(f'Paging captured controller host {console_mac}...', flush=True)
        try:
            stream.connect((console_mac, 1))
            print('RFCOMM connection completed; checking console boot separately.', flush=True)
        except OSError as exc:
            print(f'RFCOMM result: {exc}; this alone does not establish wake success.', flush=True)
    finally:
        stream.close()


def webman_status():
    try:
        with urllib.request.urlopen(f'http://{PS3_HOST}/cpursx.ps3', timeout=2) as response:
            body = response.read(200000).decode('utf-8', errors='replace')
            return response.status == 200 and 'webMAN' in body, '(XMB)' in body
    except OSError:
        return False, False


def run_child(mode, *, hci_reset=False):
    command = [sys.executable, '-B', str(Path(__file__).resolve()), mode]
    if hci_reset:
        command.append('--hci-reset')
    try:
        return subprocess.run(command, timeout=20, check=False).returncode
    except subprocess.TimeoutExpired:
        print(f'STOP: {mode} exceeded its deadline; its worker was stopped.', flush=True)
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shutdown-first', action='store_true',
                        help='Explicitly permit one normal shutdown from XMB before the wake attempt')
    parser.add_argument('--wake-worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--restore-worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--hci-reset', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.hci_reset and not (args.wake_worker or args.restore_worker):
        raise ProbeError('HCI reset is restricted to explicitly approved diagnostic workers')
    pair = load_pairing()
    if args.wake_worker or args.restore_worker:
        with radio_session(allow_address_change=True,
                           allow_hci_reset=args.hci_reset) as (info, query):
            activate = (lambda: query(0, hci_reset=True)) if args.hci_reset else None
            permitted = {pair['adapter_mac']}
            if args.restore_worker:
                permitted.add(pair['controller_mac'])
            if mac(bytes(info.address.octets)[::-1]) not in permitted:
                raise ProbeError('Windows radio identity differs from the captured adapter')
            if args.restore_worker:
                expected = mac_bytes(pair['adapter_mac'])
                if query(5) != expected:
                    query(5, address=expected)
                if activate is not None:
                    activate()
                if query(5) != expected:
                    raise ProbeError('Address recovery did not verify; unplug/replug the dongle')
                print('Original dongle address verified by recovery worker.', flush=True)
            else:
                spoof_and_page(query, pair, page_console, activate=activate)
        return 0

    online, xmb = webman_status()
    if online:
        if not args.shutdown_first:
            raise ProbeError('Console is already online; no wake test performed')
        if not xmb:
            raise ProbeError('Console is not confirmed at XMB; shutdown refused')
        print('Normal PS3 shutdown requested; AC power remains on.', flush=True)
        with urllib.request.urlopen(f'http://{PS3_HOST}/shutdown.ps3', timeout=5) as response:
            if response.status != 200:
                raise ProbeError('Shutdown request failed')
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if not webman_status()[0]:
                break
            time.sleep(1)
        else:
            raise ProbeError('Console still responds; wake attempt refused')
        time.sleep(8)

    result = 1
    try:
        result = run_child('--wake-worker')
    finally:
        recovery = run_child('--restore-worker')
    if recovery:
        raise ProbeError('Dongle address could not be verified; unplug/replug it before using Bluetooth')
    if result:
        raise ProbeError('Wake worker failed; original dongle address was recovered')
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if webman_status()[0]:
            print('PROVEN: PS3 webMAN returned online after the Bluetooth wake attempt.', flush=True)
            return 0
        time.sleep(2)
    print('UNKNOWN: no boot confirmation received. Check the PS3 power LED; '
          'press its power button if it stayed in standby.', flush=True)
    return 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ProbeError, OSError, ValueError, KeyError) as exc:
        print(f'STOP: {exc}', file=sys.stderr)
        raise SystemExit(1)
