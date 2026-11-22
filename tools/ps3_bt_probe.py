"""Read-only PS3 Bluetooth diagnostics. Never changes pairing, drivers or power.

Windows: assign WinUSB or libusbK only to external USB device 0A12:0001 before
running `probe`. `controller` uses the DS3's existing HID driver instead.
Protocol references: BlueZ HCI definitions, pywakepsx-on-bt/usb.py, and
https://github.com/tryger/barrot-tools/blob/main/doc/hci_vsc/Communication.md
Barrot support on the owner's dongle is UNKNOWN until this probe succeeds.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
import time

USB_ID = (0x0A12, 0x0001)
BARROT = 2279
READ_VERSION = 0x1001
READ_ADDRESS = 0x1009
BARROT_OPCODE = 0xFC80


class ProbeError(Exception):
    pass


def windows_dongle_status():
    """Read PnP status even when libusb cannot enumerate a failed driver."""
    if os.name != 'nt':
        return None
    import ctypes as ct
    import winreg
    from ctypes import wintypes as wt

    cfg = ct.WinDLL('cfgmgr32')
    cfg.CM_Get_Device_ID_List_SizeW.argtypes = [ct.POINTER(wt.ULONG), wt.LPCWSTR, wt.ULONG]
    cfg.CM_Get_Device_ID_List_SizeW.restype = wt.ULONG
    cfg.CM_Get_Device_ID_ListW.argtypes = [wt.LPCWSTR, wt.LPWSTR, wt.ULONG, wt.ULONG]
    cfg.CM_Get_Device_ID_ListW.restype = wt.ULONG
    cfg.CM_Locate_DevNodeW.argtypes = [ct.POINTER(wt.ULONG), wt.LPCWSTR, wt.ULONG]
    cfg.CM_Locate_DevNodeW.restype = wt.ULONG
    cfg.CM_Get_DevNode_Status.argtypes = [ct.POINTER(wt.ULONG), ct.POINTER(wt.ULONG), wt.ULONG, wt.ULONG]
    cfg.CM_Get_DevNode_Status.restype = wt.ULONG
    flags = 0x101  # CM_GETIDLIST_FILTER_ENUMERATOR | CM_GETIDLIST_FILTER_PRESENT
    size = wt.ULONG()
    if cfg.CM_Get_Device_ID_List_SizeW(ct.byref(size), 'USB', flags):
        return None
    ids = ct.create_unicode_buffer(size.value)
    if cfg.CM_Get_Device_ID_ListW('USB', ids, size.value, flags):
        return None
    result = []
    for instance in ids[:].split('\0'):
        if not instance.upper().startswith('USB\\VID_0A12&PID_0001\\'):
            continue
        devnode, status, problem = wt.ULONG(), wt.ULONG(), wt.ULONG()
        if cfg.CM_Locate_DevNodeW(ct.byref(devnode), instance, 0):
            return None
        if cfg.CM_Get_DevNode_Status(ct.byref(status), ct.byref(problem), devnode, 0):
            return None
        service = 'unknown'
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                'SYSTEM\\CurrentControlSet\\Enum\\' + instance) as key:
                service = winreg.QueryValueEx(key, 'Service')[0]
        except OSError:
            pass
        result.append({'instance': instance, 'problem': problem.value, 'service': service})
    return result


def check_windows_dongle():
    devices = windows_dongle_status()
    if devices is None:
        return
    if not devices:
        raise ProbeError('Windows does not see a connected external 0A12:0001 dongle')
    if len(devices) != 1:
        raise ProbeError(f'Windows sees {len(devices)} matching dongles; connect exactly one')
    device = devices[0]
    if device['problem']:
        raise ProbeError(f"Windows sees external 0A12:0001, but driver {device['service']} "
                         f"has Device Manager Code {device['problem']}. "
                         'This is a driver startup failure; no Bluetooth commands were sent.')
    if device['service'].lower() == 'bthusb':
        raise ProbeError('External 0A12:0001 still uses BTHUSB. Direct USB access requires '
                         'a working WinUSB or libusbK binding on this external device.')


def mac(raw):
    raw = bytes(raw)
    if len(raw) != 6 or raw in (bytes(6), bytes([255]) * 6):
        raise ProbeError('No valid Bluetooth address in response')
    return ':'.join(f'{b:02X}' for b in raw)


def ds3_pairing(report_f2, report_f5):
    """F5's USB payload can start 01 00, rather than echoing the report ID."""
    f2, f5 = bytes(report_f2), bytes(report_f5)
    if len(f2) < 17 or f2[0] != 0xF2 or len(f5) < 8:
        raise ProbeError('Invalid DS3 pairing report lengths/header')
    if f5[0] not in (0x01, 0xF5) or f5[1] != 0:
        raise ProbeError('Unrecognized DS3 saved-host report header')
    controller, host = mac(f2[4:10]), mac(f5[2:8])
    if controller == host:
        raise ProbeError('Controller and saved-host addresses must differ')
    return {'controller_mac': controller, 'console_mac': host}


def parse_complete(event, opcode):
    """USB event bytes have no leading H4 packet-type byte."""
    event = bytes(event)
    if len(event) < 2 or len(event) != event[1] + 2:
        raise ProbeError(f'Malformed HCI event: {event.hex()}')
    if event[0] == 0x0F:  # Command Status; success still needs Command Complete.
        if len(event) != 6:
            raise ProbeError('Malformed Command Status')
        if int.from_bytes(event[4:6], 'little') == opcode and event[2]:
            raise ProbeError(f'HCI 0x{opcode:04X} rejected: status 0x{event[2]:02X}')
        return None
    if event[0] != 0x0E:
        return None
    if len(event) < 6:
        raise ProbeError('Short Command Complete')
    if int.from_bytes(event[3:5], 'little') != opcode:
        return None
    if event[5]:
        raise ProbeError(f'HCI 0x{opcode:04X} failed: status 0x{event[5]:02X}')
    return event[6:]


def hci_interface(config):
    """The SCO/audio interface can share HCI's class/subclass/protocol."""
    candidates = []
    for interface in config:
        if interface.bAlternateSetting != 0:
            continue
        if (interface.bInterfaceClass, interface.bInterfaceSubClass,
                interface.bInterfaceProtocol) != (0xE0, 1, 1):
            continue
        events = [e for e in interface if (e.bmAttributes & 3) == 3 and
                  (e.bEndpointAddress & 0x80)]
        if len(events) == 1:
            candidates.append((interface, events[0]))
    if len(candidates) != 1:
        raise ProbeError('Expected one HCI interface with an interrupt-IN endpoint')
    return candidates[0]


class HciReader:
    """Only permits the four identity queries used by this diagnostic."""

    def __init__(self):
        check_windows_dongle()
        import usb.core
        import usb.util

        self.usb = usb.core
        self.util = usb.util
        self.dev = None
        self.claimed = False
        self.detached = False
        found = list(usb.core.find(find_all=True, idVendor=USB_ID[0], idProduct=USB_ID[1]) or [])
        if len(found) != 1:
            raise ProbeError(f'Expected one external 0A12:0001 dongle; found {len(found)}')
        self.dev = found[0]
        stage = 'opening the active USB configuration'
        try:
            config = self.dev.get_active_configuration()
            interface, self.events = hci_interface(config)
            self.interface = interface.bInterfaceNumber
            stage = f'claiming HCI interface {self.interface}'
            if sys.platform.startswith('linux') and self.dev.is_kernel_driver_active(self.interface):
                self.dev.detach_kernel_driver(self.interface)
                self.detached = True
            usb.util.claim_interface(self.dev, self.interface)
            self.claimed = True
        except Exception as exc:
            self.close()
            if isinstance(exc, (OSError, NotImplementedError)):
                raise ProbeError(f'USB access failed while {stage}: {exc}. '
                                 'Check Device Manager for Code 10; unplug/replug '
                                 'the external dongle after a driver change.') from exc
            raise

    def close(self):
        try:
            if self.claimed:
                self.util.release_interface(self.dev, self.interface)
                self.claimed = False
        finally:
            if self.dev is not None:
                try:
                    if self.detached:
                        self.dev.attach_kernel_driver(self.interface)
                        self.detached = False
                finally:
                    self.util.dispose_resources(self.dev)

    def query(self, opcode, parameters=b''):
        parameters = bytes(parameters)
        allowed = {(READ_VERSION, b''), (READ_ADDRESS, b''),
                   (BARROT_OPCODE, struct.pack('<H', 1)),
                   (BARROT_OPCODE, struct.pack('<H', 5))}
        if (opcode, parameters) not in allowed:
            raise ProbeError('Blocked: this diagnostic only permits identity reads')
        return self._exchange(opcode, parameters)

    def _exchange(self, opcode, parameters):
        packet = struct.pack('<HB', opcode, len(parameters)) + parameters
        print(f'TX {packet.hex(" ")}', flush=True)
        sent = self.dev.ctrl_transfer(0x20, 0, 0, 0, packet, timeout=2000)
        if sent != len(packet):
            raise ProbeError('Short USB command transfer')
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            remaining = max(1, int((deadline - time.monotonic()) * 1000))
            try:
                event = bytes(self.events.read(260, timeout=remaining))
            except self.usb.USBTimeoutError as exc:
                raise ProbeError(f'No reply to HCI 0x{opcode:04X}') from exc
            print(f'RX {event.hex(" ")}', flush=True)
            result = parse_complete(event, opcode)
            if result is not None:
                return result
        raise ProbeError(f'No matching reply to HCI 0x{opcode:04X}')


def probe():
    reader = HciReader()
    try:
        version = reader.query(READ_VERSION)
        if len(version) != 8:
            raise ProbeError('Unexpected local version response length')
        hci, revision, lmp, manufacturer, subversion = struct.unpack('<BHBHH', version)
        print(f'Manufacturer: {manufacturer} (0x{manufacturer:04X})')
        print(f'HCI version/revision: {hci}/{revision:04X}; LMP: {lmp}/{subversion:04X}')
        address = reader.query(READ_ADDRESS)
        print(f'Dongle Bluetooth address: {mac(address[::-1])}')
        if manufacturer != BARROT:
            raise ProbeError('Unexpected manufacturer; no vendor command sent')
        chip = reader.query(BARROT_OPCODE, struct.pack('<H', 1))
        if len(chip) < 28 or chip[:2] != b'\x01\x00' or chip[2:5] != b'BRT':
            raise ProbeError('Barrot chip-version layout unrecognized; stop here')
        model = int.from_bytes(chip[6:10], 'little')
        print(f'Barrot chip code: 0x{model:08X}')
        if len(chip) > 28:
            print(f'Uninterpreted chip-info extension: {chip[28:].hex(" ")}')
        vendor_address = reader.query(BARROT_OPCODE, struct.pack('<H', 5))
        if len(vendor_address) != 8 or vendor_address[:2] != b'\x05\x00':
            raise ProbeError('Barrot address-query layout unrecognized')
        if vendor_address[2:] != address:
            raise ProbeError('Standard and Barrot address queries disagree')
        print('PROVEN: USB HCI access and Barrot identity/address queries work.')
        print('UNKNOWN: address changing and PS3 wake; neither was attempted.')
    finally:
        reader.close()


def controller():
    import hid

    devices = hid.enumerate(0x054C, 0x0268)
    if not devices:
        raise ProbeError('Connect the DualShock 3 paired with this PS3 to the PC by USB')
    errors = []
    identities = set()
    for device in devices:
        handle = hid.device()
        try:
            handle.open_path(device['path'])
            reports = {}
            for report_id, minimum in ((0xF2, 17), (0xF5, 8)):
                for length in (minimum, 49):
                    try:
                        data = bytes(handle.get_feature_report(report_id, length))
                        valid_header = (data and (data[0] == report_id or
                                        (report_id == 0xF5 and data[0] == 1)))
                        if len(data) >= minimum and valid_header:
                            reports[report_id] = data
                            break
                    except OSError:
                        pass
            if len(reports) != 2:
                raise ProbeError('F2/F5 pairing reports unavailable through the current HID driver/controller')
            pair = ds3_pairing(reports[0xF2], reports[0xF5])
            identities.add((pair['controller_mac'], pair['console_mac']))
        except (OSError, ProbeError) as exc:
            errors.append(str(exc))
        finally:
            handle.close()
    if len(identities) != 1:
        raise ProbeError('Could not identify exactly one controller/console pair: ' + '; '.join(errors))
    ds3, ps3 = identities.pop()
    print(f'Controller Bluetooth address: {ds3}')
    print(f'Paired PS3 Bluetooth address: {ps3}')
    print('Pairing unchanged; these values came from USB feature reports.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('probe', 'controller'))
    args = parser.parse_args()
    try:
        {'probe': probe, 'controller': controller}[args.action]()
    except (ProbeError, ImportError, OSError, NotImplementedError) as exc:
        print(f'STOP: {exc}', file=sys.stderr)
        if args.action == 'probe':
            print('Target: external USB 0A12:0001. Leave MediaTek 0489:E0F6 alone.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
