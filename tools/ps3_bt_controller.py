"""Bounded DS3 button test over the existing isolated raw-USB Bluetooth backend.

Experimental: ACL/L2CAP protocol checks are offline; console acceptance must be
observed separately. No pairing writes, console shutdown, or smart-plug actions.
Uses only the captured controller/console identities and restores the radio.
Wire references: GIMX sixaxis.c/ds3.h and Bluetooth Core L2CAP basic mode.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import signal
import struct
import sys
import threading
import time

from ps3_bt_probe import BARROT, ProbeError, READ_ADDRESS, READ_VERSION
from ps3_ds3_hid import DS3Hid

ROOT = Path(__file__).resolve().parents[1]
BUTTONS = {
    'select': (3, 1, None), 'start': (3, 8, None),
    'up': (3, 16, 15), 'right': (3, 32, 16),
    'down': (3, 64, 17), 'left': (3, 128, 18),
    'l2': (4, 1, 19), 'r2': (4, 2, 20),
    'l1': (4, 4, 21), 'r1': (4, 8, 22),
    'triangle': (4, 16, 23), 'circle': (4, 32, 24),
    'cross': (4, 64, 25), 'square': (4, 128, 26),
    'ps': (5, 1, None),
}


def button_report(hid, button=None):
    report = bytearray(hid.input_report())
    if button is not None:
        offset, mask, pressure = BUTTONS[button]
        report[offset] |= mask
        if pressure is not None:
            report[pressure] = 255
    return bytes(report)


class L2capHid:
    """One basic-mode HID link. All outgoing SDUs remain queued for HCI credits."""

    def __init__(self, hid):
        self.hid = hid
        self.channels = {}
        self.pending = {}
        self.outgoing = deque()
        self.identifier = 0
        self.closed = False

    def signal(self, code, payload, identifier=None):
        if identifier is None:
            for _ in range(255):
                self.identifier = self.identifier % 255 + 1
                if self.identifier not in self.pending:
                    break
            else:
                raise ProbeError('L2CAP signaling identifiers exhausted')
            identifier = self.identifier
        self.outgoing.append((1, struct.pack('<BBH', code, identifier, len(payload)) + payload))
        print('L2CAP TX', code, identifier, payload.hex(' '), flush=True)
        return identifier

    def connect(self, psm):
        if psm not in (0x11, 0x13) or any(c['psm'] == psm for c in self.channels.values()):
            raise ProbeError('Duplicate or unsupported HID channel')
        cid = 0x40 if psm == 0x11 else 0x41
        self.channels[cid] = dict(psm=psm, remote=None, local_ok=False, peer_ok=False, mtu=672)
        identifier = self.signal(2, struct.pack('<HH', psm, cid))
        self.pending[identifier] = (2, cid)

    def configure(self, cid):
        remote = self.channels[cid]['remote']
        identifier = self.signal(4, struct.pack('<HHBBH', remote, 0, 1, 2, 1024))
        self.pending[identifier] = (4, cid)

    def ready(self, psm):
        return any(c['psm'] == psm and c['remote'] is not None and
                   c['local_ok'] and c['peer_ok'] for c in self.channels.values())

    def send(self, psm, payload):
        channel = next((c for c in self.channels.values() if c['psm'] == psm), None)
        if not self.ready(psm) or len(payload) > channel['mtu']:
            raise ProbeError('HID channel not configured or SDU exceeds peer MTU')
        self.outgoing.append((channel['remote'], bytes(payload)))

    def receive(self, cid, payload):
        if cid == 1:
            self._signaling(bytes(payload))
            return
        channel = self.channels.get(cid)
        if channel is None or not self.ready(channel['psm']):
            raise ProbeError('Data on an unconfigured L2CAP channel')
        print('HID RX', hex(channel['psm']), payload.hex(' '), flush=True)
        if channel['psm'] == 0x11:
            reply = self.hid.handle_control(payload)
            if reply is not None:
                self.send(0x11, reply)
                print('HID TX', reply.hex(' '), flush=True)

    def _signaling(self, data):
        while data:
            if len(data) < 4:
                raise ProbeError('Truncated L2CAP signaling header')
            code, identifier, length = struct.unpack_from('<BBH', data)
            if identifier == 0 or len(data) < length + 4:
                raise ProbeError('Invalid L2CAP signaling length/identifier')
            payload, data = data[4:4 + length], data[4 + length:]
            print('L2CAP RX', code, identifier, payload.hex(' '), flush=True)
            if code == 3:  # Connection response: DCID, SCID, result, status.
                if len(payload) != 8:
                    raise ProbeError('Invalid L2CAP connection response')
                remote, cid, result, status = struct.unpack('<HHHH', payload)
                if self.pending.get(identifier) != (2, cid):
                    raise ProbeError('Unmatched L2CAP connection response')
                if result == 1:
                    continue
                if result or status or remote < 0x40 or any(
                        c['remote'] == remote for c in self.channels.values()):
                    raise ProbeError(f'L2CAP channel rejected: result={result}, status={status}')
                del self.pending[identifier]
                self.channels[cid]['remote'] = remote
                self.configure(cid)
            elif code == 4:  # Peer configuration request for our destination CID.
                if len(payload) < 4:
                    raise ProbeError('Truncated L2CAP configuration request')
                cid, flags = struct.unpack_from('<HH', payload)
                if cid not in self.channels or flags:
                    raise ProbeError('Unknown CID or continued configuration unsupported')
                channel = self.channels[cid]
                options, unknown = payload[4:], bytearray()
                while options:
                    if len(options) < 2 or len(options) < options[1] + 2:
                        raise ProbeError('Truncated L2CAP configuration option')
                    kind, length = options[:2]
                    value, whole = options[2:2 + length], options[:2 + length]
                    options = options[2 + length:]
                    if kind & 0x7F == 1 and length == 2:
                        channel['mtu'] = int.from_bytes(value, 'little')
                        if channel['mtu'] < 50:
                            raise ProbeError('Peer MTU cannot carry DS3 reports')
                    elif kind & 0x7F == 2 and length == 2:
                        pass  # Flush timeout; no retransmission mode is enabled.
                    elif kind & 0x7F == 4 and length == 9 and value[0] == 0:
                        pass  # Basic mode only.
                    elif not kind & 0x80:
                        unknown.extend(whole)
                result = 3 if unknown else 0
                self.signal(5, struct.pack('<HHH', channel['remote'], 0, result) + unknown, identifier)
                channel['peer_ok'] = not unknown
            elif code == 5:
                if len(payload) < 6:
                    raise ProbeError('Truncated L2CAP configuration response')
                pending = self.pending.get(identifier)
                if not pending or pending[0] != 4:
                    raise ProbeError('Unmatched L2CAP configuration response')
                cid, flags, result = struct.unpack_from('<HHH', payload)
                if cid != pending[1] or flags or result not in (0, 4):
                    raise ProbeError(f'L2CAP configuration failed: {payload.hex()}')
                if result == 0:
                    del self.pending[identifier]
                    self.channels[cid]['local_ok'] = True
            elif code == 6:
                if len(payload) != 4:
                    raise ProbeError('Invalid L2CAP disconnect request')
                cid, remote = struct.unpack('<HH', payload)
                if cid not in self.channels or self.channels[cid]['remote'] != remote:
                    raise ProbeError('Disconnect for another channel')
                self.signal(7, payload, identifier)
                self.closed = True
            elif code == 8:
                self.signal(9, payload, identifier)
            elif code == 10:
                if len(payload) != 2:
                    raise ProbeError('Invalid L2CAP information request')
                kind = int.from_bytes(payload, 'little')
                info = {1: struct.pack('<H', 672), 2: bytes(4), 3: bytes((2,)) + bytes(7)}.get(kind)
                self.signal(11, payload + struct.pack('<H', int(info is None)) + (info or b''), identifier)
            elif code == 2:
                if len(payload) != 4:
                    raise ProbeError('Invalid incoming connection request')
                _, remote = struct.unpack('<HH', payload)
                self.signal(3, struct.pack('<HHHH', 0, remote, 4, 0), identifier)
            elif code in (1, 7, 9, 11):
                if code == 1 and identifier in self.pending:
                    raise ProbeError('Peer rejected our L2CAP signaling command')
            else:
                self.signal(1, bytes(2), identifier)


class AclReceiver:
    """Reassemble ACL fragments only for this connection, with bounded buffers."""

    def __init__(self, handle, receive):
        self.handle = handle
        self.receive = receive
        self.usb_buffer = bytearray()
        self.sdu = None

    def feed(self, data):
        self.usb_buffer.extend(data)
        if len(self.usb_buffer) > 8192:
            raise ProbeError('USB ACL stream exceeds bound')
        while len(self.usb_buffer) >= 4:
            flags, length = struct.unpack_from('<HH', self.usb_buffer)
            if length > 4096:
                raise ProbeError('Oversized ACL fragment')
            if len(self.usb_buffer) < length + 4:
                return
            payload = bytes(self.usb_buffer[4:4 + length])
            del self.usb_buffer[:4 + length]
            if flags & 0xFFF != self.handle:
                raise ProbeError('ACL packet for an unexpected connection')
            boundary = flags >> 12 & 3
            if boundary in (0, 2):
                if self.sdu is not None:
                    raise ProbeError('New ACL start before previous SDU completed')
                self.sdu = bytearray(payload)
            elif boundary == 1 and self.sdu is not None:
                self.sdu.extend(payload)
            else:
                raise ProbeError('Unexpected ACL packet boundary')
            if len(self.sdu) < 4:
                continue
            wanted, cid = struct.unpack_from('<HH', self.sdu)
            if wanted > 2048 or len(self.sdu) > wanted + 4:
                raise ProbeError('Invalid or oversized L2CAP SDU')
            if len(self.sdu) == wanted + 4:
                packet, self.sdu = bytes(self.sdu[4:]), None
                self.receive(cid, packet)


class UsbInputs:
    """Keep USBIP reads outstanding instead of repeatedly cancelling tiny URBs.

    Stop and join both readers before any synchronous HCI cleanup command can
    run, so they cannot consume an address-restoration completion event.
    """

    def __init__(self, radio, bulk):
        self.radio = radio
        self.stopped = threading.Event()
        self.events, self.acl, self.errors = queue.Queue(256), queue.Queue(256), queue.Queue()
        self.readers = [threading.Thread(target=self._read, args=(endpoint, size, target), daemon=True)
                        for endpoint, size, target in ((radio.events, 260, self.events), (bulk, 4096, self.acl))]

    def _read(self, endpoint, size, target):
        while not self.stopped.is_set():
            try:
                data = bytes(endpoint.read(size, timeout=200))
                if data:
                    target.put_nowait(data)
            except self.radio.usb.USBTimeoutError:
                continue
            except Exception as exc:
                self.errors.put(exc)
                self.stopped.set()

    def take(self, target):
        if not self.errors.empty():
            raise ProbeError('USB input reader failed: ' + str(self.errors.get()))
        try:
            return target.get_nowait()
        except queue.Empty:
            return None

    def __enter__(self):
        for reader in self.readers:
            reader.start()
        return self

    def __exit__(self, *_):
        self.stopped.set()
        for reader in self.readers:
            reader.join(timeout=2)
        if any(reader.is_alive() for reader in self.readers):
            raise ProbeError('USB reader did not stop before identity restoration')


def run_link(radio, pair, args):
    from ps3_bt_linux import connection_event, connection_packet
    from ps3_bt_wake import mac_bytes
    endpoints = list(radio.dev.get_active_configuration()[(radio.interface, 0)])
    incoming = [e for e in endpoints if e.bmAttributes & 3 == 2 and e.bEndpointAddress & 0x80]
    outgoing = [e for e in endpoints if e.bmAttributes & 3 == 2 and not e.bEndpointAddress & 0x80]
    if len(incoming) != 1 or len(outgoing) != 1:
        raise ProbeError('Expected one bulk-IN and one bulk-OUT HCI endpoint')
    capacity = radio._exchange(0x1005, b'')  # Read Buffer Size, before the live link.
    if len(capacity) != 7:
        raise ProbeError('Unexpected Read Buffer Size response')
    acl_size, _, total, _ = struct.unpack('<HBHH', capacity)
    if acl_size < 8 or not total:
        raise ProbeError('Invalid controller ACL capacity')
    print('ACL capacity:', acl_size, total, flush=True)
    packet = connection_packet(pair['console_mac'])
    if radio.dev.ctrl_transfer(0x20, 0, 0, 0, packet, timeout=2000) != len(packet):
        raise ProbeError('Short Create Connection transfer')
    deadline = time.monotonic() + 8
    handle = None
    while time.monotonic() < deadline:
        try:
            event = bytes(radio.events.read(260, timeout=max(1, int((deadline - time.monotonic()) * 1000))))
        except radio.usb.USBTimeoutError as exc:
            raise ProbeError('No Connection Complete within eight seconds') from exc
        print('HCI RX', event.hex(' '), flush=True)
        result = connection_event(event, mac_bytes(pair['console_mac']))
        if result is not None:
            status, handle = result
            if status or handle is None:
                raise ProbeError(f'ACL connection failed: {status}')
            break
    if handle is None:
        raise ProbeError('No matching ACL connection completion')
    with UsbInputs(radio, incoming[0]) as inputs:
        return link_loop(radio, pair, args, outgoing[0], acl_size, total, inputs, handle)


def link_loop(radio, pair, args, outgoing, acl_size, total, inputs, handle):
    from ps3_bt_linux import connection_event, connection_packet
    from ps3_bt_wake import mac_bytes
    hid = DS3Hid(captured_f2=bytes.fromhex(pair['report_f2']))
    link = L2capHid(hid)
    target = mac_bytes(pair['console_mac'])
    receiver = AclReceiver(handle, link.receive)
    link.connect(0x11)
    credits, outstanding = total, 0
    fragments = deque()
    started = time.monotonic()
    connected_at = report_at = pressed_at = None
    sent_press = released = False
    while time.monotonic() - started < args.seconds:
        event = inputs.take(inputs.events)
        if event is not None:
            if len(event) < 2 or len(event) != event[1] + 2:
                raise ProbeError('Malformed HCI event')
            print('HCI RX', event.hex(' '), flush=True)
            result = connection_event(event, target)
            if result is not None:
                raise ProbeError('Unexpected duplicate ACL connection event')
            if event[0] == 0x13:
                if len(event) < 3 or len(event) != 3 + 4 * event[2]:
                    raise ProbeError('Malformed Number Of Completed Packets')
                for i in range(event[2]):
                    completed_handle, count = struct.unpack_from('<HH', event, 3 + 4 * i)
                    if completed_handle == handle:
                        if count > outstanding:
                            raise ProbeError('Controller completed more packets than submitted')
                        outstanding -= count
                        credits += count
            elif event[0] == 5 and len(event) == 6 and int.from_bytes(event[3:5], 'little') == handle:
                raise ProbeError(f'Console disconnected ACL: reason 0x{event[5]:02X}')
            elif event[0] in (0x16, 0x17):  # PIN / link-key request, never invent a key.
                if len(event) != 8 or event[2:] != target:
                    raise ProbeError('Authentication request from an unexpected peer')
                opcode = 0x040E if event[0] == 0x16 else 0x040C
                reply = struct.pack('<HB', opcode, 6) + target
                if radio.dev.ctrl_transfer(0x20, 0, 0, 0, reply, timeout=2000) != len(reply):
                    raise ProbeError('Short negative authentication reply')
        if receiver is not None:
            data = inputs.take(inputs.acl)
            if data is not None:
                receiver.feed(data)
        now = time.monotonic()
        if link.ready(0x11) and not any(c['psm'] == 0x13 for c in link.channels.values()):
            print('HID CONTROL CONFIGURED', flush=True)
            link.connect(0x13)
        # GIMX sends periodic reports as soon as both channels are configured;
        # its reporting_enabled field is recorded but does not gate input TX.
        if link.ready(0x11) and link.ready(0x13):
            if connected_at is None:
                connected_at = now
                print('HID READY: both channels configured; starting input reports.', flush=True)
                print('Initial PS press to register the controller, then release.', flush=True)
            if args.button and pressed_at is None and now - connected_at >= 2:
                pressed_at = now
            pressed = pressed_at is not None and now - pressed_at < args.duration
            if report_at is None or now - report_at >= 0.01:
                # Skip a sample while transport is backlogged; never queue stale presses.
                if not fragments and not link.outgoing and credits:
                    initial_ps = now - connected_at < 0.2
                    link.send(0x13, button_report(hid, 'ps' if initial_ps else args.button if pressed else None))
                    report_at = now
                    if pressed and not sent_press:
                        print('BUTTON PRESS', args.button, flush=True)
                        sent_press = True
                    if sent_press and not pressed and not released:
                        print('BUTTON RELEASE', args.button, flush=True)
                        released = True
        while link.outgoing:
            cid, payload = link.outgoing.popleft()
            sdu = struct.pack('<HH', len(payload), cid) + payload
            for offset in range(0, len(sdu), acl_size):
                fragment = sdu[offset:offset + acl_size]
                fragments.append(struct.pack('<HH', handle | (0x2000 if offset == 0 else 0x1000),
                                             len(fragment)) + fragment)
        while fragments and credits:
            fragment = fragments.popleft()
            if outgoing.write(fragment, timeout=1000) != len(fragment):
                raise ProbeError('Short outgoing ACL transfer')
            credits -= 1
            outstanding += 1
        if link.closed or hid.shutdown_requested:
            raise ProbeError('Console requested HID disconnection/shutdown')
        if handle is None and now - started > 10:
            raise ProbeError('No ACL connection within ten seconds')
        time.sleep(0.001)
    if connected_at is None or (args.button and not released):
        raise ProbeError('HID channel/button test did not complete within bound')
    print('PROVEN: HID negotiation and report transport completed; inspect video for button acceptance.', flush=True)


def linux_main(args):
    from ps3_bt_linux import LinuxRadio, wait_for_usb
    from ps3_bt_wake import load_pairing, mac_bytes, spoof_and_page
    pair = load_pairing()
    wait_for_usb()
    radio = LinuxRadio(pair, keep_kernel_detached=True)
    previous = None
    original_name = None
    try:
        version = radio.query(READ_VERSION)
        if len(version) != 8 or int.from_bytes(version[4:6], 'little') != BARROT:
            raise ProbeError('Unexpected external radio manufacturer')
        original = mac_bytes(pair['adapter_mac'])
        if radio.query(READ_ADDRESS) != original or radio.address(5) != original:
            raise ProbeError('Radio not at its captured original identity; run backend recovery')
        previous = radio.class_of_device()
        state_file = ROOT / 'local_only' / 'ps3_bt_radio_state.json'
        if not state_file.is_file():
            raise ProbeError('Original radio class checkpoint missing; prepare the backend first')
        saved = json.loads(state_file.read_text())
        if saved['adapter_mac'] != pair['adapter_mac'] or previous != bytes.fromhex(saved['class']):
            raise ProbeError('Radio class differs from saved original; run backend recovery')
        radio.class_values.add(previous)
        original_name = radio._exchange(0x0C14, b'')
        if len(original_name) != 248:
            raise ProbeError('Unexpected original Bluetooth local-name length')
        name_checkpoint = ROOT / 'local_only' / 'bt_controller_original_name.json'
        name_checkpoint.write_text(json.dumps({'adapter_mac': pair['adapter_mac'],
                                               'name_hex': original_name.hex()}, indent=2))

        def connect(*_):
            radio.class_of_device(b'\x08\x05\x00')
            if radio.class_of_device() != b'\x08\x05\x00':
                raise ProbeError('Controller class did not verify')
            name = b'PLAYSTATION(R)3 Controller'.ljust(248, b'\x00')
            if radio._exchange(0x0C13, name) or radio._exchange(0x0C14, b'') != name:
                raise ProbeError('Temporary controller local name did not verify')
            run_link(radio, pair, args)

        spoof_and_page(radio.address, pair, connect, activate=radio.activate)
    finally:
        try:
            try:
                if original_name is not None:
                    if radio._exchange(0x0C13, original_name) or radio._exchange(0x0C14, b'') != original_name:
                        raise ProbeError('Original Bluetooth name restoration failed')
            finally:
                if previous is not None:
                    radio.class_of_device(previous)
                    if radio.class_of_device() != previous:
                        raise ProbeError('Original radio class restoration failed')
        finally:
            radio.close()


def windows_main(args):
    from ps3_bt_power import (DISTRO, _exclusive_radio, ensure_backend, _run, _decode,
                              _linux_worker_path, _worker)
    log_path = ROOT / 'local_only' / 'logs' / ('bt_controller_' +
               datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.log')
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with _exclusive_radio(), log_path.open('wb') as log:
        ensure_backend(log)
        resolved = _run(['wsl.exe', '-d', DISTRO, '-u', 'root', '--exec', 'wslpath', '-u',
                         Path(__file__).resolve().as_posix()], log, timeout=10, capture=True)
        path = _decode(resolved.stdout).strip()
        if resolved.returncode or not path.startswith('/') or '\n' in path or '\r' in path:
            raise ProbeError('Could not resolve controller worker path')
        command = ['wsl.exe', '-d', DISTRO, '-u', 'root', '--exec', 'timeout',
                   '--signal=TERM', '--kill-after=10s', str(args.seconds + 25) + 's',
                   'python3', '-B', path, '--seconds', str(args.seconds), '--duration', str(args.duration)]
        if args.button:
            command.extend(['--button', args.button])
        try:
            result = _run(command, log, timeout=args.seconds + 40)
        finally:
            restored = _worker(_linux_worker_path(log), '--restore-only', log) == 0
    print('Controller diagnostic log:', log_path)
    return result.returncode if restored else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--button', choices=BUTTONS)
    parser.add_argument('--duration', type=float, default=0.15)
    parser.add_argument('--seconds', type=int, default=15)
    args = parser.parse_args()
    if not 5 <= args.seconds <= 60 or not 0.05 <= args.duration <= 3:
        parser.error('Use 5..60 seconds and a button duration of 0.05..3 seconds')
    if sys.platform == 'win32':
        return windows_main(args)
    if not sys.platform.startswith('linux'):
        raise ProbeError('Controller backend requires Windows + WSL or Linux')
    def terminated(*_):
        raise ProbeError('Bounded controller worker terminated; restoring identity')
    signal.signal(signal.SIGTERM, terminated)
    linux_main(args)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ProbeError, OSError, ValueError, KeyError) as exc:
        print('STOP:', exc, file=sys.stderr, flush=True)
        raise SystemExit(1)
