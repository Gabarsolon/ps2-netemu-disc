"""Explicit PS3 identity experiment over Linux USB; no console power actions.

Uses captured controller reports and only the external 0A12:0001 dongle.
Standard reset: HCI 0x0C03, no parameters. Connection layout follows
FreeTHX/pywakepsx-on-bt hci.py (R2, no clock hint, role switch allowed).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import sys
import time

from ps3_bt_probe import BARROT, BARROT_OPCODE, HciReader, ProbeError, READ_ADDRESS, READ_VERSION, mac
from ps3_bt_wake import load_pairing, mac_bytes, spoof_and_page, webman_status


def connection_packet(console_mac):
    payload = mac_bytes(console_mac) + struct.pack('<HBBHB', 0xCC18, 2, 0, 0, 1)
    return struct.pack('<HB', 0x0405, len(payload)) + payload


def connection_event(raw, target_le):
    raw = bytes(raw)
    if len(raw) < 2 or len(raw) != raw[1] + 2:
        raise ProbeError('Truncated HCI connection event')
    if raw[0] == 0x0F:
        if len(raw) != 6:
            raise ProbeError('Malformed HCI Command Status')
        if int.from_bytes(raw[4:6], 'little') == 0x0405 and raw[2]:
            return raw[2], None
    elif raw[0] == 0x03:
        if len(raw) != 13:
            raise ProbeError('Malformed HCI Connection Complete')
        if raw[5:11] == target_le:
            return raw[2], int.from_bytes(raw[3:5], 'little') if raw[2] == 0 else None
    return None


class LinuxRadio(HciReader):
    def __init__(self, pair, *, keep_kernel_detached=False):
        self.allowed_addresses = {mac_bytes(pair['adapter_mac']), mac_bytes(pair['controller_mac'])}
        self.console_mac = pair['console_mac']
        self.class_values = {b'\x08\x05\x00'}
        super().__init__()
        self.keep_kernel_detached = keep_kernel_detached

    def close(self):
        if getattr(self, 'keep_kernel_detached', False):
            self.detached = False
        super().close()

    def class_of_device(self, value=None):
        if value is not None:
            value = bytes(value)
            if value not in self.class_values:
                raise ProbeError('Device class is neither the saved original nor the controller class')
            if self._exchange(0x0C24, value):
                raise ProbeError('Unexpected class-write response')
            return None
        value = self._exchange(0x0C23, b'')
        if len(value) != 3:
            raise ProbeError('Device class must contain three bytes')
        return value

    def address(self, command, *, address=None):
        if command != 5:
            raise ProbeError('Only the Barrot address parameter is available here')
        if address is None:
            reply = self.query(BARROT_OPCODE, b'\x05\x00')
            if len(reply) != 8 or reply[:2] != b'\x05\x00':
                raise ProbeError('Unexpected Barrot address reply')
            return reply[2:]
        address = bytes(address)
        if address not in self.allowed_addresses:
            raise ProbeError('Address write is not one of the two captured identities')
        reply = self._exchange(BARROT_OPCODE, b'\x05\x00' + address)
        if reply != b'\x05\x00':
            raise ProbeError('Unexpected Barrot address-write reply')
        return b''

    def reset(self):
        print('Standard HCI Reset 0x0C03', flush=True)
        reply = self._exchange(0x0C03, b'')
        if reply:
            raise ProbeError('Unexpected standard HCI Reset response')

    def activate(self):
        self.reset()
        address = self.query(READ_ADDRESS)
        if len(address) != 6 or address != self.address(5):
            raise ProbeError('Standard and Barrot address reads disagree after reset')
        print('Standard address after reset:', mac(address[::-1]), flush=True)

    def page(self, local_mac, console_mac, *, hold_seconds=0):
        if console_mac != self.console_mac:
            raise ProbeError('Page target differs from captured console')
        if not 0 <= hold_seconds <= 8:
            raise ProbeError('Connection hold exceeds the diagnostic bound')
        packet = connection_packet(console_mac)
        print('TX', packet.hex(' '), flush=True)
        count = self.dev.ctrl_transfer(0x20, 0, 0, 0, packet, timeout=2000)
        if count != len(packet):
            raise ProbeError('Short HCI Create Connection transfer')
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            remaining = max(1, int((deadline - time.monotonic()) * 1000))
            try:
                raw = bytes(self.events.read(260, timeout=remaining))
            except self.usb.USBTimeoutError as exc:
                raise ProbeError('No Connection Complete before the diagnostic deadline') from exc
            print('RX', raw.hex(' '), flush=True)
            result = connection_event(raw, mac_bytes(console_mac))
            if result is not None:
                status, handle = result
                print(f'Connection result: 0x{status:02X}', flush=True)
                if handle is not None:
                    if hold_seconds:
                        print('Holding the controller-class link active...', flush=True)
                        time.sleep(hold_seconds)
                    # Clear our own newly established ACL before restoring identity.
                    self.reset()
                return status
        raise ProbeError('No matching console Connection Complete received')


def controller_page(radio, local_mac, console_mac):
    controller_class = b'\x08\x05\x00'
    radio.class_of_device(controller_class)
    if radio.class_of_device() != controller_class:
        raise ProbeError('Controller device class did not verify; no page requested')
    return radio.page(local_mac, console_mac, hold_seconds=3)


def wait_for_usb():
    import usb.core
    deadline = time.monotonic() + 25
    while usb.core.find(idVendor=0x0A12, idProduct=1) is None:
        if time.monotonic() >= deadline:
            raise ProbeError('External dongle did not enumerate in Linux within 25 seconds')
        time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--identity-check', action='store_true')
    mode.add_argument('--restore-only', action='store_true')
    mode.add_argument('--wake', action='store_true')
    args = parser.parse_args()
    if not sys.platform.startswith('linux'):
        raise ProbeError('Direct USB backend requires Linux')
    pair = load_pairing()
    wait_for_usb()
    radio = LinuxRadio(pair, keep_kernel_detached=args.wake or args.restore_only)
    previous_class = None
    error = None
    state_file = Path(__file__).resolve().parents[1] / 'local_only' / 'ps3_bt_radio_state.json'
    try:
        version = radio.query(READ_VERSION)
        if len(version) != 8 or int.from_bytes(version[4:6], 'little') != BARROT:
            raise ProbeError('Unexpected manufacturer; no address writes requested')
        original = mac_bytes(pair['adapter_mac'])
        permitted = {original}
        if args.restore_only:
            permitted.add(mac_bytes(pair['controller_mac']))
        if radio.query(READ_ADDRESS) not in permitted or radio.address(5) not in permitted:
            raise ProbeError('Unexpected initial radio identity; no address writes requested')
        observed_class = radio.class_of_device()
        previous_class = observed_class
        if state_file.is_file():
            saved = json.loads(state_file.read_text())
            if saved['adapter_mac'] != pair['adapter_mac']:
                raise ProbeError('Saved radio class belongs to another adapter')
            previous_class = bytes.fromhex(saved['class'])
            if len(previous_class) != 3:
                raise ProbeError('Invalid saved original radio class')
        else:
            state_file.write_text(json.dumps({'adapter_mac': pair['adapter_mac'],
                                              'class': previous_class.hex()}, indent=2))
        radio.class_values.add(previous_class)
        if args.restore_only:
            radio.address(5, address=original)
            radio.activate()
            if radio.address(5) != original:
                raise ProbeError('Linux address recovery did not verify')
        else:
            outcome = []
            def page(local_mac, console_mac):
                if args.wake:
                    outcome.append(controller_page(radio, local_mac, console_mac))
                else:
                    outcome.append(radio.page(local_mac, console_mac))
            try:
                spoof_and_page(radio.address, pair, page, activate=radio.activate)
                if outcome != [0]:
                    raise ProbeError('Console did not accept the temporary identity: ' + str(outcome))
            except (ProbeError, OSError) as exc:
                if not args.wake:
                    raise
                error = exc
    finally:
        try:
            if previous_class is not None:
                radio.class_of_device(previous_class)
                if radio.class_of_device() != previous_class:
                    raise ProbeError('Original device class restoration did not verify')
        finally:
            radio.close()
    if args.restore_only:
        print('PROVEN: original dongle address and class restored.', flush=True)
        return 0
    if not args.wake:
        print('PROVEN: console accepted an ACL connection. This alone does not prove wake.', flush=True)
        return 0
    if error:
        print('Bluetooth attempt result:', error, flush=True)
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if webman_status()[0]:
            print('PROVEN: PS3 webMAN returned online after the controller-class wake.', flush=True)
            return 0
        time.sleep(2)
    print('UNKNOWN: no console boot confirmation after wake.', flush=True)
    return 1

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ProbeError, OSError, ImportError, ValueError, KeyError) as exc:
        print('STOP:', exc, file=sys.stderr, flush=True)
        raise SystemExit(1)
