"""Wake the owner's PS3 using the GIMX Sixaxis HID connection pattern.

Linux only. Uses the external 0A12:0001 already assigned through USB/IP.
No pairing writes, console firmware writes, AC toggles, or USB ownership changes.
References: GIMX sixaxis.c/l2cap_bluez.c and BlueZ hci.h.
"""
from __future__ import annotations

import argparse
import errno
from pathlib import Path
import select
import socket
import struct
import sys
import time

from ps3_bt_probe import BARROT, BARROT_OPCODE, ProbeError, mac, parse_complete
from ps3_bt_wake import load_pairing, mac_bytes, spoof_and_page, webman_status
from ps3_ds3_hid import DS3Hid


def find_radio():
    found = []
    for entry in Path('/sys/class/bluetooth').glob('hci*'):
        for parent in entry.resolve().parents:
            try:
                identity = ((parent / 'idVendor').read_text().strip(),
                            (parent / 'idProduct').read_text().strip())
            except FileNotFoundError:
                continue
            if identity == ('0a12', '0001'):
                found.append(int(entry.name[3:]))
            break
    if len(found) != 1:
        raise ProbeError('Expected exactly one kernel Bluetooth radio on external USB 0A12:0001')
    return found[0]


class KernelRadio:
    def __init__(self, pair):
        import fcntl
        self.fcntl = fcntl
        self.index = find_radio()
        self.addresses = {mac_bytes(pair['adapter_mac']), mac_bytes(pair['controller_mac'])}
        self.classes = {b'\x08\x05\x00'}
        self.stream = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
        try:
            self.stream.bind((self.index,))
            self.stream.setsockopt(0, 2, struct.pack('<IIIH2x', 1 << 4, 0xFFFFFFFF, 0xFFFFFFFF, 0))
            try:
                fcntl.ioctl(self.stream.fileno(), 0x400448C9, self.index)  # HCIDEVUP
            except OSError as exc:
                if exc.errno != errno.EALREADY:
                    raise
            self.stream.settimeout(3)
        except BaseException:
            self.stream.close()
            raise

    def kernel_address(self):
        info = bytearray(256)
        struct.pack_into('<H', info, 0, self.index)
        self.fcntl.ioctl(self.stream.fileno(), 0x800448D3, info, True)  # HCIGETDEVINFO
        address = bytes(info[10:16])
        if address not in self.addresses:
            raise ProbeError('Kernel radio address differs from both captured identities')
        return mac(address[::-1])

    def query(self, opcode, data=b''):
        data = bytes(data)
        allowed = (opcode in (0x1001, 0x1009, 0x0C23, 0x0C03) and not data)
        allowed |= opcode == 0x0C24 and data in self.classes
        allowed |= opcode == BARROT_OPCODE and (data == b'\x05\x00' or
                    (data[:2] == b'\x05\x00' and data[2:] in self.addresses))
        if not allowed:
            raise ProbeError('Blocked HCI command outside the identity/HID setup allowlist')
        self.stream.setblocking(False)
        try:
            while self.stream.recv(1024):
                pass
        except BlockingIOError:
            pass
        self.stream.settimeout(3)
        packet = b'\x01' + struct.pack('<HB', opcode, len(data)) + data
        print('HCI TX', packet.hex(' '), flush=True)
        if self.stream.send(packet) != len(packet):
            raise ProbeError('Short raw HCI send')
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            self.stream.settimeout(max(0.01, deadline - time.monotonic()))
            raw = self.stream.recv(1024)
            print('HCI RX', raw.hex(' '), flush=True)
            if not raw or raw[0] != 4:
                continue
            reply = parse_complete(raw[1:], opcode)
            if reply is not None:
                return reply
        raise ProbeError('Raw HCI response deadline exceeded')

    def address(self, command, *, address=None):
        if command != 5:
            raise ProbeError('Only the Barrot address parameter is permitted')
        if address is not None and bytes(address) not in self.addresses:
            raise ProbeError('Address is not a captured identity')
        response = self.query(BARROT_OPCODE, b'\x05\x00' + (bytes(address) if address is not None else b''))
        expected = 8 if address is None else 2
        if len(response) != expected or response[:2] != b'\x05\x00':
            raise ProbeError('Unexpected Barrot address response')
        return response[2:]

    def activate(self):
        self.query(0x0C03)
        if self.query(0x1009) != self.address(5):
            raise ProbeError('Standard and vendor address reads disagree after reset')
        print('Kernel address for socket binding:', self.kernel_address(), flush=True)

    def close(self):
        try:
            # Flush this dedicated radio's cached ACLs before the next attempt.
            self.fcntl.ioctl(self.stream.fileno(), 0x400448CA, self.index)  # HCIDEVDOWN
        except OSError as exc:
            print('Radio idle transition:', exc, flush=True)
        finally:
            self.stream.close()


def hid_socket(local, psm):
    stream = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
    try:
        stream.setsockopt(6, 3, struct.pack('<I', 1))  # L2CAP_LM_MASTER only
        options = bytearray(stream.getsockopt(6, 1, 32))
        if len(options) < 4:
            raise ProbeError('Unexpected L2CAP options layout')
        struct.pack_into('<H', options, 2, 1024)
        stream.setsockopt(6, 1, options)
        stream.setsockopt(274, 9, b'\x00')  # BT_POWER.force_active off, as in GIMX
        stream.bind((local, 0))
        stream.settimeout(8)
        return stream
    except BaseException:
        stream.close()
        raise


def connect_hid(radio, pair, press_ps):
    radio.query(0x0C24, b'\x08\x05\x00')
    if radio.query(0x0C23) != b'\x08\x05\x00':
        raise ProbeError('Controller Class of Device did not verify')
    local = radio.kernel_address()
    hid = DS3Hid(captured_f2=bytes.fromhex(pair['report_f2']))
    channels = []
    try:
        control = hid_socket(local, 0x11)
        channels.append(control)
        print('Connecting HID control PSM 0x11...', flush=True)
        control.connect((pair['console_mac'], 0x11))
        print('HID control connected.', flush=True)
        interrupt = hid_socket(local, 0x13)
        channels.append(interrupt)
        interrupt.setblocking(False)
        code = interrupt.connect_ex((pair['console_mac'], 0x13))
        if code not in (0, errno.EINPROGRESS, errno.EWOULDBLOCK, errno.EALREADY):
            raise OSError(code, 'HID interrupt connection failed')
        connected = code == 0
        deadline = time.monotonic() + 8
        pressed_at = None
        last_report = 0.0
        while time.monotonic() < deadline and not hid.shutdown_requested:
            readable, writable, _ = select.select([control] + ([interrupt] if connected else []),
                                                  [] if connected else [interrupt], [], 0.01)
            if writable:
                code = interrupt.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if code:
                    raise OSError(code, 'HID interrupt connection failed')
                connected = True
                print('HID interrupt connected.', flush=True)
            for stream in readable:
                payload = stream.recv(1024)
                if not payload:
                    raise ProbeError('HID peer closed its channel')
                print('HID RX', payload.hex(' '), flush=True)
                if stream is control:
                    response = hid.handle_control(payload)
                    if response is not None:
                        control.send(response)
                        print('HID TX', response.hex(' '), flush=True)
            now = time.monotonic()
            if connected and now - last_report >= 0.01:
                if press_ps and pressed_at is None:
                    pressed_at = now
                pressed = press_ps and now - pressed_at < 0.12
                interrupt.send(hid.input_report(ps_pressed=pressed))
                last_report = now
        if not connected:
            raise ProbeError('HID interrupt channel did not connect')
        print('HID connection held while the controller identity remained active.', flush=True)
    finally:
        for stream in reversed(channels):
            stream.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--wake', action='store_true')
    mode.add_argument('--restore-only', action='store_true')
    parser.add_argument('--press-ps', action='store_true')
    args = parser.parse_args()
    if not sys.platform.startswith('linux'):
        raise ProbeError('HID wake requires the Linux backend')
    pair = load_pairing()
    radio = KernelRadio(pair)
    previous_class = None
    error = None
    checkpoint = Path(__file__).resolve().parents[1] / 'local_only' / 'bt_hid_original_class.json'
    try:
        version = radio.query(0x1001)
        if len(version) != 8 or int.from_bytes(version[4:6], 'little') != BARROT:
            raise ProbeError('Unexpected radio manufacturer')
        previous_class = radio.query(0x0C23)
        if len(previous_class) != 3:
            raise ProbeError('Invalid original Class of Device')
        import json
        if args.restore_only and checkpoint.is_file():
            saved = json.loads(checkpoint.read_text())
            if saved['adapter_mac'] != pair['adapter_mac']:
                raise ProbeError('Saved class belongs to another adapter')
            previous_class = bytes.fromhex(saved['class'])
            if len(previous_class) != 3:
                raise ProbeError('Invalid saved Class of Device')
        elif not args.restore_only:
            checkpoint.write_text(json.dumps({'adapter_mac': pair['adapter_mac'], 'class': previous_class.hex()}))
        radio.classes.add(previous_class)
        original = mac_bytes(pair['adapter_mac'])
        if args.restore_only:
            radio.address(5, address=original)
            radio.activate()
            if radio.address(5) != original:
                raise ProbeError('Original address recovery did not verify')
        else:
            try:
                spoof_and_page(radio.address, pair, lambda *_: connect_hid(radio, pair, args.press_ps),
                               activate=radio.activate)
            except (OSError, ProbeError) as exc:
                error = exc
    finally:
        try:
            if previous_class is not None:
                radio.query(0x0C24, previous_class)
                if radio.query(0x0C23) != previous_class:
                    raise ProbeError('Original Class of Device did not verify')
        finally:
            radio.close()
    if args.restore_only:
        print('PROVEN: original radio address and class restored.', flush=True)
        return 0
    if error:
        print('HID attempt result:', error, flush=True)
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if webman_status()[0]:
            print('PROVEN: PS3 webMAN is online after the HID wake attempt.', flush=True)
            return 0
        time.sleep(2)
    print('UNKNOWN: no PS3 boot confirmation after HID wake.', flush=True)
    return 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ProbeError, OSError) as exc:
        print('STOP:', exc, file=sys.stderr, flush=True)
        raise SystemExit(1)
